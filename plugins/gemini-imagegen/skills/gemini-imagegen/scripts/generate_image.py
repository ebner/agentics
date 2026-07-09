#!/usr/bin/env python3
"""
Generate images from text prompts using Gemini API.

Usage:
    python generate_image.py "prompt" output.png [options]

Examples:
    python generate_image.py "A cat in space" cat.jpg
    python generate_image.py "A logo for Acme Corp" logo.png --format png --transparent
    python generate_image.py "Epic landscape" landscape.png --format png --transparent --edge-tolerance 10

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

from models import (
    DEFAULT_MODEL,
    RASTER_MODEL_CHOICES,
    default_size_for_model,
    extract_text_and_image,
)


def make_transparent(
    image: Image.Image,
    tolerance: int = 0,
    edge_tolerance: int = 0,
) -> Image.Image:
    """Convert white pixels to transparent with optional edge expansion.

    Args:
        image: PIL Image to process
        tolerance: Color distance from white (0-255). 0 = exact #FFFFFF only.
        edge_tolerance: Expand to near-white neighbors (0 = disabled).

    Algorithm:
        1. Pass 1: Convert pixels within `tolerance` of white to transparent
        2. Pass 2 (if edge_tolerance > 0): For each pixel adjacent to transparent,
           if within edge_tolerance of white, make transparent. Repeat until stable.

    Returns:
        RGBA image with transparency applied
    """
    img = image.convert("RGBA")
    pixels = img.load()
    width, height = img.size

    def is_near_white(r: int, g: int, b: int, threshold: int) -> bool:
        return r >= 255 - threshold and g >= 255 - threshold and b >= 255 - threshold

    # Pass 1: Convert pixels within tolerance of white
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if is_near_white(r, g, b, tolerance):
                pixels[x, y] = (255, 255, 255, 0)

    # Pass 2: Edge expansion (if enabled)
    if edge_tolerance > 0:
        changed = True
        while changed:
            changed = False
            for y in range(height):
                for x in range(width):
                    r, g, b, a = pixels[x, y]
                    if a == 0:  # Already transparent
                        continue
                    if not is_near_white(r, g, b, edge_tolerance):
                        continue
                    # Check if adjacent to transparent pixel
                    neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                    for nx, ny in neighbors:
                        if 0 <= nx < width and 0 <= ny < height:
                            if pixels[nx, ny][3] == 0:  # Neighbor is transparent
                                pixels[x, y] = (255, 255, 255, 0)
                                changed = True
                                break
    return img


def write_prompt_sidecar(
    output_path: str,
    prompt: str,
    model: str,
    aspect_ratio: str | None,
    image_size: str | None,
    output_format: str,
    transparent: bool,
    tolerance: int,
    edge_tolerance: int,
    content: str | None = None,
    template: str | None = None,
) -> str:
    """Write a .prompt sidecar file with generation metadata.

    Args:
        output_path: Path to the image file (sidecar will be same name with .prompt extension)
        prompt: The complete final prompt sent to Gemini
        model: Model name used
        aspect_ratio: Aspect ratio if specified
        image_size: Resolution if specified
        output_format: Output format (png, jpg, webp)
        transparent: Whether transparency conversion was applied
        tolerance: Color tolerance used
        edge_tolerance: Edge tolerance used
        content: Optional unique content/description (if using templates)
        template: Optional template text (if using templates)

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

    # Add content if provided
    if content:
        lines.append("")
        lines.append("content: |")
        for line in content.strip().split("\n"):
            lines.append(f"  {line}")

    # Add template if provided
    if template:
        lines.append("")
        lines.append("template: |")
        for line in template.strip().split("\n"):
            lines.append(f"  {line}")

    # Add final prompt
    lines.append("")
    lines.append("final_prompt: |")
    for line in prompt.strip().split("\n"):
        lines.append(f"  {line}")

    # Add empty edit history
    lines.append("")
    lines.append("edit_history: []")
    lines.append("---")

    prompt_path.write_text("\n".join(lines) + "\n")
    return str(prompt_path)


def generate_image(
    prompt: str,
    output_path: str,
    model: str = DEFAULT_MODEL,
    aspect_ratio: str | None = None,
    image_size: str | None = None,
    output_format: str = "jpg",
    transparent: bool = False,
    tolerance: int = 0,
    edge_tolerance: int = 0,
    content: str | None = None,
    template: str | None = None,
) -> str | None:
    """Generate an image from a text prompt.

    Args:
        prompt: Text description of the image to generate
        output_path: Path to save the generated image
        model: Gemini model to use
        aspect_ratio: Aspect ratio (1:1, 16:9, 9:16, etc.)
        image_size: Resolution (1K, 2K, 4K; pro defaults to 2K when unset)
        output_format: Output format (png, jpg, webp)
        transparent: Whether to convert white background to transparent
        tolerance: Color tolerance for white detection (0-255)
        edge_tolerance: Edge expansion tolerance (0 = disabled)
        content: Optional content description (for .prompt sidecar)
        template: Optional template text (for .prompt sidecar)

    Returns:
        Any text response from the model, or None

    Raises:
        ValueError: If transparent is True but format is not PNG
        EnvironmentError: If GEMINI_API_KEY is not set
        RuntimeError: If no image is generated
    """
    # Validate transparency requires PNG
    if transparent and output_format != "png":
        raise ValueError(
            f"Transparency requires PNG format, but got '{output_format}'. "
            "Use --format png with --transparent."
        )

    # Pro defaults to 2K when no explicit size was given (same cost as 1K)
    image_size = default_size_for_model(model, image_size)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY environment variable not set")

    client = genai.Client(api_key=api_key)

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
        contents=[prompt],
        config=config,
    )

    text_response, image = extract_text_and_image(response.parts)

    if image is None:
        raise RuntimeError("No image was generated. Check your prompt and try again.")

    # Convert genai Image to PIL Image for processing
    # The genai Image has a _pil_image attribute or we can use the image data
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
    write_prompt_sidecar(
        output_path=output_path,
        prompt=prompt,
        model=model,
        aspect_ratio=aspect_ratio,
        image_size=image_size,
        output_format=output_format,
        transparent=transparent,
        tolerance=tolerance,
        edge_tolerance=edge_tolerance,
        content=content,
        template=template,
    )

    return text_response


def main():
    parser = argparse.ArgumentParser(
        description="Generate images from text prompts using Gemini API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("prompt", help="Text prompt describing the image")
    parser.add_argument("output", help="Output file path (e.g., output.png)")
    parser.add_argument(
        "--model",
        "-m",
        default=DEFAULT_MODEL,
        choices=RASTER_MODEL_CHOICES,
        help=f"Model to use (default: {DEFAULT_MODEL}; "
        "use gemini-3-pro-image for identity/face preservation)",
    )
    parser.add_argument(
        "--aspect",
        "-a",
        choices=["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
        help="Aspect ratio",
    )
    parser.add_argument(
        "--size",
        "-s",
        choices=["1K", "2K", "4K"],
        help="Image resolution (default: 1K; pro model defaults to 2K)",
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
    parser.add_argument(
        "--content",
        help="Optional content description (for .prompt sidecar, when using templates)",
    )
    parser.add_argument(
        "--template",
        help="Optional template text (for .prompt sidecar)",
    )

    args = parser.parse_args()

    try:
        text = generate_image(
            prompt=args.prompt,
            output_path=args.output,
            model=args.model,
            aspect_ratio=args.aspect,
            image_size=args.size,
            output_format=args.format,
            transparent=args.transparent,
            tolerance=args.tolerance,
            edge_tolerance=args.edge_tolerance,
            content=args.content,
            template=args.template,
        )

        print(f"Image saved to: {args.output}")
        prompt_path = Path(args.output).with_suffix(".prompt")
        print(f"Prompt saved to: {prompt_path}")
        if text:
            print(f"Model response: {text}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
