from pathlib import Path
from collections import Counter

DATASET = Path("dataset/merged")

CLASS_NAMES = {
    0: "knife",
    1: "long_gun",
    2: "other",
    3: "pistol",
    4: "no_weapon"
}

counter = Counter()

for split in ["train", "valid", "test"]:

    label_dir = DATASET / split / "labels"

    if not label_dir.exists():
        continue

    print("\n==============================")
    print("SPLIT:", split)
    print("==============================")

    image_count = 0
    label_count = 0

    for label_file in label_dir.glob("*.txt"):

        label_count += 1

        with open(label_file, "r", encoding="utf-8") as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                parts = line.split()

                class_id = int(parts[0])

                counter[class_id] += 1

                image_count += 1

    print("Label files:", label_count)
    print("Objects:", image_count)


print("\n\n================================")
print("TOTAL OBJECT DISTRIBUTION")
print("================================")

for class_id in sorted(CLASS_NAMES):

    print(
        class_id,
        "->",
        CLASS_NAMES[class_id],
        ":",
        counter[class_id]
    )