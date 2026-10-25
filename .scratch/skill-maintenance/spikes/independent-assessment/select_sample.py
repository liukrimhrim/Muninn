#!/usr/bin/env python3
"""Reproduce blind inputs and isolated reference labels from a pinned release.

No model calls. No label-dependent sampling. Do not open source/ or the
withheld-reference file until the assessor output is frozen.
"""

import copy
import hashlib
import json
from pathlib import Path
import re
import urllib.request
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parent
COMMIT = "5157c69f914e8c581045c03e98f96398d40a91b8"
BASE = f"https://raw.githubusercontent.com/myrosia/semeval-2013-task7/{COMMIT}"
SOURCE_HASHES = {
    "LICENSE": "f257601c4d54b4748016ce74f671ae6be0dbb8e6b9face8f61f2d68019bee9fb",
    "README.md": "852ce1886bf902fe0ed8f3dfd0169b758d74078d12dc87a357e48fbaac1db140",
    "semeval-5way.zip": "57c14e5c260d8cfd774f3fb954985d94bcfa3407029bfe585179650b907dbf9b",
}
SEED = "mem-graph-independent-assessment-v1"
PREFIX = "sciEntsBank/test-unseen-questions/Extra/"
VISUAL_CUES = re.compile(r"\b(diagram|picture|table|graph|shown|below|above|drawing|chart|illustration|figure|image|photograph)\b", re.I)
ATTRIBUTION = {
    "dataset": "SEMEVAL 2013 Task 7 Dataset, SCIENTSBANK Extra",
    "corpus_creators": ["Rodney Nielsen", "Myroslava Dzikovska"],
    "repository": "https://github.com/myrosia/semeval-2013-task7",
    "commit": COMMIT,
    "citation": "Dzikovska et al. (2013). SemEval-2013 Task 7: The Joint Student Response Analysis and 8th Recognizing Textual Entailment Challenge. ACL, pp. 263–274.",
    "paper": "https://aclanthology.org/S13-2045/",
    "license": "CC-BY-SA-3.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/3.0/",
    "license_copy": "source/LICENSE",
    "changes": "Selected records; parsed XML into JSON; withheld response and prior-assumption annotations. Released wording, spelling and facet relations are unchanged.",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def rank(value):
    return digest((SEED + "|" + value).encode("utf-8"))


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def fetch_sources():
    source = ROOT / "source"
    source.mkdir(exist_ok=True)
    for name, expected in SOURCE_HASHES.items():
        path = source / name
        if not path.exists():
            with urllib.request.urlopen(f"{BASE}/{name}", timeout=30) as response:
                path.write_bytes(response.read())
        assert digest(path.read_bytes()) == expected, f"Source hash mismatch: {name}"


def make_pool(archive):
    """Project only input fields; annotation values cannot affect selection."""
    pool = []
    excluded = []
    for path in sorted(archive.namelist()):
        if not (path.startswith(PREFIX) and path.endswith(".xml")):
            continue
        raw = archive.read(path)
        root = ET.fromstring(raw)
        question = root.findtext("questionText")
        refs = root.findall("./referenceAnswers/referenceAnswer")
        reasons = []
        if "fruit" in question.lower():
            reasons.append("fruit-topic excluded after assessor exposure to labeled paper example")
        if VISUAL_CUES.search(question):
            reasons.append("question contains explicit cue for potentially unavailable visual/context material")
        if len(refs) != 1:
            reasons.append("requires multiple-reference-answer adjudication")
        if reasons:
            excluded.append({"question_id": root.get("id"), "source_path": path, "reasons": reasons})
            continue
        ref = refs[0]
        facets = []
        for facet in ref.findall("./facets/facet"):
            attrs = dict(facet.attrib)
            attrs.pop("isAssumed", None)
            facets.append(attrs)
        pool.append({
            "question_id": root.get("id"),
            "module": root.get("module"),
            "source_path": path,
            "question": question,
            "reference_id": ref.get("id"),
            "reference_answer": ref.get("text"),
            "reference_tokens": [{"id": token.get("id"), "text": token.text}
                                 for token in ref.findall("./tokens/token")],
            "facets": facets,
            "responses": [{"response_id": answer.get("id"), "response": answer.get("answerText")}
                          for answer in root.findall("./studentAnswers/studentAnswer")],
        })
    return pool, excluded


def choose(pool):
    selected = []
    used_modules = set()
    for question in sorted(pool, key=lambda q: (rank(q["question_id"]), q["question_id"])):
        if question["module"] in used_modules:
            continue
        record = copy.deepcopy(question)
        record["responses"] = sorted(record["responses"], key=lambda s: (rank(s["response_id"]), s["response_id"]))[:3]
        assert len(record["responses"]) == 3
        record["context_facets"] = record["facets"]
        record["facets"] = sorted(record["facets"], key=lambda f: (rank(record["question_id"] + "|" + f["id"]), f["id"]))[:4]
        assert len(record["facets"]) == 4
        selected.append(record)
        used_modules.add(record["module"])
        if len(selected) == 4:
            break
    assert len(selected) == 4
    return selected


def main():
    fetch_sources()
    with zipfile.ZipFile(ROOT / "source/semeval-5way.zip") as archive:
        pool, excluded = make_pool(archive)
        selected = choose(pool)
        blind = {
            "schema_version": 1,
            "attribution": ATTRIBUTION,
            "selection_seed": SEED,
            "task": "This is a selected-facet comparison, not a full grade of any answer. For every response, assess only the four entries in facets: does the response demonstrate that relationship, contradict it, not show it, or cannot it be judged from the provided context? context_facets contains all original reference facets solely to resolve linked propositions. Interpret facet terms in the full reference answer. Do not infer durable mastery or the cause of an omission.",
            "text_policy": "Exact XML-decoded released text. No spelling correction, paraphrase, source repair, or generated facet gloss. Facet isAssumed attributes and all student annotations are withheld.",
            "questions": selected,
        }
        withheld = {
            "schema_version": 1,
            "attribution": ATTRIBUTION,
            "blind_inputs_sha256": digest(encode(blind)),
            "notice": "Human source annotations only. Do not inspect until assessment and comparison mapping are frozen. Raw categories are preserved without an assessor output or imposed mapping.",
            "questions": [],
        }
        manifest_sources = []
        decision_count = 0
        for question in selected:
            path = question["source_path"]
            raw = archive.read(path)
            root = ET.fromstring(raw)
            ref = root.find("./referenceAnswers/referenceAnswer")
            core_path = path.replace("/Extra/", "/Core/")
            core_raw = archive.read(core_path)
            core = ET.fromstring(core_raw)
            core_answers = {s.get("id"): s.text for s in core.findall("./studentAnswers/studentAnswer")}
            assert core.find("./referenceAnswers/referenceAnswer").text == question["reference_answer"]
            source_answers = {s.get("id"): s for s in root.findall("./studentAnswers/studentAnswer")}
            ids = {f["id"] for f in question["facets"]}
            references = []
            for response in question["responses"]:
                assert response["response"] == core_answers[response["response_id"]]
                source_answer = source_answers[response["response_id"]]
                all_labels = [dict(x.attrib) for x in source_answer.findall("facetEntailment")]
                assert {x["facetID"] for x in all_labels} == {f["id"] for f in question["context_facets"]}
                labels = [x for x in all_labels if x["facetID"] in ids]
                assert len(labels) == len(ids)
                references.append({
                    "response_id": response["response_id"],
                    "source_answer_accuracy": source_answer.get("accuracy"),
                    "facet_annotations": labels,
                })
                decision_count += len(ids)
            withheld["questions"].append({
                "question_id": question["question_id"],
                "source_path": path,
                "source_xml_sha256": digest(raw),
                "reference_facet_annotations": [dict(f.attrib) for f in ref.findall("./facets/facet")],
                "responses": references,
            })
            manifest_sources.extend([
                {"archive_member": path, "sha256": digest(raw)},
                {"archive_member": core_path, "sha256": digest(core_raw)},
            ])

        # Annotation erasure check: every classification and prior-assumption
        # attribute is removed in memory before re-projecting and re-selecting.
        # This must leave the entire blind artifact unchanged.
        class ErasedArchive:
            def namelist(self):
                return archive.namelist()

            def read(self, path):
                root = ET.fromstring(archive.read(path))
                for element in root.iter():
                    for key in ("label", "accuracy", "isAssumed"):
                        element.attrib.pop(key, None)
                return ET.tostring(root, encoding="utf-8")

        erased_pool, erased_excluded = make_pool(ErasedArchive())
        assert choose(erased_pool) == selected
        assert erased_excluded == excluded
        (ROOT / "blind-inputs.json").write_bytes(encode(blind))
        (ROOT / "withheld-reference.json").write_bytes(encode(withheld))
        manifest = {
            "attribution": ATTRIBUTION,
            "source_file_sha256": SOURCE_HASHES,
            "selected_xml_members": manifest_sources,
            "seed": SEED,
            "pool": PREFIX,
            "selection_rule": "Exclude fruit-topic exposure, visual-context cue matches and multiple-reference questions; ascending SHA256(seed + '|' + question_id), first four distinct modules; within each, ascending SHA256(seed + '|' + response_id), first three responses. Within each selected question, ascending SHA256(seed + '|' + question_id + '|' + facet_id), first four facets. Ties break by exact ID. Retain all original reference facets as blind context only.",
            "visual_context_regex": VISUAL_CUES.pattern,
            "excluded_questions": excluded,
            "questions": len(selected),
            "responses": sum(len(q["responses"]) for q in selected),
            "reference_facets": sum(len(q["facets"]) for q in selected),
            "context_reference_facets": sum(len(q["context_facets"]) for q in selected),
            "facet_decisions": decision_count,
            "annotation_erasure_invariance_check": "passed",
            "selected_core_extra_text_equality_check": "passed",
            "blind_inputs_sha256": digest(encode(blind)),
            "withheld_reference_sha256": digest(encode(withheld)),
        }
        (ROOT / "source-manifest.json").write_bytes(encode(manifest))
        print(json.dumps({k: manifest[k] for k in (
            "questions", "responses", "reference_facets", "facet_decisions",
            "blind_inputs_sha256", "withheld_reference_sha256",
            "annotation_erasure_invariance_check", "selected_core_extra_text_equality_check",
        )}, indent=2))


if __name__ == "__main__":
    main()
