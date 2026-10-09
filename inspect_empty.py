from pathlib import Path
import cv2
import matplotlib.pyplot as plt
import random

DATASET = Path("dataset/merged")

IMAGE_DIR = DATASET / "train" / "images"
LABEL_DIR = DATASET / "train" / "labels"

empty_images = []

for label_file in LABEL_DIR.glob("*.txt"):

    # Read label file
    with open(label_file, "r", encoding="utf-8") as file:
        content = file.read().strip()

    # Empty label
    if content == "":

        for extension in [".jpg", ".jpeg", ".png", ".webp"]:

            image_file = IMAGE_DIR / (
                label_file.stem + extension
            )

            if image_file.exists():

                empty_images.append(image_file)
                break


print(
    "Total empty-label images:",
    len(empty_images)
)

random.seed(42)

if len(empty_images) > 20:
    empty_images = random.sample(
        empty_images,
        20
    )


output_dir = Path("results")
output_dir.mkdir(exist_ok=True)

fig, axes = plt.subplots(
    4,
    5,
    figsize=(15, 12)
)

for ax in axes.flatten():
    ax.axis("off")


for ax, image_path in zip(
    axes.flatten(),
    empty_images
):

    image = cv2.imread(
        str(image_path)
    )

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
    "Sample Images With Empty Labels",
    fontsize=16
)

plt.tight_layout()

output_path = (
    output_dir /
    "empty_label_samples.jpg"
)

plt.savefig(
    output_path,
    dpi=150
)

plt.close()

print(
    "\nSaved to:"
)

print(output_path)