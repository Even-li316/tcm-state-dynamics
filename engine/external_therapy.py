#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""External therapy operators: acupuncture, moxibustion, tuina, guasha, cupping.

The point of this module is the *contract*, not a result. An external therapy is
described by what was done (modality, points, technique) and how much of it
(duration, sessions, interval, and - for electroacupuncture - frequency and
intensity), and optionally by which of the six state axes the contributor claims
it moves and with what relative strength.

There is deliberately no built-in mapping from "ST36, 2 Hz, 20 min" to a state
vector. Any such mapping is a claim about physiology; it needs a source, and it
should be marked uncalibrated until someone fits it to data.

Usage:
    python engine/external_therapy.py contrib/external/EXAMPLE_electroacupuncture_st36.json
"""
import json
import os
import sys

import numpy as np

AXES = ["wind", "cold", "summerheat", "damp", "dryness", "fire"]


class Operator:
    """One external intervention, in the shape of schema/external_therapy.schema.json."""

    def __init__(self, doc):
        self.doc = doc
        self.modality = doc.get("modality")
        self.points = doc.get("points", [])
        self.region = doc.get("region", "")
        self.technique = doc.get("technique", "")
        self.params = doc.get("params", {})
        self.target_axes = doc.get("target_axes", [])
        self.evidence = doc.get("evidence", {})

    @classmethod
    def from_json(cls, path):
        with open(path, encoding="utf-8") as f:
            return cls(json.load(f))

    # ---- what the model needs -------------------------------------------
    def axis_vector(self):
        """Signed 6-vector: reduce = negative, increase = positive.

        Returns zeros when the contributor supplied no mapping.
        """
        v = np.zeros(len(AXES))
        for t in self.target_axes:
            axis = t.get("axis")
            if axis not in AXES:
                continue
            gain = float(t.get("gain", 1.0))
            v[AXES.index(axis)] += -gain if t.get("direction") == "reduce" else gain
        return v

    @property
    def calibrated(self):
        return bool(self.evidence.get("calibrated", False))

    @property
    def has_mapping(self):
        return len(self.target_axes) > 0

    def schedule(self, total_days=10.0):
        """Treatment windows as (start, end) pairs in day units."""
        n = int(self.params.get("sessions", 1))
        interval = float(self.params.get("interval_days", 1.0))
        dur = float(self.params.get("duration_min", 20.0)) / (60.0 * 24.0)  # minutes -> days
        return [(i * interval, i * interval + max(dur, 1e-3)) for i in range(n)]

    def describe(self):
        bits = [f"{self.modality}"]
        if self.points:
            bits.append(" ".join(self.points))
        if self.region:
            bits.append(self.region)
        if self.technique:
            bits.append(self.technique)
        p = self.params
        if "frequency_hz" in p:
            bits.append(f"{p['frequency_hz']} Hz")
        bits.append(f"{p.get('duration_min')} min x {p.get('sessions')} sessions")
        if p.get("interval_days"):
            bits.append(f"every {p['interval_days']} d")
        cal = "calibrated" if self.calibrated else "UNCALIBRATED"
        return " | ".join(bits) + f"  [{cal}]"


def combine(formula_vector, operator, weight=1.0):
    """Formula field plus an operator field, for use with simulate()'s Dnet.

    The operator's contribution is weight * axis_vector() during treatment
    windows only; outside windows the formula alone acts. This is a convenience
    for experiments, not a claim that the two effects simply add.
    """
    return np.asarray(formula_vector, dtype=float) + weight * operator.axis_vector()


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    op = Operator.from_json(argv[1])
    print(op.describe())
    print("axis vector:", dict(zip(AXES, np.round(op.axis_vector(), 2))))
    print("windows (days):", [(round(a, 3), round(b, 3)) for a, b in op.schedule()])
    if not op.has_mapping:
        print("\nNo target axes supplied: this operator contributes nothing to the state.")
        print("That is the normal state of a fresh contribution - the mapping is the work.")
    if not op.calibrated:
        print("\nMarked UNCALIBRATED: numbers above are placeholders or hand-set, not fitted.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
