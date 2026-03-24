import os
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image
import pillow_heif  # register HEIC format with Pillow
pillow_heif.register_heif_opener()

INPUT_DIR = "input_images"
OUTPUT_DIR = "clean_images"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Add .heic/.HEIC to supported formats
SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".HEIC")
MAX_WORKERS = 4  # adjust based on CPU


def process_image(filename):
    input_path = os.path.join(INPUT_DIR, filename)

    try:
        with Image.open(input_path) as img:
            img = img.convert("RGBA")  # unify mode
            arr = np.array(img)

            # pixel-level subtle noise
            noise = np.random.randint(-1, 2, arr.shape, dtype=np.int16)
            arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)

            clean_img = Image.fromarray(arr)

            name, _ = os.path.splitext(filename)
            output_path = os.path.join(OUTPUT_DIR, name + ".jpg")

            # preserve transparency if RGBA
            if clean_img.mode == "RGBA":
                clean_img.save(output_path.replace(".jpg", ".png"), format="PNG")
            else:
                rgb_img = clean_img.convert("RGB")
                clean_img.save(
                    output_path,
                    format="JPEG",
                    quality=92,
                    subsampling=2,
                    optimize=True
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