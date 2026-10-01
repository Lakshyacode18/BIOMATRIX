"""
AI Doctor Assistant - command line version.

  python main.py             interactive, stage by stage
  python main.py --demo      scripted dengue example
  python main.py --evaluate  accuracy on unseen synthetic patients
"""
import sys

from knowledge import DISCLAIMER, FEATURES
from medications import PATIENT_FACTORS, format_plan, get_plan
from model import build_model, evaluate


def label(f):
    return FEATURES[f]["label"]


def show_ranking(model, evidence, top_k=5, factors=(), full_plan=False):
    print("\n  Possible conditions (probability):")
    for disease, p in model.ranked(evidence, top_k):
        print(f"   {disease:<16} {p * 100:5.1f}%  {'#' * int(p * 30)}")
    top = model.ranked(evidence, 1)[0][0]
    plan = get_plan(top, factors)
    if full_plan:
        print("\n  --- Medication reference (for doctor review, not a prescription) ---")
        print(format_plan(plan))
    else:
        print(f"\n  For {top}: {plan['summary']}")


def show_suggestions(model, evidence):
    labs = [f for f, v in FEATURES.items() if v["kind"] == "lab"]
    print("\n  Most useful next tests (biggest reduction in uncertainty):")
    for f, gain in model.suggest_next(evidence, labs, top_k=3):
        print(f"   - {label(f)}  (information gain {gain:.2f} bits)")


def show_explanation(model, evidence):
    top = model.ranked(evidence, 1)[0][0]
    print(f"\n  Why {top}? (+ supports, - argues against)")
    for f, score in model.explain(evidence, top)[:6]:
        state = "present" if evidence[f] else "absent"
        print(f"   {score:+.2f}  {label(f)} ({state})")


def ask_multi(kind, prompt):
    names = [f for f, v in FEATURES.items() if v["kind"] == kind]
    for i, f in enumerate(names, 1):
        print(f"   {i:>2}. {label(f)}")
    raw = input(f"  {prompt} (numbers separated by commas, Enter to skip): ").strip()
    chosen = []
    for tok in raw.split(","):
        tok = tok.strip()
        if tok.isdigit() and 1 <= int(tok) <= len(names):
            chosen.append(names[int(tok) - 1])
    return chosen


def yes_no(prompt):
    return input(f"  {prompt} (y/n): ").strip().lower().startswith("y")


def interactive(model):
    print("\n" + DISCLAIMER)
    evidence = {}

    print("\n=== Patient factors (affect medicine cautions) ===")
    keys = list(PATIENT_FACTORS)
    for i, k in enumerate(keys, 1):
        print(f"   {i}. {PATIENT_FACTORS[k]}")
    raw = input("  Tick any that apply (numbers separated by commas, Enter for none): ").strip()
    factors = [keys[int(t) - 1] for t in (x.strip() for x in raw.split(",")) if t.isdigit() and 1 <= int(t) <= len(keys)]

    print("\n=== STAGE 1: Symptoms ===")
    for f in ask_multi("symptom", "Symptoms PRESENT"):
        evidence[f] = True
    print("  (Symptoms you did not select stay 'unknown'. Select absent ones below to use them.)")
    for f in ask_multi("symptom", "Symptoms confirmed ABSENT"):
        evidence.setdefault(f, False)
    if not evidence:
        print("  No symptoms entered.")
        return
    show_ranking(model, evidence)

    print("\n=== STAGE 2: Medication response ===")
    if yes_no("Has the patient taken medication for 2-3 days with NO improvement?"):
        evidence["no_response_paracetamol"] = True
        show_ranking(model, evidence)
        show_suggestions(model, evidence)
    else:
        print("  Continue treatment / review later. Exiting.")
        return

    print("\n=== STAGE 3: New symptoms + test results ===")
    for f in ask_multi("symptom", "NEW symptoms present"):
        evidence[f] = True
    print("  Test findings that are POSITIVE / ABNORMAL:")
    for f in ask_multi("lab", "Abnormal findings"):
        evidence[f] = True
    print("  Tests done that were NORMAL / NEGATIVE:")
    for f in ask_multi("lab", "Normal findings"):
        evidence.setdefault(f, False)
    show_ranking(model, evidence, factors=factors, full_plan=True)
    show_explanation(model, evidence)
    print("\n" + DISCLAIMER)


def demo(model):
    print(DISCLAIMER)
    evidence = {"fever": True, "headache": True, "cough": False}
    print("\n=== STAGE 1: fever + headache (no cough) ===")
    show_ranking(model, evidence)

    print("\n=== STAGE 2: paracetamol given, fever persists, body pain appears ===")
    evidence.update({"no_response_paracetamol": True, "body_pain": True})
    show_ranking(model, evidence)
    show_suggestions(model, evidence)

    print("\n=== STAGE 3: platelets LOW, NS1 positive ===")
    evidence.update({"low_platelets": True, "ns1_positive": True})
    show_ranking(model, evidence, factors=["liver_disease"], full_plan=True)
    show_explanation(model, evidence)


if __name__ == "__main__":
    print("Training model on synthetic data...")
    m = build_model()
    if "--evaluate" in sys.argv:
        for setting, (t1, t3) in evaluate(m).items():
            print(f"{setting:<32} top-1: {t1 * 100:.1f}%   top-3: {t3 * 100:.1f}%")
        print("(Measured on synthetic data - real-world accuracy will be lower.)")
    elif "--demo" in sys.argv:
        demo(m)
    else:
        interactive(m)
