"""Streamlit web UI:  streamlit run app.py"""
import streamlit as st

from knowledge import COINFECTION_PAIRS, DISCLAIMER, DISEASES, FEATURES
from model import build_model

SHOW_MEDICATIONS = False

if SHOW_MEDICATIONS:
    from medications import PATIENT_FACTORS, get_plan

st.set_page_config(
    page_title="Bio Matrix: Clinical Decision Support (Prototype v0.1)",
    page_icon="🩺",
    layout="wide",
)


@st.cache_resource
def get_model():
    return build_model()


model = get_model()


def names(kind):
    return [f for f, v in FEATURES.items() if v["kind"] == kind]


def fmt(f):
    return FEATURES[f]["label"]


st.title("Bio Matrix: Clinical Decision Support (Prototype v0.1)")
st.warning(DISCLAIMER)

with st.expander("About this prototype"):
    st.markdown("**Conditions covered:** " + ", ".join(DISEASES))
    st.markdown("**Assumed setting:** Indian outpatient fever workup.")
    st.markdown(
        "**Prior assumptions:** The starting disease priors are illustrative, not local prevalence "
        "estimates; actual rates vary by season, region, and clinic type."
    )
    st.markdown(
        "**Main limitation:** The model treats symptoms as independent of one another, "
        "which is a simplifying assumption and may not reflect clinical relationships."
    )
    st.markdown(
        "**Advisor review pending:** Should Leptospirosis-Dengue be included as a possible "
        "co-infection pair? Reported overlap and co-infections exist, but the pair is not flagged here."
    )

left, right = st.columns([1, 1])
evidence = {}

with left:
    st.header("Patient findings")

    factors = []
    if SHOW_MEDICATIONS:
        factors = st.multiselect(
            "Patient factors (affect medicine cautions)",
            list(PATIENT_FACTORS),
            format_func=lambda key: PATIENT_FACTORS[key],
        )

    st.subheader("Stage 1 - Symptoms")
    present = st.multiselect("Symptoms present", names("symptom"), format_func=fmt)
    absent_options = [f for f in names("symptom") if f not in present]
    absent = st.multiselect("Symptoms confirmed absent (optional)", absent_options, format_func=fmt)
    evidence.update({f: True for f in present})
    evidence.update({f: False for f in absent})

    other_symptoms = st.text_area(
        "Any other symptoms not listed above (for clinician reference only; not scored by the model). "
        "Do not enter patient names, phone numbers, or IDs.",
        placeholder="e.g. mild ear pain, occasional dizziness...")

    st.subheader("Stage 2 - Medication response")
    if st.checkbox(FEATURES["no_response_paracetamol"]["label"]):
        evidence["no_response_paracetamol"] = True

    st.subheader("Stage 3 - Occupation / place of exposure")
    st.caption("Free to ask, no test needed - often the strongest clue for diseases like leptospirosis or typhoid.")
    occ_pos = st.multiselect("Exposure factors present", names("occupation"), format_func=fmt)
    occ_neg_options = [f for f in names("occupation") if f not in occ_pos]
    occ_neg = st.multiselect("Exposure factors confirmed absent (optional)", occ_neg_options, format_func=fmt)
    evidence.update({f: True for f in occ_pos})
    evidence.update({f: False for f in occ_neg})

    st.subheader("Stage 4 - Exam findings + basic CBC")
    st.caption("Bedside exam findings cost nothing; a basic CBC (platelet/WBC count) is cheap and widely available.")
    hist_pos = st.multiselect("Exam findings present", names("history"), format_func=fmt)
    hist_neg_options = [f for f in names("history") if f not in hist_pos]
    hist_neg = st.multiselect("Exam findings confirmed absent (optional)", hist_neg_options, format_func=fmt)
    evidence.update({f: True for f in hist_pos})
    evidence.update({f: False for f in hist_neg})

    cbc_pos = st.multiselect("Basic CBC: abnormal values (if already done)", names("basic_lab"), format_func=fmt)
    cbc_neg_options = [f for f in names("basic_lab") if f not in cbc_pos]
    cbc_neg = st.multiselect("Basic CBC: normal values", cbc_neg_options, format_func=fmt)
    evidence.update({f: True for f in cbc_pos})
    evidence.update({f: False for f in cbc_neg})

    st.subheader("Stage 5 - Confirmatory test result")
    lab_pos = st.multiselect("Confirmatory test: positive/abnormal", names("confirmatory_lab"), format_func=fmt)
    lab_neg_options = [f for f in names("confirmatory_lab") if f not in lab_pos]
    lab_neg = st.multiselect("Confirmatory test: normal/negative", lab_neg_options, format_func=fmt)
    evidence.update({f: True for f in lab_pos})
    evidence.update({f: False for f in lab_neg})

with right:
    st.header("Assessment")
    if not evidence:
        st.info("Enter symptoms on the left to see possible conditions.")
    else:
        if sum(1 for value in evidence.values() if value) < 3:
            st.info("Very few findings entered. The ranking is unreliable until more are added.")

        ranked = model.ranked(evidence)
        st.subheader("Possible conditions")
        st.bar_chart({d: round(p * 100, 1) for d, p in ranked}, horizontal=True)
        top, top_p = ranked[0]
        st.metric(
            "Highest-ranked condition",
            top,
            f"{top_p * 100:.0f}% (model estimate)",
            delta_color="off",
        )
        st.caption(
            "Scores are relative likelihoods from a prototype built on synthetic data. "
            "They are not clinical probabilities."
        )

        for a, b, pa, pb in model.possible_coinfections(evidence, COINFECTION_PAIRS):
            st.warning(
                f"Possible co-infection: {a} ({pa*100:.0f}%) and {b} ({pb*100:.0f}%) "
                "remain plausible together. This may warrant considering testing for both, "
                "at the doctor's discretion."
            )

        if other_symptoms.strip():
            st.caption(f"Doctor's free-text note (not yet scored by the model): \"{other_symptoms.strip()}\"")

        st.caption("Listed in order of how well each helps separate the leading possibilities.")

        unanswered_occ = [f for f in names("occupation") if f not in evidence]
        if unanswered_occ:
            st.subheader("Most useful exposure questions to ask right now (free)")
            for feature, _ in model.suggest_next(evidence, unanswered_occ, top_k=3):
                st.write(f"- **{fmt(feature)}**")

        unanswered_history = [f for f in names("history") if f not in evidence]
        if unanswered_history:
            st.subheader("Most useful exam findings to check right now (free)")
            for feature, _ in model.suggest_next(evidence, unanswered_history, top_k=3):
                st.write(f"- **{fmt(feature)}**")

        unanswered_cbc = [f for f in names("basic_lab") if f not in evidence]
        if unanswered_cbc:
            st.subheader("Basic CBC values worth checking (cheap, widely available)")
            for feature, _ in model.suggest_next(evidence, unanswered_cbc, top_k=3):
                st.write(f"- **{fmt(feature)}**")

        confirmatory = [f for f in names("confirmatory_lab")]
        st.subheader("Suggested confirmatory test")
        for feature, _ in model.suggest_next(evidence, confirmatory, top_k=3):
            st.write(f"- **{fmt(feature)}**")

        st.subheader(f"Why {top}?")
        for f, score in model.explain(evidence, top)[:6]:
            icon = "🟢" if score > 0 else "🔴"
            state = "present" if evidence[f] else "absent"
            st.write(f"{icon} {fmt(f)} ({state}): {score:+.2f}")

        if SHOW_MEDICATIONS:
            st.subheader("Medication reference (for doctor review)")
            chosen = st.selectbox("Show plan for", [d for d, _ in ranked], index=0)
            plan = get_plan(chosen, factors)
            st.write(plan["summary"])
            for medicine in plan["medicines"]:
                st.markdown(f"**{medicine['name']}** - {medicine['purpose']}. {medicine['notes']}")
                for warning in medicine["warnings"]:
                    st.warning(warning)
            st.markdown("**Avoid:** " + "; ".join(plan["avoid"]))
            st.markdown("**Monitor:** " + "; ".join(plan["monitor"]))
            st.error("Urgent review if: " + "; ".join(plan["red_flags"]))

st.divider()
st.link_button(
    "Report a wrong result / give feedback",
    "https://docs.google.com/forms/d/e/1FAIpQLSdKD13WL52CB_nEwNWu-oObhcScoUJFhO-WhGf-wwjsjBZt1g/viewform",
)
st.caption("Bio Matrix prototype v0.1 · Oct 2026 · No patient data is stored. "
           "Decision support for qualified doctors only.")
