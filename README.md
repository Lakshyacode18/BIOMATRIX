# BioMatrix

Bio Matrix is a Streamlit clinical decision-support prototype using a synthetic patient-data generator, Naive Bayes model, and knowledge base. Medication guidance is disabled in the product UI by default.

In `knowledge.py`, disease priors and each feature's conditional probabilities are keyed by disease name, so changing disease order cannot silently remap probability values.

## Run locally

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit prints the local address, usually `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

1. Push this project to a GitHub repository.
2. In [Streamlit Community Cloud](https://share.streamlit.io/), choose **Create app** and connect that repository.
3. Select the branch you pushed and set the app file path to `app.py`.
4. Deploy. Streamlit Cloud installs the dependencies from `requirements.txt`.

Keep secrets out of GitHub. This prototype does not require secrets or external credentials.

The command-line prototype remains available with `python "main (1).py"`, or use `--demo` and `--evaluate` for its scripted example and synthetic evaluation.

All condition probabilities are learned from illustrative synthetic data. This is not a medical device, and its results must not be used as a diagnosis or prescription.

## Clinical review worksheet

Generate `review_sheet.csv` with the current disease priors and feature values:

```powershell
python generate_review_sheet.py
```

The worksheet leaves doctor values and sources blank for qualified review. The rows for paracetamol response, relative bradycardia, and disease priors include review prompts; do not replace the current illustrative values without qualified review and cited sources.

## Evaluate published cases

Use `evaluate_cases.py` to compare the model with published, de-identified cases. Do not enter patient identifiers. Record case findings and confirmed diagnoses from the source before looking at model output, and do not tune model values against cases that you report as evaluation results.

```powershell
python evaluate_cases.py --template
python evaluate_cases.py --features
python evaluate_cases.py cases.csv
```

The template's `EXAMPLE` rows are fabricated and are automatically excluded; delete or replace them. Case files use `case_id`, `source`, `confirmed_diagnosis`, and semicolon-separated `findings`. Prefix documented-absent findings with `-`, for example `fever; headache; -cough`. Unknown findings and contradictory entries are reported and skipped. Diagnoses outside the eight modeled conditions are reported but not scored.

The tool writes per-case results to `case_results.csv`. These results describe only the supplied cases and are not estimates of general clinical accuracy. Keep case datasets and results local unless you have permission to share them; CSV files are ignored by Git by default.