"""Test Bio Matrix against real or published cases, not synthetic ones.

Usage (run from the project folder, with your venv active):
    python evaluate_cases.py --template     # makes cases_template.csv to fill in
    python evaluate_cases.py --features     # lists every finding name you can use
    python evaluate_cases.py cases.csv      # scores your cases

cases.csv columns:
    case_id              any label, e.g. C01
    source               where the case came from (journal, year, link)
    confirmed_diagnosis  the proven diagnosis, e.g. Dengue
    findings             semicolon-separated findings. Put a minus sign in front
                         of a finding that was documented as ABSENT.
                         Example: fever; headache; low_platelets; -cough

RULES FOR HONEST RESULTS
  1. Write down each case's findings BEFORE you look at what the model says.
  2. Only enter findings that the published case report actually states.
  3. Do not change probabilities in knowledge.py to fix cases you are testing on.
     Keep a separate set of cases you never tune on.
  4. Use published, de-identified cases only. Do not put patient identifiers here.
"""
import csv
import math
import sys
from collections import defaultdict

from knowledge import DISEASES, FEATURES
from model import build_model

LABEL_TO_KEY = {details["label"].lower(): key for key, details in FEATURES.items()}
DISEASE_LOOKUP = {disease.lower(): disease for disease in DISEASES}


def parse_findings(text):
    """Parse findings into evidence, unknown names, and present/absent conflicts."""
    evidence, unknown, conflicts = {}, [], []
    for raw in (text or "").split(";"):
        item = raw.strip()
        if not item:
            continue
        present = True
        if item.startswith("-"):
            present, item = False, item[1:].strip()
        key = item if item in FEATURES else LABEL_TO_KEY.get(item.lower())
        if key is None:
            unknown.append(item)
            continue
        if key in evidence and evidence[key] != present:
            conflicts.append(key)
        evidence[key] = present
    return evidence, unknown, conflicts


def wilson(k, n, z=1.96):
    """Return a 95% Wilson confidence interval for a proportion k/n."""
    if n == 0:
        return 0.0, 0.0
    proportion = k / n
    denominator = 1 + z * z / n
    center = proportion + z * z / (2 * n)
    margin = z * math.sqrt(
        proportion * (1 - proportion) / n + z * z / (4 * n * n)
    )
    return (center - margin) / denominator, (center + margin) / denominator


def write_template(path="cases_template.csv"):
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["case_id", "source", "confirmed_diagnosis", "findings"])
        writer.writerow([
            "EXAMPLE-1",
            "made-up row, delete me",
            "Dengue",
            "fever; headache; body_pain; low_platelets; -cough",
        ])
        writer.writerow([
            "EXAMPLE-2",
            "made-up row, delete me",
            "UTI",
            "burning_urination; fever; urine_pus_cells_high",
        ])
    print(f"Wrote {path}. Replace the EXAMPLE rows with published cases.")


def list_features():
    for key, details in FEATURES.items():
        print(f"{key:30s} [{details['kind']}]  {details['label']}")


def evaluate(path):
    model = build_model()
    with open(path, newline="", encoding="utf-8-sig") as file:
        rows = [
            row for row in csv.DictReader(file)
            if not (row.get("case_id") or "").upper().startswith("EXAMPLE")
        ]

    scored, out_of_scope, problems, misses, details = [], [], [], [], []
    per_disease = defaultdict(lambda: [0, 0, 0])

    for row in rows:
        case_id = (row.get("case_id") or "?").strip()
        diagnosis_raw = (row.get("confirmed_diagnosis") or "").strip()
        evidence, unknown, conflicts = parse_findings(row.get("findings"))
        if unknown:
            problems.append(f"{case_id}: unknown finding(s) {unknown} (run --features)")
        if conflicts:
            problems.append(f"{case_id}: finding listed as both present and absent: {conflicts}")
        diagnosis = DISEASE_LOOKUP.get(diagnosis_raw.lower())
        if diagnosis is None:
            out_of_scope.append((case_id, diagnosis_raw))
            continue
        if unknown or conflicts:
            problems.append(f"{case_id}: skipped until finding names/conflicts are fixed")
            continue
        if not evidence:
            problems.append(f"{case_id}: no usable findings, skipped")
            continue
        if sum(evidence.values()) < 3:
            problems.append(f"{case_id}: fewer than 3 findings present, result is weak evidence")

        ranked = model.ranked(evidence)
        ranked_names = [disease for disease, _ in ranked]
        top1_correct = ranked_names[0] == diagnosis
        top3_correct = diagnosis in ranked_names[:3]
        scored.append((case_id, diagnosis, top1_correct, top3_correct))
        disease_stats = per_disease[diagnosis]
        disease_stats[0] += 1
        disease_stats[1] += top1_correct
        disease_stats[2] += top3_correct
        top3_text = ", ".join(
            f"{disease} {probability * 100:.0f}%"
            for disease, probability in ranked[:3]
        )
        rank_of_truth = ranked_names.index(diagnosis) + 1
        details.append([
            case_id,
            row.get("source", ""),
            diagnosis,
            top3_text,
            rank_of_truth,
            "yes" if top1_correct else "no",
            "yes" if top3_correct else "no",
        ])
        if not top1_correct:
            misses.append((case_id, diagnosis, top3_text, rank_of_truth))

    count = len(scored)
    print("=" * 62)
    print(
        f"Cases in file: {len(rows)}   scored: {count}   "
        f"outside the 8 diseases: {len(out_of_scope)}"
    )
    print("=" * 62)
    if count:
        top1_count = sum(1 for result in scored if result[2])
        top3_count = sum(1 for result in scored if result[3])
        low1, high1 = wilson(top1_count, count)
        low3, high3 = wilson(top3_count, count)
        print(
            f"Top-1 accuracy: {top1_count}/{count} = {top1_count / count * 100:.0f}%   "
            f"(95% range {low1 * 100:.0f}-{high1 * 100:.0f}%)"
        )
        print(
            f"Top-3 accuracy: {top3_count}/{count} = {top3_count / count * 100:.0f}%   "
            f"(95% range {low3 * 100:.0f}-{high3 * 100:.0f}%)"
        )
        if count < 25:
            print(f"NOTE: only {count} cases. Treat this as a first look, not a result. Aim for 25+.")
        print("\nBy disease (cases / top-1 correct / top-3 correct):")
        for disease in DISEASES:
            if disease in per_disease:
                case_count, top1_correct, top3_correct = per_disease[disease]
                print(f"  {disease:16s} {case_count:3d} / {top1_correct:3d} / {top3_correct:3d}")
        if misses:
            print("\nCases where the top answer was wrong:")
            for case_id, diagnosis, top3_text, rank in misses:
                print(f"  {case_id}: truth = {diagnosis} (ranked #{rank}); model said {top3_text}")
        with open("case_results.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "case_id", "source", "truth", "model_top3", "rank_of_truth",
                "top1_correct", "top3_correct",
            ])
            writer.writerows(details)
        print("\nFull per-case results saved to case_results.csv")
    if out_of_scope:
        print("\nOutside the model's scope (not scored, but report these honestly):")
        for case_id, diagnosis in out_of_scope:
            print(f"  {case_id}: {diagnosis or '(blank)'}")
    if problems:
        print("\nData problems to fix:")
        for problem in problems:
            print("  -", problem)


if __name__ == "__main__":
    argument = sys.argv[1] if len(sys.argv) > 1 else ""
    if argument == "--template":
        write_template()
    elif argument == "--features":
        list_features()
    elif argument:
        evaluate(argument)
    else:
        print(__doc__)
