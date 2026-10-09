from pathlib import Path
import shutil
import yaml

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

RAW_DIR = BASE_DIR / "dataset" / "raw"
OUTPUT_DIR = BASE_DIR / "dataset" / "merged"

WEAPON_DIR = RAW_DIR / "WeaponDataset-v11"
NOGUN_DIR = RAW_DIR / "NoGUN-v5"


# =========================================================
# FINAL CLASSES
# =========================================================

# Final class IDs
FINAL_CLASSES = {
    0: "knife",
    1: "long_gun",
    2: "other",
    3: "pistol",
    4: "no_weapon"
}


# =========================================================
# DATASET INFORMATION
# =========================================================

DATASETS = [
    {
        "name": "weapon",
        "path": WEAPON_DIR,

        # Original classes:
        # 0 knife
        # 1 long_gun
        # 2 other
        # 3 pistol

        "class_mapping": {
            0: 0,
            1: 1,
            2: 2,
            3: 3
        }
    },

    {
        "name": "nogun",
        "path": NOGUN_DIR,

        # Original:
        # 0 nogun

        # Final:
        # 4 no_weapon

        "class_mapping": {
            0: 4
        }
    }
]


# =========================================================
# IMAGE EXTENSIONS
# =========================================================

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}


# =========================================================
# COUNTERS
# =========================================================

total_images = 0
total_labels = 0
missing_labels = 0


# =========================================================
# CREATE OUTPUT FOLDERS
# =========================================================

for split in ["train", "valid", "test"]:

    (OUTPUT_DIR / split / "images").mkdir(
        parents=True,
        exist_ok=True
    )

    (OUTPUT_DIR / split / "labels").mkdir(
        parents=True,
        exist_ok=True
    )


# =========================================================
# PROCESS EACH DATASET
# =========================================================

for dataset in DATASETS:

    dataset_name = dataset["name"]
    dataset_path = dataset["path"]
    class_mapping = dataset["class_mapping"]

    print("\n===================================")
    print("Processing:", dataset_name)
    print("===================================")

    for split in ["train", "valid", "test"]:

        source_images = dataset_path / split / "images"
        source_labels = dataset_path / split / "labels"

        if not source_images.exists():

            print(
                f"Skipping {dataset_name}/{split} "
                f"(images folder not found)"
            )

            continue

        print(f"\nProcessing {split}...")

        image_files = [
            file for file in source_images.iterdir()
            if file.suffix.lower() in IMAGE_EXTENSIONS
        ]

        print("Images found:", len(image_files))

        for image_file in image_files:

            # -------------------------------------------------
            # Create unique filename
            # -------------------------------------------------

            new_stem = f"{dataset_name}_{image_file.stem}"

            new_image_name = (
                new_stem + image_file.suffix.lower()
            )

            destination_image = (
                OUTPUT_DIR
                / split
                / "images"
                / new_image_name
            )

            # -------------------------------------------------
            # Copy image
            # -------------------------------------------------

            shutil.copy2(
                image_file,
                destination_image
            )

            total_images += 1

            # -------------------------------------------------
            # Find corresponding label
            # -------------------------------------------------

            label_file = (
                source_labels
                / f"{image_file.stem}.txt"
            )

            destination_label = (
                OUTPUT_DIR
                / split
                / "labels"
                / f"{new_stem}.txt"
            )

            # -------------------------------------------------
            # Check label
            # -------------------------------------------------

            if not label_file.exists():

                print(
                    "WARNING - Missing label:",
                    image_file.name
                )

                missing_labels += 1

                # Create empty label file
                destination_label.touch()

                continue

            # -------------------------------------------------
            # Read original labels
            # -------------------------------------------------

            with open(
                label_file,
                "r",
                encoding="utf-8"
            ) as file:

                lines = file.readlines()

            new_lines = []

            for line in lines:

                line = line.strip()

                if not line:
                    continue

                parts = line.split()

                old_class = int(parts[0])

                # Check whether class exists
                if old_class not in class_mapping:

                    print(
                        "WARNING - Unknown class:",
                        old_class,
                        "in",
                        label_file
                    )

                    continue

                new_class = class_mapping[old_class]

                # Replace class ID
                parts[0] = str(new_class)

                new_lines.append(
                    " ".join(parts)
                )

            # -------------------------------------------------
            # Save mapped labels
            # -------------------------------------------------

            with open(
                destination_label,
                "w",
                encoding="utf-8"
            ) as file:

                for line in new_lines:

                    file.write(line + "\n")

            total_labels += 1


# =========================================================
# CREATE DATA.YAML
# =========================================================

data_yaml = {
    "path": str(OUTPUT_DIR.resolve()),

    "train": "train/images",
    "val": "valid/images",
    "test": "test/images",

    "nc": len(FINAL_CLASSES),

    "names": [
        FINAL_CLASSES[i]
        for i in range(len(FINAL_CLASSES))
    ]
}


yaml_path = OUTPUT_DIR / "data.yaml"

with open(
    yaml_path,
    "w",
    encoding="utf-8"
) as file:

    yaml.dump(
        data_yaml,
        file,
        sort_keys=False
    )


# =========================================================
# FINAL REPORT
# =========================================================

print("\n\n===================================")
print("MERGING COMPLETE")
print("===================================")

print("Total images:", total_images)
print("Total label files:", total_labels)
print("Missing labels:", missing_labels)

print("\nFinal classes:")

for class_id, class_name in FINAL_CLASSES.items():

    print(
        f"{class_id} -> {class_name}"
    )

print("\nMerged dataset:")
print(OUTPUT_DIR)

print("\nCreated:")
print(yaml_path)

print("\n===================================")
print("IMPORTANT")
print("===================================")

print(
    "The 'other' class has NOT been changed."
)

print(
    "We will inspect it before training."
)