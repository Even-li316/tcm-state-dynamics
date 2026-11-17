#!/usr/bin/env python3
"""Smoke test: run the engine and check the three arms separate as documented."""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")

def main():
    env = dict(os.environ, TSIE_OUT=OUT)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "engine", "tcm_energy_sim.py")],
                       capture_output=True, text=True, env=env)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        return 1
    s = json.load(open(os.path.join(OUT, "summary.json"), encoding="utf-8"))
    ok = True
    for syn, v in s.items():
        g, n, b = v["对证方残余比"], v["不用药残余比"], v["误治残余比"]
        good = g < 0.5 < n < b
        ok &= good
        print(f"{'PASS' if good else 'FAIL'}  {syn:10s} matched={g:.3f} none={n:.3f} wrong={b:.3f}")
    print("smoke:", "OK" if ok else "FAILED")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
