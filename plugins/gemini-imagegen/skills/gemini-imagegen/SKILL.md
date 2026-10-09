---
name: gemini-imagegen
description: This skill should be used when generating and editing images using the Gemini API (Nano Banana 2.1 and Nano Banana Pro). It applies when creating images from text prompts, editing existing images, applying style transfers, generating logos with text, creating stickers, product mockups, style-transferring photos of people while keeping them recognizable (identity/face preservation), keeping a character consistent across images, or any image generation/manipulation task. Supports text-to-image, image editing, multi-turn refinement, and composition from multiple reference images.
allowed-tools: Read, Write, Glob, Grep, Task, Bash(find:*gemini-imagegen*), Bash(bash:*gemini-imagegen/scripts/run.sh*)
---

# Gemini Image Generation (Nano Banana 2.1 & Pro)

Generate and edit images using Google's Gemini API. The environment variable `GEMINI_API_KEY` must be set.

## Model Selection

| Model | Alias | Resolution | Use For |
|-------|-------|------------|---------|
| `gemini-nano-banana-2.1` | Nano Banana 2.1 | 1K-4K (default 1K) | Default for all generation and editing |
| `gemini-3-pro-image` | Nano Banana Pro | 1K-4K (default 2K) | Identity/face preservation, character consistency |

Legacy IDs `gemini-3.1-flash-image` (Nano Banana 2),
`gemini-3.1-flash-image-preview`, `gemini-3-pro-image-preview`, and
`gemini-2.5-flash-image` remain accepted by all scripts (so old `.prompt`
sidecars regenerate) but must not be used for new images.

### Model decision rules

Add `--model gemini-3-pro-image` if AND ONLY IF at least one of these holds:

1. The request includes one or more reference photos of a real person or pet
   AND the output must keep that subject recognizable (examples: "make a
   Ghibli-style image of this photo of me", portrait restyles, placing a
   person into a new scene or outfit).
2. The same character or subject must stay visually consistent across two or
   more generated images.
3. The user explicitly asks for "pro", "Nano Banana Pro", "high fidelity", or
   "best quality".

In every other case use the default `gemini-nano-banana-2.1`. Do not switch to
Pro because a task merely seems difficult or detailed.

When Pro is selected without an explicit `--size`, the scripts automatically
request 2K (Pro costs the same at 1K and 2K). An explicit `--size` always wins.

## Quick Reference

### Default Settings
- **Model:** `gemini-nano-banana-2.1` (Nano Banana 2.1); `gemini-3-pro-image` per the Model decision rules
- **Resolution:** 1K default (2K default when the pro model is selected; options: 1K, 2K, 4K)
- **Aspect Ratio:** 1:1 (default)
- **Format:** jpg (default, options: png, jpg, webp)
- **Transparency:** disabled (use `--transparent` to enable)

### Available Aspect Ratios
`1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`

### Available Resolutions
`1K` (default), `2K`, `4K`

### Available Output Formats
- `jpg` (default) - Best for photos, smaller file size
- `png` - Best for illustrations, supports transparency
- `webp` - Best compression, supports transparency

## Script Path Setup (run before any script command)

The scripts directory is located alongside this SKILL.md. Before running any
script command, discover the path once and reuse it for the entire session:

```bash
# Discover the path once per session and reuse it:
RUN_SH="$(find ~/.claude -path '*/gemini-imagegen/scripts/run.sh' -print -quit 2>/dev/null)"
```

Then use `bash "$RUN_SH"` in place of the full path in all subsequent commands.
If `$RUN_SH` is empty, the skill is not installed — inform the user.

## CLI Scripts (Recommended)

Use the provided scripts for hands-free image generation. The `run.sh` wrapper automatically sets up a virtual environment and installs dependencies on first use.

### Basic Generation

```bash
# Generate an image (venv setup is automatic)
bash "$RUN_SH" generate_image.py "A teal lock icon" output.jpg

# With aspect ratio and resolution
bash "$RUN_SH" generate_image.py "A wide landscape" wide.jpg --aspect 16:9 --size 2K

# Identity-preserving restyle of a person (Model decision rule 1)
bash "$RUN_SH" edit_image.py me.jpg "Ghibli-style illustration, keep me recognizable" me-ghibli.png \
    --model gemini-3-pro-image --format png
```

### PNG with Transparency

```bash
# Generate with transparent background (converts white to transparent)
bash "$RUN_SH" generate_image.py \
    "An illustration with white background" output.png \
    --format png --transparent

# With edge tolerance for anti-aliasing (recommended for illustrations)
bash "$RUN_SH" generate_image.py \
    "An illustration with white background" output.png \
    --format png --transparent --edge-tolerance 10
```

### Edit Existing Images

```bash
bash "$RUN_SH" edit_image.py input.jpg "Add a sunset" output.jpg

# Edit and convert to transparent PNG
bash "$RUN_SH" edit_image.py input.jpg "Add a sunset" output.png \
    --format png --transparent
```

### Multi-Image Composition

```bash
bash "$RUN_SH" compose_images.py "Combine into a collage" output.jpg image1.jpg image2.jpg
```

### Subject & Face Consistency (Nano Banana Pro)

Use these recipes whenever Model decision rule 1 or 2 applies. Script choice:
`edit_image.py` for a single photo restyle; `compose_images.py` when there are
two or more reference photos (of one person or several people).

**Recipe 1: Single-photo restyle (keep the person recognizable)**

```bash
bash "$RUN_SH" edit_image.py photo.jpg \
    "Restyle this photo as a Studio Ghibli-style illustration. Preserve the person's facial features, face shape, hairstyle, skin tone, and expression exactly so they remain clearly recognizable. Keep the original pose and composition; only change the artistic style." \
    ghibli.png --model gemini-3-pro-image --format png
```

**Recipe 2: Multiple reference photos of the same person** (two to five photos
from different angles improve likeness)

```bash
bash "$RUN_SH" compose_images.py \
    "Using these photos of the same person as identity references, generate a portrait of them as a 1920s film-noir detective in a rainy street. Their face must match the reference photos exactly - do not alter facial identity, age, or skin tone." \
    noir.jpg front.jpg profile.jpg smiling.jpg --model gemini-3-pro-image
```

**Recipe 3: Group photo from individual photos**

```bash
bash "$RUN_SH" compose_images.py \
    "Create one group photo of these three people standing together in a sunlit office, natural candid poses. Each person must keep the exact face, hairstyle, and skin tone from their reference photo." \
    team.jpg person1.jpg person2.jpg person3.jpg --model gemini-3-pro-image --aspect 16:9
```

**Identity-preservation prompt patterns.** Every identity-preserving prompt
must contain all three of:

1. An explicit preservation clause: "Preserve the person's facial features,
   face shape, and expression exactly" or "must remain clearly recognizable
   as in the reference photo".
2. A negative clause: "Do not alter facial identity, age, or skin tone."
3. A scope split: name what MAY change (style, background, clothing,
   lighting) and what MUST NOT change (face, identity, body proportions).

**Resolution:** Pro defaults to 2K automatically when `--size` is omitted
(more facial detail, same cost as 1K). Use `--size 4K` only for print-scale
output.

### Multi-Turn Refinement

```bash
# Start interactive chat session
bash "$RUN_SH" multi_turn_chat.py --output-dir ./session_name
```

### Convert Existing Images to Transparent PNGs

```bash
# Dry run (shows what would be converted)
bash "$RUN_SH" convert_to_transparent.py ./images --recursive

# Execute conversion
bash "$RUN_SH" convert_to_transparent.py ./images --recursive --execute

# With edge tolerance for anti-aliased edges
bash "$RUN_SH" convert_to_transparent.py ./images --recursive --execute --edge-tolerance 10
```

### Regenerate from Sidecar Files

```bash
# Dry run - preview what would be regenerated
bash "$RUN_SH" regenerate.py ./frontend/public/images/illustrations/ -r

# Regenerate all images (reads .prompt sidecars, dispatches to correct script)
bash "$RUN_SH" regenerate.py ./frontend/public/images/illustrations/ -r --execute

# Regenerate with a new raster model (model upgrade scenario)
bash "$RUN_SH" regenerate.py ./frontend/public/images/illustrations/ -r --execute \
    --raster-model gemini-nano-banana-2.1

# Override SVG model
bash "$RUN_SH" regenerate.py ./assets/ -r --execute \
    --svg-model gemini-3.1-pro-preview

# Filter by type: svg, raster, edit, or composition
bash "$RUN_SH" regenerate.py ./assets/ -r --execute --filter svg
bash "$RUN_SH" regenerate.py ./assets/ -r --execute --filter raster
bash "$RUN_SH" regenerate.py ./assets/ -r --execute --filter edit
bash "$RUN_SH" regenerate.py ./assets/ -r --execute --filter composition

# Regenerate with a reference image (overrides sidecar source)
bash "$RUN_SH" regenerate.py ./hero.prompt --execute --reference ./source.png

# Regenerate with multiple reference images (composition mode)
bash "$RUN_SH" regenerate.py ./collage.prompt --execute --reference img1.png img2.png

# Regenerate a single image
bash "$RUN_SH" regenerate.py ./hero-main.prompt --execute
```

The script reads each `.prompt` sidecar and auto-detects the dispatch type: edits (has `source_image`), compositions (has `source_images`), SVGs (`format: svg`), or plain text-to-image generation. Each type dispatches to its original script (`edit_image`, `compose_images`, `generate_svg`, or `generate_image`) with the original parameters. Use `--reference` to override or inject reference images. The default invocation is a dry run; review its plan, then re-run with `--execute`.

## PNG Transparency

### When to Use Transparent PNGs
- Illustrations on colored or off-white page backgrounds
- Empty state graphics that should blend with the UI
- Icons and logos that need to work on any background
- Feature illustrations for landing pages

### How Transparency Works

The `--transparent` flag converts white background pixels to transparent:

1. **Pass 1:** Convert pixels matching pure white (#FFFFFF) to transparent
2. **Pass 2:** (with `--edge-tolerance`) Expand transparency to near-white pixels adjacent to already-transparent pixels

### Tolerance Options

| Flag | Default | Description |
|------|---------|-------------|
| `--tolerance N` | 0 | Color distance from pure white (0-255). 0 = exact #FFFFFF only |
| `--edge-tolerance N` | 0 | Expand transparency to near-white neighbors. Recommended: 10 for anti-aliased edges |

**Recommended for illustrations:** `--tolerance 0 --edge-tolerance 10`

This converts pure white backgrounds while cleaning up anti-aliased edges, without affecting light colors in the illustration interior.

### Example: Generate Transparent Illustration

```bash
bash "$RUN_SH" generate_image.py \
    "Create an empty state illustration in soft minimalism style. Background: pure white (#FFFFFF)." \
    empty-state.png \
    --format png --transparent --edge-tolerance 10 --aspect 1:1
```

### Example: Convert Existing JPG to Transparent PNG

```bash
bash "$RUN_SH" convert_to_transparent.py \
    ~/images/illustrations --recursive --execute --edge-tolerance 10
```

## Prompt Sidecar Files

Every generated image automatically creates a `.prompt` sidecar file containing full metadata for reproducibility.

### File Location
The `.prompt` file is created alongside the image:
- `output.png` → `output.prompt`
- `illustrations/empty-state.png` → `illustrations/empty-state.prompt`

### File Format

```yaml
---
model: gemini-nano-banana-2.1
aspect_ratio: "1:1"
resolution: 1K
format: png
transparent: true
tolerance: 0
edge_tolerance: 10
date: 2026-01-12T15:30:00Z
version: "1.0"

content: |
  An empty document inbox with a single document floating gently,
  suggesting the space is ready to be filled.

template: |
  Create an empty state illustration in soft minimalism style.
  Style requirements:
  - Primary color: teal (#3D9A8B) with lighter tints
  - Background: pure white (#FFFFFF)
  # [remaining style-requirement bullets go here]
  Subject: {content}

final_prompt: |
  Create an empty state illustration in soft minimalism style.
  Style requirements:
  - Primary color: teal (#3D9A8B) with lighter tints
  - Background: pure white (#FFFFFF)
  # [remaining style-requirement bullets go here]
  Subject: An empty document inbox with a single document floating gently,
  suggesting the space is ready to be filled.

edit_history: []
---
```

### Using Templates with CLI

```bash
bash "$RUN_SH" generate_image.py \
    "Full prompt here..." output.png \
    --format png --transparent \
    --content "Brief description of unique content" \
    --template "The template text that was used"
```

## Output Format Options

| Format | Best For | Transparency | Notes |
|--------|----------|--------------|-------|
| `jpg` (default) | Photos, realistic images | No | Smallest files |
| `png` | Illustrations, graphics | Yes (required for `--transparent`) | Lossless, larger files |
| `webp` | Web assets | Yes | Best compression |

```bash
bash "$RUN_SH" generate_image.py "prompt" output.png --format png --transparent
```

## Direct API Patterns (fallback only)

Always prefer the CLI scripts above. If a task needs the google-genai SDK
directly (Google Search grounding, custom pipelines), read
`reference/api-patterns.md` in this skill directory for the API patterns:
basic generation, resolution/aspect config, editing, multi-turn chat,
search grounding, multi-reference composition, and how to skip `part.thought`
parts (both `gemini-nano-banana-2.1` and `gemini-3-pro-image` are thinking models).

## SVG Vector Generation (Gemini 3.1 Pro)

Gemini 3.1 Pro can generate SVG markup directly as code output. This uses the **text model** (`gemini-3.1-pro-preview`), not the image model.

### When to use SVG vs Raster (PNG/JPG)

| Use SVG | Use Raster (Nano Banana 2.1) |
|---------|-----------------------------|
| Icons and simple UI graphics | Branded illustrations (style guide) |
| Animated elements (loaders, transitions) | Photorealistic or painterly scenes |
| Diagrams and infographics | Complex gradients and soft shadows |
| Assets that must scale to any size | Empty states with rich visual detail |
| Interactive web elements | Feature illustrations, hero images |

**Rule of thumb:** If the asset is geometric/flat and needs to scale — use SVG. If it's illustrative/painterly and has a fixed display size — use raster.

### CLI Script

```bash
# Basic SVG generation
bash "$RUN_SH" generate_svg.py "A minimalist lock icon" output.svg

# With specific viewBox and style constraints
bash "$RUN_SH" generate_svg.py \
    "A vault door icon with light rays" output.svg \
    --viewbox "0 0 200 200" --style minimal

# Animated SVG
bash "$RUN_SH" generate_svg.py \
    "A three-dot loading animation with staggered bounce" loader.svg \
    --animated
```

### Direct API Pattern

```python
import os
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-3.1-pro-preview",
    contents="""Generate an SVG icon. Return ONLY the SVG code, no explanation.

Requirements:
- viewBox: 0 0 200 200
- Minimalist geometric style
- Primary color: #2563EB (Royal Blue) with tints #3B82F6, #DBEAFE
- Rounded corners, soft edges
- No text elements
- Clean paths, minimal nodes

Subject: A luminous vault door with light rays emanating from the keyhole.
""",
)

svg_code = response.text
# Strip markdown code fences if present
if svg_code.startswith("```"):
    svg_code = svg_code.split("\n", 1)[1].rsplit("```", 1)[0]

with open("output.svg", "w") as f:
    f.write(svg_code.strip())
```

### SVG Prompt Guidelines

**Always include in your prompt:**
1. `Return ONLY the SVG code, no explanation` — prevents markdown wrapping
2. `viewBox` dimensions — controls the coordinate system
3. Color values as hex codes — ensures brand consistency
4. Style constraints (minimal nodes, no transforms, clean paths)

**For animated SVGs, also specify:**
- Animation type (CSS `@keyframes` vs SMIL `<animate>`)
- Timing and easing (e.g., `ease-in-out`, `0.3s delay`)
- Which elements animate and how

**Quality tips:**
- Be very specific about shapes and composition — vague prompts produce vague SVGs
- Request `single path element where possible` for icons to get optimized output
- For complex scenes, describe layers explicitly: "background layer, middle layer, foreground"
- Specify `no raster elements` to prevent embedded `<image>` tags
- Complex SVGs may take 30s–5min with thinking mode — this is normal

### Limitations

- Output quality depends on scene complexity — simple icons are excellent, photorealistic scenes are poor
- Results vary between runs — regenerate if the first attempt isn't right
- Not suitable for richly-shaded branded illustration styles (soft shadows, diffused lighting, complex layered motifs)
- Cannot edit existing raster images — use Nano Banana 2.1 for that
- A `.prompt` sidecar file is created alongside the SVG, same as for raster images

## Prompting Best Practices

### Photorealistic Scenes
Include camera details: lens type, lighting, angle, mood.
> "A photorealistic close-up portrait, 85mm lens, soft golden hour light, shallow depth of field"

### Stylized Art
Specify style explicitly:
> "A kawaii-style sticker of a happy red panda, bold outlines, cel-shading, white background"

### Text in Images
Be explicit about font style and placement:
> "Create a logo with text 'Daily Grind' in clean sans-serif, black and white, coffee bean motif"

### Product Mockups
Describe lighting setup and surface:
> "Studio-lit product photo on polished concrete, three-point softbox setup, 45-degree angle"

### For Transparent Backgrounds
Always request pure white backgrounds in the prompt:
> "...Background: pure white (#FFFFFF)..."

Then use `--format png --transparent` to convert white to transparent.

## Notes

- All generated images include SynthID watermarks
- Every generation creates a `.prompt` sidecar file for reproducibility
- `--transparent` requires PNG format (will error with jpg/webp)
- Image-only mode (`responseModalities: ["IMAGE"]`) won't work with Google Search grounding
- For editing, describe changes conversationally—the model understands semantic masking
- Flash defaults to 1K for speed; Pro auto-defaults to 2K. Use `--size 4K` when print-scale quality is required

## Error Handling

If the script fails:

- Check that `GEMINI_API_KEY` is exported; the scripts read only the environment variable.
- Verify input image files exist and are readable
- Ensure the output directory is writable
- If no image is generated, try making the prompt more specific about wanting an image
- If using `--transparent` with non-PNG format, you'll get a validation error

## Best Practices

1. Be descriptive in prompts - include style, mood, colors, composition
2. For logos/graphics, use `--aspect 1:1`
3. For social media posts, use 9:16 for stories or 1:1 for posts
4. For wallpapers, use 16:9 or 21:9
5. For UI illustrations that need transparency, use `--format png --transparent --edge-tolerance 10`
6. Always request white backgrounds in prompts when you need transparency
7. Keep `.prompt` sidecar files alongside images for reproducibility
8. When a real person must stay recognizable, follow the Model decision rules and the Subject & Face Consistency recipes (pro model + preservation clauses)
