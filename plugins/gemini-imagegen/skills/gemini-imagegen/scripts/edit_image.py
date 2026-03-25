#!/usr/bin/env python3
"""
Edit existing images using Gemini API.

Usage:
    python edit_image.py input.png "edit instruction" output.png [options]

Examples:
    python edit_image.py photo.png "Add a rainbow in the sky" edited.jpg
    python edit_image.py room.jpg "Change the sofa to red" room_edited.png --format png --transparent
    python edit_image.py portrait.png "Make it Van Gogh style" artistic.png --format png

Environment:
    GEMINI_API_KEY - Required API key
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from PIL import Image
from google import genai
from google.genai import types

from generate_image import make_transparent


def read_existing_prompt(input_path: str) -> dict | None:
    """Read existing .prompt sidecar file if it exists.

    Args:
        input_path: Path to the input image

    Returns:
        Parsed YAML dict or None if no sidecar exists
    """
    prompt_path = Path(input_path).with_suffix(".prompt")
    if not prompt_path.exists():
        return None

    content = prompt_path.read_text()
    # Parse YAML frontmatter (between --- markers)
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 2:
            try:
                return yaml.safe_load(parts[1])
            except yaml.YAMLError:
                return None
    return None


def write_edit_prompt_sidecar(
    output_path: str,
    instruction: str,
    model: str,
    aspect_ratio: str | None,
    image_size: str | None,
    output_format: str,
    transparent: bool,
    tolerance: int,
    edge_tolerance: int,
    input_path: str,
    existing_metadata: dict | None = None,
) -> str:
    """Write a .prompt sidecar file for an edited image.

    Args:
        output_path: Path to the output image file
        instruction: The edit instruction used
        model: Model name used
        aspect_ratio: Aspect ratio if specified
        image_size: Resolution if specified
        output_format: Output format (png, jpg, webp)
        transparent: Whether transparency conversion was applied
        tolerance: Color tolerance used
        edge_tolerance: Edge tolerance used
        input_path: Path to the input image
        existing_metadata: Existing metadata from input image's .prompt file

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
    lines.append(f"source_image: {input_path}")

    # Preserve content and template from original if available
    if existing_metadata:
        if "content" in existing_metadata:
            lines.append("")
            lines.append("content: |")
            content = existing_metadata["content"]
            if isinstance(content, str):
                for line in content.strip().split("\n"):
                    lines.append(f"  {line}")

        if "template" in existing_metadata:
            lines.append("")
            lines.append("template: |")
            template = existing_metadata["template"]
            if isinstance(template, str):
                for line in template.strip().split("\n"):
                    lines.append(f"  {line}")

        if "final_prompt" in existing_metadata:
            lines.append("")
            lines.append("original_prompt: |")
            original = existing_metadata["final_prompt"]
            if isinstance(original, str):
                for line in original.strip().split("\n"):
                    lines.append(f"  {line}")

    # Add edit instruction as current prompt
    lines.append("")
    lines.append("edit_instruction: |")
    for line in instruction.strip().split("\n"):
        lines.append(f"  {line}")

    # Build edit history
    lines.append("")
    lines.append("edit_history:")

    # Include previous edit history if available
    if existing_metadata and "edit_history" in existing_metadata:
        prev_history = existing_metadata["edit_history"]
        if isinstance(prev_history, list):
            for entry in prev_history:
                if isinstance(entry, dict):
                    lines.append(f"  - date: {entry.get('date', 'unknown')}")
                    lines.append(f"    instruction: \"{entry.get('instruction', '')}\"")

    # Add current edit
    lines.append(f"  - date: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f'    instruction: "{instruction}"')

    lines.append("---")

    prompt_path.write_text("\n".join(lines) + "\n")
    return str(prompt_path)


def edit_image(
    input_path: str,
    instruction: str,
    output_path: str,
    model: str = "gemini-2.5-flash-image",
    aspect_ratio: str | None = None,
    image_size: str | None = None,
    output_format: str = "jpg",
    transparent: bool = False,
    tolerance: int = 0,
    edge_tolerance: int = 0,
) -> str | None:
    """Edit an existing image based on text instructions.

    Args:
        input_path: Path to the input image
        instruction: Text description of edits to make
        output_path: Path to save the edited image
        model: Gemini model to use
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
        EnvironmentError: If GEMINI_API_KEY is not set
        FileNotFoundError: If input image doesn't exist
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

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input image not found: {input_path}")

    client = genai.Client(api_key=api_key)

    # Load input image
    input_image = Image.open(input_path)

    # Read existing prompt metadata if available
    existing_metadata = read_existing_prompt(input_path)

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
        contents=[instruction, input_image],
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
        raise RuntimeError("No image was generated. Check your instruction and try again.")

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

    # Write .prompt sidecar file with edit history
    write_edit_prompt_sidecar(
        output_path=output_path,
        instruction=instruction,
        model=model,
        aspect_ratio=aspect_ratio,
        image_size=image_size,
        output_format=output_format,
        transparent=transparent,
        tolerance=tolerance,
        edge_tolerance=edge_tolerance,
        input_path=input_path,
        existing_metadata=existing_metadata,
    )

    return text_response


def main():
    parser = argparse.ArgumentParser(
        description="Edit images using Gemini API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("input", help="Input image path")
    parser.add_argument("instruction", help="Edit instruction")
    parser.add_argument("output", help="Output file path")
    parser.add_argument(
        "--model",
        "-m",
        default="gemini-2.5-flash-image",
        choices=["gemini-2.5-flash-image", "gemini-3.1-flash-image-preview"],
        help="Model to use (default: gemini-2.5-flash-image)",
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
        text = edit_image(
            input_path=args.input,
            instruction=args.instruction,
            output_path=args.output,
            model=args.model,
            aspect_ratio=args.aspect,
            image_size=args.size,
            output_format=args.format,
            transparent=args.transparent,
            tolerance=args.tolerance,
            edge_tolerance=args.edge_tolerance,
        )

        print(f"Edited image saved to: {args.output}")
        prompt_path = Path(args.output).with_suffix(".prompt")
        print(f"Prompt saved to: {prompt_path}")
        if text:
            print(f"Model response: {text}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
