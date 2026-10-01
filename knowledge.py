"""
Knowledge base for the AI Doctor Assistant prototype.

IMPORTANT: The numbers below are ILLUSTRATIVE, hand-written values used to
generate SYNTHETIC training data for a college prototype. They are NOT clinical
statistics. Before any real use they must be replaced with data/guidelines
reviewed by qualified doctors.
"""

# Order matters: every probability list below follows this disease order.
DISEASES = ["Viral fever", "Dengue", "Typhoid", "Malaria",
            "Pneumonia", "UTI", "Gastroenteritis", "Leptospirosis"]

# Rough share of each disease among patients who walk in with an illness.
PRIORS = [0.33, 0.10, 0.08, 0.07, 0.10, 0.12, 0.17, 0.03]  # Leptospirosis kept low: real but less common than dengue/typhoid

# feature name -> kind, human label, P(feature present | disease) per disease
#                                Viral Dengue Typhoid Malaria Pneum UTI  Gastro
FEATURES = {
    # ---- symptoms ----
    "fever":              {"kind": "symptom", "label": "Fever",                      "p": [.90, .98, .95, .98, .85, .40, .30, 0.95]},
    "headache":           {"kind": "symptom", "label": "Headache",                   "p": [.50, .80, .55, .70, .25, .10, .15, 0.7]},
    "body_pain":          {"kind": "symptom", "label": "Body pain / myalgia",        "p": [.55, .90, .50, .70, .30, .10, .20, 0.85]},
    "chills":             {"kind": "symptom", "label": "Chills / rigors",            "p": [.30, .40, .40, .90, .30, .20, .05, 0.45]},
    "cough":              {"kind": "symptom", "label": "Cough",                      "p": [.45, .10, .15, .05, .90, .03, .03, 0.05]},
    "sore_throat":        {"kind": "symptom", "label": "Sore throat",                "p": [.55, .05, .10, .03, .15, .02, .03, 0.05]},
    "runny_nose":         {"kind": "symptom", "label": "Runny nose",                 "p": [.55, .05, .05, .03, .20, .02, .03, 0.03]},
    "breathlessness":     {"kind": "symptom", "label": "Breathlessness",             "p": [.03, .05, .05, .05, .60, .02, .03, 0.1]},
    "vomiting":           {"kind": "symptom", "label": "Vomiting",                   "p": [.15, .45, .40, .35, .10, .15, .75, 0.35]},
    "diarrhea":           {"kind": "symptom", "label": "Diarrhea",                   "p": [.10, .15, .35, .10, .05, .03, .85, 0.1]},
    "abdominal_pain":     {"kind": "symptom", "label": "Abdominal pain",             "p": [.10, .40, .55, .15, .05, .35, .60, 0.15]},
    "rash":               {"kind": "symptom", "label": "Skin rash",                  "p": [.05, .40, .15, .03, .02, .02, .02, 0.05]},
    "joint_pain":         {"kind": "symptom", "label": "Joint pain",                 "p": [.25, .70, .15, .30, .05, .03, .05, 0.3]},
    "retro_orbital_pain": {"kind": "symptom", "label": "Pain behind the eyes",       "p": [.05, .55, .03, .05, .02, .01, .02, 0.05]},
    "burning_urination":  {"kind": "symptom", "label": "Burning urination",          "p": [.02, .02, .02, .02, .02, .95, .02, 0.03]},
    "fatigue":            {"kind": "symptom", "label": "Fatigue / weakness",         "p": [.50, .85, .75, .75, .60, .35, .50, 0.8]},
    "bleeding_gums_nosebleed": {"kind": "symptom", "label": "Bleeding gums or nosebleed",
                                 "p": [.02, .35, .05, .05, .02, .01, .02, 0.10]},
    "relative_bradycardia":   {"kind": "symptom", "label": "Pulse slower than expected for the fever (relative bradycardia)",
                                "p": [.05, .05, .55, .05, .03, .02, .02, 0.05]},
    "rose_spots":             {"kind": "symptom", "label": "Rose-coloured skin spots on abdomen/chest",
                                "p": [.01, .02, .20, .01, .01, .01, .01, 0.01]},
    # ---- medication response ----
    "no_response_paracetamol": {"kind": "medication",
                                "label": "Fever persisted after 2-3 days of paracetamol",
                                "p": [.15, .70, .80, .75, .70, .50, .20, 0.75]},
    # ---- lab / test findings ----
    "low_platelets":      {"kind": "basic_lab", "label": "Low platelet count (from CBC)",       "p": [.05, .85, .15, .70, .05, .03, .03, 0.35]},
    "high_wbc":           {"kind": "basic_lab", "label": "High WBC count (from CBC)",           "p": [.10, .03, .10, .10, .75, .55, .15, 0.4]},
    "low_wbc":            {"kind": "basic_lab", "label": "Low WBC count (from CBC)",            "p": [.15, .60, .30, .15, .03, .02, .03, 0.05]},
    "ns1_positive":       {"kind": "confirmatory_lab", "label": "Dengue NS1 antigen positive",    "p": [.01, .80, .01, .01, .01, .01, .01, 0.01]},
    "widal_positive":     {"kind": "confirmatory_lab", "label": "Widal / typhoid test positive",  "p": [.03, .03, .70, .03, .02, .02, .02, 0.03]},
    "malaria_parasite_positive": {"kind": "confirmatory_lab", "label": "Malaria parasite test positive",
                                  "p": [.01, .01, .01, .85, .01, .01, .01, 0.01]},
    "urine_pus_cells_high": {"kind": "confirmatory_lab", "label": "Pus cells high in urine test", "p": [.03, .03, .03, .03, .03, .90, .03, 0.03]},
    "chest_xray_infiltrate": {"kind": "confirmatory_lab", "label": "Chest X-ray shows infiltrate", "p": [.02, .01, .01, .01, .85, .01, .01, 0.02]},
    "leptospirosis_igm_positive": {"kind": "confirmatory_lab", "label": "Leptospirosis IgM ELISA / MAT positive",
                                   "p": [.01, .01, .01, .01, .01, .01, .01, .80]},
    # ---- occupation / place exposure (ask directly - no test needed) ----
    "farm_fieldwork":         {"kind": "occupation", "label": "Works in farming / fieldwork",
                                "p": [.05, .05, .08, .10, .03, .02, .05, .55]},
    "animal_rodent_contact":  {"kind": "occupation", "label": "Regular contact with rodents / cattle / other animals",
                                "p": [.03, .03, .05, .05, .02, .01, .03, .60]},
    "sewage_sanitation_work": {"kind": "occupation", "label": "Works in sewage / sanitation / waste handling",
                                "p": [.03, .03, .25, .05, .02, .02, .10, .55]},
    "water_body_contact":     {"kind": "occupation", "label": "Recent wading/swimming in ponds, rivers, or stagnant water",
                                "p": [.05, .15, .05, .20, .02, .02, .05, .55]},
    "flood_affected_residence": {"kind": "occupation", "label": "Lives in / recently visited a flood-affected area",
                                  "p": [.05, .20, .08, .20, .03, .02, .05, .65]},

    # ---- history / exam findings (no lab needed) ----
    "calf_tenderness":       {"kind": "history", "label": "Calf muscle tenderness on pressing",
                               "p": [.02, .05, .03, .05, .01, .01, .02, .65]},
    "conjunctival_redness":  {"kind": "history", "label": "Eye redness without discharge (conjunctival suffusion)",
                               "p": [.03, .05, .02, .03, .02, .01, .02, .55]},
    "jaundice":              {"kind": "history", "label": "Yellowing of skin or eyes (jaundice)",
                               "p": [.02, .03, .05, .05, .02, .01, .02, .40]},
    "reduced_urine_output":  {"kind": "history", "label": "Reduced urine output",
                               "p": [.02, .05, .03, .05, .03, .05, .03, .35]},
    "biphasic_fever":        {"kind": "history", "label": "Fever improved then returned after a few days",
                               "p": [.10, .15, .10, .20, .05, .03, .05, .45]},
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

DISCLAIMER = ("Decision-support prototype trained on SYNTHETIC data. Not a medical device. "
              "Intended for use by qualified doctors. Final diagnosis and treatment must be made "
              "by a qualified doctor. No patient data is stored.")
