# Xujianian Network Analysis

Replication repository for the paper:

> **Peripheral Elites: Status-Centrality Decoupling in Social Networks.**
> Manuscript under review at *Social Networks*.

This repository contains the dataset, analysis notebooks, scripts, and outputs
required to reproduce every quantitative result reported in the manuscript and
the Supplementary Materials, including the similarity network construction,
centrality analysis, MRQAP regressions, network role classification, all
robustness and sensitivity checks, and the stability-oriented betweenness
variants reported in the supplement.

---

## Repository structure

```
xujianian-network-analysis/
├── README.md                              # This file
├── LICENSE                                # CC BY 4.0 for data, MIT for code
├── requirements.txt                       # Python dependencies
├── data/
│   ├── xujianian_english_final.csv        # Coded dataset: 104 burials × 22 variables
│   └── data_dictionary.md                 # Variable definitions
├── code/
│   ├── main_analysis.ipynb                # Main manuscript analyses (Sections 4.1–4.7)
│   ├── betweenness_variants_analysis.ipynb  # Supplementary Materials analyses
│   └── betweenness_variants_analysis.py   # Standalone script version
├── results/
│   ├── betweenness_variants_results.json  # Numerical results from the supplement
│   └── betweenness_variants_table.csv     # Summary table from the supplement
└── figures/
    ├── betweenness_variants_comparison.png  # Figure S1 (supplement)
    └── stabler_sensitivity.png              # Figure S2 (supplement)
```

---

## Data

The primary data source is the published excavation report of the Xujianian
cemetery (Institute of Archaeology, Chinese Academy of Social Sciences, 2006).
The file `data/xujianian_english_final.csv` is our coded version of the report,
with 104 burials and 22 variables covering artifact counts by category, burial
style, sex, age, and contextual notes. See `data/data_dictionary.md` for a
full description of each variable.

All artifact counts were coded directly from the excavation report tables and
appendices. Pottery, bronze, bone, jade, agate, turquoise, stone ornament,
shell ornament, cowrie, and spindle whorl counts are recorded per burial. No
inferences or imputations were applied to the raw counts. Fields with unknown
or unrecorded values follow the convention used in the original report.

---

## Reproducing the main-text analyses

The main manuscript results (Tables 2–10 and Figures 1–3, Sections 4.1–4.7)
are reproduced by running `code/main_analysis.ipynb` from start to finish.
The notebook is organized in numbered modules corresponding to the manuscript
sections:

- **Modules 1–3**: data loading, rare-goods classification, similarity network
  construction at Jaccard threshold 0.30
- **Modules 4–5**: Louvain community detection, modularity null model test
- **Module 6**: centrality computation (degree, eigenvector, betweenness,
  closeness) and network role classification
- **Module 7**: node-level permutation tests (10,000 iterations) for all four
  centrality measures
- **Module 8**: MRQAP regression with the six nested specifications reported
  in Section 4.4 (Models 1, 2, 3a, 3, 4, 5)
- **Module 9**: Fisher's exact test and chi-square test on the network role
  classification (Section 4.3)
- **Module 10**: consolidated robustness and sensitivity analyses
  (common-artifacts-only, Bray–Curtis abundance network, unweighted,
  threshold sensitivity, status threshold sensitivity, continuous regression)

The notebook runs end-to-end in approximately 8–12 minutes on a standard
laptop. All random seeds are fixed for exact reproducibility.

---

## Reproducing the Supplementary Materials analyses

The supplementary betweenness centrality variants analysis is reproduced by
either of two equivalent paths:

```bash
# Option 1: Jupyter notebook
cd code/
jupyter notebook betweenness_variants_analysis.ipynb

# Option 2: standalone script
cd code/
python betweenness_variants_analysis.py
```

Both paths produce the same outputs:

- `results/betweenness_variants_results.json` — all numerical results
- `results/betweenness_variants_table.csv` — summary table (Table S1)
- `figures/betweenness_variants_comparison.png` — Figure S1
- `figures/stabler_sensitivity.png` — Figure S2

The script takes approximately 3–5 minutes on a standard laptop. The script
computes five betweenness-like centrality measures on the same similarity
network used in the main text:

- **B1.** Unweighted betweenness
- **B2.** Similarity-as-weight betweenness (matches main text primary)
- **B3.** Distance-as-weight betweenness (distance = 1 − similarity)
- **V1.** Stabler betweenness (Segarra & Ribeiro, 2015)
- **V2.** Gromov centrality (Babul & Reggiani, 2022)

For each measure the script reports the rare-goods to non-rare centrality
ratio and a 10,000-iteration permutation p-value, matching the node-level
inference protocol used in the main text. The stabler betweenness measure
is additionally checked across a 3 × 3 parameter sensitivity grid.

---

## Software environment

All analyses were run under Python 3.12. Required packages and minimum
versions are listed in `requirements.txt`. To install:

```bash
pip install -r requirements.txt
```

The analysis relies on `networkx` for graph construction and centrality
measures, `python-louvain` for community detection, `pandas` and `numpy`
for data handling, `scipy` for statistical tests, `matplotlib` and `seaborn`
for figures, and `scikit-learn` for auxiliary standardization.

---

## License

- **Data** (`data/`): Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Code** (`code/`, scripts and notebooks): MIT License

See `LICENSE` for full terms.

---

## Citation

If you use this repository, please cite the paper once it is published. In
the meantime, the repository itself can be cited using its anonymous URL.

---

## Contact

This repository is anonymized for double-blind peer review. Correspondence
information will be added after acceptance.
