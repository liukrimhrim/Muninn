"""Embed the throwaway pure model in one locally openable HTML artifact."""
from pathlib import Path

here = Path(__file__).resolve().parent
model = (here / "c-model.mjs").read_text().replace("export const CModel", "const CModel", 1)
shell = (here / "c-shell.html").read_text()
(here / "c-walkthrough.html").write_text(shell.replace("/* MODEL_SOURCE */", model))
print("Generated c-walkthrough.html (authored examples only; no server or persistence).")
