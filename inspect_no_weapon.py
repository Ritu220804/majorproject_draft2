from pathlib import Path
import cv2
import matplotlib.pyplot as plt
import random

DATASET = Path("dataset/merged")

IMAGE_DIR = DATASET / "train" / "images"
LABEL_DIR = DATASET / "train" / "labels"

TARGET_CLASS = 4

samples = []

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

        for extension in [".jpg", ".jpeg", ".png", ".webp"]:

            image_file = IMAGE_DIR / (
                label_file.stem + extension
            )

            if image_file.exists():
                samples.append(image_file)
                break


print(
    "Total images containing no_weapon:",
    len(samples)
)

random.seed(42)

if len(samples) > 20:
    samples = random.sample(samples, 20)


output_dir = Path("results")
output_dir.mkdir(exist_ok=True)

fig, axes = plt.subplots(
    4,
    5,
    figsize=(15, 12)
)

for ax in axes.flatten():
    ax.axis("off")


for ax, image_path in zip(axes.flatten(), samples):

    image = cv2.imread(str(image_path))

    if image is None:
        continue

    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    ax.imshow(image)
    ax.set_title(
        image_path.name,
        fontsize=7
    )
    ax.axis("off")


plt.suptitle(
    "Sample Images Containing 'NO WEAPON'",
    fontsize=16
)

plt.tight_layout()

output_path = (
    output_dir /
    "no_weapon_samples.jpg"
)

plt.savefig(
    output_path,
    dpi=150
)

plt.close()

print("\nSaved to:")
print(output_path)