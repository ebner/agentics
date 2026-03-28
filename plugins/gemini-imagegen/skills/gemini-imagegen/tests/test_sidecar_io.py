"""Tests for sidecar read/write functions in edit_image.py and compose_images.py."""

import pytest
from pathlib import Path

import yaml

from edit_image import read_existing_prompt, write_edit_prompt_sidecar
from compose_images import write_compose_prompt_sidecar


# ---------------------------------------------------------------------------
# read_existing_prompt  (from edit_image.py)
# ---------------------------------------------------------------------------

class TestReadExistingPrompt:
    def test_valid_sidecar_returns_dict(self, tmp_path):
        img = tmp_path / "photo.png"
        img.write_bytes(b"fake")
        sidecar = tmp_path / "photo.prompt"
        sidecar.write_text("---\nmodel: gemini-flash\nformat: png\nfinal_prompt: hello\n---\n")
        result = read_existing_prompt(str(img))
        assert result is not None
        assert result["model"] == "gemini-flash"
        assert result["final_prompt"] == "hello"

    def test_no_sidecar_returns_none(self, tmp_path):
        img = tmp_path / "photo.png"
        img.write_bytes(b"fake")
        result = read_existing_prompt(str(img))
        assert result is None

    def test_invalid_yaml_returns_none(self, tmp_path):
        img = tmp_path / "photo.png"
        img.write_bytes(b"fake")
        sidecar = tmp_path / "photo.prompt"
        sidecar.write_text("---\n: :\n  - [\n---\n")
        result = read_existing_prompt(str(img))
        assert result is None


# ---------------------------------------------------------------------------
# write_edit_prompt_sidecar  (from edit_image.py)
# ---------------------------------------------------------------------------

class TestWriteEditPromptSidecar:
    def test_creates_prompt_file(self, tmp_path):
        output = str(tmp_path / "edited.png")
        write_edit_prompt_sidecar(
            output_path=output,
            instruction="make it blue",
            model="gemini-flash",
            aspect_ratio=None,
            image_size=None,
            output_format="png",
            transparent=False,
            tolerance=0,
            edge_tolerance=0,
            input_path="source.png",
        )
        prompt_path = tmp_path / "edited.prompt"
        assert prompt_path.exists()

    def test_contains_source_and_edit_fields(self, tmp_path):
        output = str(tmp_path / "edited.png")
        write_edit_prompt_sidecar(
            output_path=output,
            instruction="make it blue",
            model="gemini-flash",
            aspect_ratio=None,
            image_size=None,
            output_format="png",
            transparent=False,
            tolerance=0,
            edge_tolerance=0,
            input_path="source.png",
        )
        content = (tmp_path / "edited.prompt").read_text()
        parts = content.split("---", 2)
        parsed = yaml.safe_load(parts[1])
        assert parsed["source_image"] == "source.png"
        assert "make it blue" in parsed["edit_instruction"]
        assert "edit_history" in parsed

    def test_preserves_previous_edit_history(self, tmp_path):
        existing_metadata = {
            "edit_history": [
                {"date": "2025-01-01T00:00:00Z", "instruction": "first edit"},
                {"date": "2025-06-01T00:00:00Z", "instruction": "second edit"},
            ]
        }
        output = str(tmp_path / "edited.png")
        write_edit_prompt_sidecar(
            output_path=output,
            instruction="third edit",
            model="gemini-flash",
            aspect_ratio=None,
            image_size=None,
            output_format="png",
            transparent=False,
            tolerance=0,
            edge_tolerance=0,
            input_path="source.png",
            existing_metadata=existing_metadata,
        )
        content = (tmp_path / "edited.prompt").read_text()
        parts = content.split("---", 2)
        parsed = yaml.safe_load(parts[1])
        history = parsed["edit_history"]
        assert isinstance(history, list)
        # Should have 2 previous + 1 current = 3
        assert len(history) == 3
        instructions = [entry["instruction"] for entry in history]
        assert "first edit" in instructions
        assert "second edit" in instructions
        assert "third edit" in instructions


# ---------------------------------------------------------------------------
# write_compose_prompt_sidecar  (from compose_images.py)
# ---------------------------------------------------------------------------

class TestWriteComposePromptSidecar:
    def test_creates_prompt_file(self, tmp_path):
        output = str(tmp_path / "composed.png")
        write_compose_prompt_sidecar(
            output_path=output,
            instruction="combine into collage",
            model="gemini-flash",
            aspect_ratio=None,
            image_size=None,
            output_format="png",
            transparent=False,
            tolerance=0,
            edge_tolerance=0,
            source_images=["a.png", "b.png"],
        )
        prompt_path = tmp_path / "composed.prompt"
        assert prompt_path.exists()

    def test_contains_source_images_and_type(self, tmp_path):
        output = str(tmp_path / "composed.png")
        write_compose_prompt_sidecar(
            output_path=output,
            instruction="combine into collage",
            model="gemini-flash",
            aspect_ratio=None,
            image_size=None,
            output_format="png",
            transparent=False,
            tolerance=0,
            edge_tolerance=0,
            source_images=["a.png", "b.png"],
        )
        content = (tmp_path / "composed.prompt").read_text()
        parts = content.split("---", 2)
        parsed = yaml.safe_load(parts[1])
        assert parsed["type"] == "composition"
        assert isinstance(parsed["source_images"], list)
        assert "a.png" in parsed["source_images"]
        assert "b.png" in parsed["source_images"]

    def test_contains_final_prompt(self, tmp_path):
        output = str(tmp_path / "composed.png")
        write_compose_prompt_sidecar(
            output_path=output,
            instruction="combine into collage",
            model="gemini-flash",
            aspect_ratio=None,
            image_size=None,
            output_format="png",
            transparent=False,
            tolerance=0,
            edge_tolerance=0,
            source_images=["a.png"],
        )
        content = (tmp_path / "composed.prompt").read_text()
        parts = content.split("---", 2)
        parsed = yaml.safe_load(parts[1])
        assert "final_prompt" in parsed
        assert "combine into collage" in parsed["final_prompt"]
