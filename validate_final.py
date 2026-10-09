from pathlib import Path
from collections import Counter

DATASET = Path("dataset/final")

CLASS_NAMES = {
    0: "knife",
    1: "long_gun",
    2: "other_weapon",
    3: "pistol",
    4: "no_weapon"
}

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}

total_images = 0
total_labels = 0
missing_labels = 0
invalid_labels = 0

class_counts = Counter()
split_counts = Counter()


for split in ["train", "valid", "test"]:

    image_dir = DATASET / split / "images"
    label_dir = DATASET / split / "labels"

    print("\n==============================")
    print("CHECKING:", split)
    print("==============================")

    images = [
        x for x in image_dir.iterdir()
        if x.suffix.lower() in IMAGE_EXTENSIONS
    ]

    split_counts[split] = len(images)

    print("Images:", len(images))

    for image in images:

        total_images += 1

        label = label_dir / f"{image.stem}.txt"

        if not label.exists():

            missing_labels += 1

            continue

        total_labels += 1

        with open(
            label,
            "r",
            encoding="utf-8"
        ) as file:

            lines = file.readlines()

        for line in lines:

            parts = line.strip().split()

            if not parts:
                continue

            if len(parts) != 5:

                invalid_labels += 1

                continue

            try:
                class_id = int(parts[0])

                x = float(parts[1])
                y = float(parts[2])
                w = float(parts[3])
                h = float(parts[4])

            except ValueError:

                invalid_labels += 1

                continue

            # Check class ID

            if class_id not in CLASS_NAMES:

                invalid_labels += 1

                continue

            # Check bounding box values

            if not (
                0 <= x <= 1 and
                0 <= y <= 1 and
                0 < w <= 1 and
                0 < h <= 1
            ):

                invalid_labels += 1

                continue

            class_counts[class_id] += 1


print("\n")
print("======================================")
print("FINAL DATASET VALIDATION")
print("======================================")

print("\nImages:", total_images)
print("Label files:", total_labels)
print("Missing labels:", missing_labels)
print("Invalid labels:", invalid_labels)

print("\nSplit distribution:")

for split in ["train", "valid", "test"]:

    print(
        split,
        "->",
        split_counts[split]
    )

print("\nObject distribution:")

for class_id in CLASS_NAMES:

    print(
        class_id,
        "->",
        CLASS_NAMES[class_id],
        ":",
        class_counts[class_id]
    )

print("\n======================================")

if missing_labels == 0 and invalid_labels == 0:

    print("DATASET STATUS: READY FOR TRAINING")

else:

    print("DATASET STATUS: NEEDS FIXING")

print("======================================")