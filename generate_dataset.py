import pandas as pd
import random

data = []

for i in range(3000):
    patient_id = f"P{i+1}"

    age = random.randint(18, 75)
    gender = random.choice(["Male", "Female"])

    bone_loss = round(random.uniform(5, 80), 2)

    if bone_loss < 30:
        severity = "Mild"
    elif bone_loss < 50:
        severity = "Moderate"
    else:
        severity = "Severe"

    pocket_depth = round(random.uniform(2, 8), 2)
    plaque_index = round(random.uniform(0.5, 3.5), 2)

    data.append([
        patient_id,
        age,
        gender,
        bone_loss,
        severity,
        pocket_depth,
        plaque_index
    ])

df = pd.DataFrame(data, columns=[
    "patient_id",
    "age",
    "gender",
    "bone_loss_percent",
    "severity",
    "pocket_depth",
    "plaque_index"
])

df.to_csv("bone_loss_dataset.csv", index=False)

print("✅ Dataset generated: bone_loss_dataset.csv")