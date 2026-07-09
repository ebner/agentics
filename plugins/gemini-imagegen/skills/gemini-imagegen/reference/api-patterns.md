# Direct Gemini API Patterns (google-genai SDK)

Fallback patterns for when the CLI scripts cannot be used (custom pipelines,
Google Search grounding, embedding in other Python code). Always prefer the
CLI scripts in `scripts/` — they handle venv setup, sidecar files, and
transparency automatically.

## Core API Pattern

```python
import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Basic generation (1K, 1:1 - defaults)
response = client.models.generate_content(
    model="gemini-3.1-flash-image",
    contents=["Your prompt here"],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
    ),
)

for part in response.parts:
    if part.text:
        print(part.text)
    elif part.inline_data:
        image = part.as_image()
        image.save("output.jpg")
```

**Thought parts (`gemini-3-pro-image`):** the pro model is a thinking model
and can return interleaved thought text/images in `response.parts`, marked
with `part.thought == True`. Skip them when extracting output:

```python
for part in response.parts:
    if getattr(part, "thought", None):
        continue  # interim reasoning, not the final output
    if part.text:
        print(part.text)
    elif part.inline_data:
        image = part.as_image()
```

## Custom Resolution & Aspect Ratio

```python
from google.genai import types

response = client.models.generate_content(
    model="gemini-3.1-flash-image",
    contents=[prompt],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",  # Wide format
            image_size="2K"       # Higher resolution
        ),
    )
)
```

## Editing Images

Pass existing images with text prompts:

```python
from PIL import Image

img = Image.open("input.png")
response = client.models.generate_content(
    model="gemini-3.1-flash-image",
    contents=["Add a sunset to this scene", img],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
    ),
)
```

## Multi-Turn Refinement

Use chat for iterative editing:

```python
from google.genai import types

chat = client.chats.create(
    model="gemini-3.1-flash-image",
    config=types.GenerateContentConfig(response_modalities=['TEXT', 'IMAGE'])
)

response = chat.send_message("Create a logo for 'Acme Corp'")
# Save first image...

response = chat.send_message("Make the text bolder and add a blue gradient")
# Save refined image...
```

## Advanced Features

### Google Search Grounding

Generate images based on real-time data (pro model capability):

```python
response = client.models.generate_content(
    model="gemini-3-pro-image",
    contents=["Visualize today's weather in Tokyo as an infographic"],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        tools=[{"google_search": {}}]
    )
)
```

### Multiple Reference Images (Up to 14)

Combine elements from multiple sources. Use `gemini-3-pro-image` when the
people in the reference images must stay recognizable:

```python
response = client.models.generate_content(
    model="gemini-3-pro-image",
    contents=[
        "Create a group photo of these people in an office",
        Image.open("person1.png"),
        Image.open("person2.png"),
        Image.open("person3.png"),
    ],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
    ),
)
```
