import argparse
import subprocess
import tempfile
from pathlib import Path

from withoutbg import WithoutBG


HEIC_EXTENSIONS = {".heic", ".heif"}


def prepare_input_image(input_path: str) -> tuple[str, tempfile.TemporaryDirectory | None]:
    path = Path(input_path)

    if path.suffix.lower() not in HEIC_EXTENSIONS:
        return input_path, None

    temp_dir = tempfile.TemporaryDirectory()
    converted_path = Path(temp_dir.name) / f"{path.stem}.png"

    try:
        subprocess.run(
            ["sips", "-s", "format", "png", str(path), "--out", str(converted_path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        temp_dir.cleanup()
        raise RuntimeError("HEIC input requires the macOS 'sips' command, but it was not found.") from exc
    except subprocess.CalledProcessError as exc:
        temp_dir.cleanup()
        stderr = exc.stderr.strip() or exc.stdout.strip() or "Unknown error"
        raise RuntimeError(f"Failed to convert HEIC image '{input_path}' to PNG: {stderr}") from exc

    return str(converted_path), temp_dir

def main():
    parser = argparse.ArgumentParser(description="Remove background from an image")
    parser.add_argument("input", help="Path to the input image file")
    parser.add_argument("-o", "--output", default="result.png", help="Path to the output image file (default: result.png)")
    
    args = parser.parse_args()
    
    model = WithoutBG.opensource()
    prepared_input, temp_dir = prepare_input_image(args.input)

    try:
        model.remove_background(prepared_input).save(args.output)
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()

    print(f"Background removed successfully. Output saved to: {args.output}")

if __name__ == "__main__":
    main()
