"""
Betweenness Centrality Variants on the Xujianian Similarity Network
===================================================================

Supplementary analysis for "Peripheral Elites: Status-Centrality Decoupling
in Social Networks" (Xujianian cemetery, Siwa culture, twelfth to eleventh
centuries BCE).

Standard betweenness centrality is known to be unstable on dense weighted
networks: small fluctuations in edge weights can dramatically reroute
shortest paths, so the betweenness score of any given node can depend on
narrow margins in a few individual ties (Segarra & Ribeiro, 2015). For a
similarity network with density 0.606 this instability is a concrete concern,
and it is compounded by the fact that shortest-path centralities on
similarity networks require a choice between several possible weighting
conventions that can produce different answers on the same network.

This script implements two stability-oriented betweenness variants and
compares them against three baseline specifications of standard betweenness
on the Xujianian similarity network.

Baselines:
    B1. Unweighted betweenness
    B2. Similarity-as-weight betweenness (matches main text Section 4.2 primary)
    B3. Distance-as-weight betweenness (distance = 1 - similarity)

Variants:
    V1. Stabler betweenness (Segarra & Ribeiro, 2015)
    V2. Gromov centrality (Babul & Reggiani, 2022)

For each measure the script computes the rare-goods to non-rare ratio and
runs a 10,000-iteration permutation test matching the node-level inference
protocol used in the main text.

Convention note. NetworkX's betweenness_centrality treats edge weight as
distance (cost). Passing similarity directly therefore produces shortest
paths that preferentially traverse dissimilar pairs, which is not the
intended topology. The technically consistent convention is to use
distance = 1 - similarity; the variants in this script use that convention.
All three baselines are reported side by side to document the sensitivity
of standard betweenness to the convention chosen.
"""

import json
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

OUTDIR = Path(__file__).resolve().parent.parent / 'results'
FIGDIR = Path(__file__).resolve().parent.parent / 'figures'
OUTDIR.mkdir(parents=True, exist_ok=True)
FIGDIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 1. Data and network construction
# ============================================================

print("="*70)
print("DATA AND NETWORK CONSTRUCTION")
print("="*70)

df = pd.read_csv('../data/xujianian_english_final.csv')
print(f"Loaded {len(df)} burials.")

ARTIFACT_COLS = [
    'pottery_count', 'bronze_count', 'bone_count', 'jade_count',
    'agate_count', 'turquoise_count', 'stone_count',
    'shell_ornament_count', 'cowrie_count', 'spindle_whorl'
]

df_binary = (df[ARTIFACT_COLS] > 0).astype(int)
df_binary.index = df['burial_id']

RARE_THRESHOLD = 0.10
presence_rates = (df[ARTIFACT_COLS] > 0).mean()
rare_artifacts = presence_rates[presence_rates < RARE_THRESHOLD].index.tolist()
df['has_rare_goods'] = (df[rare_artifacts].sum(axis=1) > 0).astype(int)
print(f"Rare artifact types (<10% presence): {rare_artifacts}")
print(f"Burials with rare goods: {df['has_rare_goods'].sum()} / {len(df)}")


def jaccard_similarity(a, b):
    inter = np.sum((a == 1) & (b == 1))
    union = np.sum((a == 1) | (b == 1))
    return inter / union if union > 0 else 0


n = len(df_binary)
sim_matrix = np.zeros((n, n))
for i in range(n):
    for j in range(i, n):
        s = jaccard_similarity(df_binary.iloc[i].values, df_binary.iloc[j].values)
        sim_matrix[i, j] = s
        sim_matrix[j, i] = s

THRESHOLD = 0.3
G = nx.Graph()
G.add_nodes_from(df_binary.index)
for i, n1 in enumerate(df_binary.index):
    for j, n2 in enumerate(df_binary.index):
        if i < j and sim_matrix[i, j] >= THRESHOLD:
            G.add_edge(n1, n2,
                       weight=sim_matrix[i, j],
                       distance=1.0 - sim_matrix[i, j] + 1e-9)

print(f"\nNetwork: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, "
      f"density = {nx.density(G):.4f}")

rare_map = dict(zip(df['burial_id'], df['has_rare_goods']))
rare_nodes = [n for n in G.nodes() if rare_map[n] == 1]
nonrare_nodes = [n for n in G.nodes() if rare_map[n] == 0]
print(f"Rare-goods holders: {len(rare_nodes)}, non-holders: {len(nonrare_nodes)}")

# ============================================================
# 2. Helpers
# ============================================================


def group_ratio(centrality, rare, nonrare):
    rm = np.mean([centrality[n] for n in rare])
    nm = np.mean([centrality[n] for n in nonrare])
    return rm / nm if nm > 0 else float('inf'), rm, nm


def permutation_test(centrality, rare, nonrare, n_perms=10000, seed=42):
    """Two-sided permutation test on the rare-to-non-rare centrality ratio."""
    rng = np.random.default_rng(seed)
    nodes = list(centrality.keys())
    n_rare = len(rare)
    obs_ratio, _, _ = group_ratio(centrality, rare, nonrare)
    arr = np.array([centrality[n] for n in nodes])
    n_total = len(nodes)
    null_ratios = np.empty(n_perms)
    for k in range(n_perms):
        idx = rng.permutation(n_total)
        rm = arr[idx[:n_rare]].mean()
        nm = arr[idx[n_rare:]].mean()
        null_ratios[k] = rm / nm if nm > 0 else np.nan
    null_ratios = null_ratios[~np.isnan(null_ratios)]
    p = (np.sum(np.abs(null_ratios - 1) >= abs(obs_ratio - 1)) + 1) / (len(null_ratios) + 1)
    return obs_ratio, p


def report(label, centrality, rare, nonrare):
    obs, p = permutation_test(centrality, rare, nonrare, n_perms=10000)
    rm = np.mean([centrality[n] for n in rare])
    nm = np.mean([centrality[n] for n in nonrare])
    print(f"  {label}:")
    print(f"    Mean (rare):     {rm:.6f}")
    print(f"    Mean (non-rare): {nm:.6f}")
    print(f"    Ratio:           {obs:.4f}")
    print(f"    Permutation p:   {p:.4f}")
    return {'rare_mean': float(rm), 'nonrare_mean': float(nm),
            'ratio': float(obs), 'p_value': float(p)}


# ============================================================
# 3. Baseline betweenness under three conventions
# ============================================================

print("\n" + "="*70)
print("BASELINE BETWEENNESS (THREE CONVENTIONS)")
print("="*70)

print("\nB1. Unweighted betweenness")
bc_unw = nx.betweenness_centrality(G, normalized=True)
res_b1 = report("Unweighted", bc_unw, rare_nodes, nonrare_nodes)

print("\nB2. Similarity-as-weight betweenness")
bc_simw = nx.betweenness_centrality(G, weight='weight', normalized=True)
res_b2 = report("Similarity-as-weight", bc_simw, rare_nodes, nonrare_nodes)

print("\nB3. Distance-as-weight betweenness (distance = 1 - similarity)")
bc_distw = nx.betweenness_centrality(G, weight='distance', normalized=True)
res_b3 = report("Distance-as-weight", bc_distw, rare_nodes, nonrare_nodes)

# ============================================================
# 4. Stabler betweenness (Segarra & Ribeiro, 2015)
# ============================================================

print("\n" + "="*70)
print("STABLER BETWEENNESS")
print("="*70)


def stabler_betweenness(G, n_perturbations=100, sigma=0.10, seed=42):
    """
    Stabler betweenness via repeated edge-weight perturbation.

    Following Segarra and Ribeiro (2015), standard betweenness is averaged
    across multiple realisations of a small random perturbation of the edge
    weights. Gaussian noise with standard deviation sigma * original
    similarity is added to each edge; values are clipped to [0.001, 0.999]
    and converted to distance for input to NetworkX's shortest-path
    betweenness. The output is the arithmetic mean of n_perturbations
    perturbed betweenness scores.
    """
    rng = np.random.default_rng(seed)
    nodes = list(G.nodes())
    accum = {n: 0.0 for n in nodes}
    for k in range(n_perturbations):
        Gp = G.copy()
        for u, v, d in Gp.edges(data=True):
            sim_orig = d['weight']
            sim_pert = max(0.001, min(0.999, sim_orig + rng.normal(0, sigma * sim_orig)))
            d['weight'] = sim_pert
            d['distance'] = 1.0 - sim_pert + 1e-9
        bc = nx.betweenness_centrality(Gp, weight='distance', normalized=True)
        for n in nodes:
            accum[n] += bc[n]
    return {n: accum[n] / n_perturbations for n in nodes}


print("\nV1. Stabler betweenness (n_perturbations=100, sigma=0.10)")
bc_stab = stabler_betweenness(G, n_perturbations=100, sigma=0.10, seed=42)
res_stab = report("Stabler", bc_stab, rare_nodes, nonrare_nodes)

print("\nParameter sensitivity (3x3 grid)")
sensitivity = {}
for n_p in [50, 100, 200]:
    for sg in [0.05, 0.10, 0.15]:
        bc_s = stabler_betweenness(G, n_perturbations=n_p, sigma=sg, seed=42)
        r, p = permutation_test(bc_s, rare_nodes, nonrare_nodes, n_perms=2000, seed=43)
        sensitivity[(n_p, sg)] = (r, p)
        print(f"  n={n_p}, sigma={sg}: ratio={r:.4f}, p={p:.4f}")

# ============================================================
# 5. Gromov centrality (Babul & Reggiani, 2022)
# ============================================================

print("\n" + "="*70)
print("GROMOV CENTRALITY")
print("="*70)


def gromov_centrality(G, weight='distance'):
    """
    Gromov centrality (Babul & Reggiani, 2022).

    The Gromov product (x | y)_v = (1/2)(d(x,v) + d(y,v) - d(x,y)) is the
    triangle inequality excess for the triple (x, y, v), and quantifies how
    far node v lies from the geodesic between x and y. Averaging the Gromov
    product over all pairs (x, y) distinct from v yields a per-node score;
    small values indicate that v lies on many geodesics and is "metrically
    central," large values indicate that v lies off to the side of the
    metric structure. Gromov centrality is defined by inverting the sign of
    the per-node score so that high values correspond to central positions,
    matching the convention used for other centrality measures.

    The function below computes Gromov centrality exactly by enumerating
    all triples. This is tractable for the Xujianian network because it
    has only 104 nodes.
    """
    nodes = list(G.nodes())
    n = len(nodes)
    node_idx = {nd: i for i, nd in enumerate(nodes)}

    print("    Computing all-pairs shortest paths...")
    dist_dict = dict(nx.all_pairs_dijkstra_path_length(G, weight=weight))
    D = np.full((n, n), np.inf)
    for u in dist_dict:
        for v, d in dist_dict[u].items():
            D[node_idx[u], node_idx[v]] = d
    finite_D = D[np.isfinite(D)]
    diameter = finite_D.max() if len(finite_D) > 0 else 1.0
    D[np.isinf(D)] = diameter

    print("    Computing Gromov products over all triples...")
    avg_gp = np.zeros(n)
    for v_i in range(n):
        gp_sum = 0.0
        cnt = 0
        for x_i in range(n):
            if x_i == v_i:
                continue
            for y_i in range(x_i + 1, n):
                if y_i == v_i:
                    continue
                gp = 0.5 * (D[x_i, v_i] + D[y_i, v_i] - D[x_i, y_i])
                gp_sum += gp
                cnt += 1
        avg_gp[v_i] = gp_sum / cnt if cnt > 0 else 0.0

    max_gp = avg_gp.max()
    return {nodes[i]: float(max_gp - avg_gp[i]) for i in range(n)}


print("\nV2. Gromov centrality (exact, all triples)")
gc_gromov = gromov_centrality(G, weight='distance')
res_gromov = report("Gromov centrality", gc_gromov, rare_nodes, nonrare_nodes)

# ============================================================
# 6. Summary, figures, JSON export
# ============================================================

print("\n" + "="*70)
print("SUMMARY")
print("="*70)

results = {
    'baseline_unweighted': {**res_b1, 'name': 'Unweighted betweenness'},
    'baseline_sim_weight': {
        **res_b2, 'name': 'Similarity-as-weight betweenness',
        'note': 'Matches main text Section 4.2 primary specification'},
    'baseline_dist_weight': {
        **res_b3, 'name': 'Distance-as-weight betweenness',
        'note': 'distance = 1 - similarity, technically consistent convention'},
    'stabler': {
        **res_stab, 'name': 'Stabler betweenness',
        'reference': 'Segarra & Ribeiro (2015)',
        'parameters': {'n_perturbations': 100, 'sigma': 0.10}},
    'gromov': {
        **res_gromov, 'name': 'Gromov centrality',
        'reference': 'Babul & Reggiani (2022)'},
    'sensitivity': {
        f"n={k[0]},sigma={k[1]}": {'ratio': float(v[0]), 'p_value': float(v[1])}
        for k, v in sensitivity.items()}
}

with open(OUTDIR / 'betweenness_variants_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {OUTDIR / 'betweenness_variants_results.json'}")

table = pd.DataFrame([
    {'Measure': 'B1. Unweighted betweenness',
     'Mean (rare)': f"{res_b1['rare_mean']:.6f}",
     'Mean (non-rare)': f"{res_b1['nonrare_mean']:.6f}",
     'Ratio': f"{res_b1['ratio']:.3f}",
     'Permutation p': f"{res_b1['p_value']:.4f}"},
    {'Measure': 'B2. Similarity-as-weight betweenness',
     'Mean (rare)': f"{res_b2['rare_mean']:.6f}",
     'Mean (non-rare)': f"{res_b2['nonrare_mean']:.6f}",
     'Ratio': f"{res_b2['ratio']:.3f}",
     'Permutation p': f"{res_b2['p_value']:.4f}"},
    {'Measure': 'B3. Distance-as-weight betweenness',
     'Mean (rare)': f"{res_b3['rare_mean']:.6f}",
     'Mean (non-rare)': f"{res_b3['nonrare_mean']:.6f}",
     'Ratio': f"{res_b3['ratio']:.3f}",
     'Permutation p': f"{res_b3['p_value']:.4f}"},
    {'Measure': 'V1. Stabler betweenness',
     'Mean (rare)': f"{res_stab['rare_mean']:.6f}",
     'Mean (non-rare)': f"{res_stab['nonrare_mean']:.6f}",
     'Ratio': f"{res_stab['ratio']:.3f}",
     'Permutation p': f"{res_stab['p_value']:.4f}"},
    {'Measure': 'V2. Gromov centrality',
     'Mean (rare)': f"{res_gromov['rare_mean']:.6f}",
     'Mean (non-rare)': f"{res_gromov['nonrare_mean']:.6f}",
     'Ratio': f"{res_gromov['ratio']:.3f}",
     'Permutation p': f"{res_gromov['p_value']:.4f}"},
])
print()
print(table.to_string(index=False))
table.to_csv(OUTDIR / 'betweenness_variants_table.csv', index=False)

# ============================================================
# 7. Figures
# ============================================================

print("\nGenerating comparison figure...")

variants_data = [
    ('B1. Unweighted', bc_unw, res_b1),
    ('B2. Similarity-as-weight', bc_simw, res_b2),
    ('B3. Distance-as-weight', bc_distw, res_b3),
    ('V1. Stabler', bc_stab, res_stab),
    ('V2. Gromov centrality', gc_gromov, res_gromov),
]

fig, axes = plt.subplots(1, 5, figsize=(20, 5))
for ax, (title, cent, res) in zip(axes, variants_data):
    rare_vals = [cent[n] for n in rare_nodes]
    nonrare_vals = [cent[n] for n in nonrare_nodes]
    bp = ax.boxplot([nonrare_vals, rare_vals],
                    tick_labels=['Non-rare\n(n=86)', 'Rare-goods\n(n=18)'],
                    patch_artist=True, widths=0.6)
    for patch, color in zip(bp['boxes'], ['#6baed6', '#e6550d']):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
    sig = '***' if res['p_value'] < 0.001 else ('**' if res['p_value'] < 0.01 else ('*' if res['p_value'] < 0.05 else 'ns'))
    ax.set_title(f"{title}\nratio = {res['ratio']:.2f}, p = {res['p_value']:.4f} {sig}",
                 fontsize=10)
    ax.set_ylabel('Centrality')
    ax.grid(True, alpha=0.3)

plt.tight_layout()
fig_path = FIGDIR / 'betweenness_variants_comparison.png'
plt.savefig(fig_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"  Saved {fig_path}")

# Sensitivity heatmap
sens_df = pd.DataFrame(
    [[sensitivity[(n_p, sg)][0] for sg in [0.05, 0.10, 0.15]] for n_p in [50, 100, 200]],
    index=['n=50', 'n=100', 'n=200'],
    columns=['sigma=0.05', 'sigma=0.10', 'sigma=0.15']
)
fig, ax = plt.subplots(figsize=(7, 4))
sns.heatmap(sens_df, annot=True, fmt='.3f', cmap='RdBu_r', center=1.0,
            cbar_kws={'label': 'Rare/non-rare ratio'}, ax=ax,
            vmin=0.1, vmax=0.4)
ax.set_title('Stabler Betweenness: Parameter Sensitivity\n(rare/non-rare ratio)',
             fontsize=11)
plt.tight_layout()
sens_path = FIGDIR / 'stabler_sensitivity.png'
plt.savefig(sens_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"  Saved {sens_path}")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
