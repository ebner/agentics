#!/usr/bin/env python3
"""
Regenerate images from .prompt sidecar files.

Reads existing .prompt metadata and dispatches to the correct generation
script (raster via generate_image or vector via generate_svg) with the
original parameters. Useful for bulk regeneration after model upgrades.

Usage:
    python regenerate.py path/to/image.prompt                    # Dry run (single file)
    python regenerate.py path/to/illustrations/ --recursive      # Dry run (batch)
    python regenerate.py path/to/illustrations/ -r --execute     # Regenerate all
    python regenerate.py path/to/ -r --execute --raster-model gemini-3.1-flash-image-preview

Examples:
    # Preview what would be regenerated
    python regenerate.py ./frontend/public/images/illustrations/ -r

    # Regenerate all with a new model (raster only)
    python regenerate.py ./frontend/public/images/illustrations/ -r --execute \
        --raster-model gemini-3.1-flash-image-preview

    # Regenerate only SVGs
    python regenerate.py ./assets/ -r --execute --filter svg

    # Regenerate a single image
    python regenerate.py ./hero-main.prompt --execute

Environment:
    GEMINI_API_KEY - Required API key
"""

import argparse
import sys
import traceback
from pathlib import Path

import yaml

from generate_image import generate_image
from generate_svg import generate_svg


def parse_sidecar(prompt_path: Path) -> dict | None:
    """Parse a .prompt sidecar file into a metadata dict.

    Args:
        prompt_path: Path to the .prompt file

    Returns:
        Parsed YAML dict, or None if parsing fails
    """
    content = prompt_path.read_text()
    if not content.startswith("---"):
        return None

    parts = content.split("---", 2)
    if len(parts) < 2:
        return None

    try:
        return yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None


def resolve_output_path(prompt_path: Path, fmt: str) -> Path:
    """Determine the image output path from a sidecar path and format.

    Args:
        prompt_path: Path to the .prompt file
        fmt: Output format (png, jpg, webp, svg)

    Returns:
        Path to the image file
    """
    ext = f".{fmt}" if fmt != "jpeg" else ".jpg"
    return prompt_path.with_suffix(ext)


def collect_sidecars(target: Path, recursive: bool) -> list[Path]:
    """Find all .prompt sidecar files in a path.

    Args:
        target: A single .prompt file or a directory
        recursive: Whether to search directories recursively

    Returns:
        Sorted list of .prompt file paths
    """
    if target.is_file():
        if target.suffix == ".prompt":
            return [target]
        # Try finding a sidecar for an image file
        sidecar = target.with_suffix(".prompt")
        if sidecar.exists():
            return [sidecar]
        return []

    if target.is_dir():
        pattern = "**/*.prompt" if recursive else "*.prompt"
        return sorted(target.glob(pattern))

    return []


def plan_regeneration(
    metadata: dict,
    prompt_path: Path,
    raster_model: str | None,
    svg_model: str | None,
) -> dict:
    """Build a regeneration plan from sidecar metadata.

    Args:
        metadata: Parsed sidecar YAML
        prompt_path: Path to the .prompt file
        raster_model: Override model for raster images, or None
        svg_model: Override model for SVG images, or None

    Returns:
        Dict with keys: format, output_path, model, kwargs, prompt
    """
    fmt = metadata.get("format", "png")
    is_svg = fmt == "svg"
    output_path = resolve_output_path(prompt_path, fmt)

    # Extract the prompt text
    final_prompt = metadata.get("final_prompt", "")
    if isinstance(final_prompt, str):
        final_prompt = final_prompt.strip()

    if not final_prompt:
        raise ValueError("No final_prompt found in sidecar")

    # Determine model
    original_model = metadata.get("model", "")
    if is_svg:
        model = svg_model or original_model or "gemini-3.1-pro-preview"
    else:
        model = raster_model or original_model or "gemini-3.1-flash-image-preview"

    model_changed = model != original_model

    if is_svg:
        kwargs = {
            "viewbox": metadata.get("viewbox"),
            "animated": metadata.get("animated", False),
            "style": metadata.get("style"),
        }
    else:
        kwargs = {
            "aspect_ratio": metadata.get("aspect_ratio"),
            "image_size": metadata.get("resolution"),
            "output_format": fmt,
            "transparent": metadata.get("transparent", False),
            "tolerance": metadata.get("tolerance", 0),
            "edge_tolerance": metadata.get("edge_tolerance", 0),
            "content": metadata.get("content"),
            "template": metadata.get("template"),
        }

    return {
        "format": fmt,
        "is_svg": is_svg,
        "output_path": str(output_path),
        "model": model,
        "original_model": original_model,
        "model_changed": model_changed,
        "kwargs": kwargs,
        "prompt": final_prompt,
    }


def print_plan(plans: list[dict], total_skipped: int) -> None:
    """Print a summary of planned regenerations."""
    svg_count = sum(1 for p in plans if p["is_svg"])
    raster_count = len(plans) - svg_count
    model_changes = sum(1 for p in plans if p["model_changed"])

    print(f"\n{'=' * 60}")
    print(f"Regeneration Plan")
    print(f"{'=' * 60}")
    print(f"  Total sidecars found:  {len(plans) + total_skipped}")
    print(f"  To regenerate:         {len(plans)}")
    if total_skipped:
        print(f"  Skipped (filtered):    {total_skipped}")
    print(f"  Raster (png/jpg/webp): {raster_count}")
    print(f"  Vector (svg):          {svg_count}")
    if model_changes:
        print(f"  Model upgrades:        {model_changes}")
    print()

    for i, plan in enumerate(plans, 1):
        path = plan["output_path"]
        model_info = plan["model"]
        if plan["model_changed"]:
            model_info = f"{plan['original_model']} -> {plan['model']}"
        fmt_label = "SVG" if plan["is_svg"] else plan["format"].upper()
        print(f"  [{i:3d}] {fmt_label:4s}  {path}")
        if plan["model_changed"]:
            print(f"         model: {model_info}")

    print(f"\n{'=' * 60}")
    print("Dry run - no files changed. Use --execute to regenerate.")
    print(f"{'=' * 60}\n")


def execute_regeneration(plans: list[dict]) -> tuple[int, int]:
    """Execute all planned regenerations.

    Returns:
        Tuple of (success_count, failure_count)
    """
    successes = 0
    failures = 0
    total = len(plans)

    for i, plan in enumerate(plans, 1):
        output_path = plan["output_path"]
        fmt_label = "SVG" if plan["is_svg"] else plan["format"].upper()
        model_note = ""
        if plan["model_changed"]:
            model_note = f" (model: {plan['original_model']} -> {plan['model']})"

        print(f"[{i}/{total}] {fmt_label} {output_path}{model_note}")

        try:
            if plan["is_svg"]:
                generate_svg(
                    prompt=plan["prompt"],
                    output_path=output_path,
                    model=plan["model"],
                    **plan["kwargs"],
                )
            else:
                generate_image(
                    prompt=plan["prompt"],
                    output_path=output_path,
                    model=plan["model"],
                    **plan["kwargs"],
                )
            print(f"  -> OK")
            successes += 1

        except Exception as e:
            print(f"  -> FAILED: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            failures += 1

    print(f"\nDone: {successes} succeeded, {failures} failed out of {total}")
    return successes, failures


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate images from .prompt sidecar files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "target",
        help="A .prompt file, image file, or directory to scan",
    )
    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="Scan directories recursively",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually regenerate (default is dry run)",
    )
    parser.add_argument(
        "--raster-model",
        metavar="MODEL",
        help="Override model for raster images (png/jpg/webp)",
    )
    parser.add_argument(
        "--svg-model",
        metavar="MODEL",
        help="Override model for SVG generation",
    )
    parser.add_argument(
        "--filter",
        choices=["svg", "raster"],
        help="Only regenerate SVG or raster images",
    )

    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f"Error: {target} does not exist", file=sys.stderr)
        sys.exit(1)

    sidecars = collect_sidecars(target, args.recursive)
    if not sidecars:
        print(f"No .prompt sidecar files found in {target}")
        sys.exit(0)

    # Parse and plan
    plans = []
    skipped = 0
    parse_errors = 0

    for sidecar in sidecars:
        metadata = parse_sidecar(sidecar)
        if metadata is None:
            print(f"Warning: could not parse {sidecar}", file=sys.stderr)
            parse_errors += 1
            continue

        fmt = metadata.get("format", "png")
        is_svg = fmt == "svg"

        # Apply filter
        if args.filter == "svg" and not is_svg:
            skipped += 1
            continue
        if args.filter == "raster" and is_svg:
            skipped += 1
            continue

        try:
            plan = plan_regeneration(
                metadata, sidecar, args.raster_model, args.svg_model
            )
            plans.append(plan)
        except ValueError as e:
            print(f"Warning: skipping {sidecar}: {e}", file=sys.stderr)
            skipped += 1

    if parse_errors:
        print(f"\n{parse_errors} sidecar(s) could not be parsed.", file=sys.stderr)

    if not plans:
        print("No images to regenerate after filtering.")
        sys.exit(0)

    if args.execute:
        print(f"Regenerating {len(plans)} image(s)...\n")
        _, failures = execute_regeneration(plans)
        sys.exit(1 if failures else 0)
    else:
        print_plan(plans, skipped)


if __name__ == "__main__":
    main()
