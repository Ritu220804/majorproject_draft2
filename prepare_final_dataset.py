from pathlib import Path
import shutil
import random
from collections import Counter

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

SOURCE_DIR = BASE_DIR / "dataset" / "merged"
FINAL_DIR = BASE_DIR / "dataset" / "final"


# ============================================================
# SETTINGS
# ============================================================

RANDOM_SEED = 42

TRAIN_RATIO = 0.70
VALID_RATIO = 0.15
TEST_RATIO = 0.15

random.seed(RANDOM_SEED)


# ============================================================
# FINAL CLASSES
# ============================================================

CLASS_NAMES = {
    0: "knife",
    1: "long_gun",
    2: "other_weapon",
    3: "pistol",
    4: "no_weapon"
}


# ============================================================
# IMAGE EXTENSIONS
# ============================================================

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}


# ============================================================
# CREATE FINAL FOLDERS
# ============================================================

for split in ["train", "valid", "test"]:

    (FINAL_DIR / split / "images").mkdir(
        parents=True,
        exist_ok=True
    )

    (FINAL_DIR / split / "labels").mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# COLLECT ALL IMAGE-LABEL PAIRS
# ============================================================

all_samples = []

print("\nCollecting images and labels...\n")

for split in ["train", "valid", "test"]:

    image_dir = SOURCE_DIR / split / "images"
    label_dir = SOURCE_DIR / split / "labels"

    if not image_dir.exists():
        print(f"Skipping {split}: images folder not found")
        continue

    for image_file in image_dir.iterdir():

        if image_file.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        label_file = label_dir / f"{image_file.stem}.txt"

        if not label_file.exists():
            print("Missing label:", image_file.name)
            continue

        # ----------------------------------------------------
        # Read labels
        # ----------------------------------------------------

        valid_labels = []

        with open(
            label_file,
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                parts = line.strip().split()

                if not parts:
                    continue

                try:
                    class_id = int(parts[0])
                except ValueError:
                    continue

                if class_id not in CLASS_NAMES:
                    print(
                        "Invalid class ID:",
                        class_id,
                        "in",
                        label_file
                    )
                    continue

                # YOLO format should contain:
                # class x_center y_center width height

                if len(parts) != 5:
                    print(
                        "Invalid label format:",
                        label_file
                    )
                    continue

                valid_labels.append(line.strip())

        if not valid_labels:
            print(
                "Empty/invalid label:",
                label_file
            )
            continue

        # ----------------------------------------------------
        # Use first class as primary class
        # for stratified splitting
        # ----------------------------------------------------

        primary_class = int(
            valid_labels[0].split()[0]
        )

        all_samples.append(
            {
                "image": image_file,
                "label": label_file,
                "primary_class": primary_class
            }
        )


# ============================================================
# BASIC INFORMATION
# ============================================================

print("Total valid image-label pairs:", len(all_samples))

print("\nPrimary class distribution:")

primary_counts = Counter(
    sample["primary_class"]
    for sample in all_samples
)

for class_id in CLASS_NAMES:

    print(
        f"{class_id} -> "
        f"{CLASS_NAMES[class_id]}: "
        f"{primary_counts[class_id]}"
    )


# ============================================================
# GROUP BY PRIMARY CLASS
# ============================================================

class_groups = {}

for class_id in CLASS_NAMES:
    class_groups[class_id] = []


for sample in all_samples:

    class_groups[
        sample["primary_class"]
    ].append(sample)


# ============================================================
# CREATE STRATIFIED SPLIT
# ============================================================

final_splits = {
    "train": [],
    "valid": [],
    "test": []
}


for class_id, samples in class_groups.items():

    random.shuffle(samples)

    total = len(samples)

    train_count = int(
        total * TRAIN_RATIO
    )

    valid_count = int(
        total * VALID_RATIO
    )

    train_samples = samples[
        :train_count
    ]

    valid_samples = samples[
        train_count:
        train_count + valid_count
    ]

    test_samples = samples[
        train_count + valid_count:
    ]

    final_splits["train"].extend(
        train_samples
    )

    final_splits["valid"].extend(
        valid_samples
    )

    final_splits["test"].extend(
        test_samples
    )


# ============================================================
# SHUFFLE FINAL SPLITS
# ============================================================

for split in final_splits:

    random.shuffle(
        final_splits[split]
    )


# ============================================================
# COPY FILES
# ============================================================

print("\nCopying files...\n")

total_copied = 0

for split, samples in final_splits.items():

    print(
        f"{split}: {len(samples)} images"
    )

    for sample in samples:

        image_file = sample["image"]
        label_file = sample["label"]

        destination_image = (
            FINAL_DIR
            / split
            / "images"
            / image_file.name
        )

        destination_label = (
            FINAL_DIR
            / split
            / "labels"
            / label_file.name
        )

        shutil.copy2(
            image_file,
            destination_image
        )

        shutil.copy2(
            label_file,
            destination_label
        )

        total_copied += 1


# ============================================================
# CREATE DATA.YAML
# ============================================================

yaml_content = f"""path: {FINAL_DIR.resolve()}
train: train/images
val: valid/images
test: test/images

nc: 5

names:
  - knife
  - long_gun
  - other_weapon
  - pistol
  - no_weapon
"""


yaml_path = FINAL_DIR / "data.yaml"

with open(
    yaml_path,
    "w",
    encoding="utf-8"
) as file:

    file.write(yaml_content)


# ============================================================
# FINAL REPORT
# ============================================================

print("\n")
print("==========================================")
print("FINAL DATASET CREATED")
print("==========================================")

print(
    "Total images:",
    total_copied
)

print(
    "\nTrain:",
    len(final_splits["train"])
)

print(
    "Validation:",
    len(final_splits["valid"])
)

print(
    "Test:",
    len(final_splits["test"])
)

print(
    "\nFinal dataset:"
)

print(
    FINAL_DIR
)

print(
    "\nData YAML:"
)

print(
    yaml_path
)

print("\nClasses:")

for class_id, name in CLASS_NAMES.items():

    print(
        f"{class_id} -> {name}"
    )

print("\n==========================================")
print("DONE")
print("==========================================")