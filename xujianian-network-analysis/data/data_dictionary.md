# Data Dictionary: `xujianian_english_final.csv`

## Overview

This file contains the coded dataset used in the manuscript "Peripheral
Elites: Status-Centrality Decoupling in Social Networks." It represents
104 burials from the Xujianian cemetery (Siwa culture, northwest China,
twelfth to eleventh centuries BCE), coded directly from the excavation
report:

> Institute of Archaeology, Chinese Academy of Social Sciences (CASS). (2006).
> *Xujianian Cemetery Excavation Report* [徐家碾墓地发掘报告]. Beijing:
> Science Press.

Each row represents one burial. The file has 104 rows and 21 columns.

---

## Variables

### Identification

| Column | Type | Description |
|---|---|---|
| `burial_id` | string | Burial identifier from the excavation report (format `M1`, `M2`, ..., `M104`). |
| `site` | string | Site name. Constant value `Xujianian`. |
| `culture` | string | Archaeological culture affiliation. Constant value `Siwa`. |
| `pathway` | string | Subsistence mode inferred from the excavation report. Constant value `Pastoral`. |

### Demographic and burial context

| Column | Type | Description |
|---|---|---|
| `sex` | string | Biological sex determination from the excavation report. Values: `M` (male), `F` (female), `U` (unknown / not determined). |
| `age_description` | string | Age description as given in the excavation report. Values include `Adult`, specific age ranges (`16-18 years`, etc.), or `Unknown`. |
| `age_group` | string | Coarse age category derived from `age_description`. Values: `sub_adult`, `16-30`, `31-45`, `46+`, or `unknown`. |
| `burial_style` | string | Burial posture and treatment as reported. Values: `extended_supine`, `flexed`, `secondary`, `prone`, `disturbed`, `unknown`. |

### Artifact counts

All artifact count columns are non-negative integers representing the number
of items of the given type recovered from each burial. Counts are taken
directly from the excavation report tables and appendices. No imputation or
adjustment was applied.

| Column | Type | Description |
|---|---|---|
| `pottery_count` | int | Number of pottery vessels. |
| `bronze_count` | int | Number of bronze objects (ornaments, weapons, tools). |
| `bone_count` | int | Number of bone objects (beads, tools, ornaments). |
| `jade_count` | int | Number of jade objects. |
| `agate_count` | int | Number of agate beads or ornaments. |
| `turquoise_count` | int | Number of turquoise beads or ornaments. |
| `stone_count` | int | Number of worked-stone ornaments (excluding jade and agate). |
| `shell_ornament_count` | int | Number of shell ornaments (excluding cowrie money, which is a separate category). |
| `cowrie_count` | int | Number of cowrie shells used as currency or ornament. |
| `spindle_whorl` | int | Number of spindle whorls. |

### Derived aggregates

| Column | Type | Description |
|---|---|---|
| `stone_jade_total` | int | Sum of `jade_count + agate_count + turquoise_count + stone_count + shell_ornament_count`. Used as a diagnostic for ornament-rich burials. |
| `total_artifacts` | int | Sum of all ten artifact count columns above. |

### Source notes

| Column | Type | Description |
|---|---|---|
| `original_notes_chinese` | string | Verbatim description notes from the Chinese-language excavation report, retained for reference and traceability. May contain comma-separated item descriptions with sub-totals in parentheses. Used during coding to disambiguate ambiguous entries. |

---

## Rare-goods classification

The `has_rare_goods` variable used throughout the analysis is **not stored
in this file** but is computed at runtime in the analysis notebooks. The
classification applies a 10% presence threshold: any artifact type present
in fewer than 10% of burials is classified as rare, and a burial is classified
as a rare-goods holder if it contains at least one rare artifact.

Applied to the Xujianian dataset, the 10% threshold classifies three artifact
types as rare (`turquoise_count`, `stone_count`, `agate_count`), yielding
18 rare-goods holders out of 104 burials.

Sensitivity analyses using 5% and 15% thresholds are reported in the main
text (Section 4.6, Table 8) and implemented in the main analysis notebook.

---

## Coding decisions and known limitations

1. **Burial completeness.** The excavation report documents variable
   preservation across burials. Some burials were disturbed or partially
   robbed. Artifact counts reflect what was recovered and documented in
   the report, not necessarily what was originally deposited. This
   limitation is discussed in the main text.

2. **Sex and age uncertainty.** A substantial fraction of burials have
   `sex = U` (unknown) or `age_group = unknown`. This reflects the
   preservation state of the skeletal remains rather than coding
   limitations. Analyses conditional on sex or age use only burials with
   determined values.

3. **Constant columns.** The columns `site`, `culture`, and `pathway` are
   constant across all 104 rows because the dataset comes from a single
   site. They are retained to support potential future pooling with
   comparable datasets from other Siwa-culture sites.

4. **Stone vs jade distinction.** "Stone" (`stone_count`) refers to worked
   non-jade stone ornaments in the excavation report; these are
   distinguishable from `jade_count` in the original documentation through
   material-level description. Where the report did not distinguish, items
   were conservatively coded as `stone_count`.

5. **Chronology.** The 104 burials span the twelfth to eleventh centuries
   BCE as a single chronological block. The excavation report evaluates
   the possibility of subdividing the cemetery into earlier and later
   phases on three independent grounds (stratigraphy, artifact typology,
   pottery combination patterns) and concludes that such a subdivision
   is not warranted. See Section 3.1 of the main text for discussion.

---

## Usage

The analysis notebooks in `code/` load this file with a relative path:

```python
df = pd.read_csv('../data/xujianian_english_final.csv')
```

All downstream variables (binarized artifact presence, rare-goods indicator,
network adjacency, centrality scores, community assignments) are computed
from this file in the notebooks. The file itself contains only the primary
coded observations.
