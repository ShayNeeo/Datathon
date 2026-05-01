"""
Part 2 - Chart 1: Revenue Timeline with COVID Regime
Chart 2: Monthly Seasonality Heatmap
Chart 3: Tet Lunar New Year Effect
"""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
from pathlib import Path

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 150, "savefig.bbox": "tight", "savefig.pad_inches": 0.3,
})

DATA = Path(r"c:\Users\TRIDELL\Desktop\vinuni\datathon-2026-round-1")
OUT  = Path(r"c:\Users\TRIDELL\Desktop\vinuni\part2\charts")
sales = pd.read_csv(DATA / "sales.csv", parse_dates=["Date"])
sales["year"]  = sales.Date.dt.year
sales["month"] = sales.Date.dt.month

TET = {2013:"2013-02-10",2014:"2014-01-31",2015:"2015-02-19",2016:"2016-02-08",
       2017:"2017-01-28",2018:"2018-02-16",2019:"2019-02-05",2020:"2020-01-25",
       2021:"2021-02-12",2022:"2022-02-01"}

# ═══════════════════════════════════════════════════════════════════════
# CHART 1: Revenue Timeline with COVID Regime Overlay
# ═══════════════════════════════════════════════════════════════════════
print("[1/3] Revenue Timeline...")
fig, ax = plt.subplots(figsize=(16, 6))

# 30-day rolling average
sales_sorted = sales.sort_values("Date")
roll = sales_sorted.set_index("Date")["Revenue"].rolling(30).mean()

ax.plot(roll.index, roll.values / 1e6, color="#1E293B", lw=1.5, alpha=0.9)
ax.fill_between(roll.index, roll.values / 1e6, alpha=0.08, color="#1E293B")

# COVID shading
covid_start = pd.Timestamp("2020-01-01")
covid_end   = pd.Timestamp("2021-12-31")
ax.axvspan(covid_start, covid_end, alpha=0.15, color="#EF4444", zorder=0)
ax.text(pd.Timestamp("2020-07-01"), ax.get_ylim()[1]*0.92, "COVID-19\nImpact Zone",
        ha="center", fontsize=10, color="#EF4444", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#EF4444", alpha=0.9))

# Growth phases
phases = [
    ("2013-01-01","2015-12-31","Growth\nPhase","#93FA64"),
    ("2016-01-01","2018-12-31","Maturity\nPhase","#F59E0B"),
    ("2022-01-01","2022-12-31","Recovery","#8B5CF6"),
]
for s, e, label, color in phases:
    mid = pd.Timestamp(s) + (pd.Timestamp(e) - pd.Timestamp(s)) / 2
    ax.annotate(label, xy=(mid, 0.3), fontsize=8, ha="center", color=color, fontweight="bold")

# Peak & Trough annotations
peak_date = sales_sorted.loc[sales_sorted.Revenue.idxmax(), "Date"]
peak_val  = sales_sorted.Revenue.max()
trough = sales_sorted[(sales_sorted.Date >= "2020-01-01") & (sales_sorted.Date <= "2021-12-31")]
trough_date = trough.loc[trough.Revenue.idxmin(), "Date"]
trough_val  = trough.Revenue.min()

ax.annotate(f"Peak: {peak_val/1e6:.1f}M", xy=(peak_date, peak_val/1e6),
            xytext=(peak_date + pd.Timedelta(days=120), peak_val/1e6 + 1),
            fontsize=9, fontweight="bold", color="#4ADE80",
            arrowprops=dict(arrowstyle="->", color="#4ADE80", lw=1.5))

ax.annotate(f"COVID Trough:\n{trough_val/1e6:.1f}M (-82%)", xy=(trough_date, trough_val/1e6),
            xytext=(trough_date + pd.Timedelta(days=150), trough_val/1e6 + 2),
            fontsize=9, fontweight="bold", color="#DC2626",
            arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.5))

# YoY labels
for yr in [2013,2015,2017,2019,2022]:
    ymean = sales[sales.year==yr].Revenue.mean()/1e6
    ax.plot(pd.Timestamp(f"{yr}-07-01"), ymean, "o", color="#1E293B", ms=4)

ax.set_xlabel(""); ax.set_ylabel("Revenue (Million VND)", fontsize=12)
ax.set_title("10-Year Revenue Journey: From Growth to COVID Crisis to Recovery",
             fontsize=14, fontweight="bold", pad=15)
ax.set_ylim(bottom=0)
fig.savefig(OUT / "chart1_revenue_timeline.png")
plt.close()
print("  -> chart1_revenue_timeline.png")

# ═══════════════════════════════════════════════════════════════════════
# CHART 2: Monthly Seasonality Heatmap
# ═══════════════════════════════════════════════════════════════════════
print("[2/3] Monthly Seasonality Heatmap...")
monthly = sales.groupby(["year","month"])["Revenue"].mean().unstack(fill_value=0) / 1e6
years_show = range(2013, 2023)
monthly = monthly.loc[monthly.index.isin(years_show)]

fig, ax = plt.subplots(figsize=(14, 7))
im = ax.imshow(monthly.values, cmap="YlOrRd", aspect="auto", interpolation="nearest")

ax.set_xticks(range(12))
ax.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
ax.set_yticks(range(len(monthly)))
ax.set_yticklabels(monthly.index.astype(int))

# Add text annotations
for i in range(len(monthly)):
    for j in range(12):
        val = monthly.values[i, j]
        color = "white" if val > monthly.values.max() * 0.6 else "black"
        ax.text(j, i, f"{val:.1f}", ha="center", va="center", fontsize=8, color=color)

# Highlight COVID years
for idx, yr in enumerate(monthly.index):
    if yr in [2020, 2021]:
        rect = plt.Rectangle((-0.5, idx-0.5), 12, 1, fill=False,
                              edgecolor="#EF4444", linewidth=2.5, linestyle="--")
        ax.add_patch(rect)

ax.annotate("COVID Years\n(Revenue Collapse)", xy=(11.8, 7.5),
            fontsize=10, color="#EF4444", fontweight="bold", ha="right")

# Highlight peak months
ax.annotate("Peak Season\n(Apr-Jun)", xy=(4, -1.2), fontsize=9,
            color="#B45309", fontweight="bold", ha="center")
ax.annotate("", xy=(3, -0.7), xytext=(5, -0.7),
            arrowprops=dict(arrowstyle="<->", color="#B45309", lw=2))

cbar = fig.colorbar(im, ax=ax, shrink=0.8, label="Avg Daily Revenue (M VND)")
ax.set_title("Revenue Seasonality Heatmap: Year x Month\nDarker = Higher Revenue",
             fontsize=14, fontweight="bold", pad=15)
fig.savefig(OUT / "chart2_seasonality_heatmap.png")
plt.close()
print("  -> chart2_seasonality_heatmap.png")

# ═══════════════════════════════════════════════════════════════════════
# CHART 3: Tet Lunar New Year Effect
# ═══════════════════════════════════════════════════════════════════════
print("[3/3] Tet Effect Analysis...")
pre_covid = sales[sales.year.between(2013, 2018)].copy()

windows = []
for yr, tet_str in TET.items():
    if yr > 2018: continue
    tet = pd.Timestamp(tet_str)
    for delta in range(-30, 31):
        d = tet + pd.Timedelta(days=delta)
        row = pre_covid[pre_covid.Date == d]
        if len(row) > 0:
            windows.append({"delta": delta, "revenue": row.Revenue.values[0], "year": yr})

df_tet = pd.DataFrame(windows)
avg_tet = df_tet.groupby("delta")["revenue"].mean() / 1e6

fig, ax = plt.subplots(figsize=(14, 6))
colors = np.where(avg_tet.index < 0, "#F59E0B",
         np.where(avg_tet.index <= 7, "#EF4444", "#93FA64"))

ax.bar(avg_tet.index, avg_tet.values, color=colors, alpha=0.8, width=0.8)
baseline = pre_covid.Revenue.mean() / 1e6
ax.axhline(baseline, color="#6B7280", ls="--", lw=1, alpha=0.7)
ax.text(25, baseline + 0.15, f"Baseline: {baseline:.1f}M", fontsize=9, color="#6B7280")

# Phase annotations with boxes
phases_tet = [
    (-25, -1, "PRE-TET SURGE\n+40-80% Revenue", "#F59E0B"),
    (0, 7, "TET HOLIDAY\n-50% Revenue (DIP)", "#EF4444"),
    (8, 20, "POST-TET RECOVERY\nGradual Return", "#93FA64"),
]
for s, e, label, color in phases_tet:
    mid = (s + e) / 2
    y_pos = avg_tet.max() * 1.05
    ax.annotate(label, xy=(mid, y_pos), fontsize=9, ha="center",
                fontweight="bold", color=color,
                bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                          edgecolor=color, alpha=0.9))
    ax.axvspan(s-0.5, e+0.5, alpha=0.05, color=color)

# Peak spike arrow
peak_delta = avg_tet.idxmax()
peak_rev = avg_tet.max()
ax.annotate(f"Peak: {peak_rev:.1f}M\n(Day {peak_delta})",
            xy=(peak_delta, peak_rev), xytext=(peak_delta+8, peak_rev+0.5),
            fontsize=9, fontweight="bold", color="#B45309",
            arrowprops=dict(arrowstyle="->", color="#B45309", lw=1.5))

ax.set_xlabel("Days Relative to Tet (Day 0 = Tet)", fontsize=12)
ax.set_ylabel("Avg Revenue (Million VND)", fontsize=12)
ax.set_title("The Tet Effect: Vietnam's Largest Commercial Event\nPre-COVID Average (2013-2018)",
             fontsize=14, fontweight="bold", pad=15)
ax.set_ylim(bottom=0)

legend_elements = [
    mpatches.Patch(facecolor="#F59E0B", alpha=0.8, label="Pre-Tet (Shopping Frenzy)"),
    mpatches.Patch(facecolor="#EF4444", alpha=0.8, label="Tet Holiday (Store Closure)"),
    mpatches.Patch(facecolor="#93FA64", alpha=0.8, label="Post-Tet (Recovery)"),
]
ax.legend(handles=legend_elements, loc="upper right", framealpha=0.9)
fig.savefig(OUT / "chart3_tet_effect.png")
plt.close()
print("  -> chart3_tet_effect.png")

print("\nBatch 1 DONE!")
