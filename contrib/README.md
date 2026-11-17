# contrib/ — what people send in

Every JSON file here is validated by `tools/validate_contribution.py` (schema + privacy lint) on each pull
request. Files named `EXAMPLE_*` are documentation, not data.

| Folder | Schema | What goes in |
|---|---|---|
| `cases/` | `schema/case_record.schema.json` | one treated episode: syndrome → formula (± external therapy) → outcome |
| `external/` | `schema/external_therapy.schema.json` | one external-therapy operator: modality, points, technique, parameters, optional axis mapping |

## Why the outcome field is the whole point

A record without an outcome cannot falsify anything. The model predicts *how fast* a state resolves; a
record that says "treated, then unknown" contributes nothing to the fit, and a record that says "treated,
resolved in 3 visits" contributes a data point. If you only have the former, still send it — the follow-up
gap is itself a finding — but mark it `unknown`.

## Status

| | Count |
|---|---:|
| Case records (excluding examples) | 0 |
| External-therapy operators (excluding examples) | 0 |

This table is maintained by hand in the README of each release; the authoritative count is
`ls contrib/cases/*.json` minus the `EXAMPLE_*` files.

## Contributors

None yet. The first accepted record gets its contributor named here and in the next preprint version.
