# Gemini Image Generation Plugin

Image generation and editing using Google's Gemini API (Nano Banana 2.1, plus Nano Banana Pro for identity-preserving edits).

## Installation

```bash
/plugin marketplace add ebner/agentics
/plugin install gemini-imagegen@agentics
```

## Prerequisites

- `GEMINI_API_KEY` environment variable must be set
- Python 3.10+ (for the generation scripts)
- Dependencies are auto-installed via virtual environment on first use

## Features

- Text-to-image generation (1K, 2K, 4K resolution)
- Image editing with natural language instructions
- Identity/face-preserving style transfer and character consistency (Nano Banana Pro, auto-selected; defaults to 2K)
- SVG vector generation
- Multi-image composition
- Multi-turn interactive refinement
- Automatic transparency conversion (white background to transparent)
- Batch regeneration from `.prompt` sidecar files
- Multiple aspect ratios (1:1, 16:9, 9:16, etc.)
- Output formats: JPG, PNG, WebP

## Permissions

The skill invokes generation scripts via `bash .../run.sh`. To avoid repeated
permission prompts, add the following to `~/.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(find:*gemini-imagegen*)",
      "Bash(bash:*gemini-imagegen/scripts/run.sh*)"
    ]
  }
}
```

The first pattern permits the one-time script discovery (`find`), the second
permits all image generation/editing calls routed through `run.sh`.

## Usage

The skill triggers automatically when you ask Claude to generate or edit images.
You can also invoke it directly:

```
/gemini-imagegen Generate a teal lock icon
```

Or naturally: "generate an image of...", "create an illustration...", "edit this image..."

## License

MIT
