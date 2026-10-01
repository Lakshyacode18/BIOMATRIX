"""Compatibility entry point. Start the canonical site with streamlit run app.py."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("app.py")))
