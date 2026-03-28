"""Tests for pure functions in generate_svg.py."""

import pytest

from generate_svg import extract_svg, build_prompt


# ---------------------------------------------------------------------------
# extract_svg
# ---------------------------------------------------------------------------

class TestExtractSvg:
    def test_svg_in_markdown_code_block(self):
        text = '```svg\n<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40"/></svg>\n```'
        result = extract_svg(text)
        assert result.startswith("<svg")
        assert "</svg>" in result

    def test_svg_in_xml_code_block(self):
        text = '```xml\n<svg xmlns="http://www.w3.org/2000/svg"><rect width="10" height="10"/></svg>\n```'
        result = extract_svg(text)
        assert result.startswith("<svg")
        assert "</svg>" in result

    def test_raw_svg_tags(self):
        text = 'Here is an SVG:\n<svg viewBox="0 0 50 50"><line x1="0" y1="0" x2="50" y2="50"/></svg>\nDone.'
        result = extract_svg(text)
        assert result.startswith("<svg")
        assert "</svg>" in result

    def test_svg_with_xml_declaration_extracts_svg_tag(self):
        """When input has <?xml> + <svg>...</svg>, the regex extracts the <svg> element."""
        text = '<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'
        result = extract_svg(text)
        assert result.startswith("<svg")
        assert "</svg>" in result

    def test_bare_xml_declaration_with_self_closing_svg(self):
        """The startswith('<?xml') fallback handles cases where the regex can't match
        (e.g., self-closing SVG without </svg>)."""
        text = '<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg" />'
        result = extract_svg(text)
        assert result.startswith("<?xml")

    def test_no_svg_content_raises(self):
        text = "This is just plain text with no SVG at all."
        with pytest.raises(RuntimeError, match="Could not extract SVG"):
            extract_svg(text)


# ---------------------------------------------------------------------------
# build_prompt
# ---------------------------------------------------------------------------

class TestBuildPrompt:
    def test_basic_prompt_contains_subject_and_instruction(self):
        result = build_prompt("A lock icon", viewbox=None, animated=False, style=None)
        assert "Subject: A lock icon" in result
        assert "Generate an SVG" in result

    def test_with_viewbox(self):
        result = build_prompt("test", viewbox="0 0 200 200", animated=False, style=None)
        assert "viewBox: 0 0 200 200" in result

    def test_animated_true(self):
        result = build_prompt("test", viewbox=None, animated=True, style=None)
        assert "keyframes" in result.lower() or "CSS" in result

    def test_animated_false(self):
        result = build_prompt("test", viewbox=None, animated=False, style=None)
        assert "Static SVG" in result

    def test_with_style(self):
        result = build_prompt("test", viewbox=None, animated=False, style="minimal")
        assert "Style: minimal" in result
