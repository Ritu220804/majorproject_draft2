from pathlib import Path
from collections import Counter

DATASET = Path("dataset/merged")

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}

CLASS_NAMES = {
    0: "knife",
    1: "long_gun",
    2: "other_weapon",
    3: "pistol",
    4: "no_weapon"
}

total_images = 0
missing_label = 0
empty_label = 0
invalid_format = 0
invalid_class = 0
valid_images = 0

reason_examples = {
    "missing_label": [],
    "empty_label": [],
    "invalid_format": [],
    "invalid_class": []
}


for split in ["train", "valid", "test"]:

    image_dir = DATASET / split / "images"
    label_dir = DATASET / split / "labels"

    if not image_dir.exists():
        continue

    for image_file in image_dir.iterdir():

        if image_file.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        total_images += 1

        label_file = label_dir / f"{image_file.stem}.txt"

        # ------------------------------------------
        # Missing label
        # ------------------------------------------

        if not label_file.exists():

            missing_label += 1

            if len(reason_examples["missing_label"]) < 10:
                reason_examples["missing_label"].append(
                    f"{split}/{image_file.name}"
                )

            continue

        # ------------------------------------------
        # Read label
        # ------------------------------------------

        with open(
            label_file,
            "r",
            encoding="utf-8"
        ) as file:

            lines = [
                line.strip()
                for line in file.readlines()
                if line.strip()
            ]

        # ------------------------------------------
        # Empty label
        # ------------------------------------------

        if not lines:

            empty_label += 1

            if len(reason_examples["empty_label"]) < 10:
                reason_examples["empty_label"].append(
                    f"{split}/{image_file.name}"
                )

            continue

        valid_image = True

        for line in lines:

            parts = line.split()

            # YOLO format:
            # class x y width height

            if len(parts) != 5:

                invalid_format += 1
                valid_image = False

                if len(reason_examples["invalid_format"]) < 10:
                    reason_examples["invalid_format"].append(
                        f"{split}/{image_file.name} -> {line}"
                    )

                break

            try:
                class_id = int(parts[0])

            except ValueError:

                invalid_format += 1
                valid_image = False

                if len(reason_examples["invalid_format"]) < 10:
                    reason_examples["invalid_format"].append(
                        f"{split}/{image_file.name} -> {line}"
                    )

                break

            if class_id not in CLASS_NAMES:

                invalid_class += 1
                valid_image = False

                if len(reason_examples["invalid_class"]) < 10:
                    reason_examples["invalid_class"].append(
                        f"{split}/{image_file.name} -> class {class_id}"
                    )

                break

        if valid_image:
            valid_images += 1


# ======================================================
# REPORT
# ======================================================

print("\n==========================================")
print("DROPPED IMAGE ANALYSIS")
print("==========================================")

print("Total images in merged dataset:", total_images)
print("Valid images:", valid_images)

print("\nPossible reasons:")

print("Missing labels:", missing_label)
print("Empty labels:", empty_label)
print("Invalid format:", invalid_format)
print("Invalid class:", invalid_class)

print("\nTotal potentially excluded:")

print(
    missing_label
    + empty_label
    + invalid_format
    + invalid_class
)

print("\n------------------------------------------")
print("EXAMPLES")
print("------------------------------------------")

for reason, examples in reason_examples.items():

    print("\n", reason)

    for example in examples:
        print("  ", example)

print("\n==========================================")