# TSIE — TCM State-Dynamics Inference Engine

**Give it a syndrome state and a formula; it returns a state trajectory and an outcome class — not a paragraph of text.**

Most "AI + TCM" work today is text in, text out: an LLM writes a plausible-sounding prescription.
TSIE does something different and much smaller in scope: it keeps an explicit **state vector** over six
pathogenic axes (风 wind / 寒 cold / 暑 summer-heat / 湿 damp / 燥 dryness / 火 fire), applies a formula
as a **vector field with a release time-constant**, and integrates the state forward in time.

Because it is a dynamical system, it can answer questions a language model cannot: *does this state
converge, persist, or get worse — and when?*

![trajectory demo](figures/demo.gif)

## What this is / is not

| It **is** | It is **not** |
|---|---|
| A ~300-line, single-file, auditable dynamical model | A TCM large language model |
| A rollout: state → trajectory → outcome class | A knowledge graph or a formula search engine |
| Parameters written out in plain Python, every step traceable | A calibrated clinical predictor |
| A reference implementation to argue about | A medical device or a dosing tool |

## Quick start

```bash
pip install -r requirements.txt

# 1) run the engine: writes out/*.png + out/summary.json
python engine/tcm_energy_sim.py

# 2) open the interactive demo (single file, no server, no build)
open demo/tcm_engine_demo.html
```

Python 3.9+, `numpy`, `matplotlib`. No GPU, no model weights, no downloads.

## The model in five lines

1. **State**: `E(t) ∈ R^6` — deviations on wind / cold / summer-heat / damp / dryness / fire; `|E|` is the
   degree of imbalance, zero = balanced.
2. **Herb → vector**: each herb's four-nature / five-flavour properties are mapped to a 6-axis vector by
   explicit rules (`drug_vector()`), scaled by a potency factor.
3. **Formula → net field**: weighted sum with classic roles 君 1.0 / 臣 0.6 / 佐 0.4 / 使 0.25.
4. **Dosage form = time constant**: 汤 decoction 1.0 / 散 powder 1.5 / 丹 3.0 / 丸 pill 4.0 / 膏 paste 6.0 —
   the classical dosage forms already encode a release rate.
5. **Dynamics**: `dE/dt = −k0·E + M·E + α·D_net·pulse(t)`, plus four gating rules:
   `R1` stop when the illness is gone (dose is gated by remaining illness), `R2` wrong treatment amplifies
   the pathogenic dynamic, `R3` cold-bitter herbs given to a cold-damp state aggravate it,
   `R4` pungent-warm herbs given to a blazing summer-heat/fire state add fuel.

Everything above lives in `engine/tcm_energy_sim.py` and can be read in one sitting.

## Demo results

Residual imbalance after 10 doses, normalised to the pre-treatment state (`1.0` = unchanged):

| Syndrome | Matched formula | No treatment | Wrong formula |
|---|---:|---:|---:|
| 风寒表实 (wind-cold, exterior excess) | **0.04** | 0.77 | 1.58 |
| 暑湿困脾 (summer-heat dampness) | **0.33** | 1.01 | 2.58 |
| 阴虚火旺 (yin deficiency, fire) | **0.01** | 1.34 | 3.32 |
| 寒厥·少阴 (cold reversal, lesser yin) | **0.07** | 0.88 | 2.19 |

The three arms separate cleanly. **That is a statement about internal consistency of the rules, not
about clinical validity** — see the next section.

## Honest limits (read before citing this)

- **Every coefficient is hand-set** from qualitative textbook rules (four natures, five flavours, channel
  entered, trend, pathogenesis transmission, dosage-form constants). None is fitted and none is measured.
- **All numbers are dimensionless** relative quantities. They are not µV, not mmHg, not a probability.
- **Coverage is deliberately tiny**: 6 axes, 43 herbs, 4 syndromes. This is a mechanism demonstration,
  not a materia medica.
- **The clean three-way separation is by construction.** The rules were written to produce it. A model that
  cannot be wrong is not evidence — which is why the roadmap below is about fitting and falsification.
- **Not a medical device.** No diagnosis, no prescription, no dose advice. Do not use it on patients.

## Repo layout

```
engine/tcm_energy_sim.py   the whole model + figure generation
demo/tcm_engine_demo.html  interactive single-file demo (choose state → formula → watch trajectory)
figures/                   generated figures + this README's GIF
docs/model.md              equations, symbols, rule table
tests/smoke.py             one-command sanity check
out/                       engine output (generated on first run)
```

## Roadmap

1. **Fit the coefficients** to retrospective case series (`k0`, `M`, `α` from observed "how many visits
   until resolution") — until then the numbers stay dimensionless and the model stays a demo.
2. **Reverse mode**: give a target state, search the operator space for formula combinations; judge it by
   whether it recovers known formula–syndrome pairs.
3. **Extend the herb table** from 43 to a few hundred entries, each with a cited source.
4. **Add external-therapy operators** (acupuncture, moxibustion, tuina) as parametric inputs with physical
   units (frequency, intensity, duration) rather than qualitative labels.
5. **Falsification harness**: state in advance which case must fail, then run it.

## License

MIT. See `LICENSE`.

Contributions that make a coefficient *measurable* are worth more than contributions that add syndromes.
