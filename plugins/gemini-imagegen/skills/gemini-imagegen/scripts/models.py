"""Shared Gemini image-model IDs and response helpers.

Single source of truth for model identifiers used by generate_image.py,
edit_image.py, compose_images.py, multi_turn_chat.py, gemini_images.py,
and regenerate.py.
"""

# GA model IDs (canonical)
FLASH_MODEL = "gemini-nano-banana-2.1"  # Nano Banana 2.1 -- default
PRO_MODEL = "gemini-3-pro-image"        # Nano Banana Pro

# Superseded IDs still accepted so existing .prompt sidecars regenerate unchanged
LEGACY_MODELS = [
    "gemini-3.1-flash-image",
    "gemini-3.1-flash-image-preview",
    "gemini-3-pro-image-preview",
    "gemini-2.5-flash-image",
]

DEFAULT_MODEL = FLASH_MODEL

# argparse --model choices for every raster script
RASTER_MODEL_CHOICES = [FLASH_MODEL, PRO_MODEL, *LEGACY_MODELS]

# Models that default to 2K output (Pro costs the same at 1K and 2K)
PRO_MODELS = frozenset({PRO_MODEL, "gemini-3-pro-image-preview"})


def default_size_for_model(model: str, image_size: str | None) -> str | None:
    """Return the effective image size for a request.

    An explicit image_size always wins. With no explicit size, Pro models
    default to "2K" (same cost as 1K, more detail); all other models return
    None so the API default (1K) applies.
    """
    if image_size is not None:
        return image_size
    if model in PRO_MODELS:
        return "2K"
    return None


def extract_text_and_image(parts):
    """Extract the final text and image from response parts.

    Skips thought parts: gemini-nano-banana-2.1 and gemini-3-pro-image are
    thinking models that can return interleaved thought text/images marked
    with part.thought == True.
    Returns (text, image) where image is the result of part.as_image() on the
    last non-thought inline_data part, or None for either slot if absent.
    """
    text = None
    image = None
    for part in parts:
        if getattr(part, "thought", None):
            continue
        if part.text is not None:
            text = part.text
        elif part.inline_data is not None:
            image = part.as_image()
    return text, image
