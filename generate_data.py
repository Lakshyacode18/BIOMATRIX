"""Generate a synthetic patient dataset from the knowledge base."""
import csv
import random

from knowledge import DISEASES, FEATURES, PRIORS


def generate(n=6000, seed=42):
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        disease = rng.choices(DISEASES, weights=[PRIORS[name] for name in DISEASES])[0]
        row = {"disease": disease}
        for name, f in FEATURES.items():
            row[name] = 1 if rng.random() < f["p"][disease] else 0
        rows.append(row)
    return rows


def save_csv(rows, path="synthetic_patients.csv"):
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["disease"] + list(FEATURES))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    data = generate()
    save_csv(data)
    print(f"Saved {len(data)} synthetic patients to synthetic_patients.csv")
