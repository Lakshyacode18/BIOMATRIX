"""
Bio Matrix prototype knowledge base.

IMPORTANT: The probabilities are illustrative, hand-written estimates that have
not been clinically validated. They are not clinical statistics or learned from
patient data, and require qualified-doctor review before any real-world use.
"""

# Disease names are the keys used by priors and feature probabilities below.
DISEASES = ["Viral fever", "Dengue", "Typhoid", "Malaria",
            "Pneumonia", "UTI", "Gastroenteritis", "Leptospirosis"]

# Illustrative prior assumptions for an Indian outpatient fever workup only.
# These are not prevalence estimates; actual priors vary by season, region, and clinic type.
PRIORS = {
    "Viral fever": 0.33,
    "Dengue": 0.10,
    "Typhoid": 0.08,
    "Malaria": 0.07,
    "Pneumonia": 0.10,
    "UTI": 0.12,
    "Gastroenteritis": 0.17,
    "Leptospirosis": 0.03,
}

# Feature probabilities are keyed by disease so changing disease order is safe.
FEATURES = {
    # ---- symptoms ----
    "fever": {"kind": "symptom", "label": "Fever", "p": {"Viral fever": .90, "Dengue": .98, "Typhoid": .95, "Malaria": .98, "Pneumonia": .85, "UTI": .40, "Gastroenteritis": .30, "Leptospirosis": .95}},
    "headache": {"kind": "symptom", "label": "Headache", "p": {"Viral fever": .50, "Dengue": .80, "Typhoid": .55, "Malaria": .70, "Pneumonia": .25, "UTI": .10, "Gastroenteritis": .15, "Leptospirosis": .70}},
    "body_pain": {"kind": "symptom", "label": "Body pain / myalgia", "p": {"Viral fever": .55, "Dengue": .90, "Typhoid": .50, "Malaria": .70, "Pneumonia": .30, "UTI": .10, "Gastroenteritis": .20, "Leptospirosis": .85}},
    "chills": {"kind": "symptom", "label": "Chills / rigors", "p": {"Viral fever": .30, "Dengue": .40, "Typhoid": .40, "Malaria": .90, "Pneumonia": .30, "UTI": .20, "Gastroenteritis": .05, "Leptospirosis": .45}},
    "cough": {"kind": "symptom", "label": "Cough", "p": {"Viral fever": .45, "Dengue": .10, "Typhoid": .15, "Malaria": .05, "Pneumonia": .90, "UTI": .03, "Gastroenteritis": .03, "Leptospirosis": .05}},
    "sore_throat": {"kind": "symptom", "label": "Sore throat", "p": {"Viral fever": .55, "Dengue": .05, "Typhoid": .10, "Malaria": .03, "Pneumonia": .15, "UTI": .02, "Gastroenteritis": .03, "Leptospirosis": .05}},
    "runny_nose": {"kind": "symptom", "label": "Runny nose", "p": {"Viral fever": .55, "Dengue": .05, "Typhoid": .05, "Malaria": .03, "Pneumonia": .20, "UTI": .02, "Gastroenteritis": .03, "Leptospirosis": .03}},
    "breathlessness": {"kind": "symptom", "label": "Breathlessness", "p": {"Viral fever": .03, "Dengue": .05, "Typhoid": .05, "Malaria": .05, "Pneumonia": .60, "UTI": .02, "Gastroenteritis": .03, "Leptospirosis": .10}},
    "vomiting": {"kind": "symptom", "label": "Vomiting", "p": {"Viral fever": .15, "Dengue": .45, "Typhoid": .40, "Malaria": .35, "Pneumonia": .10, "UTI": .15, "Gastroenteritis": .75, "Leptospirosis": .35}},
    "diarrhea": {"kind": "symptom", "label": "Diarrhea", "p": {"Viral fever": .10, "Dengue": .15, "Typhoid": .35, "Malaria": .10, "Pneumonia": .05, "UTI": .03, "Gastroenteritis": .85, "Leptospirosis": .10}},
    "abdominal_pain": {"kind": "symptom", "label": "Abdominal pain", "p": {"Viral fever": .10, "Dengue": .40, "Typhoid": .55, "Malaria": .15, "Pneumonia": .05, "UTI": .35, "Gastroenteritis": .60, "Leptospirosis": .15}},
    "rash": {"kind": "symptom", "label": "Skin rash", "p": {"Viral fever": .05, "Dengue": .40, "Typhoid": .15, "Malaria": .03, "Pneumonia": .02, "UTI": .02, "Gastroenteritis": .02, "Leptospirosis": .05}},
    "joint_pain": {"kind": "symptom", "label": "Joint pain", "p": {"Viral fever": .25, "Dengue": .70, "Typhoid": .15, "Malaria": .30, "Pneumonia": .05, "UTI": .03, "Gastroenteritis": .05, "Leptospirosis": .30}},
    "retro_orbital_pain": {"kind": "symptom", "label": "Pain behind the eyes", "p": {"Viral fever": .05, "Dengue": .55, "Typhoid": .03, "Malaria": .05, "Pneumonia": .02, "UTI": .01, "Gastroenteritis": .02, "Leptospirosis": .05}},
    "burning_urination": {"kind": "symptom", "label": "Burning urination", "p": {"Viral fever": .02, "Dengue": .02, "Typhoid": .02, "Malaria": .02, "Pneumonia": .02, "UTI": .95, "Gastroenteritis": .02, "Leptospirosis": .03}},
    "fatigue": {"kind": "symptom", "label": "Fatigue / weakness", "p": {"Viral fever": .50, "Dengue": .85, "Typhoid": .75, "Malaria": .75, "Pneumonia": .60, "UTI": .35, "Gastroenteritis": .50, "Leptospirosis": .80}},
    "bleeding_gums_nosebleed": {"kind": "symptom", "label": "Bleeding gums or nosebleed",
                                 "p": {"Viral fever": .02, "Dengue": .35, "Typhoid": .05, "Malaria": .05, "Pneumonia": .02, "UTI": .01, "Gastroenteritis": .02, "Leptospirosis": .10}},
    "relative_bradycardia":   {"kind": "symptom", "label": "Pulse slower than expected for the fever (relative bradycardia)",
                                # Clinician review requested; validate this illustrative Typhoid value.
                                "p": {"Viral fever": .05, "Dengue": .05, "Typhoid": .55, "Malaria": .05, "Pneumonia": .03, "UTI": .02, "Gastroenteritis": .02, "Leptospirosis": .05}},
    "rose_spots":             {"kind": "symptom", "label": "Rose-coloured skin spots on abdomen/chest",
                                "p": {"Viral fever": .01, "Dengue": .02, "Typhoid": .20, "Malaria": .01, "Pneumonia": .01, "UTI": .01, "Gastroenteritis": .01, "Leptospirosis": .01}},
    # ---- medication response ----
    "no_response_paracetamol": {"kind": "medication",
                                "label": "Fever persisted after 2-3 days of paracetamol",
                                # Clinician review requested; antipyretic response may not discriminate well.
                                          "p": {"Viral fever": .15, "Dengue": .70, "Typhoid": .80, "Malaria": .75, "Pneumonia": .70, "UTI": .50, "Gastroenteritis": .20, "Leptospirosis": .75}},
    # ---- lab / test findings ----
     "low_platelets": {"kind": "basic_lab", "label": "Low platelet count (from CBC)", "p": {"Viral fever": .05, "Dengue": .85, "Typhoid": .15, "Malaria": .70, "Pneumonia": .05, "UTI": .03, "Gastroenteritis": .03, "Leptospirosis": .35}},
     "high_wbc": {"kind": "basic_lab", "label": "High WBC count (from CBC)", "p": {"Viral fever": .10, "Dengue": .03, "Typhoid": .10, "Malaria": .10, "Pneumonia": .75, "UTI": .55, "Gastroenteritis": .15, "Leptospirosis": .40}},
     "low_wbc": {"kind": "basic_lab", "label": "Low WBC count (from CBC)", "p": {"Viral fever": .15, "Dengue": .60, "Typhoid": .30, "Malaria": .15, "Pneumonia": .03, "UTI": .02, "Gastroenteritis": .03, "Leptospirosis": .05}},
     "ns1_positive": {"kind": "confirmatory_lab", "label": "Dengue NS1 antigen positive", "p": {"Viral fever": .01, "Dengue": .80, "Typhoid": .01, "Malaria": .01, "Pneumonia": .01, "UTI": .01, "Gastroenteritis": .01, "Leptospirosis": .01}},
     "widal_positive": {"kind": "confirmatory_lab", "label": "Widal / typhoid test positive", "p": {"Viral fever": .03, "Dengue": .03, "Typhoid": .70, "Malaria": .03, "Pneumonia": .02, "UTI": .02, "Gastroenteritis": .02, "Leptospirosis": .03}},
    "malaria_parasite_positive": {"kind": "confirmatory_lab", "label": "Malaria parasite test positive",
                                             "p": {"Viral fever": .01, "Dengue": .01, "Typhoid": .01, "Malaria": .85, "Pneumonia": .01, "UTI": .01, "Gastroenteritis": .01, "Leptospirosis": .01}},
     "urine_pus_cells_high": {"kind": "confirmatory_lab", "label": "Pus cells high in urine test", "p": {"Viral fever": .03, "Dengue": .03, "Typhoid": .03, "Malaria": .03, "Pneumonia": .03, "UTI": .90, "Gastroenteritis": .03, "Leptospirosis": .03}},
     "chest_xray_infiltrate": {"kind": "confirmatory_lab", "label": "Chest X-ray shows infiltrate", "p": {"Viral fever": .02, "Dengue": .01, "Typhoid": .01, "Malaria": .01, "Pneumonia": .85, "UTI": .01, "Gastroenteritis": .01, "Leptospirosis": .02}},
    "leptospirosis_igm_positive": {"kind": "confirmatory_lab", "label": "Leptospirosis IgM ELISA / MAT positive",
                                              "p": {"Viral fever": .01, "Dengue": .01, "Typhoid": .01, "Malaria": .01, "Pneumonia": .01, "UTI": .01, "Gastroenteritis": .01, "Leptospirosis": .80}},
    # ---- occupation / place exposure (ask directly - no test needed) ----
    "farm_fieldwork":         {"kind": "occupation", "label": "Works in farming / fieldwork",
                                                                "p": {"Viral fever": .05, "Dengue": .05, "Typhoid": .08, "Malaria": .10, "Pneumonia": .03, "UTI": .02, "Gastroenteritis": .05, "Leptospirosis": .55}},
    "animal_rodent_contact":  {"kind": "occupation", "label": "Regular contact with rodents / cattle / other animals",
                                                                "p": {"Viral fever": .03, "Dengue": .03, "Typhoid": .05, "Malaria": .05, "Pneumonia": .02, "UTI": .01, "Gastroenteritis": .03, "Leptospirosis": .60}},
    "sewage_sanitation_work": {"kind": "occupation", "label": "Works in sewage / sanitation / waste handling",
                                                                "p": {"Viral fever": .03, "Dengue": .03, "Typhoid": .25, "Malaria": .05, "Pneumonia": .02, "UTI": .02, "Gastroenteritis": .10, "Leptospirosis": .55}},
    "water_body_contact":     {"kind": "occupation", "label": "Recent wading/swimming in ponds, rivers, or stagnant water",
                                                                "p": {"Viral fever": .05, "Dengue": .15, "Typhoid": .05, "Malaria": .20, "Pneumonia": .02, "UTI": .02, "Gastroenteritis": .05, "Leptospirosis": .55}},
    "flood_affected_residence": {"kind": "occupation", "label": "Lives in / recently visited a flood-affected area",
                                                                    "p": {"Viral fever": .05, "Dengue": .20, "Typhoid": .08, "Malaria": .20, "Pneumonia": .03, "UTI": .02, "Gastroenteritis": .05, "Leptospirosis": .65}},

    # ---- history / exam findings (no lab needed) ----
    "calf_tenderness":       {"kind": "history", "label": "Calf muscle tenderness on pressing",
                               "p": {"Viral fever": .02, "Dengue": .05, "Typhoid": .03, "Malaria": .05, "Pneumonia": .01, "UTI": .01, "Gastroenteritis": .02, "Leptospirosis": .65}},
    "conjunctival_redness":  {"kind": "history", "label": "Eye redness without discharge (conjunctival suffusion)",
                               "p": {"Viral fever": .03, "Dengue": .05, "Typhoid": .02, "Malaria": .03, "Pneumonia": .02, "UTI": .01, "Gastroenteritis": .02, "Leptospirosis": .55}},
    "jaundice":              {"kind": "history", "label": "Yellowing of skin or eyes (jaundice)",
                               "p": {"Viral fever": .02, "Dengue": .03, "Typhoid": .05, "Malaria": .05, "Pneumonia": .02, "UTI": .01, "Gastroenteritis": .02, "Leptospirosis": .40}},
    "reduced_urine_output":  {"kind": "history", "label": "Reduced urine output",
                               "p": {"Viral fever": .02, "Dengue": .05, "Typhoid": .03, "Malaria": .05, "Pneumonia": .03, "UTI": .05, "Gastroenteritis": .03, "Leptospirosis": .35}},
    "biphasic_fever":        {"kind": "history", "label": "Fever improved then returned after a few days",
                               "p": {"Viral fever": .10, "Dengue": .15, "Typhoid": .10, "Malaria": .20, "Pneumonia": .05, "UTI": .03, "Gastroenteritis": .05, "Leptospirosis": .45}},
}

# Reported co-infections; these citations document reports, not model validity:
# - Dengue and enteric fever in North India: https://pubmed.ncbi.nlm.nih.gov/25653945/
# - Malaria and enteric fever in North India: https://pubmed.ncbi.nlm.nih.gov/24995183/
# - Adult malaria co-infections in Eastern India: https://pubmed.ncbi.nlm.nih.gov/35910822/
# Advisor review pending: should Leptospirosis-Dengue be flagged as a pair?
# Their overlapping presentation and co-infection reports are discussed at:
# https://pubmed.ncbi.nlm.nih.gov/39856559/ and https://pubmed.ncbi.nlm.nih.gov/30483374/
# Do not add that pair until a qualified advisor reviews its appropriateness.
COINFECTION_PAIRS = [("Dengue", "Typhoid"), ("Typhoid", "Malaria")]

# General, well-known supportive/treatment approaches shown for the DOCTOR to consider.
# This is NOT a prescription and contains no doses.
TREATMENT_NOTES = {
    "Viral fever": "Rest, fluids, paracetamol for fever; review if fever lasts beyond 3-5 days.",
    "Dengue": "Plenty of fluids, paracetamol for fever; avoid aspirin/NSAIDs; monitor platelets and warning signs.",
    "Typhoid": "Antibiotic choice guided by the doctor (ideally culture/sensitivity); fluids and rest.",
    "Malaria": "Antimalarial choice depends on parasite species and local guidelines; doctor to decide.",
    "Pneumonia": "Antibiotics chosen by severity and local guidelines; assess oxygen level and chest findings.",
    "UTI": "Antibiotics guided by urine culture where possible; encourage fluids.",
    "Gastroenteritis": "ORS/fluids to prevent dehydration; assess dehydration severity; antibiotics only if indicated.",
    "Leptospirosis": "Early antibiotics (e.g. doxycycline for mild cases, IV penicillin/ceftriaxone for severe) plus supportive care; monitor kidney and liver function.",
}

DISCLAIMER = ("Decision-support prototype built on illustrative, hand-written estimates that have not been "
              "clinically validated. Not a medical device. Intended for use by qualified doctors. "
              "Final diagnosis and treatment must be made by a qualified doctor. "
              "No patient data is stored.")


def validate_knowledge():
    assert len(DISEASES) == len(PRIORS), "PRIORS must match DISEASES"
    assert set(DISEASES) == set(PRIORS), "PRIORS keys must match DISEASES"
    for disease, prior in PRIORS.items():
        assert 0 <= prior <= 1, f"{disease}: prior {prior} is not between 0 and 1"

    for name, feature in FEATURES.items():
        missing = set(DISEASES) - set(feature["p"])
        extra = set(feature["p"]) - set(DISEASES)
        assert not missing and not extra, f"{name}: missing {missing}, unknown {extra}"
        for disease, probability in feature["p"].items():
            assert 0 <= probability <= 1, (
                f"{name}/{disease}: probability {probability} is not between 0 and 1"
            )


try:
    from reviewed_values import apply_overrides

    apply_overrides(FEATURES, PRIORS, DISEASES)
except ImportError:
    pass  # no doctor-reviewed values yet


validate_knowledge()
