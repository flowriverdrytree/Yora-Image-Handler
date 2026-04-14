import os
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image, PngImagePlugin
import pillow_heif
import piexif

pillow_heif.register_heif_opener()

INPUT_DIR = "wash_input"
OUTPUT_DIR = "wash_output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".HEIC")
MAX_WORKERS = 4

COPYRIGHT = "Yora Lab"


def build_exif():
    """Build EXIF bytes with copyright tag for JPEG."""
    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}
    exif_dict["0th"][piexif.ImageIFD.Copyright] = COPYRIGHT.encode("utf-8")
    return piexif.dump(exif_dict)


def process_image(filename):
    input_path = os.path.join(INPUT_DIR, filename)

    try:
        with Image.open(input_path) as img:
            img = img.convert("RGBA")
            arr = np.array(img)

            noise = np.random.randint(-1, 2, arr.shape, dtype=np.int16)
            arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)

            clean_img = Image.fromarray(arr)
            name, _ = os.path.splitext(filename)

            if clean_img.mode == "RGBA":
                output_path = os.path.join(OUTPUT_DIR, name + ".png")
                png_info = PngImagePlugin.PngInfo()
                png_info.add_text("Copyright", COPYRIGHT)
                clean_img.save(output_path, format="PNG", pnginfo=png_info)

            else:
                output_path = os.path.join(OUTPUT_DIR, name + ".jpg")
                rgb_img = clean_img.convert("RGB")
                exif_bytes = build_exif()
                rgb_img.save(
                    output_path,
                    format="JPEG",
                    quality=92,
                    subsampling=2,
                    optimize=True,
                    exif=exif_bytes
                )

        print(f"✅ {filename}")

    except Exception as e:
        print(f"❌ {filename} | {e}")


def main():
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(SUPPORTED_FORMATS)]
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(process_image, files)


if __name__ == "__main__":
    main()