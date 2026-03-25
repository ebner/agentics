#!/usr/bin/env python3
"""
Convert existing images with white backgrounds to transparent PNGs.

Usage:
    python convert_to_transparent.py <directory> [options]

Examples:
    # Dry run (shows what would be converted)
    python convert_to_transparent.py ./images --recursive

    # Execute conversion
    python convert_to_transparent.py ./images --recursive --execute

    # With edge tolerance for anti-aliasing
    python convert_to_transparent.py ./images --execute --edge-tolerance 10

This script:
1. Scans for JPG/PNG images in the specified directory
2. Detects white backgrounds using corner pixel sampling
3. Converts images with white backgrounds to transparent PNGs
4. Generates a report of conversions and any issues
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

from generate_image import make_transparent


def detect_white_background(image_path: Path, threshold: int = 5) -> tuple[bool, str]:
    """Detect if an image has a white background using corner pixel sampling.

    Args:
        image_path: Path to the image file
        threshold: Color distance from white to consider as "white" (0-255)

    Returns:
        Tuple of (is_white_background, detected_color_hex)
    """
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        return False, f"Error: {e}"

    width, height = img.size
    pixels = img.load()

    # Sample 4 corners (with small inset to avoid edge artifacts)
    inset = min(5, width // 10, height // 10)
    corners = [
        (inset, inset),  # Top-left
        (width - 1 - inset, inset),  # Top-right
        (inset, height - 1 - inset),  # Bottom-left
        (width - 1 - inset, height - 1 - inset),  # Bottom-right
    ]

    corner_colors = []
    for x, y in corners:
        r, g, b = pixels[x, y]
        corner_colors.append((r, g, b))

    # Check if majority of corners are near white
    white_corners = 0
    avg_r, avg_g, avg_b = 0, 0, 0
    for r, g, b in corner_colors:
        avg_r += r
        avg_g += g
        avg_b += b
        if r >= 255 - threshold and g >= 255 - threshold and b >= 255 - threshold:
            white_corners += 1

    avg_r //= 4
    avg_g //= 4
    avg_b //= 4
    avg_hex = f"#{avg_r:02X}{avg_g:02X}{avg_b:02X}"

    # Majority (3+) of corners must be white
    is_white = white_corners >= 3

    return is_white, avg_hex


def convert_image(
    input_path: Path,
    output_path: Path,
    tolerance: int = 0,
    edge_tolerance: int = 0,
) -> bool:
    """Convert an image to transparent PNG.

    Args:
        input_path: Source image path
        output_path: Destination PNG path
        tolerance: Color tolerance for white detection
        edge_tolerance: Edge expansion tolerance

    Returns:
        True if successful, False otherwise
    """
    try:
        img = Image.open(input_path)
        img = make_transparent(img, tolerance, edge_tolerance)
        img.save(output_path, format="PNG")
        return True
    except Exception:
        return False


def generate_report(
    converted: list[tuple[Path, Path, str]],
    needs_regeneration: list[tuple[Path, str]],
    errors: list[tuple[Path, str]],
    skipped: list[tuple[Path, str]],
    output_path: Path,
) -> None:
    """Generate a markdown report of the conversion results.

    Args:
        converted: List of (original, new_path, background_color) tuples
        needs_regeneration: List of (path, reason) tuples
        errors: List of (path, error_message) tuples
        skipped: List of (path, reason) tuples
        output_path: Path to write the report
    """
    lines = [
        "# Transparency Conversion Report",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Summary",
        f"- Total processed: {len(converted) + len(needs_regeneration) + len(errors)}",
        f"- Converted: {len(converted)}",
        f"- Needs regeneration: {len(needs_regeneration)}",
        f"- Errors: {len(errors)}",
        f"- Skipped: {len(skipped)}",
        "",
    ]

    if converted:
        lines.append("## Converted Files")
        lines.append("")
        lines.append("| Original | New File | Background Detected |")
        lines.append("|----------|----------|---------------------|")
        for orig, new, bg_color in converted:
            lines.append(f"| {orig.name} | {new.name} | {bg_color} |")
        lines.append("")

    if needs_regeneration:
        lines.append("## Needs Regeneration")
        lines.append("")
        lines.append("These files have non-white backgrounds and need to be regenerated:")
        lines.append("")
        lines.append("| File | Background Color |")
        lines.append("|------|------------------|")
        for path, reason in needs_regeneration:
            lines.append(f"| {path.name} | {reason} |")
        lines.append("")

    if errors:
        lines.append("## Errors")
        lines.append("")
        lines.append("| File | Error |")
        lines.append("|------|-------|")
        for path, error in errors:
            lines.append(f"| {path.name} | {error} |")
        lines.append("")

    if skipped:
        lines.append("## Skipped Files")
        lines.append("")
        lines.append("| File | Reason |")
        lines.append("|------|--------|")
        for path, reason in skipped:
            lines.append(f"| {path.name} | {reason} |")
        lines.append("")

    output_path.write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(
        description="Convert images with white backgrounds to transparent PNGs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing images to convert",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform conversions (default: dry run)",
    )
    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="Process subdirectories recursively",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("conversion-report.md"),
        help="Output report file (default: conversion-report.md)",
    )
    parser.add_argument(
        "--tolerance",
        type=int,
        default=0,
        metavar="N",
        help="Color tolerance for white detection (0-255, default: 0)",
    )
    parser.add_argument(
        "--edge-tolerance",
        type=int,
        default=0,
        metavar="N",
        help="Expand transparency to near-white neighbors (default: 0)",
    )
    parser.add_argument(
        "--detection-threshold",
        type=int,
        default=5,
        metavar="N",
        help="Threshold for detecting white background in corner pixels (default: 5)",
    )

    args = parser.parse_args()

    if not args.directory.exists():
        print(f"Error: Directory not found: {args.directory}", file=sys.stderr)
        sys.exit(1)

    # Find all image files
    if args.recursive:
        jpg_files = list(args.directory.rglob("*.jpg")) + list(args.directory.rglob("*.jpeg"))
        png_files = list(args.directory.rglob("*.png"))
    else:
        jpg_files = list(args.directory.glob("*.jpg")) + list(args.directory.glob("*.jpeg"))
        png_files = list(args.directory.glob("*.png"))

    all_files = sorted(jpg_files + png_files)

    if not all_files:
        print(f"No image files found in {args.directory}")
        sys.exit(0)

    print(f"Found {len(all_files)} image(s) to process")
    print(f"Mode: {'EXECUTE' if args.execute else 'DRY RUN'}")
    print()

    converted: list[tuple[Path, Path, str]] = []
    needs_regeneration: list[tuple[Path, str]] = []
    errors: list[tuple[Path, str]] = []
    skipped: list[tuple[Path, str]] = []

    for img_path in all_files:
        # Skip if PNG already exists with same base name
        output_path = img_path.with_suffix(".png")
        if img_path.suffix.lower() != ".png" and output_path.exists():
            skipped.append((img_path, "PNG version already exists"))
            print(f"  SKIP: {img_path.name} (PNG exists)")
            continue

        # Detect background
        is_white, bg_color = detect_white_background(img_path, args.detection_threshold)

        if bg_color.startswith("Error:"):
            errors.append((img_path, bg_color))
            print(f"  ERROR: {img_path.name} - {bg_color}")
            continue

        if not is_white:
            needs_regeneration.append((img_path, bg_color))
            print(f"  REGEN: {img_path.name} (background: {bg_color})")
            continue

        # White background detected - convert
        if args.execute:
            success = convert_image(
                img_path,
                output_path,
                args.tolerance,
                args.edge_tolerance,
            )
            if success:
                converted.append((img_path, output_path, bg_color))
                print(f"  OK: {img_path.name} -> {output_path.name}")
            else:
                errors.append((img_path, "Conversion failed"))
                print(f"  ERROR: {img_path.name} - Conversion failed")
        else:
            converted.append((img_path, output_path, bg_color))
            print(f"  WOULD CONVERT: {img_path.name} -> {output_path.name}")

    # Generate report
    if args.execute:
        generate_report(converted, needs_regeneration, errors, skipped, args.report)
        print(f"\nReport saved to: {args.report}")

    # Summary
    print()
    print("=" * 50)
    print("Summary:")
    print(f"  Converted: {len(converted)}")
    print(f"  Needs regeneration: {len(needs_regeneration)}")
    print(f"  Errors: {len(errors)}")
    print(f"  Skipped: {len(skipped)}")

    if not args.execute and converted:
        print()
        print("This was a dry run. Use --execute to perform actual conversions.")


if __name__ == "__main__":
    main()
