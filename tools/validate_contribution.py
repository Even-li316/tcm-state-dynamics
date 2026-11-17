#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate contributed records against the schemas, plus a privacy lint.

Usage:
    python tools/validate_contribution.py            # check everything under contrib/
    python tools/validate_contribution.py path.json  # check one file

Exit code 0 = all good, 1 = at least one failure (CI uses this).
"""
import json
import os
import re
import sys

try:
    import jsonschema
except ImportError:
    print("pip install jsonschema")
    sys.exit(2)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMAS = {
    "cases": os.path.join(ROOT, "schema", "case_record.schema.json"),
    "external": os.path.join(ROOT, "schema", "external_therapy.schema.json"),
}

# --- privacy lint -----------------------------------------------------------
# Anything matching these is refused outright: contributions must be
# de-identified at the source, not scrubbed here.
FORBIDDEN_KEYS = {
    "name", "姓名", "patient_name", "id", "id_card", "身份证", "phone", "tel",
    "telephone", "手机", "手机号", "address", "住址", "mrn", "住院号", "病历号",
    "hospital_id", "就诊卡号",
}
PATTERNS = [
    (re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), "possible CN mobile number"),
    (re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)"), "possible CN ID number"),
    (re.compile(r"\b(19|20)\d{2}[-/年](0?[1-9]|1[0-2])[-/月](0?[1-9]|[12]\d|3[01])"), "exact date"),
]


def walk_keys(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_keys(v, f"{path}.{k}" if path else k)
            yield k, path
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_keys(v, f"{path}[{i}]")


def lint(doc):
    problems = []
    for k, path in walk_keys(doc):
        # "name" is legitimate for formulas and sources; it is only a privacy
        # problem in patient-level containers.
        if path.startswith(("formula", "source")):
            continue
        if k.lower() in FORBIDDEN_KEYS:
            problems.append(f"forbidden field '{path}.{k}' — de-identify at source")
    text = json.dumps(doc, ensure_ascii=False)
    for rx, label in PATTERNS:
        m = rx.search(text)
        if m:
            problems.append(f"{label}: '{m.group(0)}' — remove or coarsen")
    return problems


def validate_file(path, kind):
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    schema_path = SCHEMAS[kind]
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    errs = []
    try:
        jsonschema.validate(doc, schema)
    except jsonschema.ValidationError as e:
        loc = "/".join(str(p) for p in e.absolute_path) or "(root)"
        errs.append(f"schema: {loc}: {e.message}")
    except jsonschema.SchemaError as e:
        errs.append(f"schema itself is invalid: {e.message}")
    errs += lint(doc)
    return errs


def main(argv):
    targets = []
    if len(argv) > 1:
        for p in argv[1:]:
            kind = "external" if "external" in p else "cases"
            targets.append((p, kind))
    else:
        for kind, sub in (("cases", "cases"), ("external", "external")):
            d = os.path.join(ROOT, "contrib", sub)
            if os.path.isdir(d):
                for fn in sorted(os.listdir(d)):
                    if fn.endswith(".json"):
                        targets.append((os.path.join(d, fn), kind))
    if not targets:
        print("no contribution files found")
        return 0

    bad = 0
    for path, kind in targets:
        rel = os.path.relpath(path, ROOT)
        try:
            errs = validate_file(path, kind)
        except Exception as e:
            errs = [f"unreadable: {e}"]
        if errs:
            bad += 1
            print(f"FAIL  {rel}")
            for e in errs:
                print(f"      - {e}")
        else:
            print(f"PASS  {rel}")
    print(f"\n{len(targets) - bad}/{len(targets)} files valid")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
