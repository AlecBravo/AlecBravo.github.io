import duckdb
import pandas as pd
import numpy as np
import textwrap
import os
import re
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio
from matplotlib.ticker import PercentFormatter
from matplotlib import gridspec

def wrap_text(s, width=55):
    """Wrap text for neat display inside a chart."""
    return "\n".join(textwrap.wrap(s, width=width))


#  ----------------------------------------------- 1) SQL Query ----------------------------------------------------
con = duckdb.connect('games.duckdb')

df = con.execute("""
WITH base AS (
    SELECT
        g."Game"  AS game,
        g."Price" AS price,
        g."Release date" AS release_date,
        g."Owners" AS owners,                    -- cleaned like 0-20000
        g."Playtime (Median)" AS playtime_median,
        g."Developer(s)" AS developers,
        g."Publisher(s)" AS publishers
    FROM main.sample_game_data_rpgs_csv g
),
ea_norm AS (
    SELECT LOWER(TRIM(ea."Game")) AS game_key
    FROM main.early_access ea
),
joined AS (
    SELECT
        b.*,
        CASE WHEN ea.game_key IS NOT NULL THEN 1 ELSE 0 END AS is_early_access
    FROM base b
    LEFT JOIN ea_norm ea
      ON LOWER(TRIM(b.game)) = ea.game_key
),
enriched AS (
    SELECT
        j.*,
        -- numeric price + finer buckets with explicit "At $60"
        CAST(j.price AS DOUBLE) AS numeric_price,
        CASE
            WHEN CAST(j.price AS DOUBLE) = 0  THEN 'Free'
            WHEN CAST(j.price AS DOUBLE) < 5  THEN 'Below $5'
            WHEN CAST(j.price AS DOUBLE) < 10 THEN 'Below $10'
            WHEN CAST(j.price AS DOUBLE) < 20 THEN 'Below $20'
            WHEN CAST(j.price AS DOUBLE) < 30 THEN 'Below $30'
            WHEN CAST(j.price AS DOUBLE) < 60 THEN 'Below $60'
            WHEN CAST(j.price AS DOUBLE) = 60 THEN 'At $60'
            ELSE 'Above $60'
        END AS price_range,

        -- owners split (owners is like 0-20000)
        TRY_CAST(SPLIT_PART(j.owners, '-', 1) AS DOUBLE) AS owners_min,
        TRY_CAST(SPLIT_PART(j.owners, '-', 2) AS DOUBLE) AS owners_max,
        (TRY_CAST(SPLIT_PART(j.owners, '-', 1) AS DOUBLE)
       + TRY_CAST(SPLIT_PART(j.owners, '-', 2) AS DOUBLE)) / 2.0 AS owners_estimate,
        (TRY_CAST(SPLIT_PART(j.owners, '-', 2) AS DOUBLE)
       - TRY_CAST(SPLIT_PART(j.owners, '-', 1) AS DOUBLE)) AS owners_range,

        -- parse release date
        COALESCE(
            TRY_STRPTIME(j.release_date, '%Y-%m-%d'),
            TRY_STRPTIME(j.release_date, '%b %d, %Y'),
            TRY_STRPTIME(j.release_date, '%d %b %Y')
        ) AS release_dt
    FROM joined j
),
final_rows AS (
    SELECT
        e.*,
        CASE WHEN e.is_early_access = 1 THEN 'Early Access' ELSE 'Full Release' END AS release_type,
        EXTRACT(YEAR FROM e.release_dt)    AS release_year,
        EXTRACT(QUARTER FROM e.release_dt) AS release_quarter
    FROM enriched e
)
SELECT
    -- Overall rank
    ROW_NUMBER() OVER (
        ORDER BY owners_estimate DESC NULLS LAST
    ) AS popularity_rank_overall,

    -- Rank within release type
    ROW_NUMBER() OVER (
        PARTITION BY release_type
        ORDER BY owners_estimate DESC NULLS LAST
    ) AS popularity_rank_in_type,

    -- Rank within price bucket
    ROW_NUMBER() OVER (
        PARTITION BY price_range
        ORDER BY owners_estimate DESC NULLS LAST
    ) AS rank_in_price_range,

    -- Rank within release year
    ROW_NUMBER() OVER (
        PARTITION BY release_year
        ORDER BY owners_estimate DESC NULLS LAST
    ) AS rank_in_release_year,

    final_rows.*
FROM final_rows
ORDER BY owners_estimate DESC NULLS LAST;
""").fetchdf()

# ---------------- 2) Light typing/sanity ----------------
num_cols = [
    'numeric_price','owners_min','owners_max','owners_estimate','owners_range',
    'popularity_rank_overall','popularity_rank_in_type','rank_in_price_range','rank_in_release_year',
    'release_year'
]
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce')

CURRENT_YEAR = pd.Timestamp.now().year
# ==== switch from 5 years to 10 years ====
CUTOFF_YEAR  = CURRENT_YEAR - 9
years_full   = list(range(int(CUTOFF_YEAR), int(CURRENT_YEAR) + 1))

dfN = df[df['release_year'].notna() & (df['release_year'] >= CUTOFF_YEAR)].copy()

print(f"\nRelease counts last {len(years_full)} years:")
print(dfN.groupby(['release_year','release_type']).size())


# ---------------- Bump Chart with Insights Panel (now includes Overall Takeaways) ----------------
CURRENT_YEAR = pd.Timestamp.now().year
YEARS_5 = list(range(CURRENT_YEAR - 4, CURRENT_YEAR + 1))

# Filter last 5 years
df5_ranks = (
    df.dropna(subset=['release_year','release_type'])
      .query("release_year >= @YEARS_5[0]")
      .copy()
)

rank_metrics = [
    ('popularity_rank_overall', 'Overall Rank',
     'Rank of the game compared to ALL games in the dataset (1 = most owners).'),
    ('popularity_rank_in_type', 'Rank in Type',
     'Rank of the game only among games with the SAME release type (EA or Full).'),
    ('rank_in_price_range', 'Rank in Price Range',
     'Rank of the game only among games in the SAME price bucket.'),
    ('rank_in_release_year', 'Rank in Release Year',
     'Rank of the game only among games released in the SAME year.')
]

# Create figure with extra row for insights
fig = plt.figure(figsize=(13, 9))
gs = plt.GridSpec(3, 2, height_ratios=[1, 1, 0.75])  # taller insights block

axes = [
    fig.add_subplot(gs[0, 0]),
    fig.add_subplot(gs[0, 1]),
    fig.add_subplot(gs[1, 0]),
    fig.add_subplot(gs[1, 1]),
]
ax_text = fig.add_subplot(gs[2, :])  # full-width insights panel

for ax, (rank_col, rank_label, rank_desc) in zip(axes, rank_metrics):
    med_ranks = (
        df5_ranks
          .groupby(['release_year','release_type'])[rank_col]
          .median()
          .unstack('release_type')
          .reindex(index=YEARS_5, columns=['Early Access','Full Release'])
    )

    ax.plot(med_ranks.index, med_ranks['Early Access'], marker='o', linestyle='--', label='Early Access')
    ax.plot(med_ranks.index, med_ranks['Full Release'], marker='o', linestyle='-',  label='Full Release')

    ax.set_title(f"{rank_label} (Median Rank)", pad=10)
    ax.set_ylabel("Median Rank (Lower is better)")
    ax.set_xticks(YEARS_5)
    ax.set_xticklabels([str(y) for y in YEARS_5])
    ax.grid(True, axis='y', alpha=0.3)

    # Description under each subplot
    ax.text(0.5, -0.25, rank_desc, ha='center', va='top',
            fontsize=8, transform=ax.transAxes, wrap=True)

# One legend for all charts
fig.legend(['Early Access', 'Full Release'],
           loc='upper right', bbox_to_anchor=(0.96, 0.97),
           frameon=True, fontsize=9)

# ---- Insights panel text (includes Overall Takeaways) ----
insights = """
Key Insights
• Full Release generally leads in absolute popularity (Overall Rank), but EA is competitive in some years.
• EA tends to rank better within contextual cohorts (Release Year; within EA Type), signaling strong relative performance.
• Pricing cohorts still favor Full Release on median, but gaps are not uniform across years.

---------------------------------------------------------------------------------------------------------------------------

METRIC-BY-METRIC INSIGHTS

[Overall Rank]
• Full Release titles typically achieve better median overall ranks than EA.
• EA shows higher volatility; occasional years narrow the gap.

[Rank in Type]
• EA maintains strong median ranks within its own category—often near the top of the EA distribution.
• Full Release median ranks within its large category remain higher (worse) than EA’s within EA.

[Rank in Price Range]
• Full Release outperforms EA within price buckets on median rank.
• EA is steady in pricing cohorts but usually trails Full Release.

[Rank in Release Year]
• EA frequently achieves better median rank among titles released in the same year.
• 2025 shows a notable EA advantage year-cohort wise.

—
Interpretation: Lower median rank = better performance (1 = best). EA’s relative strengths show up in like-for-like comparisons (same year / same type), while Full Release dominates in absolute popularity and most price-cohorts.
"""
ax_text.axis('off')
ax_text.text(
    0.01, 0.96, wrap_text(insights.strip(), width=155),
    fontsize=10, ha='left', va='top',
    bbox=dict(facecolor='white', alpha=0.65, edgecolor='none', boxstyle='round,pad=0.4')
)

fig.suptitle("Median Rank by Year & Release Type — Last 5 Years", fontsize=14, fontweight='bold', y=0.995)
plt.subplots_adjust(hspace=0.95, wspace=0.35, top=0.94, bottom=0.05)
plt.show()
# ---------------- Plot B: 4 line charts (EA vs Full) + single INSIGHTS panel below ----------------
pm_src = dfN.dropna(subset=['release_year','release_type','price_range']).copy()
pm_src['_one'] = 1.0

counts = (
    pm_src.pivot_table(
        index=['release_year','release_type'],
        columns='price_range',
        values='_one',
        aggfunc='sum',
        fill_value=0.0,
    )
)

row_sums  = counts.sum(axis=1).replace(0, np.nan)
price_mix = (counts.div(row_sums, axis=0) * 100.0)

price_order = ["Free", "Below $5", "Below $10", "Below $20", "Below $30", "Below $60", "At $60", "Above $60"]
price_mix   = price_mix.reindex(columns=price_order)

def series_for(rt: str, bucket: str) -> pd.Series:
    if 'release_type' not in price_mix.index.names:
        return pd.Series(index=years_full, dtype=float)
    if rt not in price_mix.index.get_level_values('release_type'):
        return pd.Series(index=years_full, dtype=float)
    s = price_mix.xs(rt, level='release_type', drop_level=False).get(bucket)
    if s is None:
        return pd.Series(index=years_full, dtype=float)
    return s.droplevel('release_type').reindex(years_full)

groups = [
    ("Free", ["Free"]),
    ("Below $5 and Below $10", ["Below $5", "Below $10"]),
    ("Below $20 and Below $30", ["Below $20", "Below $30"]),
    ("At $60 and Above $60", ["At $60", "Above $60"]),
]
scale_map = {"Free": 20, "Below $5 and Below $10": 40, "Below $20 and Below $30": 50, "At $60 and Above $60": 2}

fig = plt.figure(figsize=(13, 10.5))
gs = gridspec.GridSpec(3, 2, height_ratios=[1.0, 1.0, 0.65])

axes = [
    fig.add_subplot(gs[0, 0]),
    fig.add_subplot(gs[0, 1]),
    fig.add_subplot(gs[1, 0]),
    fig.add_subplot(gs[1, 1]),
]
ax_text = fig.add_subplot(gs[2, :])

for ax, (title, buckets) in zip(axes, groups):
    legend_patches, legend_labels = [], []
    ax.set_title(title, pad=10)
    for bucket in buckets:
        ea = series_for('Early Access', bucket)
        fr = series_for('Full Release', bucket)
        if ea.notna().any():
            line_ea, = ax.plot(ea.index, ea.values, linestyle='--', marker='o', label=f"{bucket} — EA")
            legend_patches.append(line_ea); legend_labels.append(line_ea.get_label())
        if fr.notna().any():
            line_fr, = ax.plot(fr.index, fr.values, linestyle='-', marker='o', label=f"{bucket} — Full")
            legend_patches.append(line_fr); legend_labels.append(line_fr.get_label())

    ax.set_ylabel("% of releases")
    ax.set_ylim(0, scale_map[title])
    ax.set_xticks(years_full)
    ax.set_xticklabels([str(y) for y in years_full])
    ax.set_xlim(min(years_full), max(years_full))
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100))
    ax.grid(True, axis='y', alpha=0.4)

    ax.legend(
        legend_patches, legend_labels,
        loc="upper center", bbox_to_anchor=(0.5, -0.26),
        ncol=2, fontsize=9, frameon=True, framealpha=1, fancybox=True,
        edgecolor='black', handlelength=2
    )

for ax in axes:
    ax.set_xlabel("Release Year (calendar)")

ax_text.axis('off')
insights = """
KEY INSIGHTS (last ten release years)

[Free]
• Both Early Access and Full Release shares trend downward.

[Below $5 and Below $10]
• Stable overall; Full Release tends to be higher than EA with slight decline.

[Below $20 and Below $30]
• EA under $20 grows in share; under $30 remains small and fairly stable.

[At $60 and Above $60]
• Very small shares for both EA and Full; consistent with AAA pricing rarely using EA.

-----------------------------------------
Note: “% of releases” = within a given year and release type, the percentage of titles in the shown price bucket.
"""
ax_text.text(
    0.01, 0.92, wrap_text(insights.strip(), width=155),
    fontsize=10, ha='left', va='top',
    bbox=dict(facecolor='white', alpha=0.65, edgecolor='none', boxstyle='round,pad=0.4')
)

fig.suptitle("Price Range Mix — EA vs Full (trends over last 10 years)", fontsize=12, fontweight='bold', y=0.995)
plt.subplots_adjust(hspace=0.95, wspace=0.35, top=0.94, bottom=0.05)
plt.show()

# ---------------- Plot C: Hybrid Metrics Sankey Diagram ----------------

# Force Plotly to open in your default web browser
pio.renderers.default = "browser"

# Filter for last 5 years
YEARS_5 = list(range(CURRENT_YEAR - 4, CURRENT_YEAR + 1))
df_sankey = (
    df.dropna(subset=['developers', 'release_type', 'price_range', 'owners_estimate'])
      .query("release_year in @YEARS_5")
      .copy()
)

# Focus on top developers by Owners Estimate
top_devs = (
    df_sankey.groupby('developers')['owners_estimate']
    .sum()
    .nlargest(10)
    .index
)
df_sankey = df_sankey[df_sankey['developers'].isin(top_devs)]

# Helper to build "Name pct% (xxx.xk)" labels
def labels_with_pct(series: pd.Series) -> list:
    total = series.sum()
    if total <= 0:
        return [f"{idx} 0.00% (0.0k)" for idx in series.index]
    return [f"{idx} {val/total*100:.2f}% ({val/1000:.1f}k)" for idx, val in series.items()]

# Build node labels
dev_totals   = df_sankey.groupby('developers')['owners_estimate'].sum().reindex(top_devs)
type_totals  = df_sankey.groupby('release_type')['owners_estimate'].sum().sort_index()
price_totals = df_sankey.groupby('price_range')['owners_estimate'].sum().sort_index()

dev_labels   = labels_with_pct(dev_totals)
type_labels  = labels_with_pct(type_totals)
price_labels = labels_with_pct(price_totals)

node_labels = dev_labels + type_labels + price_labels

# Map labels → node index
node_index = {name: i for i, name in enumerate(node_labels)}

# Links: Developers → Release Type
links_dev_type = (
    df_sankey.groupby(['developers', 'release_type'])['owners_estimate']
    .sum()
    .reset_index()
)
links_dev_type['source'] = links_dev_type['developers'].map(
    lambda x: node_index[dev_labels[dev_totals.index.get_loc(x)]]
)
links_dev_type['target'] = links_dev_type['release_type'].map(
    lambda x: node_index[type_labels[type_totals.index.get_loc(x)]]
)
links_dev_type['value']  = links_dev_type['owners_estimate']

# Links: Release Type → Price Range
links_type_price = (
    df_sankey.groupby(['release_type', 'price_range'])['owners_estimate']
    .sum()
    .reset_index()
)
links_type_price['source'] = links_type_price['release_type'].map(
    lambda x: node_index[type_labels[type_totals.index.get_loc(x)]]
)
links_type_price['target'] = links_type_price['price_range'].map(
    lambda x: node_index[price_labels[price_totals.index.get_loc(x)]]
)
links_type_price['value']  = links_type_price['owners_estimate']

# Combine links
link_df = pd.concat([links_dev_type, links_type_price], ignore_index=True)

# Sankey Diagram
fig_c = go.Figure(data=[go.Sankey(
    node=dict(
        pad=24,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=node_labels,
        color="rgba(150,170,220,0.35)"
    ),
    link=dict(
        source=link_df['source'],
        target=link_df['target'],
        value=link_df['value'],
        color="rgba(140,140,200,0.35)"
    )
)])

fig_c.update_layout(
    title_text="Top Developers → Release Type → Price Range — Owners Estimate (Last 5 Years)",
    font_size=11,
    margin=dict(l=10, r=10, t=50, b=10)
)

# Opens in your default browser
fig_c.show()