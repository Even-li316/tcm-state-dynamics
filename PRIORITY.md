# Priority and defensive-publication statement

**Status: published deliberately as prior art, in place of a patent.**

| | |
|---|---|
| First published | 2026-11-17 |
| Archived record | Zenodo, concept DOI [10.5281/zenodo.24296397](https://doi.org/10.5281/zenodo.24296397) |
| Paper (this record) | `paper/tsie_preprint.pdf` — §9 sets out the full statement |
| Code | this repository, tag `v0.3.0`, MIT |
| PDF SHA-256 | `942440d487dc3c970585b7945dc082dc372c26fa4017e15995bae47043f01e4c` |

## What is claimed — elements E1–E5

1. **E1** — a six-axis state vector over the six pathogenic factors (wind, cold, summer-heat, damp, dryness,
   fire) for one treated episode, with herb vectors derived from four-nature / five-flavour by an explicit,
   published coefficient set.
2. **E2** — dosage form as a release time constant inside the dynamics (decoction 1.0, powder 1.5, pellet 3.0,
   pill 4.0, paste 6.0), with dosing as a pulsed input through that constant.
3. **E3** — continuous-time decomposition of the clinical course into self-healing decay, a sparse
   pathogenesis-transmission matrix, and a drug-gain term.
4. **E4** — four qualitative treatment rules implemented as dynamical terms: dose gated by remaining illness;
   wrong treatment amplifying transmission while suppressing self-healing; cold-bitter herbs aggravating
   cold-damp; pungent-warm herbs fuelling an already-flourishing fire.
5. **E5** — a machine-readable operator contract for external therapies in which the parameter-to-axis mapping
   is deliberately contributed data rather than hard-coded, with schemas and a privacy-linted pipeline.

Each element is located precisely in §9.1 of the paper. Without that location the disclosure would not be
enabling, and an enabling disclosure is what makes it prior art.

## What is NOT claimed

- **Not** the general idea of formalising TCM as a state space with operators. That is prior art:
  Dong Y, Wan X, Deng K, Peng C, Luo M, *Digital Chinese Medicine*, 2026-09-01,
  doi:10.1016/j.dcmed.2026.08.001 — an n-dimensional state space with a state-correction operator and a
  single-step affine transition; no time integration, no dosage-form constant, no treatment rules.
- **Not** ODE models of yin–yang or the five phases as such (翟忠信 1999; 四川中医 2006).
- **Not** release kinetics of TCM dosage forms as a pharmaceutical phenomenon (pharmaceutics literature, e.g.
  盐城工学院学报 2007).
- **Not** any clinical effect, diagnostic accuracy, or specific coefficient value.
- **Not** third-party data contributed to this repository later.

## Notice

> This work is published as a deliberate public disclosure intended to constitute prior art under
> 35 U.S.C. §102 and corresponding provisions worldwide. No patent protection is sought or held by the authors
> for any subject matter disclosed herein, and the authors intend this dated public record to preclude the
> patenting of the disclosed subject matter by any party. First published 2026-11-17. Archived with DOI
> 10.5281/zenodo.24296397.

The same trade cuts both ways: this disclosure also means the **authors** cannot obtain patent protection on
E1–E5 where this record is prior art. That was the intention — the goal is that nobody encloses it, not that
we do.

## Search basis

Prior-art check performed 2026-11-17 against a general web index and DOI landing pages, with citation chasing
from the closest paper. Relevant queries are listed in §9.3 of the paper. **No systematic patent-database
search was run**; the adjacent patent CN120600335A was found incidentally. This is a good-faith disclosure by
non-lawyers, not a freedom-to-operate opinion, and whether a given disclosure bars a particular claim is a
question for counsel.
