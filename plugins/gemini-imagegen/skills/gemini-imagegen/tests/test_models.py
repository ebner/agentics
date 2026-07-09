"""Tests for models.py: default sizes, choices contract, thought filtering."""

from types import SimpleNamespace

from models import (
    DEFAULT_MODEL,
    FLASH_MODEL,
    PRO_MODEL,
    RASTER_MODEL_CHOICES,
    default_size_for_model,
    extract_text_and_image,
)


# ---------------------------------------------------------------------------
# default_size_for_model
# ---------------------------------------------------------------------------

class TestDefaultSizeForModel:
    def test_pro_without_size_defaults_to_2k(self):
        assert default_size_for_model(PRO_MODEL, None) == "2K"

    def test_pro_preview_without_size_defaults_to_2k(self):
        assert default_size_for_model("gemini-3-pro-image-preview", None) == "2K"

    def test_flash_without_size_stays_none(self):
        assert default_size_for_model(FLASH_MODEL, None) is None

    def test_legacy_flash_without_size_stays_none(self):
        assert default_size_for_model("gemini-2.5-flash-image", None) is None
        assert default_size_for_model("gemini-3.1-flash-image-preview", None) is None

    def test_explicit_size_wins_on_pro(self):
        assert default_size_for_model(PRO_MODEL, "1K") == "1K"

    def test_explicit_size_wins_on_flash(self):
        assert default_size_for_model(FLASH_MODEL, "4K") == "4K"


# ---------------------------------------------------------------------------
# Model ID contract
# ---------------------------------------------------------------------------

class TestModelChoicesContract:
    def test_ga_ids_are_canonical(self):
        # Pins the sidecar/docs contract: GA IDs, flash is the default
        assert FLASH_MODEL == "gemini-3.1-flash-image"
        assert PRO_MODEL == "gemini-3-pro-image"
        assert DEFAULT_MODEL == FLASH_MODEL

    def test_choices_accept_ga_and_all_legacy_ids(self):
        # Old .prompt sidecars must keep regenerating via the CLI
        assert FLASH_MODEL in RASTER_MODEL_CHOICES
        assert PRO_MODEL in RASTER_MODEL_CHOICES
        for legacy in (
            "gemini-3.1-flash-image-preview",
            "gemini-3-pro-image-preview",
            "gemini-2.5-flash-image",
        ):
            assert legacy in RASTER_MODEL_CHOICES


# ---------------------------------------------------------------------------
# extract_text_and_image
# ---------------------------------------------------------------------------

def _part(text=None, inline=None, thought=None):
    p = SimpleNamespace(text=text, inline_data=inline, thought=thought)
    if inline is not None:
        p.as_image = lambda inline=inline: inline
    return p


class TestExtractTextAndImage:
    def test_skips_thought_text_and_image_parts(self):
        parts = [
            _part(text="thinking...", thought=True),
            _part(inline=b"thought-img", thought=True),
            _part(text="final caption"),
            _part(inline=b"final-img"),
        ]
        text, image = extract_text_and_image(parts)
        assert text == "final caption"
        assert image == b"final-img"

    def test_thought_part_never_wins_even_when_last(self):
        parts = [
            _part(text="real"),
            _part(inline=b"real-img"),
            _part(text="late thought", thought=True),
            _part(inline=b"late-thought-img", thought=True),
        ]
        text, image = extract_text_and_image(parts)
        assert text == "real"
        assert image == b"real-img"

    def test_last_non_thought_image_wins(self):
        parts = [_part(inline=b"first"), _part(inline=b"second")]
        _, image = extract_text_and_image(parts)
        assert image == b"second"

    def test_parts_without_thought_attribute(self):
        # Older SDK Part objects may lack .thought entirely
        p = SimpleNamespace(text="hello", inline_data=None)
        text, image = extract_text_and_image([p])
        assert text == "hello"
        assert image is None

    def test_no_parts_returns_none_pair(self):
        assert extract_text_and_image([]) == (None, None)
