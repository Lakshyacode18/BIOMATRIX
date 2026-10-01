"""
Knowledge base for the AI Doctor Assistant prototype.

IMPORTANT: The numbers below are ILLUSTRATIVE, hand-written values used to
generate SYNTHETIC training data for a college prototype. They are NOT clinical
statistics. Before any real use they must be replaced with data/guidelines
reviewed by qualified doctors.
"""

# Order matters: every probability list below follows this disease order.
DISEASES = ["Viral fever", "Dengue", "Typhoid", "Malaria",
            "Pneumonia", "UTI", "Gastroenteritis"]

# Rough share of each disease among patients who walk in with an illness.
PRIORS = [0.35, 0.10, 0.08, 0.07, 0.10, 0.12, 0.18]

# feature name -> kind, human label, P(feature present | disease) per disease
#                                Viral Dengue Typhoid Malaria Pneum UTI  Gastro
FEATURES = {
    # ---- symptoms ----
    "fever":              {"kind": "symptom", "label": "Fever",                      "p": [.90, .98, .95, .98, .85, .40, .30]},
    "headache":           {"kind": "symptom", "label": "Headache",                   "p": [.50, .80, .55, .70, .25, .10, .15]},
    "body_pain":          {"kind": "symptom", "label": "Body pain / myalgia",        "p": [.55, .90, .50, .70, .30, .10, .20]},
    "chills":             {"kind": "symptom", "label": "Chills / rigors",            "p": [.30, .40, .40, .90, .30, .20, .05]},
    "cough":              {"kind": "symptom", "label": "Cough",                      "p": [.45, .10, .15, .05, .90, .03, .03]},
    "sore_throat":        {"kind": "symptom", "label": "Sore throat",                "p": [.55, .05, .10, .03, .15, .02, .03]},
    "runny_nose":         {"kind": "symptom", "label": "Runny nose",                 "p": [.55, .05, .05, .03, .20, .02, .03]},
    "breathlessness":     {"kind": "symptom", "label": "Breathlessness",             "p": [.03, .05, .05, .05, .60, .02, .03]},
    "vomiting":           {"kind": "symptom", "label": "Vomiting",                   "p": [.15, .45, .40, .35, .10, .15, .75]},
    "diarrhea":           {"kind": "symptom", "label": "Diarrhea",                   "p": [.10, .15, .35, .10, .05, .03, .85]},
    "abdominal_pain":     {"kind": "symptom", "label": "Abdominal pain",             "p": [.10, .40, .55, .15, .05, .35, .60]},
    "rash":               {"kind": "symptom", "label": "Skin rash",                  "p": [.05, .40, .15, .03, .02, .02, .02]},
    "joint_pain":         {"kind": "symptom", "label": "Joint pain",                 "p": [.25, .70, .15, .30, .05, .03, .05]},
    "retro_orbital_pain": {"kind": "symptom", "label": "Pain behind the eyes",       "p": [.05, .55, .03, .05, .02, .01, .02]},
    "burning_urination":  {"kind": "symptom", "label": "Burning urination",          "p": [.02, .02, .02, .02, .02, .95, .02]},
    "fatigue":            {"kind": "symptom", "label": "Fatigue / weakness",         "p": [.50, .85, .75, .75, .60, .35, .50]},
    # ---- medication response ----
    "no_response_paracetamol": {"kind": "medication",
                                "label": "Fever persisted after 2-3 days of paracetamol",
                                "p": [.15, .70, .80, .75, .70, .50, .20]},
    # ---- lab / test findings ----
    "low_platelets":      {"kind": "lab", "label": "Low platelet count",             "p": [.05, .85, .15, .70, .05, .03, .03]},
    "high_wbc":           {"kind": "lab", "label": "High WBC count",                 "p": [.10, .03, .10, .10, .75, .55, .15]},
    "low_wbc":            {"kind": "lab", "label": "Low WBC count",                  "p": [.15, .60, .30, .15, .03, .02, .03]},
    "ns1_positive":       {"kind": "lab", "label": "Dengue NS1 antigen positive",    "p": [.01, .80, .01, .01, .01, .01, .01]},
    "widal_positive":     {"kind": "lab", "label": "Widal / typhoid test positive",  "p": [.03, .03, .70, .03, .02, .02, .02]},
    "malaria_parasite_positive": {"kind": "lab", "label": "Malaria parasite test positive",
                                  "p": [.01, .01, .01, .85, .01, .01, .01]},
    "urine_pus_cells_high": {"kind": "lab", "label": "Pus cells high in urine test", "p": [.03, .03, .03, .03, .03, .90, .03]},
    "chest_xray_infiltrate": {"kind": "lab", "label": "Chest X-ray shows infiltrate", "p": [.02, .01, .01, .01, .85, .01, .01]},
}

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
}

# Symptom combinations that should always prompt urgent clinical review.
DISCLAIMER = ("Decision-support prototype trained on SYNTHETIC data. Not a medical device. "
              "Final diagnosis and treatment must be made by a qualified doctor.")
