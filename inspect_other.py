from pathlib import Path
import cv2
import matplotlib.pyplot as plt
import random

DATASET = Path("dataset/merged")

IMAGE_DIR = DATASET / "train" / "images"
LABEL_DIR = DATASET / "train" / "labels"

TARGET_CLASS = 2
TARGET_NAME = "other"

samples = []

# Find images containing class 2
for label_file in LABEL_DIR.glob("*.txt"):

    with open(label_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    found = False

    for line in lines:

        parts = line.strip().split()

        if not parts:
            continue

        class_id = int(parts[0])

        if class_id == TARGET_CLASS:
            found = True
            break

    if found:

        image_file = None

        for extension in [".jpg", ".jpeg", ".png", ".webp"]:

            possible = IMAGE_DIR / (label_file.stem + extension)

            if possible.exists():
                image_file = possible
                break

        if image_file:
            samples.append(image_file)


print("Total images containing 'other':", len(samples))

# Take maximum 20 random examples
random.seed(42)

if len(samples) > 20:
    samples = random.sample(samples, 20)


# Create output folder
output_dir = Path("results")
output_dir.mkdir(exist_ok=True)

# Create contact sheet
fig, axes = plt.subplots(4, 5, figsize=(15, 12))

for ax in axes.flatten():
    ax.axis("off")

for ax, image_path in zip(axes.flatten(), samples):

    image = cv2.imread(str(image_path))

    if image is None:
        continue

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    ax.imshow(image)
    ax.set_title(image_path.name, fontsize=7)
    ax.axis("off")


plt.suptitle(
    "Sample Images Containing 'OTHER'",
    fontsize=16
)

plt.tight_layout()

output_path = output_dir / "other_samples.jpg"

plt.savefig(output_path, dpi=150)

plt.close()

print("\nSaved sample images to:")
print(output_path)