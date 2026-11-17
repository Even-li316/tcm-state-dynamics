# Model specification

The whole model is `engine/tcm_energy_sim.py`. This page states it compactly so it can be argued with.

## 1. State

```
E(t) = (E_wind, E_cold, E_summerheat, E_damp, E_dryness, E_fire) ∈ R^6
```

`E_i > 0` = excess of that pathogenic factor, `E_i < 0` = deficiency. `|E|` is the imbalance magnitude
used to summarise "how ill". Balanced health is `E = 0`.

Clamped to `[-3, 3]` at every step purely to keep the demo bounded.

## 2. Herb → vector

Each entry of the herb table carries five qualitative attributes:

```
(name, nature ∈ {寒, 凉, 平, 温, 热}, flavour ⊂ {辛, 甘, 苦, 酸, 咸, 淡, 涩},
 channel entered, trend ∈ {升, 升浮, 降, 平}, potency)
```

Mapping rules (all hand-set, all visible in `drug_vector()`):

| Axis | Rule (coefficients as implemented) |
|---|---|
| cold | `−0.45 · max(q, 0)` — warm/hot herbs dispel cold |
| fire | `+0.45 · min(q, 0)` — cold/cool herbs clear fire |
| summer-heat | `0.6 · fire term` — fire-clearing herbs also clear summer-heat |
| wind | `−0.40 · [pungent]` |
| damp | `−0.35·[bitter] − 0.55·[bland] − 0.25·[pungent∧bitter] − 0.30·[aromatic] + 0.15·([sour]+[astringent])` |
| dryness | `+0.20·[bitter] − 0.40·[salty] − 0.25·[sweet ∧ cold]` |

`q ∈ {−2,−1,0,1,2}` for 寒/凉/平/温/热. `[·]` is an indicator.

## 3. Formula → net field

```
D_net = Σ_h  w_role(h) · potency(h) · v(h),     w: 君 1.0, 臣 0.6, 佐 0.4, 使 0.25
tonic = min(0.25, Σ_h w_role(h) · [sweet] · 0.05)      # 扶正 / self-healing boost
warm  = Σ_h w_role(h) · max(q,0) · [pungent]           # used by rule R4
```

## 4. Dosage form = time constant

```
τ: 汤 1.0 · 散 1.5 · 丹 3.0 · 丸 4.0 · 膏 6.0
pulse(t) = Σ_{k: k·T_dose ≤ t} exp(−(t − k·T_dose)/τ)
```

The claim is modest and classical: the dosage form *is* the release kinetics. Decoction acts fast and
fades fast; a paste acts slowly and long.

## 5. Dynamics

```
dE/dt = −k0·E + M·E + α·D_eff·pulse(t)
k0 = (0.05 + tonic) · (0.5 if D_net·E0 > 0 else 1.0)
M  = M0 · (1.8 if D_net·E0 > 0 else 1.0)
```

`M0` — pathogenesis transmission matrix, hand-set:

| from → to | coefficient |
|---|---|
| wind → fire | 0.10 |
| fire → dryness | 0.08 |
| dryness → fire | 0.04 |
| damp → cold | 0.06 |
| cold → damp | 0.04 |
| summer-heat → damp | 0.07 |
| fire → wind | 0.03 |

Sign of `D_net·E0` is the crude test for "does this formula push in the same direction as the illness" —
same direction means wrong treatment, which both speeds transmission and halves self-healing.

## 6. Gating rules

| Rule | Statement | Implementation |
|---|---|---|
| R1 | stop when illness is gone | per-axis dose is multiplied by `min(1, E/0.15)`, and aggravating components by `1/(1+E)` |
| R2 | wrong treatment amplifies | `M × 1.8`, `k0 × 0.5` when `D_net·E0 > 0` |
| R3 | cold-bitter herbs aggravate cold-damp | if `E_cold > 0.3` and clearing term `< −0.3`: add `0.35·|clear|` to cold, `0.15·|clear|` to damp |
| R4 | pungent-warm herbs add fuel to blazing fire | if `E_summerheat + E_fire > 0.3`: add `0.20·warm·pulse·scaling` to fire |

## 7. Integration

Explicit Euler, `dt = 0.02`, `T = 10` (one dose per unit time), `α = 1.1`. Output `out/summary.json`
holds `|E(T)| / |E(0)|` for the matched / no-treatment / wrong-treatment arms of each of the four
syndromes.

## 8. What would falsify it

The current parameters were chosen to reproduce classical qualitative expectations, so agreement is not
evidence. Two tests that *could* fail:

1. **Fit test** — with `k0, M, α` estimated from retrospective case series, does the model predict the
   observed number of visits to resolution out of sample?
2. **Reversal test** — given a target state, does the reverse search return formulas that clinicians
   actually use, or arbitrary combinations?

Until at least one of these has been run and passed, treat every number here as a design choice.
