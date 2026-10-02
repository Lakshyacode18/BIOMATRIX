"""Export model assumptions for qualified-clinician review."""
import csv

from knowledge import DISEASES, FEATURES, PRIORS


REVIEW_NOTES = {
    "__calibration__": (
        "Review probability calibration on an independent set of published, de-identified cases; "
        "the current model percentages may be overconfident."
    ),
    "__prior__": (
        "Review against the intended season, region, and clinic type; this is a synthetic starting assumption."
    ),
    "no_response_paracetamol": (
        "Review whether antipyretic response meaningfully separates these diseases; fever reduction may be temporary."
    ),
    "relative_bradycardia": (
        "Review the Typhoid value against clinical evidence; this sign may occur in only a minority of patients."
    ),
}


def generate_review_sheet(path="review_sheet.csv"):
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "disease",
            "feature",
            "kind",
            "model_value",
            "doctor_value",
            "source",
            "comment",
        ])

        writer.writerow([
            "All diseases",
            "Probability calibration",
            "model_review",
            "Uncalibrated",
            "",
            "",
            REVIEW_NOTES["__calibration__"],
        ])

        for disease in DISEASES:
            writer.writerow([
                disease,
                "Assumed disease prior",
                "prior",
            PRIORS[disease],
                "",
                "",
                REVIEW_NOTES["__prior__"],
            ])

            for feature, details in FEATURES.items():
                writer.writerow([
                    disease,
                    details["label"],
                    details["kind"],
                    details["p"][disease],
                    "",
                    "",
                    REVIEW_NOTES.get(feature, ""),
                ])


if __name__ == "__main__":
    generate_review_sheet()