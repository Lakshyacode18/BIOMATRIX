"""
AI Doctor Assistant - command line version.

  python main.py             interactive, stage by stage
  python main.py --demo      scripted dengue example
  python main.py --evaluate  accuracy on unseen synthetic patients
"""
import sys

from knowledge import COINFECTION_PAIRS, DISCLAIMER, FEATURES
from medications import PATIENT_FACTORS, format_plan, get_plan
from model import build_model, evaluate


def label(f):
    return FEATURES[f]["label"]


def show_ranking(model, evidence, top_k=5, factors=(), full_plan=False):
    print("\n  Possible conditions (probability):")
    for disease, p in model.ranked(evidence, top_k):
        print(f"   {disease:<16} {p * 100:5.1f}%  {'#' * int(p * 30)}")
    for a, b, pa, pb in model.possible_coinfections(evidence, COINFECTION_PAIRS):
        print(f"\n  Note: {a} ({pa*100:.0f}%) and {b} ({pb*100:.0f}%) are both still strongly "
              f"possible - consider testing for BOTH rather than assuming one rules out the other.")
    top = model.ranked(evidence, 1)[0][0]
    plan = get_plan(top, factors)
    if full_plan:
        print("\n  --- Medication reference (for doctor review, not a prescription) ---")
        print(format_plan(plan))
    else:
        print(f"\n  For {top}: {plan['summary']}")


def show_suggestions(model, evidence, kind="lab", heading="Most useful next tests (biggest reduction in uncertainty)"):
    candidates = [f for f, v in FEATURES.items() if v["kind"] == kind]
    print(f"\n  {heading}:")
    for f, gain in model.suggest_next(evidence, candidates, top_k=3):
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
    else:
        print("  Continue treatment / review later. Exiting.")
        return

    print("\n=== STAGE 3: Occupation / place of exposure ===")
    show_suggestions(model, evidence, kind="occupation",
                      heading="Most useful exposure questions to ask right now")
    for f in ask_multi("occupation", "Exposure factors PRESENT"):
        evidence[f] = True
    for f in ask_multi("occupation", "Exposure factors confirmed ABSENT"):
        evidence.setdefault(f, False)
    show_ranking(model, evidence)

    print("\n=== STAGE 4: Exam findings + basic CBC (free or already done) ===")
    show_suggestions(model, evidence, kind="history",
                      heading="Most useful exam findings to check right now")
    for f in ask_multi("history", "Findings PRESENT"):
        evidence[f] = True
    for f in ask_multi("history", "Findings confirmed ABSENT"):
        evidence.setdefault(f, False)
    print("  If a basic CBC (platelet/WBC count) has already been done, enter it here:")
    for f in ask_multi("basic_lab", "CBC findings ABNORMAL"):
        evidence[f] = True
    for f in ask_multi("basic_lab", "CBC findings NORMAL"):
        evidence.setdefault(f, False)
    show_ranking(model, evidence)

    print("\n=== STAGE 5: Suggested confirmatory test + result ===")
    show_suggestions(model, evidence, kind="confirmatory_lab")
    for f in ask_multi("symptom", "Any NEW symptoms present"):
        evidence[f] = True
    print("  Confirmatory test result(s) POSITIVE / ABNORMAL:")
    for f in ask_multi("confirmatory_lab", "Abnormal findings"):
        evidence[f] = True
    print("  Confirmatory test(s) done that were NORMAL / NEGATIVE:")
    for f in ask_multi("confirmatory_lab", "Normal findings"):
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

    print("\n=== STAGE 3: occupation / place of exposure ===")
    show_suggestions(model, evidence, kind="occupation",
                      heading="Most useful exposure questions to ask right now")
    evidence.update({"flood_affected_residence": True, "water_body_contact": True})
    show_ranking(model, evidence)

    print("\n=== STAGE 4: exam findings + basic CBC ===")
    show_suggestions(model, evidence, kind="history",
                      heading="Most useful exam findings to check right now")
    evidence.update({"calf_tenderness": True})
    show_suggestions(model, evidence, kind="basic_lab", heading="Basic CBC values worth checking")
    evidence.update({"low_platelets": True})
    show_ranking(model, evidence)

    print("\n=== STAGE 5: suggested confirmatory test, based on updated suspicion ===")
    show_suggestions(model, evidence, kind="confirmatory_lab")
    evidence.update({"leptospirosis_igm_positive": True})
    show_ranking(model, evidence, factors=["liver_disease"], full_plan=True)
    show_explanation(model, evidence)
    print("\n" + DISCLAIMER)

    # --- Second scripted case: dengue (no leptospirosis exposure), for contrast ---
    print("\n\n############  SECOND CASE (dengue, for contrast)  ############")
    ev2 = {"fever": True, "headache": True, "cough": False,
           "no_response_paracetamol": True, "body_pain": True}
    print("\n=== fever, headache, body pain, no response to paracetamol ===")
    show_ranking(model, ev2)
    print("\n=== occupation: no flood/water/farm exposure ===")
    ev2.update({"flood_affected_residence": False, "water_body_contact": False, "farm_fieldwork": False})
    print("\n=== exam: no calf tenderness; CBC: low platelets ===")
    ev2.update({"calf_tenderness": False, "low_platelets": True})
    show_ranking(model, ev2)
    print("\n=== confirmatory test: NS1 positive ===")
    ev2.update({"ns1_positive": True})
    show_ranking(model, ev2, full_plan=True)

    # --- Third scripted case: dengue-typhoid CO-INFECTION ---
    print("\n\n############  THIRD CASE (possible dengue-typhoid co-infection)  ############")
    ev3 = {"fever": True, "headache": True, "body_pain": True, "abdominal_pain": True,
           "no_response_paracetamol": True}
    print("\n=== fever, headache, body pain, abdominal pain, no response to paracetamol ===")
    show_ranking(model, ev3)
    print("\n=== CBC: low platelets AND high WBC (mixed picture) ===")
    ev3.update({"low_platelets": True, "high_wbc": True})
    show_ranking(model, ev3)
    print("\n=== BOTH confirmatory tests come back positive ===")
    ev3.update({"ns1_positive": True, "widal_positive": True})
    show_ranking(model, ev3, full_plan=True)


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
