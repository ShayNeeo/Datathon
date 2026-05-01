"""
Part 2 - Chart 4: COGS Margin Danger Zones
Chart 5: Day-of-Month Payday Effect
Chart 6: Promotion Campaign ROI
"""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 150, "savefig.bbox": "tight",
})

DATA = Path(r"c:\Users\TRIDELL\Desktop\vinuni\datathon-2026-round-1")
OUT  = Path(r"c:\Users\TRIDELL\Desktop\vinuni\part2\charts")
sales = pd.read_csv(DATA / "sales.csv", parse_dates=["Date"])
promo = pd.read_csv(DATA / "promotions.csv", parse_dates=["start_date","end_date"])
sales["year"]  = sales.Date.dt.year
sales["month"] = sales.Date.dt.month
sales["day"]   = sales.Date.dt.day
sales["dow"]   = sales.Date.dt.dayofweek
sales["margin"] = 1 - sales["COGS"] / sales["Revenue"]
pre = sales[sales.year.between(2013, 2018)]

# ═══════════════════════════════════════════════════════════════════════
# CHART 4: COGS Margin Analysis - Monthly Danger Zones
# ═══════════════════════════════════════════════════════════════════════
print("[4/6] COGS Margin Danger Zones...")
monthly_margin = pre.groupby("month")["margin"].mean() * 100
monthly_rev = pre.groupby("month")["Revenue"].mean() / 1e6

fig, ax1 = plt.subplots(figsize=(14, 7))

# Bar chart for margin
colors = []
for m in range(1, 13):
    mg = monthly_margin[m]
    if mg < 5:
        colors.append("#EF4444")   # Danger
    elif mg < 12:
        colors.append("#F59E0B")   # Warning
    else:
        colors.append("#93FA64")   # Healthy
bars = ax1.bar(range(1, 13), monthly_margin.values, color=colors, alpha=0.85, width=0.6)

# Danger zone line
ax1.axhline(5, color="#EF4444", ls="--", lw=1.5, alpha=0.6)
ax1.text(12.5, 5.5, "DANGER ZONE (< 5%)", fontsize=8, color="#EF4444", fontweight="bold", ha="right")
ax1.axhline(12, color="#F59E0B", ls="--", lw=1, alpha=0.4)

# Revenue overlay
ax2 = ax1.twinx()
ax2.plot(range(1, 13), monthly_rev.values, "o-", color="#1E293B", lw=2, ms=7, zorder=5)
ax2.set_ylabel("Avg Revenue (M VND)", color="#1E293B", fontsize=12)
ax2.tick_params(axis="y", labelcolor="#1E293B")

# Annotate danger months
for m in [7, 8, 12]:
    mg = monthly_margin[m]
    ax1.annotate(f"{mg:.1f}%", xy=(m, mg), xytext=(m, mg + 3),
                 fontsize=10, fontweight="bold", color="#EF4444", ha="center",
                 arrowprops=dict(arrowstyle="->", color="#EF4444", lw=1.2))

# Annotate best month
best_m = monthly_margin.idxmax()
ax1.annotate(f"Best: {monthly_margin[best_m]:.1f}%", xy=(best_m, monthly_margin[best_m]),
             xytext=(best_m+1.5, monthly_margin[best_m]+2),
             fontsize=10, fontweight="bold", color="#4ADE80",
             arrowprops=dict(arrowstyle="->", color="#4ADE80", lw=1.2))

ax1.set_xticks(range(1, 13))
ax1.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
ax1.set_ylabel("Gross Margin (%)", fontsize=12)
ax1.set_title("Monthly Margin vs Revenue: The Profitability Paradox\nHigh-Revenue Months Often Have Lowest Margins",
              fontsize=14, fontweight="bold", pad=15)
ax1.set_ylim(0, 25)

legend = [
    mpatches.Patch(color="#93FA64", label="Healthy (> 12%)"),
    mpatches.Patch(color="#F59E0B", label="Warning (5-12%)"),
    mpatches.Patch(color="#EF4444", label="Danger (< 5%)"),
    plt.Line2D([0],[0], color="#1E293B", marker="o", label="Revenue"),
]
ax1.legend(handles=legend, loc="upper left", framealpha=0.9)
fig.savefig(OUT / "chart4_margin_danger.png")
plt.close()
print("  -> chart4_margin_danger.png")

# ═══════════════════════════════════════════════════════════════════════
# CHART 5: Day-of-Month Revenue Pattern (Payday Effect)
# ═══════════════════════════════════════════════════════════════════════
print("[5/6] Day-of-Month Payday Effect...")
dom_avg = pre.groupby("day")["Revenue"].mean()
dom_ratio = dom_avg / dom_avg.mean()

fig, ax = plt.subplots(figsize=(14, 6))
colors = ["#EF4444" if r > 1.3 else "#F59E0B" if r > 1.1 else
          "#334155" if r < 0.85 else "#94A3B8" for r in dom_ratio.values]

ax.bar(dom_ratio.index, (dom_ratio.values - 1) * 100, color=colors, alpha=0.85, width=0.7)
ax.axhline(0, color="#374151", lw=1)

# Highlight key days
highlights = {
    1:  ("Day 1: +{:.0f}%\n(Month Start Rush)", "#EF4444", 15),
    5:  ("Day 5: {:.0f}%\n(Post-Rush Dip)", "#334155", -15),
    15: ("Day 15: +{:.0f}%\n(Mid-Month Payday)", "#F59E0B", 12),
    30: ("Day 30: +{:.0f}%\n(Month-End Surge)", "#EF4444", 15),
}
for day, (template, color, offset) in highlights.items():
    if day in dom_ratio.index:
        pct = (dom_ratio[day] - 1) * 100
        label = template.format(abs(pct))
        y = pct
        ax.annotate(label, xy=(day, y), xytext=(day, y + offset),
                    fontsize=9, fontweight="bold", color=color, ha="center",
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.5),
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                              edgecolor=color, alpha=0.9))

ax.set_xlabel("Day of Month", fontsize=12)
ax.set_ylabel("Revenue vs Average (%)", fontsize=12)
ax.set_title("Day-of-Month Revenue Pattern: The Vietnamese Payday Effect\n"
             "Revenue Spikes at Month Start (Day 1) and Month End (Day 30)",
             fontsize=14, fontweight="bold", pad=15)
ax.set_xticks(range(1, 32))
fig.savefig(OUT / "chart5_payday_effect.png")
plt.close()
print("  -> chart5_payday_effect.png")

# ═══════════════════════════════════════════════════════════════════════
# CHART 6: Promotion Campaign Impact Analysis
# ═══════════════════════════════════════════════════════════════════════
print("[6/6] Promotion Campaign Impact...")

campaign_types = {
    "Spring Sale": "spring", "Mid-Year Sale": "midyear",
    "Fall Launch": "fall", "Year-End Sale": "yearend",
    "Urban Blowout": "urban", "Rural Special": "rural",
}

results = []
for _, p in promo.iterrows():
    start, end = p["start_date"], p["end_date"]
    duration = (end - start).days + 1
    # During promo
    during = pre[(pre.Date >= start) & (pre.Date <= end)]
    # Before promo (same duration)
    before = pre[(pre.Date >= start - pd.Timedelta(days=duration)) & (pre.Date < start)]
    if len(during) > 0 and len(before) > 0:
        lift = (during.Revenue.mean() - before.Revenue.mean()) / before.Revenue.mean() * 100
        margin_during = during.margin.mean() * 100
        ctype = "other"
        for k, v in campaign_types.items():
            if k in p["promo_name"]:
                ctype = v; break
        results.append({"campaign": ctype, "lift": lift, "margin": margin_during,
                        "rev_during": during.Revenue.mean()/1e6, "discount": p["discount_value"]})

df_camp = pd.DataFrame(results)
camp_avg = df_camp.groupby("campaign").agg(
    lift=("lift", "mean"), margin=("margin", "mean"),
    rev=("rev_during", "mean"), discount=("discount", "mean")
).sort_values("lift", ascending=True)

fig, ax = plt.subplots(figsize=(12, 7))
colors_camp = {"spring":"#93FA64","midyear":"#334155","fall":"#F59E0B",
               "yearend":"#EF4444","urban":"#8B5CF6","rural":"#EC4899"}

y_pos = range(len(camp_avg))
bar_colors = [colors_camp.get(c, "#94A3B8") for c in camp_avg.index]
bars = ax.barh(y_pos, camp_avg["lift"].values, color=bar_colors, alpha=0.85, height=0.6)

# Add value labels
for i, (idx, row) in enumerate(camp_avg.iterrows()):
    sign = "+" if row["lift"] > 0 else ""
    ax.text(row["lift"] + (2 if row["lift"] > 0 else -2), i,
            f"{sign}{row['lift']:.1f}% lift | Margin: {row['margin']:.1f}%",
            va="center", fontsize=10, fontweight="bold",
            color=colors_camp.get(idx, "#374151"))

ax.set_yticks(y_pos)
ax.set_yticklabels([c.replace("_"," ").title() for c in camp_avg.index], fontsize=11)
ax.axvline(0, color="#374151", lw=1)
ax.set_xlabel("Revenue Lift vs Pre-Promo Period (%)", fontsize=12)
ax.set_title("Campaign Effectiveness: Revenue Lift vs Margin Trade-off\nNot All Promotions Are Created Equal",
             fontsize=14, fontweight="bold", pad=15)
fig.savefig(OUT / "chart6_campaign_impact.png")
plt.close()
print("  -> chart6_campaign_impact.png")

print("\nBatch 2 DONE!")
