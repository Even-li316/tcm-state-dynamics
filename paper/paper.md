---
title: "A Six-Axis State-Space Model of Syndrome–Formula Dynamics in Traditional Chinese Medicine: Mechanism, Reference Implementation, and Explicit Non-Claims"
author: "Yafeng Li (Even Li)"
date: "2026-11-17"
abstract: |
  Most computational work on Traditional Chinese Medicine (TCM) is text-in, text-out: a language model
  produces a plausible diagnosis and prescription, and nothing in the output can be rolled forward in time.
  We describe a deliberately small alternative — a six-axis state-space model in which a syndrome is a
  vector of deviations over wind, cold, summer-heat, damp, dryness and fire, a formula is a vector field
  with a dosage-form-dependent release time constant, and the clinical course is the integral of that field
  under four qualitative gating rules. The complete model is ~300 lines of readable Python with no learned
  parameters. On four classical syndromes it reproduces the intended three-way separation between a matched
  formula, no treatment, and a wrong formula; that separation survives ±20% multiplicative perturbation of
  all five free constants in 90.7% of 300 draws. We are explicit that this is a statement about internal
  consistency, not about clinical validity: every coefficient is hand-set from qualitative rules, all
  quantities are dimensionless, and nothing here has been fitted to outcomes. The contribution is the
  formalisation and the falsification agenda, not a result.
---

*Preprint. DOI: [10.5281/zenodo.24296397](https://doi.org/10.5281/zenodo.24296397) · Code: [github.com/Even-li316/tcm-state-dynamics](https://github.com/Even-li316/tcm-state-dynamics)*

# 1. Introduction

Computational TCM has converged on one architecture: a large language model (LLM), optionally augmented
with retrieval over classical texts or a knowledge graph, which maps a patient description to a syndrome
label and a prescription. This is useful for look-up and for drafting, but it has a structural limitation:
the output is text. A text cannot be integrated forward. It cannot say whether the state will resolve in
three days or persist for three weeks, nor what happens to the state if the formula is wrong.

Clinical reasoning, however, is largely about that forward question. The classical literature is explicit
about direction, rate and sequence — "one dose and the exterior is released", "if the pulse does not change,
the disease is entering the interior" — and the classical dosage forms (decoction, powder, pill, paste)
encode release rates well enough that they behave as time constants in practice.

We therefore formalise a much smaller object than a model of a patient: a **state vector plus operators**.
The claim we defend is narrow:

> Given a syndrome state and a formula, a hand-specified dynamical system can generate a trajectory and an
> outcome class that is auditable line by line, and whose failure modes can be stated in advance.

We do not claim diagnostic accuracy, we do not claim clinical benefit, and we do not claim that the
coefficients are correct. Section 6 makes the non-claims as explicit as the claims; Section 7 states what
would falsify the approach.

# 2. Model

## 2.1 State

$$E(t) = (E_{\text{wind}}, E_{\text{cold}}, E_{\text{summer}}, E_{\text{damp}}, E_{\text{dry}}, E_{\text{fire}}) \in \mathbb{R}^6$$

$E_i > 0$ denotes excess of that pathogenic factor and $E_i < 0$ deficiency; $|E|$ is the scalar "degree of
imbalance" used throughout. Balance is $E = 0$. Six axes were chosen because the six-pathogenic-factor
vocabulary is the coarsest one that still distinguishes clinically distinct courses; it is not claimed to be
a basis, and no attempt is made to represent organ localisation (藏象) or the eight-principle pairs.

## 2.2 Herbs as vectors

Each herb in the table (43 entries) carries five qualitative attributes known from the classical materia
medica: four-nature (寒/凉/平/温/热), five-flavour (辛/甘/苦/酸/咸/淡/涩), channels entered, tendency
(升/降/浮/沉), and a potency scalar. A deterministic mapping produces the six-axis vector, for example

$$v_{\text{cold}} = -0.45 \cdot \max(q,0), \qquad v_{\text{fire}} = +0.45 \cdot \min(q,0)$$

with $q \in \{-2,-1,0,1,2\}$ for 寒/凉/平/温/热, and analogous indicators for pungency (wind), bitterness,
blandness and aromatics (damp), and salt/sweet-cold (dryness). The mapping is *the* modelling choice in this
paper: it is a claim that four-nature and five-flavour are, functionally, a vector of first-order effects on
six state axes. Every coefficient is visible in `drug_vector()` and can be replaced.

## 2.3 Formulas as weighted fields

The net field is the role-weighted sum

$$D_{\text{net}} = \sum_h w_{\text{role}(h)} \cdot \text{potency}(h) \cdot v(h), \qquad
w: \text{jun } 1.0,\ \text{chen } 0.6,\ \text{zuo } 0.4,\ \text{shi } 0.25$$

together with a tonic (扶正) term that raises the self-healing coefficient, and a scalar `warm` used by
rule R4 below.

## 2.4 Dosage form as a release time constant

$$\text{pulse}(t) = \sum_{k:\, k T_{\text{dose}} \le t} \exp\!\left(-\frac{t - k T_{\text{dose}}}{\tau}\right),
\qquad \tau: \text{decoction }1.0,\ \text{powder }1.5,\ \text{pill }4.0,\ \text{paste }6.0,\ \text{pellet }3.0$$

This is the least speculative part of the model: it states only that classical dosage forms differ in onset
and persistence by a factor of a few, in the direction the tradition asserts.

## 2.5 Dynamics and gating rules

$$\frac{dE}{dt} = -k_0 E + M E + \alpha\, D_{\text{eff}}\, \text{pulse}(t)$$

with $k_0 = (0.05 + \text{tonic})$ the self-healing rate, $M$ a sparse 6×6 pathogenesis-transmission matrix
(seven hand-set entries, e.g. wind→fire 0.10, damp→cold 0.06), and $\alpha = 1.1$ the drug gain. Four
qualitative rules modify the field at each step:

| Rule | Statement | Implementation |
|---|---|---|
| R1 | stop when the illness is gone | per-axis dose gated by $\min(1, E/0.15)$ |
| R2 | wrong treatment amplifies the disease | $M \times 1.8$, $k_0 \times 0.5$ when $D_{\text{net}}\!\cdot\!E_0 > 0$ |
| R3 | cold-bitter herbs aggravate cold-damp | clearing term leaks into cold and damp axes |
| R4 | pungent-warm herbs add fuel to blazing fire | fire axis incremented by `warm` × pulse when summer+fire > 0.3 |

Integration is explicit Euler with $dt = 0.02$ over $T = 10$ (one dose per unit time, ten doses).

# 3. Implementation

The model, the four syndromes, the drug table and all figures are produced by one file
(`engine/tcm_energy_sim.py`, ~300 lines, NumPy and Matplotlib only). An interactive single-file HTML demo
(`demo/tcm_engine_demo.html`) lets a reader choose a syndrome, a formula, a dosage form and a number of
doses, and watch the radar plot and trajectory evolve; it requires no server and no build step. A smoke
test regenerates the results and asserts the ordering reported below. Everything is MIT-licensed.

# 4. Results

## 4.1 Three-arm separation

Residual imbalance $|E(T)|/|E(0)|$ after ten doses, four classical syndromes, three arms each:

| Syndrome | Matched formula | No treatment | Wrong formula |
|---|---:|---:|---:|
| wind-cold, exterior excess (风寒表实, Mahuang Tang) | 0.037 | 0.765 | 1.582 |
| summer-heat with dampness (暑湿困脾, Huoxiang Zhengqi) | 0.333 | 1.008 | 2.584 |
| yin deficiency with fire (阴虚火旺) | 0.010 | 1.340 | 3.316 |
| cold reversal, lesser yin (寒厥, Sini Tang) | 0.069 | 0.879 | 2.188 |

![**Figure 1.** Six-axis state for the wind-cold exterior-excess syndrome: balanced baseline (green), pathological state (red), state after ten doses of the matched formula (blue), and the formula's own net vector (orange). The matched formula pushes every axis back toward the origin.](figures/fig1_six_qi_radar.png)

The trajectory view makes the mechanism visible: the matched formula drives all six components toward zero,
the wrong formula both fails to reduce the dominant axes and, through R2, accelerates transmission into
adjacent axes.

![**Figure 2.** Left: scalar imbalance |E| over time for the matched formula, no treatment, and the wrong formula. Right: the six components separately under the matched formula.](figures/fig2_trajectories.png)

## 4.2 Robustness of the separation

Because the separation could be an artefact of a lucky parameter set, we perturbed all five free constants
($k_0$ baseline, $M$ scale, $\alpha$, and the five $\tau$ values) multiplicatively by
$\text{lognormal}(0, 0.2)$ and re-ran 300 draws (seed 20261117):

| Quantity | Value |
|---|---:|
| ordering `matched < none < wrong` preserved, all four syndromes | **90.7%** |
| additionally `matched < 0.5`, all four syndromes | 48.3% |
| per-syndrome ordering survival | 1.00 / 0.91 / 1.00 / 1.00 |
| matched residual 5th–95th percentile, summer-heat+damp | 0.27 – 1.17 |

![**Figure 3.** Parameter sensitivity (300 draws, lognormal σ = 0.2 on all five free constants). Left: distribution of the matched-arm residual, with the arbitrary 0.5 threshold dashed. Right: fraction of draws preserving the three-arm ordering, per syndrome.](figures/fig4_sensitivity.png)

Two honest readings. First, the qualitative ordering is not fragile — it is a property of the rule structure
rather than of the specific numbers. Second, the 0.5 cut-off *is* arbitrary: for the summer-heat+damp
syndrome the matched arm crosses 1.0 in the upper tail, meaning the same rules can produce "matched formula
does no better than nothing" when the gain is low and the transmission matrix is high. That is a feature of
the formalisation, not a bug we hid.

# 5. Relation to existing work

Three families of prior work are relevant, and this model is a deliberate departure from all of them.
LLM-based TCM assistants produce text and are evaluated on question-answering or prescription-matching
accuracy. Knowledge graphs and formula-retrieval systems encode static associations between symptoms,
patterns and formulas. Physiological or device-based TCM research measures the body (tongue imaging, pulse
waveform) and classifies. None of the three produces a state trajectory: the first cannot, because text has
no dynamics; the second does not, because a graph has no time axis; the third measures an input rather than
a course.

Conversely, the mainstream literature that *does* model disease dynamics — compartmental epidemic models,
pharmacokinetic models — operates on quantities with units, fitted to data. Our model is at neither extreme:
it has a time axis and operators, but dimensionless states and hand-set coefficients. Its nearest formal
relatives are qualitative or signed-graph dynamical models in systems biology, and it should be read in that
spirit.

# 6. Non-claims

We state these as plainly as the claims, because the failure mode of this genre is a demonstration mistaken
for evidence.

1. **No coefficient is measured or fitted.** $k_0$, $M$, $\alpha$, the $\tau$ values and every mapping
   coefficient in §2.2 were chosen by hand to reproduce qualitative classical expectations.
2. **All quantities are dimensionless.** They are not probabilities, not concentrations, not volts.
3. **The clean separation is by construction.** The rules were written to produce it. A model that cannot
   be wrong cannot be evidence; §4.2 is a robustness check on parameters, not a validation.
4. **Coverage is minimal**: six axes, 43 herbs, four syndromes. This is a mechanism demonstration.
5. **No patient data were used**, and the model is not a medical device: it does not diagnose, does not
   prescribe, and must not be used for dosing.

# 7. Falsification agenda

The model becomes scientific when it can lose. Two tests are specified in advance:

1. **Fitting test.** Estimate $k_0$, $M$ and $\alpha$ from retrospective case series with a well-defined
   endpoint (e.g. number of visits to resolution), then predict that endpoint out of sample. Pre-registered
   success criterion: out-of-sample rank correlation above 0.3 with a bootstrap CI excluding zero. Under
   this criterion the current parameters would almost certainly fail, which is the point.
2. **Reversal test.** Given a target state, search the operator space for formula combinations. Judge the
   search by whether it recovers formula–syndrome pairs that clinicians actually use, not by whether it
   finds *some* combination that lowers $|E|$.

A third, cheaper test is available immediately: publish the parameter table and invite readers to find a
syndrome–formula pair that the model orders incorrectly. Any such pair is a falsification of the mapping
rules as stated.

# 8. Reproducibility

```
git clone https://github.com/Even-li316/tcm-state-dynamics
pip install -r requirements.txt
python engine/tcm_energy_sim.py        # regenerates Table 1 and Figs. 1-3
python experiments/sensitivity.py      # regenerates §4.2 and Fig. 4
python tests/smoke.py                  # asserts the ordering in Table 1
```

The sensitivity analysis is seeded (20261117); Figure 4 and the percentages in §4.2 are reproduced exactly.

# 9. Priority, prior art, and defensive-publication statement

This section exists because the work is published **instead of patented**. It states what is claimed, what is
explicitly *not* claimed, what prior art was found when we looked, and the documentary basis for the date.

## 9.1 What is claimed (elements E1–E5)

Each element is identified by where it is disclosed, so a reader can check that the disclosure is enabling and
that the date is not retrospective.

| # | Element | Disclosed at |
|---|---|---|
| **E1** | A six-axis state vector over the six pathogenic factors (wind / cold / summer-heat / damp / dryness / fire) representing one treated episode, with herb vectors derived from four-nature and five-flavour by an explicit published coefficient set | §2.1–2.2; `engine/tcm_energy_sim.py::drug_vector` |
| **E2** | Dosage form implemented as a release time constant inside the dynamics — decoction 1.0, powder 1.5, pellet 3.0, pill 4.0, paste 6.0 — with dosing as a pulsed input through that constant | §2.4; `DOSE_TAU` |
| **E3** | A continuous-time decomposition of the clinical course into self-healing decay, a sparse pathogenesis-transmission matrix, and a drug-gain term: *dE/dt* = −k₀·*E* + *M*·*E* + α·*D*<sub>eff</sub>·pulse(*t*) | §2.5 |
| **E4** | Four qualitative treatment rules implemented as dynamical terms: dose gated by remaining illness; wrong treatment amplifying transmission (×1.8) while halving self-healing (×0.5); cold-bitter herbs aggravating cold-damp; pungent-warm herbs fuelling an already-flourishing fire | §2.5 table; `simulate()` |
| **E5** | A machine-readable operator contract for external therapies (acupuncture, electroacupuncture, moxibustion, tuina, guasha, cupping) in which the parameter-to-axis mapping is deliberately left as contributed data rather than hard-coded, together with schemas and a privacy-linted contribution pipeline | `engine/external_therapy.py`, `schema/*.json`, `tools/validate_contribution.py` |

## 9.2 Prior art found, and what is not claimed

**We do not claim to be first to formalise TCM as a state space with operators.** That step is already in the
literature, and the closest work appeared two months before this record:

- Dong Y, Wan X, Deng K, Peng C, Luo M. *Formalization, structural representation, and construction of
  equivalent mathematical expressions for basic theories of traditional Chinese medicine.* Digital Chinese
  Medicine, published 2026-09-01. doi:10.1016/j.dcmed.2026.08.001. — an n-dimensional state space **S**, a
  constitutional baseline **B**, a state-correction operator **O**, a harmonisation coefficient α and
  compatibility coefficients λ, with a first-order affine transition and a Guizhi Tang worked example.
  Differences from the present work: their transition is a **single discrete step**, not a time-integrated
  course; there is no self-healing term, no transmission matrix, no dosage-form time constant, no treatment
  rules, no implementation, and no falsification criteria.

Earlier work in the same direction, acknowledged rather than disputed:

- 翟忠信. 中医阴阳学说的一个数学模型. 数理医药学杂志, 1999(4):302–304. — a two-variable ODE model of yin–yang
  with stability analysis.
- 五行理论的数学模型及其微分方程组的通解. 四川中医, 2006(11). — ODE system for the five phases.
- Release-kinetics studies of TCM dosage forms in the pharmaceutics literature (e.g. 张建国, 周玲. 中药在人体内
  释放过程的研究. 盐城工学院学报(自然科学版), 2007, 20(4):55–59), which model release physically but do not
  use the dosage form as a time constant inside a syndrome dynamics.
- Adjacent patent art on mapping symptoms and prescriptions into structured vectors for state-transition
  mining, e.g. CN120600335A (dynamic-efficacy-feedback sequential-diagnosis logic mining). This is cited to
  show the neighbourhood is occupied; E1–E5 are not read onto it.

So the claim is **narrow and additive**: E1–E5, as specified above, disclosed in this record on the date below.
We make no claim to the general idea, to any specific coefficient value, or to any clinical effect.

## 9.3 Search basis

Searched on 2026-11-17 with a general web index and DOI landing pages, using, among others:
"ordinary differential equation model traditional Chinese medicine syndrome dynamics";
"TCM state space state-correction operator";
"中药剂型 释放 动力学 时间常数 证候 演化";
plus citation chasing from the Dong et al. paper. **No systematic patent-database search was performed**; the
patent cited above was found incidentally. This is a good-faith prior-art check by non-lawyers, not a
freedom-to-operate opinion.

## 9.4 Defensive-publication notice

> **Defensive publication notice.** This work is published as a deliberate public disclosure intended to
> constitute prior art under 35 U.S.C. §102 and corresponding provisions worldwide. No patent protection is
> sought or held by the authors for any subject matter disclosed herein, and the authors intend this dated
> public record to preclude the patenting of the disclosed subject matter by any party. First published
> 2026-11-17. Archived with DOI 10.5281/zenodo.24296397. The declaration covers elements E1–E5 of §9.1.

Scope. The declaration covers the modelling elements E1–E5 and the artefacts that implement them (engine,
schemas, operator contract, validator) as they exist in the cited commit. It does not cover, and is not
intended to cover, any third-party data contributed later to the repository, nor any clinical method not
described here.

Caveat. Whether a given disclosure bars a particular claim is a question for counsel, not for this document.
This section records intent, scope and timing; it is not a legal opinion. Publishing also means **the authors
themselves can no longer obtain patent protection on E1–E5** in jurisdictions where this disclosure is prior
art — that trade was made deliberately.

## 9.5 Documentary basis

| Item | Value |
|---|---|
| Concept DOI (always resolves to the latest version) | 10.5281/zenodo.24296397 |
| First published version | v1, 2026-11-17 |
| Source repository | https://github.com/Even-li316/tcm-state-dynamics |
| Code licence | MIT (explicit patent grant is not implied by MIT; the notice above is the operative statement) |
| Data contributed later | CC BY 4.0, per `CONTRIBUTING.md` |

# References

1. 张仲景. *伤寒杂病论*. ca. 220 CE. (Syndrome differentiation and formula families; source of the four
   syndromes and of the directional claims in §1.)
2. 李时珍. *本草纲目*. 1578. (Four-nature / five-flavour attributes used to build the herb vectors.)
3. *黄帝内经·素问*. compiled ca. 1st century BCE. (Six pathogenic factors; the six-axis vocabulary.)
4. Dong Y, Wan X, Deng K, Peng C, Luo M. Formalization, structural representation, and construction of
   equivalent mathematical expressions for basic theories of traditional Chinese medicine. *Digital Chinese
   Medicine*, 2026-09-01. doi:10.1016/j.dcmed.2026.08.001.
5. 翟忠信. 中医阴阳学说的一个数学模型. *数理医药学杂志*, 1999(4):302-304.
6. 五行理论的数学模型及其微分方程组的通解. *四川中医*, 2006(11).
7. 张建国, 周玲. 中药在人体内释放过程的研究. *盐城工学院学报(自然科学版)*, 2007, 20(4):55-59.
8. CN120600335A. 动态疗效反馈的中医序贯诊疗逻辑挖掘方法、系统及介质 (adjacent patent art, cited in §9.2).
9. Source code and figures: https://github.com/Even-li316/tcm-state-dynamics (MIT).
