import os
import shutil
import random
import cv2
import numpy as np

SOURCE_FOLDER = "uploads"
DATASET_FOLDER = "dataset"

TRAIN_SPLIT = 0.8

classes = ["mild", "moderate", "severe"]

# -------- CREATE FOLDERS --------
for split in ["train", "val"]:
    for cls in classes:
        os.makedirs(os.path.join(DATASET_FOLDER, split, cls), exist_ok=True)

# -------- GET IMAGES (RECURSIVE) --------
images = []

for root, dirs, files in os.walk(SOURCE_FOLDER):
    for file in files:
        full_path = os.path.join(root, file)

        img = cv2.imread(full_path)
        if img is not None:
            images.append(full_path)

print("Total images found:", len(images))

random.shuffle(images)

# -------- LABEL FUNCTION --------
def assign_label(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if img is None:
        return "mild"

    brightness = np.mean(img)

    if brightness > 180:
        return "mild"
    elif brightness > 120:
        return "moderate"
    else:
        return "severe"

# -------- SPLIT --------
split_index = int(len(images) * TRAIN_SPLIT)

train_images = images[:split_index]
val_images = images[split_index:]

# -------- PROCESS --------
def process(image_list, split):
    for img_path in image_list:
        try:
            label = assign_label(img_path)

            img_name = os.path.basename(img_path)

            dst_folder = os.path.join(DATASET_FOLDER, split, label)

            # 🔥 FORCE create folder before copy
            os.makedirs(dst_folder, exist_ok=True)

            dst = os.path.join(dst_folder, img_name)

            shutil.copy(img_path, dst)

        except Exception as e:
            print("Error:", e)

process(train_images, "train")
process(val_images, "val")

print("✅ Done: Auto labeling + split completed")