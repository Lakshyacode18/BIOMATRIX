"""Streamlit website for the BioMatrix clinical decision-support prototype."""
import streamlit as st

from knowledge import DISCLAIMER, FEATURES
from medications import PATIENT_FACTORS, get_plan
from model import build_model

st.set_page_config(page_title="BioMatrix | Clinical Assistant", page_icon="B", layout="wide")


@st.cache_resource
def get_model():
    return build_model()


def feature_names(kind):
    return [feature for feature, details in FEATURES.items() if details["kind"] == kind]


def feature_label(feature):
    return FEATURES[feature]["label"]


model = get_model()
st.title("BioMatrix | Clinical Decision Support")
st.warning(DISCLAIMER)
st.caption("Educational prototype. Its probabilities come from synthetic training data and are not clinical estimates.")

patient_column, assessment_column = st.columns([1, 1])

with patient_column:
    st.header("Patient findings")
    with st.form("patient_assessment"):
        st.subheader("Stage 1 - Symptoms")
        symptoms_present = st.multiselect(
            "Symptoms present", feature_names("symptom"), format_func=feature_label
        )
        symptoms_absent = st.multiselect(
            "Symptoms confirmed absent",
            [feature for feature in feature_names("symptom") if feature not in symptoms_present],
            format_func=feature_label,
            help="Leave unreported symptoms unselected; they remain unknown to the model.",
        )

        st.subheader("Patient factors")
        patient_factors = st.multiselect(
            "Factors affecting medication cautions",
            list(PATIENT_FACTORS),
            format_func=lambda key: PATIENT_FACTORS[key],
        )

        st.subheader("Stage 2 - Medication response")
        no_response = st.checkbox(FEATURES["no_response_paracetamol"]["label"])

        st.subheader("Stage 3 - Test results")
        labs_positive = st.multiselect(
            "Abnormal / positive findings", feature_names("lab"), format_func=feature_label
        )
        labs_negative = st.multiselect(
            "Tests done: normal / negative",
            [feature for feature in feature_names("lab") if feature not in labs_positive],
            format_func=feature_label,
        )

        submitted = st.form_submit_button("Run assessment", type="primary", use_container_width=True)

    if submitted:
        evidence = {feature: True for feature in symptoms_present + labs_positive}
        evidence.update({feature: False for feature in symptoms_absent + labs_negative})
        if no_response:
            evidence["no_response_paracetamol"] = True
        st.session_state["assessment_evidence"] = evidence
        st.session_state["assessment_factors"] = patient_factors

with assessment_column:
    st.header("Assessment")
    evidence = st.session_state.get("assessment_evidence", {})
    if not evidence:
        st.info("Enter patient findings and run an assessment to view decision-support results.")
    else:
        ranked = model.ranked(evidence)
        st.subheader("Possible conditions")
        for disease, probability in ranked:
            st.progress(probability, text=f"{disease} · {probability:.1%}")

        top_disease, top_probability = ranked[0]
        st.metric("Highest model score", top_disease, f"{top_probability:.1%}")

        st.subheader("Suggested next tests")
        lab_features = feature_names("lab")
        suggestions = model.suggest_next(evidence, lab_features, top_k=3)
        if suggestions:
            for feature, information_gain in suggestions:
                st.write(f"- **{feature_label(feature)}** (information gain: {information_gain:.2f} bits)")
        else:
            st.info("All available test findings have already been entered.")

        st.subheader(f"Evidence affecting {top_disease}")
        for feature, score in model.explain(evidence, top_disease)[:6]:
            direction = "supports" if score > 0 else "argues against"
            state = "present" if evidence[feature] else "absent"
            st.write(f"- {feature_label(feature)} ({state}) {direction} this model result ({score:+.2f})")

        st.subheader("Medication reference for clinician review")
        selected_disease = st.selectbox("Reference condition", [disease for disease, _ in ranked])
        plan = get_plan(selected_disease, st.session_state.get("assessment_factors", []))
        st.write(plan["summary"])
        for medicine in plan["medicines"]:
            st.markdown(f"**{medicine['name']}** - {medicine['purpose']}")
            st.caption(medicine["notes"])
            for warning in medicine["warnings"]:
                st.warning(warning)
        st.markdown("**Avoid:** " + "; ".join(plan["avoid"]))
        st.markdown("**Monitor:** " + "; ".join(plan["monitor"]))
        st.error("Urgent clinical review if: " + "; ".join(plan["red_flags"]))