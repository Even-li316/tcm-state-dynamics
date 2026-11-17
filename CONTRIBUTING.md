# Contributing

The model is a skeleton. What it lacks is not code — it is **data and parameter claims**.
This document says exactly what is useful, what is not, and how to send it.

## Three ways to contribute

| Effort | How | Good for |
|---|---|---|
| 2 minutes | [Open an issue](https://github.com/Even-li316/tcm-state-dynamics/issues/new/choose) with one of the contribution forms | a single case, a single operator, a correction |
| 10 minutes | Add a JSON file under `contrib/` and open a pull request | a batch of cases, a full parameter set |
| as long as you like | [Discussions](https://github.com/Even-li316/tcm-state-dynamics/discussions) | arguing about the model, proposing a different mapping |

No Git experience is needed for the first route: the issue form collects the same fields, and a
maintainer will convert it into a JSON file, crediting you in the commit.

## What we need most, in order

1. **Case records with an outcome.** The single most valuable thing. A record is only useful if it has the
   intervention *and* what happened (resolved / improved / persisting / worsened, and how many visits).
   Format: `schema/case_record.schema.json`.
2. **External-therapy operators** — acupuncture, electroacupuncture, moxibustion, tuina, guasha, cupping —
   described as parameters: points, technique, frequency, intensity, duration, number of sessions, interval.
   Format: `schema/external_therapy.schema.json`. The model has **no** built-in mapping from these
   parameters to the six state axes; if you can supply that mapping with a source, that is the contribution.
3. **Herb-table entries** (currently 43 herbs). One herb needs: four-nature, five-flavour, channels entered,
   tendency, a potency estimate, and a citation. Send as an issue; additions are cheap and additive.
4. **Parameter fits.** If you have a series big enough to estimate `k0`, `M` or `α`, you do not need to send
   data — send the fitted values plus the fit script. That converts a demo into a model.

## Rules that are not negotiable

- **De-identify at the source, not here.** No names, no ID numbers, no phone numbers, no exact dates, no
  hospital record numbers, no faces. Age goes in bands; dates go to month at most. The validator refuses
  submissions that contain these patterns — that is a safety net, not a licence to send them and hope.
- **Published cases need a citation.** `source.type = "published"` and `source.citation` filled. Classical
  texts (public domain) are welcome and are the easiest place to start.
- **Do not invent outcomes.** If the record does not say how it ended, use `"unknown"`. An honest `unknown`
  is more valuable than a guess: it tells us the follow-up rate.
- **Do not submit AI-generated or reconstructed cases.** If a record was not observed (or transcribed from a
  real source), it is not a case. Fabricated records poison the only thing this project has.
- **Mark estimates as estimates.** `evidence.calibrated = false` unless the number came from a fit or a
  measurement with data attached. Being wrong in the open is fine; being silently confident is not.

## Adding a record

```bash
git clone https://github.com/Even-li316/tcm-state-dynamics
cd tcm-state-dynamics
cp contrib/cases/EXAMPLE_wind_cold_mahuang_tang.json contrib/cases/2026-11-vanilla-wind-cold.json
# edit the file, then:
pip install jsonschema
python tools/validate_contribution.py
```

Filename convention: `contrib/cases/<year>-<month>-<short-slug>.json`, ASCII, no patient identifiers
(obviously). Only files whose names start with `EXAMPLE_` are exempt from review — rename yours.

The validator checks the schema **and** runs a privacy lint (mobile numbers, ID numbers, exact dates,
patient-name fields). CI runs the same command on every pull request, so a green local run means a merge.

## Licensing of contributions

- Code: MIT (as the repository).
- Contributed data (case records, operator parameter sets): **CC BY 4.0**.
- By opening a pull request you confirm you have the right to share the material under those terms, and that
  the records are de-identified. If your institution requires an ethics approval or a data-use agreement for
  retrospective case data, get it before you send anything — we cannot retroactively fix that.

## What gets rejected

Unverifiable claims, marketing copy, anything containing identifiers, AI-fabricated cases, and bulk dumps
with no outcomes. Everything else — including "your mapping for herb X is wrong, here is why" — is welcome.

## Credit

Contributors are credited in the commit, in `contrib/README.md`, and in the next preprint version. If a
contribution changes a result, it gets its own paragraph rather than a line in an acknowledgements section.
