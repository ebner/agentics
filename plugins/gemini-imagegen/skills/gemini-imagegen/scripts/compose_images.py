#!/usr/bin/env python3
"""
Compose multiple images into a new image using Gemini API.

Usage:
    python compose_images.py "instruction" output.png image1.png [image2.png ...]

Examples:
    python compose_images.py "Create a group photo" group.jpg person1.png person2.png
    python compose_images.py "Combine into collage" result.png --format png --transparent img1.png img2.png
    python compose_images.py "Apply style from first to second" styled.png style.png photo.png

Note: Supports up to 14 reference images (Gemini 3 Pro only).

Environment:
    GEMINI_API_KEY - Required API key
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image
from google import genai
from google.genai import types

from generate_image import make_transparent


def write_compose_prompt_sidecar(
    output_path: str,
    instruction: str,
    model: str,
    aspect_ratio: str | None,
    image_size: str | None,
    output_format: str,
    transparent: bool,
    tolerance: int,
    edge_tolerance: int,
    source_images: list[str],
) -> str:
    """Write a .prompt sidecar file for a composed image.

    Args:
        output_path: Path to the output image file
        instruction: The composition instruction used
        model: Model name used
        aspect_ratio: Aspect ratio if specified
        image_size: Resolution if specified
        output_format: Output format (png, jpg, webp)
        transparent: Whether transparency conversion was applied
        tolerance: Color tolerance used
        edge_tolerance: Edge tolerance used
        source_images: List of source image paths

    Returns:
        Path to the created .prompt file
    """
    prompt_path = Path(output_path).with_suffix(".prompt")

    # Build YAML frontmatter
    lines = ["---"]
    lines.append(f"model: {model}")
    if aspect_ratio:
        lines.append(f'aspect_ratio: "{aspect_ratio}"')
    if image_size:
        lines.append(f"resolution: {image_size}")
    lines.append(f"format: {output_format}")
    lines.append(f"transparent: {str(transparent).lower()}")
    if transparent:
        lines.append(f"tolerance: {tolerance}")
        lines.append(f"edge_tolerance: {edge_tolerance}")
    lines.append(f"date: {datetime.now(timezone.utc).isoformat()}")
    lines.append('version: "1.0"')
    lines.append("type: composition")

    # Add source images
    lines.append("")
    lines.append("source_images:")
    for img_path in source_images:
        lines.append(f'  - "{img_path}"')

    # Add composition instruction
    lines.append("")
    lines.append("final_prompt: |")
    for line in instruction.strip().split("\n"):
        lines.append(f"  {line}")

    # Empty edit history
    lines.append("")
    lines.append("edit_history: []")
    lines.append("---")

    prompt_path.write_text("\n".join(lines) + "\n")
    return str(prompt_path)


def compose_images(
    instruction: str,
    output_path: str,
    image_paths: list[str],
    model: str = "gemini-3.1-flash-image-preview",
    aspect_ratio: str | None = None,
    image_size: str | None = None,
    output_format: str = "jpg",
    transparent: bool = False,
    tolerance: int = 0,
    edge_tolerance: int = 0,
) -> str | None:
    """Compose multiple images based on instructions.

    Args:
        instruction: Text description of how to combine images
        output_path: Path to save the result
        image_paths: List of input image paths (up to 14)
        model: Gemini model to use (pro recommended)
        aspect_ratio: Output aspect ratio
        image_size: Output resolution
        output_format: Output format (png, jpg, webp)
        transparent: Whether to convert white background to transparent
        tolerance: Color tolerance for white detection (0-255)
        edge_tolerance: Edge expansion tolerance (0 = disabled)

    Returns:
        Any text response from the model, or None

    Raises:
        ValueError: If transparent is True but format is not PNG
        ValueError: If too many or too few images provided
        EnvironmentError: If GEMINI_API_KEY is not set
        FileNotFoundError: If any input image doesn't exist
        RuntimeError: If no image is generated
    """
    # Validate transparency requires PNG
    if transparent and output_format != "png":
        raise ValueError(
            f"Transparency requires PNG format, but got '{output_format}'. "
            "Use --format png with --transparent."
        )

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY environment variable not set")

    if len(image_paths) > 14:
        raise ValueError("Maximum 14 reference images supported")

    if len(image_paths) < 1:
        raise ValueError("At least one image is required")

    # Verify all images exist
    for path in image_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image not found: {path}")

    client = genai.Client(api_key=api_key)

    # Load images
    images = [Image.open(path) for path in image_paths]

    # Build contents: instruction first, then images
    contents = [instruction] + images

    # Build config
    config_kwargs = {"response_modalities": ["TEXT", "IMAGE"]}

    image_config_kwargs = {}
    if aspect_ratio:
        image_config_kwargs["aspect_ratio"] = aspect_ratio
    if image_size:
        image_config_kwargs["image_size"] = image_size

    if image_config_kwargs:
        config_kwargs["image_config"] = types.ImageConfig(**image_config_kwargs)

    config = types.GenerateContentConfig(**config_kwargs)

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )

    text_response = None
    image = None

    for part in response.parts:
        if part.text is not None:
            text_response = part.text
        elif part.inline_data is not None:
            image = part.as_image()

    if image is None:
        raise RuntimeError("No image was generated.")

    # Convert genai Image to PIL Image for processing
    if hasattr(image, "_pil_image"):
        pil_image = image._pil_image
    else:
        # Fallback: save to bytes and reload with PIL
        import io
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        pil_image = Image.open(img_bytes)

    # Apply transparency conversion if requested
    if transparent:
        pil_image = make_transparent(pil_image, tolerance, edge_tolerance)

    image = pil_image

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Save with appropriate format
    if output_format == "png":
        image.save(output_path, format="PNG")
    elif output_format == "webp":
        image.save(output_path, format="WEBP")
    else:
        # JPEG doesn't support RGBA, convert if needed
        if image.mode == "RGBA":
            image = image.convert("RGB")
        image.save(output_path, format="JPEG")

    # Write .prompt sidecar file
    write_compose_prompt_sidecar(
        output_path=output_path,
        instruction=instruction,
        model=model,
        aspect_ratio=aspect_ratio,
        image_size=image_size,
        output_format=output_format,
        transparent=transparent,
        tolerance=tolerance,
        edge_tolerance=edge_tolerance,
        source_images=image_paths,
    )

    return text_response


def main():
    parser = argparse.ArgumentParser(
        description="Compose multiple images using Gemini API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("instruction", help="Composition instruction")
    parser.add_argument("output", help="Output file path")
    parser.add_argument("images", nargs="+", help="Input images (up to 14)")
    parser.add_argument(
        "--model",
        "-m",
        default="gemini-3.1-flash-image-preview",
        choices=["gemini-2.5-flash-image", "gemini-3.1-flash-image-preview"],
        help="Model to use (pro recommended for composition)",
    )
    parser.add_argument(
        "--aspect",
        "-a",
        choices=["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
        help="Output aspect ratio",
    )
    parser.add_argument(
        "--size",
        "-s",
        choices=["1K", "2K", "4K"],
        help="Output resolution",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["png", "jpg", "webp"],
        default="jpg",
        help="Output format (default: jpg)",
    )
    parser.add_argument(
        "--transparent",
        "-t",
        action="store_true",
        help="Convert white background to transparent (requires PNG format)",
    )
    parser.add_argument(
        "--tolerance",
        type=int,
        default=0,
        metavar="N",
        help="Color tolerance for white detection (0-255, default: 0 = exact #FFFFFF)",
    )
    parser.add_argument(
        "--edge-tolerance",
        type=int,
        default=0,
        metavar="N",
        help="Expand transparency to near-white neighbors (0 = disabled, recommended: 10)",
    )

    args = parser.parse_args()

    try:
        text = compose_images(
            instruction=args.instruction,
            output_path=args.output,
            image_paths=args.images,
            model=args.model,
            aspect_ratio=args.aspect,
            image_size=args.size,
            output_format=args.format,
            transparent=args.transparent,
            tolerance=args.tolerance,
            edge_tolerance=args.edge_tolerance,
        )

        print(f"Composed image saved to: {args.output}")
        prompt_path = Path(args.output).with_suffix(".prompt")
        print(f"Prompt saved to: {prompt_path}")
        if text:
            print(f"Model response: {text}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
