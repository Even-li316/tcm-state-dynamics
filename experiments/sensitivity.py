#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parameter sensitivity of the three-arm separation.

Perturbs the free constants multiplicatively (lognormal, sigma configurable) and
records how often the documented ordering  matched < none < wrong  survives.

Output: experiments/sensitivity.json + figures/fig4_sensitivity.png
Usage: python experiments/sensitivity.py [n_draws] [sigma]
"""
import json, os, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
import tcm_energy_sim as E  # noqa: E402


def evaluate(cases, traj_kwargs=None):
    out = {}
    for name, c in cases.items():
        e0 = np.array(c["E"], dtype=float)
        dg, tg, _, wg = E.net_formula(c["good"])
        db, tb, _, wb = E.net_formula(c["bad"])
        rg = np.linalg.norm(E.simulate(e0, dg, tg, warm=wg)[-1]) / np.linalg.norm(e0)
        rb = np.linalg.norm(E.simulate(e0, db, tb, warm=wb)[-1]) / np.linalg.norm(e0)
        rn = np.linalg.norm(E.simulate(e0, np.zeros(6), 0.0, warm=0.0)[-1]) / np.linalg.norm(e0)
        out[name] = (float(rg), float(rn), float(rb))
    return out


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    sigma = float(sys.argv[2]) if len(sys.argv) > 2 else 0.2
    rng = np.random.default_rng(20261117)

    base_k0, base_M, base_alpha = E.K0_BASE, E.M_SCALE, E.ALPHA
    base_tau = dict(E.DOSE_TAU)

    base = evaluate(E.CASES)
    rows = []
    for i in range(n):
        E.K0_BASE = base_k0 * rng.lognormal(0, sigma)
        E.M_SCALE = base_M * rng.lognormal(0, sigma)
        E.ALPHA = base_alpha * rng.lognormal(0, sigma)
        E.DOSE_TAU = {k: v * rng.lognormal(0, sigma) for k, v in base_tau.items()}
        r = evaluate(E.CASES)
        ok = all(v[0] < v[1] < v[2] for v in r.values())
        strict = all(v[0] < 0.5 < v[1] < v[2] for v in r.values())
        rows.append({"i": i, "order_ok": bool(ok), "strict_ok": bool(strict),
                     **{k: v for k, v in r.items()}})
    E.K0_BASE, E.M_SCALE, E.ALPHA, E.DOSE_TAU = base_k0, base_M, base_alpha, base_tau

    order = np.mean([r["order_ok"] for r in rows])
    strict = np.mean([r["strict_ok"] for r in rows])
    per_syn = {}
    for syn in base:
        per_syn[syn] = float(np.mean([r[syn][0] < r[syn][1] < r[syn][2] for r in rows]))
    matched = {syn: [r[syn][0] for r in rows] for syn in base}

    summary = {"n_draws": n, "sigma": sigma, "baseline": base,
               "order_preserved": round(float(order), 3),
               "strict_preserved": round(float(strict), 3),
               "per_syndrome_order": {k: round(v, 3) for k, v in per_syn.items()},
               "matched_residual_p5_p95": {k: [round(float(np.percentile(v, 5)), 3),
                                               round(float(np.percentile(v, 95)), 3)]
                                           for k, v in matched.items()}}
    os.makedirs(os.path.join(ROOT, "experiments"), exist_ok=True)
    json.dump(summary, open(os.path.join(ROOT, "experiments", "sensitivity.json"), "w"),
              ensure_ascii=False, indent=1)

    # figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]:
        if os.path.exists(f):
            font_manager.fontManager.addfont(f)
            plt.rcParams["font.sans-serif"] = [font_manager.FontProperties(fname=f).get_name()]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.2))
    names = list(base.keys())
    ax[0].boxplot([matched[s] for s in names], tick_labels=names, widths=0.55,
                  medianprops=dict(color="#d1495b"))
    ax[0].axhline(0.5, color="k", ls="--", lw=1, label="0.5 threshold")
    ax[0].set_ylabel("matched-formula residual  |E(T)|/|E(0)|")
    ax[0].set_title(f"(a) sensitivity of the matched arm (n={n}, sigma={sigma})", fontsize=10)
    ax[0].legend(fontsize=8)
    ax[0].tick_params(labelsize=8)
    bars = [per_syn[s] for s in names]
    ax[1].bar(range(len(names)), bars, color="#00798c")
    ax[1].set_xticks(range(len(names)))
    ax[1].set_xticklabels(names, fontsize=8)
    ax[1].set_ylim(0, 1.02)
    ax[1].axhline(order, color="#d1495b", ls="--", lw=1, label=f"all-syndrome {order:.0%}")
    ax[1].set_ylabel("fraction of draws keeping  matched < none < wrong")
    ax[1].set_title("(b) ordering survival per syndrome", fontsize=10)
    ax[1].legend(fontsize=8)
    os.makedirs(os.path.join(ROOT, "figures"), exist_ok=True)
    fig.tight_layout()
    fig.savefig(os.path.join(ROOT, "figures", "fig4_sensitivity.png"), dpi=180)
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
