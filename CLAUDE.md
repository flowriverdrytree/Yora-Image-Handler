# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
pipenv install       # Install dependencies
pipenv shell         # Activate environment
```

Python 3.14.1 is required (see `.python-version`).

## Commands

```bash
# Remove background from a single image
python rmbg.py <input_image> [-o <output_path>]

# Batch process images: add noise + inject copyright metadata
# Place inputs in wash_input/, outputs go to wash_output/
python wash.py
```

## Architecture

Two-stage pipeline for e-commerce product images:

1. **`rmbg.py`** — Background removal. Uses the `withoutbg` ML library. On macOS, HEIC files are first converted to PNG via the system `sips` command. Outputs transparent PNG.

2. **`wash.py`** — Batch metadata injection. Reads all images from `wash_input/`, applies ±1 pixel noise, embeds "Yora Lab" copyright (EXIF for JPEG, PNG text chunks for RGBA), and writes to `wash_output/`. Uses `ThreadPoolExecutor` with 4 workers. RGBA images are saved as PNG; everything else as JPEG at 92% quality.

**Typical flow:** raw photos → `rmbg.py` → `wash_input/` → `wash.py` → `wash_output/` (ready for listing).

Key libraries: `withoutbg`, `Pillow`, `piexif`, `pillow-heif`.
