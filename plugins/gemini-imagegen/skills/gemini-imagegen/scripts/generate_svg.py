#!/usr/bin/env python3
"""
Generate SVG vector graphics from text prompts using Gemini 3.1 Pro.

Uses the text model (not the image model) to generate SVG markup directly.
Best for icons, diagrams, animated elements, and simple geometric illustrations.

Usage:
    python generate_svg.py "prompt" output.svg [options]

Examples:
    python generate_svg.py "A minimalist lock icon" lock.svg
    python generate_svg.py "A vault door with light rays" vault.svg --viewbox "0 0 200 200"
    python generate_svg.py "A three-dot loading animation" loader.svg --animated

Environment:
    GEMINI_API_KEY - Required API key
"""

import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from google import genai


def write_prompt_sidecar(
    output_path: str,
    prompt: str,
    model: str,
    viewbox: str | None,
    animated: bool,
    style: str | None,
) -> str:
    """Write a .prompt sidecar file with generation metadata."""
    prompt_path = Path(output_path).with_suffix(".prompt")

    lines = ["---"]
    lines.append(f"model: {model}")
    lines.append("format: svg")
    if viewbox:
        lines.append(f'viewbox: "{viewbox}"')
    lines.append(f"animated: {str(animated).lower()}")
    if style:
        lines.append(f"style: {style}")
    lines.append(f"date: {datetime.now(timezone.utc).isoformat()}")
    lines.append('version: "1.0"')

    lines.append("")
    lines.append("final_prompt: |")
    for line in prompt.strip().split("\n"):
        lines.append(f"  {line}")

    lines.append("")
    lines.append("edit_history: []")
    lines.append("---")

    prompt_path.write_text("\n".join(lines) + "\n")
    return str(prompt_path)


def extract_svg(text: str) -> str:
    """Extract SVG content from model response, stripping markdown fences."""
    # Try to extract from markdown code block
    match = re.search(r"```(?:svg|xml)?\s*\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Try to find raw SVG tags
    match = re.search(r"(<svg[\s\S]*?</svg>)", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Return as-is if it looks like SVG
    stripped = text.strip()
    if stripped.startswith("<svg") or stripped.startswith("<?xml"):
        return stripped

    raise RuntimeError(
        "Could not extract SVG from model response. "
        "The model may not have returned valid SVG markup."
    )


def build_prompt(
    user_prompt: str,
    viewbox: str | None,
    animated: bool,
    style: str | None,
) -> str:
    """Build the full prompt with SVG-specific instructions."""
    parts = [
        "Generate an SVG image. Return ONLY the SVG code, no explanation or markdown.",
        "",
    ]

    if viewbox:
        parts.append(f"viewBox: {viewbox}")
    if style:
        parts.append(f"Style: {style}")

    parts.append("Requirements:")
    parts.append("- Clean paths with minimal nodes")
    parts.append("- No embedded raster <image> elements")
    parts.append("- No inline JavaScript")
    parts.append("- Use hex color values")

    if animated:
        parts.append("- Include CSS @keyframes animations (not SMIL)")
        parts.append("- Use <style> block inside the SVG for animations")
    else:
        parts.append("- Static SVG, no animations")

    parts.append("")
    parts.append(f"Subject: {user_prompt}")

    return "\n".join(parts)


def generate_svg(
    prompt: str,
    output_path: str,
    model: str = "gemini-3.1-pro-preview",
    viewbox: str | None = None,
    animated: bool = False,
    style: str | None = None,
) -> None:
    """Generate an SVG from a text prompt.

    Args:
        prompt: Text description of the SVG to generate
        output_path: Path to save the generated SVG
        model: Gemini text model to use
        viewbox: SVG viewBox attribute (e.g., "0 0 200 200")
        animated: Whether to request CSS animations
        style: Style hint (e.g., "minimal", "geometric", "line-art")
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY environment variable not set")

    client = genai.Client(api_key=api_key)

    full_prompt = build_prompt(prompt, viewbox, animated, style)

    response = client.models.generate_content(
        model=model,
        contents=[full_prompt],
    )

    if not response.text:
        raise RuntimeError("No response from model. Try a more specific prompt.")

    svg_code = extract_svg(response.text)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(svg_code + "\n")

    write_prompt_sidecar(
        output_path=output_path,
        prompt=full_prompt,
        model=model,
        viewbox=viewbox,
        animated=animated,
        style=style,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate SVG vector graphics from text prompts using Gemini 3.1 Pro",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("prompt", help="Text prompt describing the SVG to generate")
    parser.add_argument("output", help="Output file path (e.g., icon.svg)")
    parser.add_argument(
        "--model",
        "-m",
        default="gemini-3.1-pro-preview",
        help="Gemini text model to use (default: gemini-3.1-pro-preview)",
    )
    parser.add_argument(
        "--viewbox",
        help='SVG viewBox attribute (e.g., "0 0 200 200")',
    )
    parser.add_argument(
        "--animated",
        action="store_true",
        help="Request CSS @keyframes animations in the SVG",
    )
    parser.add_argument(
        "--style",
        choices=["minimal", "geometric", "line-art", "flat", "outline"],
        help="Style hint for the SVG",
    )

    args = parser.parse_args()

    if not args.output.endswith(".svg"):
        print("Warning: output file does not end with .svg", file=sys.stderr)

    try:
        generate_svg(
            prompt=args.prompt,
            output_path=args.output,
            model=args.model,
            viewbox=args.viewbox,
            animated=args.animated,
            style=args.style,
        )

        print(f"SVG saved to: {args.output}")
        prompt_path = Path(args.output).with_suffix(".prompt")
        print(f"Prompt saved to: {prompt_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
