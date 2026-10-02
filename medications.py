"""
Medication reference for the Bio Matrix prototype.

For the DOCTOR to review - this is a decision-support reference, not a prescription.
Doses are intentionally NOT included: they depend on age, weight, kidney/liver function,
pregnancy and local guidelines. Verify everything against current national guidelines
(e.g. ICMR, NCVBDC for malaria/dengue, WHO) and have it reviewed by a qualified doctor
before any real-world use.
"""

# Patient factors the doctor can tick. Each medicine lists which of these need caution.
PATIENT_FACTORS = {
    "pregnancy": "Pregnant",
    "child": "Child (under 12)",
    "penicillin_allergy": "Penicillin / beta-lactam allergy",
    "sulfa_allergy": "Sulfa drug allergy",
    "kidney_disease": "Kidney disease",
    "liver_disease": "Liver disease",
    "g6pd_deficiency": "G6PD deficiency",
}

MEDICATIONS = {
    "Viral fever": {
        "summary": "Usually self-limiting; treat symptoms and hydrate. Antibiotics are not needed unless a bacterial infection is suspected.",
        "medicines": [
            {"name": "Paracetamol", "purpose": "Fever and body pain",
             "notes": "Dose by age/weight; do not exceed the daily maximum.",
             "caution_if": {"liver_disease": "Use with caution / reduced dose in liver disease."}},
            {"name": "ORS / oral fluids", "purpose": "Prevent dehydration", "notes": "Encourage frequent fluids and rest.",
             "caution_if": {}},
            {"name": "Antihistamine or saline nasal drops", "purpose": "Runny nose / congestion (symptomatic)",
             "notes": "Only if symptoms are troublesome.",
             "caution_if": {"child": "Check age suitability; avoid cough/cold combinations in young children.",
                            "pregnancy": "Check suitability with the treating doctor."}},
        ],
        "avoid": ["Routine antibiotics for a viral illness",
                  "Aspirin in children (risk of Reye syndrome)"],
        "monitor": ["Fever pattern and hydration", "Review if fever lasts more than 3-5 days or new symptoms appear"],
        "red_flags": ["Persistent high fever", "Breathlessness", "Confusion or drowsiness", "Unable to drink fluids"],
    },

    "Dengue": {
        "summary": "Supportive care: fluids and fever control, with careful monitoring of platelets and warning signs. No specific antiviral exists.",
        "medicines": [
            {"name": "Paracetamol", "purpose": "Fever and body pain",
             "notes": "Dose by age/weight; do not exceed the daily maximum.",
             "caution_if": {"liver_disease": "Dengue can affect the liver; use cautiously and monitor liver enzymes."}},
            {"name": "Oral rehydration / IV fluids", "purpose": "Maintain hydration and circulation",
             "notes": "IV fluids under medical supervision if oral intake is poor or warning signs appear.",
             "caution_if": {"kidney_disease": "Fluid volume needs careful medical supervision."}},
        ],
        "avoid": ["Aspirin", "NSAIDs such as ibuprofen and diclofenac (bleeding risk)",
                  "Antibiotics unless a separate bacterial infection is proven", "Steroids without a clear indication"],
        "monitor": ["Platelet count and haematocrit", "Urine output and hydration", "Bleeding signs"],
        "red_flags": ["Severe abdominal pain", "Persistent vomiting", "Bleeding from gums/nose or black stools",
                      "Rapid drop in platelets", "Restlessness or lethargy", "Cold clammy skin"],
    },

    "Typhoid": {
        "summary": "Confirm with blood culture where possible, then use an antibiotic guided by local resistance patterns. Fluoroquinolone resistance is common in South Asia.",
        "medicines": [
            {"name": "Azithromycin", "purpose": "Antibiotic for uncomplicated typhoid (oral)",
             "notes": "Commonly used in India because of fluoroquinolone resistance; doctor chooses regimen.",
             "caution_if": {"liver_disease": "Use with caution.",
                            "kidney_disease": "Check dose adjustment need."}},
            {"name": "Cefixime (oral) or Ceftriaxone (injection)", "purpose": "Alternative or more severe cases (third-generation cephalosporin)",
             "notes": "Ceftriaxone is generally used for severe disease in hospital.",
             "caution_if": {"penicillin_allergy": "Cross-reactivity possible; avoid if there was a severe allergic reaction.",
                            "kidney_disease": "Check dose adjustment need."}},
            {"name": "Paracetamol and fluids", "purpose": "Fever control and hydration", "notes": "Supportive care.",
             "caution_if": {"liver_disease": "Use with caution / reduced dose."}},
        ],
        "avoid": ["Empirical fluoroquinolones where resistance is high (check local guidelines)",
                  "Starting antibiotics without considering culture if it can be collected first"],
        "monitor": ["Fever curve over several days", "Abdominal signs", "Hydration and diet"],
        "red_flags": ["Severe abdominal pain (possible perforation)", "Black or bloody stools",
                      "Confusion or drowsiness", "Persistent vomiting"],
    },

    "Malaria": {
        "summary": "Treatment depends on the parasite species and severity, so a confirmed test (rapid test or smear) comes first. Follow national malaria guidelines.",
        "medicines": [
            {"name": "Chloroquine (+ Primaquine for P. vivax)", "purpose": "P. vivax malaria; primaquine gives radical cure",
             "notes": "Confirm species first. Primaquine needs G6PD consideration.",
             "caution_if": {"g6pd_deficiency": "Primaquine can cause haemolysis; avoid or specialist advice.",
                            "pregnancy": "Primaquine is not used in pregnancy.",
                            "child": "Primaquine is not used in infants; check age limits."}},
            {"name": "Artemisinin-based combination therapy (ACT)", "purpose": "P. falciparum malaria",
             "notes": "Exact combination follows the state/regional guideline; usually with single-dose primaquine.",
             "caution_if": {"pregnancy": "Regimen differs by trimester; doctor to decide.",
                            "sulfa_allergy": "Some ACT partners contain a sulfa component; check the combination used.",
                            "g6pd_deficiency": "Primaquine component needs caution."}},
            {"name": "IV Artesunate", "purpose": "Severe malaria (hospital care)", "notes": "Emergency treatment under medical supervision.",
             "caution_if": {}},
            {"name": "Paracetamol", "purpose": "Fever control", "notes": "Supportive care.",
             "caution_if": {"liver_disease": "Use with caution / reduced dose."}},
        ],
        "avoid": ["Treating without confirmation of malaria where testing is possible",
                  "Primaquine before considering G6PD status, pregnancy and age"],
        "monitor": ["Fever pattern (cyclical fever with chills)", "Repeat test if symptoms persist", "Haemoglobin and platelets"],
        "red_flags": ["Confusion, seizures or drowsiness", "Severe anaemia or jaundice", "Breathlessness",
                      "Dark urine", "Persistent vomiting - cannot take oral medicine"],
    },

    "Pneumonia": {
        "summary": "Antibiotic choice depends on severity, age and local guidelines. Severe cases need hospital care and oxygen.",
        "medicines": [
            {"name": "Amoxicillin or Amoxicillin-clavulanate", "purpose": "First-line antibiotic for many community-acquired cases",
             "notes": "Doctor to choose by severity and local guidelines.",
             "caution_if": {"penicillin_allergy": "Avoid - use an alternative class.",
                            "kidney_disease": "Check dose adjustment need."}},
            {"name": "Azithromycin or Doxycycline", "purpose": "Atypical organisms / alternative in penicillin allergy",
             "notes": "Often combined or used as an alternative.",
             "caution_if": {"pregnancy": "Doxycycline is avoided in pregnancy.",
                            "child": "Doxycycline is avoided in young children (under 8).",
                            "liver_disease": "Use with caution."}},
            {"name": "Ceftriaxone (injection) + Oxygen", "purpose": "Moderate/severe pneumonia (hospital)", "notes": "Admit and monitor oxygen level.",
             "caution_if": {"penicillin_allergy": "Cross-reactivity possible; avoid if severe allergy history.",
                            "kidney_disease": "Check dose adjustment need."}},
            {"name": "Paracetamol", "purpose": "Fever and chest pain", "notes": "Supportive care.",
             "caution_if": {"liver_disease": "Use with caution / reduced dose."}},
        ],
        "avoid": ["Routine cough suppressants that hide worsening illness", "Delaying referral if oxygen level is low"],
        "monitor": ["Oxygen saturation", "Respiratory rate", "Chest examination; chest X-ray if unclear"],
        "red_flags": ["Oxygen saturation below about 94%", "Fast breathing or breathlessness at rest",
                      "Confusion", "Bluish lips", "Unable to drink or eat"],
    },

    "UTI": {
        "summary": "Send a urine culture where possible. Choose the antibiotic by local resistance, and treat kidney infection more seriously than simple bladder infection.",
        "medicines": [
            {"name": "Nitrofurantoin", "purpose": "Uncomplicated bladder infection",
             "notes": "Not suitable for kidney infection (pyelonephritis).",
             "caution_if": {"kidney_disease": "Avoid if kidney function is reduced.",
                            "g6pd_deficiency": "Risk of haemolysis.",
                            "pregnancy": "Avoid near term; doctor to decide."}},
            {"name": "Fosfomycin", "purpose": "Uncomplicated bladder infection (alternative)", "notes": "Often a single-dose option.",
             "caution_if": {}},
            {"name": "Cotrimoxazole", "purpose": "Alternative if local resistance is low",
             "notes": "Check local resistance patterns.",
             "caution_if": {"sulfa_allergy": "Contraindicated in sulfa allergy.",
                            "pregnancy": "Avoid in first trimester and near term.",
                            "kidney_disease": "Dose adjustment and monitoring needed.",
                            "g6pd_deficiency": "Risk of haemolysis."}},
            {"name": "Ceftriaxone (injection)", "purpose": "Kidney infection or severe/complicated UTI", "notes": "Usually with hospital or supervised care.",
             "caution_if": {"penicillin_allergy": "Cross-reactivity possible; avoid if severe allergy history.",
                            "kidney_disease": "Check dose adjustment need."}},
            {"name": "Plenty of fluids + Paracetamol", "purpose": "Symptom relief", "notes": "Supportive care.",
             "caution_if": {"liver_disease": "Use with caution / reduced dose."}},
        ],
        "avoid": ["Empirical fluoroquinolones for simple UTI (resistance and side effects)",
                  "Treating without a urine test when it is possible to send one"],
        "monitor": ["Symptom improvement in 48-72 hours", "Urine culture result", "Recurrent infections need investigation"],
        "red_flags": ["Fever with flank or back pain", "Vomiting", "UTI in pregnancy", "Blood in urine",
                      "UTI in men or children (needs further evaluation)"],
    },

    "Gastroenteritis": {
        "summary": "Rehydration is the main treatment. Most cases are viral and do not need antibiotics.",
        "medicines": [
            {"name": "ORS (oral rehydration solution)", "purpose": "Replace fluid and salt losses", "notes": "Mainstay of treatment at any age.",
             "caution_if": {}},
            {"name": "Zinc", "purpose": "Shorter and milder diarrhoea in children", "notes": "Used in children under guidance.",
             "caution_if": {}},
            {"name": "Ondansetron", "purpose": "Severe vomiting that prevents ORS", "notes": "Short course if needed.",
             "caution_if": {"pregnancy": "Check suitability with the treating doctor.",
                            "liver_disease": "Dose adjustment may be needed."}},
            {"name": "Antibiotic (only if indicated)", "purpose": "Bloody diarrhoea, cholera, or severe bacterial illness",
             "notes": "Choice depends on the suspected organism and local guidelines.",
             "caution_if": {"pregnancy": "Choice of antibiotic needs care.",
                            "child": "Choice and dose depend on age/weight."}},
        ],
        "avoid": ["Routine antibiotics", "Loperamide or other anti-motility drugs in children or with bloody diarrhoea"],
        "monitor": ["Hydration: urine output, thirst, dry mouth", "Number of stools and vomits"],
        "red_flags": ["Signs of severe dehydration (very dry mouth, sunken eyes, no urine)", "Blood in stool",
                      "High fever", "Lethargy or drowsiness", "Diarrhoea lasting more than a few days"],
    },

    "Leptospirosis": {
        "summary": "Prompt clinician assessment is important after compatible exposure; treatment depends on severity and local guidance.",
        "medicines": [
            {"name": "Clinician-directed antibiotics", "purpose": "Treat suspected or confirmed infection",
             "notes": "Choice and route depend on severity; severe illness needs hospital care.",
             "caution_if": {"pregnancy": "Antibiotic choice requires clinician review.",
                            "penicillin_allergy": "Select an appropriate alternative if allergy is significant.",
                            "kidney_disease": "Review kidney function and dosing."}},
            {"name": "Supportive care", "purpose": "Maintain hydration and monitor organ function",
             "notes": "Medical supervision is important if kidney, liver, lung, or bleeding complications are suspected.",
             "caution_if": {"kidney_disease": "Fluid management requires clinician supervision.",
                            "liver_disease": "Monitor liver function."}},
        ],
        "avoid": ["Self-starting antibiotics", "Delaying urgent review when jaundice, reduced urine, or breathlessness occurs"],
        "monitor": ["Kidney and liver function", "Urine output", "Breathing and bleeding symptoms"],
        "red_flags": ["Jaundice", "Reduced urine output", "Breathlessness", "Confusion", "Bleeding"],
    },
}


def get_plan(disease, factors=()):
    """Return the medication plan for a disease, with per-medicine warnings for the patient's factors."""
    base = MEDICATIONS[disease]
    factors = set(factors)
    medicines = []
    for m in base["medicines"]:
        warnings = [msg for key, msg in m["caution_if"].items() if key in factors]
        medicines.append({**m, "warnings": warnings})
    return {"disease": disease, "summary": base["summary"], "medicines": medicines,
            "avoid": base["avoid"], "monitor": base["monitor"], "red_flags": base["red_flags"]}


def format_plan(plan):
    """Plain-text version for the command line."""
    lines = [f"  {plan['disease']}: {plan['summary']}", "  Medicines the doctor may consider:"]
    for m in plan["medicines"]:
        lines.append(f"   - {m['name']}: {m['purpose']}. {m['notes']}")
        for w in m["warnings"]:
            lines.append(f"       !! Caution: {w}")
    lines.append("  Avoid: " + "; ".join(plan["avoid"]))
    lines.append("  Monitor: " + "; ".join(plan["monitor"]))
    lines.append("  Urgent review if: " + "; ".join(plan["red_flags"]))
    return "\n".join(lines)


if __name__ == "__main__":
    print(format_plan(get_plan("Dengue", ["liver_disease"])))
