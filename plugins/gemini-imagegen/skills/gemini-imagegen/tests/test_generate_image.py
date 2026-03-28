"""Tests for pure functions in generate_image.py."""

import pytest
from pathlib import Path

import yaml
from PIL import Image

from generate_image import make_transparent, write_prompt_sidecar


# ---------------------------------------------------------------------------
# make_transparent
# ---------------------------------------------------------------------------

class TestMakeTransparent:
    def test_pure_white_becomes_transparent(self):
        img = Image.new("RGB", (2, 2), (255, 255, 255))
        result = make_transparent(img, tolerance=0)
        assert result.mode == "RGBA"
        # All pixels should be transparent
        for x in range(2):
            for y in range(2):
                r, g, b, a = result.getpixel((x, y))
                assert a == 0, f"Pixel ({x},{y}) should be transparent"

    def test_non_white_stays_opaque(self):
        img = Image.new("RGB", (2, 2), (255, 0, 0))  # red
        result = make_transparent(img, tolerance=0)
        for x in range(2):
            for y in range(2):
                r, g, b, a = result.getpixel((x, y))
                assert a == 255, f"Red pixel ({x},{y}) should stay opaque"
                assert r == 255
                assert g == 0

    def test_near_white_stays_opaque_with_zero_tolerance(self):
        img = Image.new("RGB", (1, 1), (250, 250, 250))
        result = make_transparent(img, tolerance=0)
        _, _, _, a = result.getpixel((0, 0))
        assert a == 255, "Near-white pixel should stay opaque at tolerance=0"

    def test_near_white_transparent_with_tolerance(self):
        img = Image.new("RGB", (1, 1), (250, 250, 250))
        result = make_transparent(img, tolerance=10)
        _, _, _, a = result.getpixel((0, 0))
        assert a == 0, "Near-white pixel should become transparent at tolerance=10"

    def test_edge_expansion(self):
        """A near-white pixel adjacent to a transparent (white) pixel should become
        transparent when edge_tolerance is high enough."""
        img = Image.new("RGB", (3, 1))
        pixels = img.load()
        pixels[0, 0] = (255, 255, 255)  # white -> transparent at tolerance=0
        pixels[1, 0] = (248, 248, 248)  # near-white -> opaque at tolerance=0, but within edge_tolerance=10
        pixels[2, 0] = (100, 100, 100)  # dark -> stays opaque regardless

        result = make_transparent(img, tolerance=0, edge_tolerance=10)
        _, _, _, a0 = result.getpixel((0, 0))
        _, _, _, a1 = result.getpixel((1, 0))
        _, _, _, a2 = result.getpixel((2, 0))

        assert a0 == 0, "White pixel should be transparent"
        assert a1 == 0, "Near-white pixel adjacent to transparent should become transparent"
        assert a2 == 255, "Dark pixel should stay opaque"

    def test_output_is_rgba(self):
        img = Image.new("RGB", (1, 1), (128, 128, 128))
        result = make_transparent(img, tolerance=0)
        assert result.mode == "RGBA"


# ---------------------------------------------------------------------------
# write_prompt_sidecar
# ---------------------------------------------------------------------------

class TestWritePromptSidecar:
    def test_creates_file_at_correct_path(self, tmp_path):
        output = str(tmp_path / "image.png")
        write_prompt_sidecar(
            output_path=output,
            prompt="A test prompt",
            model="gemini-flash",
            aspect_ratio=None,
            image_size=None,
            output_format="png",
            transparent=False,
            tolerance=0,
            edge_tolerance=0,
        )
        prompt_path = tmp_path / "image.prompt"
        assert prompt_path.exists()

    def test_yaml_is_parseable(self, tmp_path):
        output = str(tmp_path / "image.png")
        write_prompt_sidecar(
            output_path=output,
            prompt="A test prompt",
            model="gemini-flash",
            aspect_ratio="16:9",
            image_size="2K",
            output_format="png",
            transparent=False,
            tolerance=0,
            edge_tolerance=0,
        )
        content = (tmp_path / "image.prompt").read_text()
        assert content.startswith("---")
        parts = content.split("---", 2)
        parsed = yaml.safe_load(parts[1])
        assert parsed is not None
        assert isinstance(parsed, dict)

    def test_all_fields_present(self, tmp_path):
        output = str(tmp_path / "image.png")
        write_prompt_sidecar(
            output_path=output,
            prompt="My prompt text",
            model="gemini-flash",
            aspect_ratio="16:9",
            image_size="2K",
            output_format="png",
            transparent=False,
            tolerance=0,
            edge_tolerance=0,
        )
        content = (tmp_path / "image.prompt").read_text()
        parts = content.split("---", 2)
        parsed = yaml.safe_load(parts[1])
        assert parsed["model"] == "gemini-flash"
        assert parsed["format"] == "png"
        assert parsed["aspect_ratio"] == "16:9"
        assert parsed["resolution"] == "2K"
        assert "final_prompt" in parsed
        assert "My prompt text" in parsed["final_prompt"]
        assert "date" in parsed
        assert "version" in parsed

    def test_content_and_template_included(self, tmp_path):
        output = str(tmp_path / "image.png")
        write_prompt_sidecar(
            output_path=output,
            prompt="Final prompt",
            model="gemini-flash",
            aspect_ratio=None,
            image_size=None,
            output_format="png",
            transparent=False,
            tolerance=0,
            edge_tolerance=0,
            content="My unique content",
            template="My template text",
        )
        content = (tmp_path / "image.prompt").read_text()
        parts = content.split("---", 2)
        parsed = yaml.safe_load(parts[1])
        assert "content" in parsed
        assert "My unique content" in parsed["content"]
        assert "template" in parsed
        assert "My template text" in parsed["template"]

    def test_transparency_fields_when_transparent(self, tmp_path):
        output = str(tmp_path / "image.png")
        write_prompt_sidecar(
            output_path=output,
            prompt="A transparent image",
            model="gemini-flash",
            aspect_ratio=None,
            image_size=None,
            output_format="png",
            transparent=True,
            tolerance=5,
            edge_tolerance=10,
        )
        content = (tmp_path / "image.prompt").read_text()
        parts = content.split("---", 2)
        parsed = yaml.safe_load(parts[1])
        assert parsed["transparent"] is True
        assert parsed["tolerance"] == 5
        assert parsed["edge_tolerance"] == 10

    def test_no_tolerance_fields_when_not_transparent(self, tmp_path):
        output = str(tmp_path / "image.png")
        write_prompt_sidecar(
            output_path=output,
            prompt="An opaque image",
            model="gemini-flash",
            aspect_ratio=None,
            image_size=None,
            output_format="png",
            transparent=False,
            tolerance=0,
            edge_tolerance=0,
        )
        content = (tmp_path / "image.prompt").read_text()
        parts = content.split("---", 2)
        parsed = yaml.safe_load(parts[1])
        assert parsed["transparent"] is False
        # tolerance and edge_tolerance should NOT be written when transparent=False
        assert "tolerance" not in parsed
        assert "edge_tolerance" not in parsed
