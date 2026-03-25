"""
Gemini Image Generation Library

A simple Python library for generating and editing images with the Gemini API.

Usage:
    from gemini_images import GeminiImageGenerator

    gen = GeminiImageGenerator()
    gen.generate("A sunset over mountains", "sunset.png")
    gen.generate("Illustration", "logo.png", output_format="png", transparent=True)
    gen.edit("input.png", "Add clouds", "output.png")

Environment:
    GEMINI_API_KEY - Required API key
"""

import os
from pathlib import Path
from typing import Literal

from PIL import Image
from google import genai
from google.genai import types

from generate_image import make_transparent, write_prompt_sidecar
from edit_image import write_edit_prompt_sidecar, read_existing_prompt
from compose_images import write_compose_prompt_sidecar


AspectRatio = Literal["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]
ImageSize = Literal["1K", "2K", "4K"]
Model = Literal["gemini-2.5-flash-image", "gemini-3.1-flash-image-preview"]
OutputFormat = Literal["png", "jpg", "webp"]


class GeminiImageGenerator:
    """High-level interface for Gemini image generation."""

    FLASH = "gemini-2.5-flash-image"
    PRO = "gemini-3.1-flash-image-preview"

    def __init__(self, api_key: str | None = None, model: Model = FLASH):
        """Initialize the generator.

        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
            model: Default model to use
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("GEMINI_API_KEY not set")

        self.client = genai.Client(api_key=self.api_key)
        self.model = model

    def _build_config(
        self,
        aspect_ratio: AspectRatio | None = None,
        image_size: ImageSize | None = None,
        google_search: bool = False,
    ) -> types.GenerateContentConfig:
        """Build generation config."""
        kwargs = {"response_modalities": ["TEXT", "IMAGE"]}

        img_config = {}
        if aspect_ratio:
            img_config["aspect_ratio"] = aspect_ratio
        if image_size:
            img_config["image_size"] = image_size

        if img_config:
            kwargs["image_config"] = types.ImageConfig(**img_config)

        if google_search:
            kwargs["tools"] = [{"google_search": {}}]

        return types.GenerateContentConfig(**kwargs)

    def _save_image(
        self,
        image: Image.Image,
        output: Path,
        output_format: OutputFormat,
        transparent: bool,
        tolerance: int,
        edge_tolerance: int,
    ) -> Image.Image:
        """Save image with format and transparency handling.

        Args:
            image: PIL Image to save
            output: Output file path
            output_format: Output format (png, jpg, webp)
            transparent: Whether to apply transparency
            tolerance: Color tolerance for white detection
            edge_tolerance: Edge expansion tolerance

        Returns:
            The processed image (possibly with transparency applied)
        """
        # Apply transparency conversion if requested
        if transparent:
            image = make_transparent(image, tolerance, edge_tolerance)

        # Ensure output directory exists
        output.parent.mkdir(parents=True, exist_ok=True)

        # Save with appropriate format
        if output_format == "png":
            image.save(output, format="PNG")
        elif output_format == "webp":
            image.save(output, format="WEBP")
        else:
            # JPEG doesn't support RGBA, convert if needed
            if image.mode == "RGBA":
                image = image.convert("RGB")
            image.save(output, format="JPEG")

        return image

    def generate(
        self,
        prompt: str,
        output: str | Path,
        *,
        model: Model | None = None,
        aspect_ratio: AspectRatio | None = None,
        image_size: ImageSize | None = None,
        output_format: OutputFormat = "jpg",
        transparent: bool = False,
        tolerance: int = 0,
        edge_tolerance: int = 0,
        google_search: bool = False,
        content: str | None = None,
        template: str | None = None,
    ) -> tuple[Path, str | None]:
        """Generate an image from a text prompt.

        Args:
            prompt: Text description
            output: Output file path
            model: Override default model
            aspect_ratio: Output aspect ratio
            image_size: Output resolution
            output_format: Output format (png, jpg, webp)
            transparent: Convert white background to transparent (requires PNG)
            tolerance: Color tolerance for white detection (0-255)
            edge_tolerance: Edge expansion tolerance (0 = disabled)
            google_search: Enable Google Search grounding (Pro only)
            content: Optional content description for .prompt sidecar
            template: Optional template text for .prompt sidecar

        Returns:
            Tuple of (output path, optional text response)

        Raises:
            ValueError: If transparent is True but format is not PNG
        """
        if transparent and output_format != "png":
            raise ValueError(
                f"Transparency requires PNG format, but got '{output_format}'. "
                "Use output_format='png' with transparent=True."
            )

        output = Path(output)
        used_model = model or self.model
        config = self._build_config(aspect_ratio, image_size, google_search)

        response = self.client.models.generate_content(
            model=used_model,
            contents=[prompt],
            config=config,
        )

        text = None
        image = None
        for part in response.parts:
            if part.text:
                text = part.text
            elif part.inline_data:
                image = part.as_image()

        if image is None:
            raise RuntimeError("No image was generated. Check your prompt and try again.")

        self._save_image(image, output, output_format, transparent, tolerance, edge_tolerance)

        # Write .prompt sidecar file
        write_prompt_sidecar(
            output_path=str(output),
            prompt=prompt,
            model=used_model,
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            output_format=output_format,
            transparent=transparent,
            tolerance=tolerance,
            edge_tolerance=edge_tolerance,
            content=content,
            template=template,
        )

        return output, text

    def edit(
        self,
        input_image: str | Path | Image.Image,
        instruction: str,
        output: str | Path,
        *,
        model: Model | None = None,
        aspect_ratio: AspectRatio | None = None,
        image_size: ImageSize | None = None,
        output_format: OutputFormat = "jpg",
        transparent: bool = False,
        tolerance: int = 0,
        edge_tolerance: int = 0,
    ) -> tuple[Path, str | None]:
        """Edit an existing image.

        Args:
            input_image: Input image (path or PIL Image)
            instruction: Edit instruction
            output: Output file path
            model: Override default model
            aspect_ratio: Output aspect ratio
            image_size: Output resolution
            output_format: Output format (png, jpg, webp)
            transparent: Convert white background to transparent (requires PNG)
            tolerance: Color tolerance for white detection (0-255)
            edge_tolerance: Edge expansion tolerance (0 = disabled)

        Returns:
            Tuple of (output path, optional text response)

        Raises:
            ValueError: If transparent is True but format is not PNG
        """
        if transparent and output_format != "png":
            raise ValueError(
                f"Transparency requires PNG format, but got '{output_format}'. "
                "Use output_format='png' with transparent=True."
            )

        output = Path(output)
        used_model = model or self.model
        input_path_str = None

        if isinstance(input_image, (str, Path)):
            input_path_str = str(input_image)
            input_image = Image.open(input_image)

        # Read existing prompt metadata if available
        existing_metadata = None
        if input_path_str:
            existing_metadata = read_existing_prompt(input_path_str)

        config = self._build_config(aspect_ratio, image_size)

        response = self.client.models.generate_content(
            model=used_model,
            contents=[instruction, input_image],
            config=config,
        )

        text = None
        image = None
        for part in response.parts:
            if part.text:
                text = part.text
            elif part.inline_data:
                image = part.as_image()

        if image is None:
            raise RuntimeError("No image was generated. Check your instruction and try again.")

        self._save_image(image, output, output_format, transparent, tolerance, edge_tolerance)

        # Write .prompt sidecar file with edit history
        write_edit_prompt_sidecar(
            output_path=str(output),
            instruction=instruction,
            model=used_model,
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            output_format=output_format,
            transparent=transparent,
            tolerance=tolerance,
            edge_tolerance=edge_tolerance,
            input_path=input_path_str or "unknown",
            existing_metadata=existing_metadata,
        )

        return output, text

    def compose(
        self,
        instruction: str,
        images: list[str | Path | Image.Image],
        output: str | Path,
        *,
        model: Model | None = None,
        aspect_ratio: AspectRatio | None = None,
        image_size: ImageSize | None = None,
        output_format: OutputFormat = "jpg",
        transparent: bool = False,
        tolerance: int = 0,
        edge_tolerance: int = 0,
    ) -> tuple[Path, str | None]:
        """Compose multiple images into one.

        Args:
            instruction: Composition instruction
            images: List of input images (up to 14)
            output: Output file path
            model: Override default model (Pro recommended)
            aspect_ratio: Output aspect ratio
            image_size: Output resolution
            output_format: Output format (png, jpg, webp)
            transparent: Convert white background to transparent (requires PNG)
            tolerance: Color tolerance for white detection (0-255)
            edge_tolerance: Edge expansion tolerance (0 = disabled)

        Returns:
            Tuple of (output path, optional text response)

        Raises:
            ValueError: If transparent is True but format is not PNG
        """
        if transparent and output_format != "png":
            raise ValueError(
                f"Transparency requires PNG format, but got '{output_format}'. "
                "Use output_format='png' with transparent=True."
            )

        output = Path(output)
        used_model = model or self.PRO  # Pro recommended for composition

        # Load images and track paths
        loaded = []
        source_paths = []
        for img in images:
            if isinstance(img, (str, Path)):
                source_paths.append(str(img))
                loaded.append(Image.open(img))
            else:
                source_paths.append("inline_image")
                loaded.append(img)

        config = self._build_config(aspect_ratio, image_size)
        contents = [instruction] + loaded

        response = self.client.models.generate_content(
            model=used_model,
            contents=contents,
            config=config,
        )

        text = None
        image = None
        for part in response.parts:
            if part.text:
                text = part.text
            elif part.inline_data:
                image = part.as_image()

        if image is None:
            raise RuntimeError("No image was generated.")

        self._save_image(image, output, output_format, transparent, tolerance, edge_tolerance)

        # Write .prompt sidecar file
        write_compose_prompt_sidecar(
            output_path=str(output),
            instruction=instruction,
            model=used_model,
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            output_format=output_format,
            transparent=transparent,
            tolerance=tolerance,
            edge_tolerance=edge_tolerance,
            source_images=source_paths,
        )

        return output, text

    def chat(self) -> "ImageChat":
        """Start an interactive chat session for iterative refinement."""
        return ImageChat(self.client, self.model)


class ImageChat:
    """Multi-turn chat session for iterative image generation."""

    def __init__(self, client: genai.Client, model: Model):
        self.client = client
        self.model = model
        self._chat = client.chats.create(
            model=model,
            config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
        )
        self.current_image: Image.Image | None = None

    def send(
        self,
        message: str,
        image: Image.Image | str | Path | None = None,
    ) -> tuple[Image.Image | None, str | None]:
        """Send a message and optionally an image.

        Returns:
            Tuple of (generated image or None, text response or None)
        """
        contents = [message]
        if image:
            if isinstance(image, (str, Path)):
                image = Image.open(image)
            contents.append(image)

        response = self._chat.send_message(contents)

        text = None
        img = None
        for part in response.parts:
            if part.text:
                text = part.text
            elif part.inline_data:
                img = part.as_image()
                self.current_image = img

        return img, text

    def reset(self):
        """Reset the chat session."""
        self._chat = self.client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
        )
        self.current_image = None
