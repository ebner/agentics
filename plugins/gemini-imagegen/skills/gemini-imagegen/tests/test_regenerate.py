"""Tests for pure functions in regenerate.py."""

import pytest
from pathlib import Path

from regenerate import parse_sidecar, resolve_output_path, collect_sidecars, plan_regeneration


# ---------------------------------------------------------------------------
# parse_sidecar
# ---------------------------------------------------------------------------

class TestParseSidecar:
    def test_valid_yaml_frontmatter(self, tmp_path):
        p = tmp_path / "test.prompt"
        p.write_text("---\nmodel: gemini-flash\nformat: png\nfinal_prompt: hello\n---\n")
        result = parse_sidecar(p)
        assert result is not None
        assert result["model"] == "gemini-flash"
        assert result["format"] == "png"
        assert result["final_prompt"] == "hello"

    def test_file_without_triple_dash_prefix(self, tmp_path):
        p = tmp_path / "test.prompt"
        p.write_text("model: gemini-flash\nformat: png\n")
        result = parse_sidecar(p)
        assert result is None

    def test_invalid_yaml(self, tmp_path):
        p = tmp_path / "test.prompt"
        p.write_text("---\n: :\n  - [\ninvalid: {{\n---\n")
        result = parse_sidecar(p)
        assert result is None

    def test_only_one_delimiter(self, tmp_path):
        """Content that starts with --- but has no second delimiter produces only 2 parts
        from split('---', 2): ['', 'content...'].  The YAML in parts[1] may or may not
        parse, but the function should handle it gracefully."""
        p = tmp_path / "test.prompt"
        p.write_text("---\nmodel: gemini-flash\nformat: png\n")
        # split("---", 2) on this gives ['', '\nmodel: gemini-flash\nformat: png\n']
        # which is len 2, so it tries to parse parts[1]. This actually parses fine.
        # But content with truly broken single-delimiter should return None.
        # A better test: content with only the opening --- and no YAML.
        p.write_text("---")
        result = parse_sidecar(p)
        # split("---", 2) gives ['', ''] which is len 2; yaml.safe_load('') returns None
        assert result is None


# ---------------------------------------------------------------------------
# resolve_output_path
# ---------------------------------------------------------------------------

class TestResolveOutputPath:
    def test_png_format(self, tmp_path):
        p = tmp_path / "image.prompt"
        result = resolve_output_path(p, "png")
        assert result == tmp_path / "image.png"
        assert result.suffix == ".png"

    def test_jpg_format(self, tmp_path):
        p = tmp_path / "image.prompt"
        result = resolve_output_path(p, "jpg")
        assert result == tmp_path / "image.jpg"
        assert result.suffix == ".jpg"

    def test_jpeg_maps_to_jpg(self, tmp_path):
        p = tmp_path / "image.prompt"
        result = resolve_output_path(p, "jpeg")
        assert result == tmp_path / "image.jpg"
        assert result.suffix == ".jpg"

    def test_svg_format(self, tmp_path):
        p = tmp_path / "icon.prompt"
        result = resolve_output_path(p, "svg")
        assert result == tmp_path / "icon.svg"
        assert result.suffix == ".svg"


# ---------------------------------------------------------------------------
# collect_sidecars
# ---------------------------------------------------------------------------

class TestCollectSidecars:
    def test_single_prompt_file(self, tmp_path):
        p = tmp_path / "hero.prompt"
        p.write_text("---\nmodel: x\n---\n")
        result = collect_sidecars(p, recursive=False)
        assert result == [p]

    def test_image_file_with_matching_prompt(self, tmp_path):
        img = tmp_path / "hero.png"
        img.write_bytes(b"fake png")
        sidecar = tmp_path / "hero.prompt"
        sidecar.write_text("---\nmodel: x\n---\n")
        result = collect_sidecars(img, recursive=False)
        assert result == [sidecar]

    def test_image_file_without_prompt(self, tmp_path):
        img = tmp_path / "hero.png"
        img.write_bytes(b"fake png")
        result = collect_sidecars(img, recursive=False)
        assert result == []

    def test_directory_non_recursive(self, tmp_path):
        (tmp_path / "a.prompt").write_text("---\nx: 1\n---\n")
        (tmp_path / "b.prompt").write_text("---\nx: 2\n---\n")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "c.prompt").write_text("---\nx: 3\n---\n")
        result = collect_sidecars(tmp_path, recursive=False)
        names = [p.name for p in result]
        assert "a.prompt" in names
        assert "b.prompt" in names
        assert "c.prompt" not in names

    def test_directory_recursive(self, tmp_path):
        (tmp_path / "a.prompt").write_text("---\nx: 1\n---\n")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "c.prompt").write_text("---\nx: 3\n---\n")
        result = collect_sidecars(tmp_path, recursive=True)
        names = [p.name for p in result]
        assert "a.prompt" in names
        assert "c.prompt" in names

    def test_empty_directory(self, tmp_path):
        result = collect_sidecars(tmp_path, recursive=True)
        assert result == []


# ---------------------------------------------------------------------------
# plan_regeneration
# ---------------------------------------------------------------------------

def _make_prompt_path(tmp_path, name="test.prompt"):
    p = tmp_path / name
    p.write_text("")  # needs to exist for Path operations
    return p


class TestPlanRegeneration:
    def test_text_only_raster(self, tmp_path):
        prompt_path = _make_prompt_path(tmp_path)
        metadata = {
            "format": "png",
            "final_prompt": "A cat in space",
            "model": "gemini-flash",
            "content": "cat content",
            "template": "cat template",
        }
        plan = plan_regeneration(metadata, prompt_path, raster_model=None, svg_model=None)
        assert plan["dispatch"] == "generate"
        assert plan["prompt"] == "A cat in space"
        assert plan["kwargs"]["content"] == "cat content"
        assert plan["kwargs"]["template"] == "cat template"
        assert plan["is_svg"] is False

    def test_edit_sidecar(self, tmp_path):
        # Create the source image so validation passes
        src = tmp_path / "source.png"
        src.write_bytes(b"fake")
        prompt_path = _make_prompt_path(tmp_path)
        metadata = {
            "format": "png",
            "source_image": "source.png",
            "edit_instruction": "make it blue",
            "model": "gemini-flash",
        }
        plan = plan_regeneration(metadata, prompt_path, raster_model=None, svg_model=None)
        assert plan["dispatch"] == "edit"
        assert plan["prompt"] == "make it blue"
        assert "content" not in plan["kwargs"]
        assert "template" not in plan["kwargs"]

    def test_composition_sidecar_with_source_images(self, tmp_path):
        img1 = tmp_path / "a.png"
        img2 = tmp_path / "b.png"
        img1.write_bytes(b"fake")
        img2.write_bytes(b"fake")
        prompt_path = _make_prompt_path(tmp_path)
        metadata = {
            "format": "png",
            "source_images": ["a.png", "b.png"],
            "final_prompt": "combine them",
            "model": "gemini-flash",
        }
        plan = plan_regeneration(metadata, prompt_path, raster_model=None, svg_model=None)
        assert plan["dispatch"] == "compose"
        assert plan["prompt"] == "combine them"
        assert "content" not in plan["kwargs"]
        assert "template" not in plan["kwargs"]

    def test_composition_sidecar_with_type_field(self, tmp_path):
        prompt_path = _make_prompt_path(tmp_path)
        metadata = {
            "format": "png",
            "type": "composition",
            "final_prompt": "compose something",
            "model": "gemini-flash",
        }
        plan = plan_regeneration(metadata, prompt_path, raster_model=None, svg_model=None)
        assert plan["dispatch"] == "compose"

    def test_svg_sidecar(self, tmp_path):
        prompt_path = _make_prompt_path(tmp_path)
        metadata = {
            "format": "svg",
            "final_prompt": "A lock icon",
            "model": "gemini-pro",
            "viewbox": "0 0 100 100",
            "animated": True,
            "style": "minimal",
        }
        plan = plan_regeneration(metadata, prompt_path, raster_model=None, svg_model=None)
        assert plan["dispatch"] == "generate"
        assert plan["is_svg"] is True
        assert plan["kwargs"]["viewbox"] == "0 0 100 100"
        assert plan["kwargs"]["animated"] is True
        assert plan["kwargs"]["style"] == "minimal"

    def test_raster_model_override(self, tmp_path):
        prompt_path = _make_prompt_path(tmp_path)
        metadata = {
            "format": "png",
            "final_prompt": "A cat",
            "model": "old-model",
        }
        plan = plan_regeneration(metadata, prompt_path, raster_model="new-model", svg_model=None)
        assert plan["model"] == "new-model"
        assert plan["model_changed"] is True

    def test_svg_model_override(self, tmp_path):
        prompt_path = _make_prompt_path(tmp_path)
        metadata = {
            "format": "svg",
            "final_prompt": "An icon",
            "model": "old-svg-model",
        }
        plan = plan_regeneration(metadata, prompt_path, raster_model=None, svg_model="new-svg-model")
        assert plan["model"] == "new-svg-model"
        assert plan["model_changed"] is True

    def test_no_prompt_raises(self, tmp_path):
        prompt_path = _make_prompt_path(tmp_path)
        metadata = {"format": "png", "model": "gemini-flash"}
        with pytest.raises(ValueError, match="No prompt found"):
            plan_regeneration(metadata, prompt_path, raster_model=None, svg_model=None)

    def test_missing_source_image_raises(self, tmp_path):
        prompt_path = _make_prompt_path(tmp_path)
        metadata = {
            "format": "png",
            "source_image": "nonexistent.png",
            "edit_instruction": "make it blue",
            "model": "gemini-flash",
        }
        with pytest.raises(ValueError, match="Source image not found"):
            plan_regeneration(metadata, prompt_path, raster_model=None, svg_model=None)

    def test_missing_source_images_raises(self, tmp_path):
        prompt_path = _make_prompt_path(tmp_path)
        metadata = {
            "format": "png",
            "source_images": ["nonexistent1.png", "nonexistent2.png"],
            "final_prompt": "combine them",
            "model": "gemini-flash",
        }
        with pytest.raises(ValueError, match="Source image not found"):
            plan_regeneration(metadata, prompt_path, raster_model=None, svg_model=None)

    def test_reference_single_image_overrides_to_edit(self, tmp_path):
        ref = tmp_path / "ref.png"
        ref.write_bytes(b"fake")
        prompt_path = _make_prompt_path(tmp_path)
        metadata = {
            "format": "png",
            "final_prompt": "A cat",
            "model": "gemini-flash",
        }
        plan = plan_regeneration(
            metadata, prompt_path, raster_model=None, svg_model=None,
            reference_images=[str(ref)],
        )
        assert plan["dispatch"] == "edit"
        assert plan["source_image"] == str(ref)

    def test_reference_multiple_images_overrides_to_compose(self, tmp_path):
        ref1 = tmp_path / "ref1.png"
        ref2 = tmp_path / "ref2.png"
        ref1.write_bytes(b"fake")
        ref2.write_bytes(b"fake")
        prompt_path = _make_prompt_path(tmp_path)
        metadata = {
            "format": "png",
            "final_prompt": "Combine them",
            "model": "gemini-flash",
        }
        plan = plan_regeneration(
            metadata, prompt_path, raster_model=None, svg_model=None,
            reference_images=[str(ref1), str(ref2)],
        )
        assert plan["dispatch"] == "compose"
        assert plan["source_images"] == [str(ref1), str(ref2)]

    def test_reference_on_svg_stays_generate(self, tmp_path, capsys):
        ref = tmp_path / "ref.png"
        ref.write_bytes(b"fake")
        prompt_path = _make_prompt_path(tmp_path)
        metadata = {
            "format": "svg",
            "final_prompt": "An icon",
            "model": "gemini-pro",
        }
        plan = plan_regeneration(
            metadata, prompt_path, raster_model=None, svg_model=None,
            reference_images=[str(ref)],
        )
        assert plan["dispatch"] == "generate"
        assert plan["is_svg"] is True
        captured = capsys.readouterr()
        assert "Warning" in captured.err

    def test_reference_clears_opposing_field(self, tmp_path):
        """When a single reference overrides to edit, source_images should be None."""
        ref = tmp_path / "ref.png"
        ref.write_bytes(b"fake")
        prompt_path = _make_prompt_path(tmp_path)
        # Start with a compose sidecar that has source_images
        metadata = {
            "format": "png",
            "source_images": ["old1.png", "old2.png"],
            "final_prompt": "Combine them",
            "model": "gemini-flash",
        }
        plan = plan_regeneration(
            metadata, prompt_path, raster_model=None, svg_model=None,
            reference_images=[str(ref)],
        )
        assert plan["dispatch"] == "edit"
        assert plan["source_image"] == str(ref)
        assert plan["source_images"] is None
