"""Turn a doctor-reviewed workbook into an auditable Bio Matrix override file.

Usage:
    python apply_review.py review_sheet.xlsx --reviewer "Dr A. Sharma, GP"
    python apply_review.py review_sheet.xlsx --dry-run

The workbook must have Review and Priors sheets. See generate_review_sheet.py
for the matching template. Values are applied only when Doctor value is filled
and Decision is Change or blank; Agree and Unsure rows are never applied.
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

from openpyxl import load_workbook

from knowledge import DISEASES, FEATURES


OVERRIDE_FUNCTIONS = '''
import warnings


def _get(container, diseases, disease):
    return container[disease] if isinstance(container, dict) else container[diseases.index(disease)]


def _set(container, diseases, disease, value):
    if isinstance(container, dict):
        container[disease] = value
    else:
        container[diseases.index(disease)] = value


def apply_overrides(features, priors, diseases):
    for disease, override in OVERRIDES["priors"].items():
        if disease not in diseases:
            warnings.warn(f"reviewed_values: unknown disease {disease!r} in priors, skipped")
            continue
        if abs(_get(priors, diseases, disease) - override["old"]) > 1e-9:
            warnings.warn(f"reviewed_values: prior for {disease} changed since review")
        _set(priors, diseases, disease, override["value"])

    for key, per_disease in OVERRIDES["features"].items():
        if key not in features:
            warnings.warn(f"reviewed_values: unknown feature {key!r}, skipped")
            continue
        for disease, override in per_disease.items():
            if disease not in diseases:
                warnings.warn(f"reviewed_values: unknown disease {disease!r} for {key}, skipped")
                continue
            values = features[key]["p"]
            if abs(_get(values, diseases, disease) - override["old"]) > 1e-9:
                warnings.warn(f"reviewed_values: {key}/{disease} changed since review")
            _set(values, diseases, disease, override["value"])
'''


def parse_value(raw):
    """Return (0..1 value, error); percent strings are accepted, bare 60 is not."""
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return None, None
    try:
        if isinstance(raw, str):
            text = raw.strip()
            value = float(text[:-1]) / 100 if text.endswith("%") else float(text)
        else:
            value = float(raw)
    except (TypeError, ValueError):
        return None, f"not a number: {raw!r}"
    if not 0 <= value <= 1:
        return None, f"{raw!r} is outside 0-100% (enter a decimal or e.g. 60%)"
    return round(value, 4), None


def column_map(worksheet, required):
    headers = {
        str(cell.value).strip(): index
        for index, cell in enumerate(worksheet[1])
        if cell.value is not None
    }
    missing = [header for header in required if header not in headers]
    if missing:
        raise ValueError(f"Sheet {worksheet.title!r} is missing columns: {missing}")
    return headers


def read_review(workbook, warnings_out):
    if "Review" not in workbook.sheetnames:
        raise ValueError("Workbook is missing the 'Review' sheet")
    worksheet = workbook["Review"]
    headers = column_map(worksheet, [
        "Disease", "Key", "Kind", "Our estimate", "Doctor value", "Decision", "Source", "Comment"
    ])
    changes = {}
    for row in worksheet.iter_rows(min_row=2, values_only=True):
        disease = row[headers["Disease"]]
        key = row[headers["Key"]]
        kind = row[headers["Kind"]]
        if not disease or not key or kind in {"prior", "model_review"}:
            continue

        raw = row[headers["Doctor value"]]
        decision = str(row[headers["Decision"]] or "").strip().casefold()
        tag = f"{disease} / {key}"
        value, error = parse_value(raw)
        if error:
            warnings_out.append(f"{tag}: {error}. Skipped.")
            continue
        if value is None:
            if decision == "change":
                warnings_out.append(f"{tag}: Decision is Change but Doctor value is empty. Skipped.")
            continue
        if decision in {"agree", "unsure"}:
            warnings_out.append(f"{tag}: value supplied but Decision is {decision.title()}. Skipped.")
            continue
        if decision not in {"", "change"}:
            warnings_out.append(f"{tag}: unknown Decision {decision!r}. Skipped.")
            continue
        if key not in FEATURES:
            warnings_out.append(f"{tag}: unknown feature key. Skipped.")
            continue
        if disease not in DISEASES:
            warnings_out.append(f"{tag}: unknown disease. Skipped.")
            continue
        old_raw = row[headers["Our estimate"]]
        old, old_error = parse_value(old_raw)
        if old_error or old is None:
            warnings_out.append(f"{tag}: invalid Our estimate {old_raw!r}. Skipped.")
            continue
        if abs(value - old) < 1e-9:
            continue
        changes.setdefault(key, {})[disease] = {
            "value": value,
            "old": old,
            "source": row[headers["Source"]] or "",
            "comment": row[headers["Comment"]] or "",
        }
    return changes


def read_priors(workbook, warnings_out):
    if "Priors" not in workbook.sheetnames:
        return {}, ""
    worksheet = workbook["Priors"]
    setting = ""
    for row in worksheet.iter_rows(min_row=1, max_row=min(4, worksheet.max_row), values_only=True):
        if row[0] and str(row[0]).startswith("Clinic type"):
            setting = next((str(value) for value in row[1:] if value), "")

    header_row = None
    headers = None
    for row_index, row in enumerate(worksheet.iter_rows(values_only=True), start=1):
        if row and row[0] == "Disease":
            header_row = row_index
            headers = {str(value).strip(): index for index, value in enumerate(row) if value is not None}
            break
    if header_row is None:
        warnings_out.append("Priors sheet: header row not found; prior changes skipped.")
        return {}, setting

    required = ["Disease", "Our prior", "Doctor prior", "Source", "Comment"]
    missing = [name for name in required if name not in headers]
    if missing:
        raise ValueError(f"Priors sheet is missing columns: {missing}")

    changes = {}
    for row in worksheet.iter_rows(min_row=header_row + 1, values_only=True):
        disease = row[headers["Disease"]]
        if not disease or disease == "Total":
            continue
        raw = row[headers["Doctor prior"]]
        value, error = parse_value(raw)
        if error:
            warnings_out.append(f"Prior for {disease}: {error}. Skipped.")
            continue
        if value is None:
            continue
        if disease not in DISEASES:
            warnings_out.append(f"Prior for {disease}: unknown disease. Skipped.")
            continue
        old_raw = row[headers["Our prior"]]
        old, old_error = parse_value(old_raw)
        if old_error or old is None:
            warnings_out.append(f"Prior for {disease}: invalid Our prior {old_raw!r}. Skipped.")
            continue
        if abs(value - old) < 1e-9:
            continue
        changes[disease] = {
            "value": value,
            "old": old,
            "source": row[headers["Source"]] or "",
            "comment": row[headers["Comment"]] or "",
        }
    return changes, setting


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("xlsx", help="returned review workbook (.xlsx)")
    parser.add_argument("--reviewer", default="(not stated)")
    parser.add_argument("--out", default="reviewed_values.py")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    workbook = load_workbook(args.xlsx, data_only=True, read_only=True)
    warnings_out = []
    features = read_review(workbook, warnings_out)
    priors, setting = read_priors(workbook, warnings_out)
    workbook.close()
    feature_count = sum(len(values) for values in features.values())

    print("=" * 66)
    print(f"Changed findings: {feature_count}    Changed priors: {len(priors)}")
    print("=" * 66)
    changes = [
        (abs(change["value"] - change["old"]), key, disease, change)
        for key, per_disease in features.items()
        for disease, change in per_disease.items()
    ]
    for _, key, disease, change in sorted(changes, key=lambda item: -item[0]):
        print(
            f"  {disease:16s} {key:28s} {change['old'] * 100:3.0f}% -> "
            f"{change['value'] * 100:3.0f}%   {change['source']}"
        )
    for disease, change in priors.items():
        print(
            f"  PRIOR {disease:16s} {change['old'] * 100:3.0f}% -> "
            f"{change['value'] * 100:3.0f}%   {change['source']}"
        )
    if warnings_out:
        print("\nWARNINGS (these rows were not applied):")
        for warning in warnings_out:
            print(f"  - {warning}")

    if args.dry_run or (not feature_count and not priors):
        print("\nNothing written." + (" (dry run)" if args.dry_run else " No changes found."))
        return

    source_file = Path(args.xlsx).name
    info = {
        "reviewer": args.reviewer,
        "clinic_setting": setting,
        "generated": str(date.today()),
        "source_file": source_file,
    }
    data = {"priors": priors, "features": features}
    output = (
        '"""Doctor-reviewed Bio Matrix overrides. Generated by apply_review.py; '
        'do not edit by hand."""\n'
        f"REVIEW_INFO = {json.dumps(info, indent=2, ensure_ascii=False)}\n\n"
        f"OVERRIDES = {json.dumps(data, indent=2, ensure_ascii=False)}\n"
        f"{OVERRIDE_FUNCTIONS}"
    )
    Path(args.out).write_text(output, encoding="utf-8")
    print(f"\nWrote {args.out}. Delete or rename it to turn reviewed values off.")


if __name__ == "__main__":
    main()