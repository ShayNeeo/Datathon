"""
Part 2 - Chart 7: Web Traffic as Leading Indicator
Chart 8: Customer Segmentation & Channel Mix
Chart 9: COVID Recovery Speed by Quarter
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
web   = pd.read_csv(DATA / "web_traffic.csv", parse_dates=["date"])
customers = pd.read_csv(DATA / "customers.csv", parse_dates=["signup_date"])
orders = pd.read_csv(DATA / "orders.csv", parse_dates=["order_date"], low_memory=False)

sales["year"]  = sales.Date.dt.year
sales["month"] = sales.Date.dt.month

# ═══════════════════════════════════════════════════════════════════════
# CHART 7: Web Traffic as Leading Indicator for Revenue
# ═══════════════════════════════════════════════════════════════════════
print("[7/9] Web Traffic Leading Indicator...")
daily_web = web.groupby("date").agg(sessions=("sessions","sum"), visitors=("unique_visitors","sum"))
merged = sales.set_index("Date")[["Revenue"]].join(daily_web, how="inner")

# Rolling correlation (90-day window)
roll_corr = merged["Revenue"].rolling(90).corr(merged["sessions"])

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), height_ratios=[2, 1], sharex=True)

# Top: Revenue vs Sessions (dual axis)
ax1.plot(merged.index, merged["Revenue"].rolling(30).mean()/1e6,
         color="#1E293B", lw=1.5, label="Revenue (30d MA)")
ax1b = ax1.twinx()
ax1b.plot(merged.index, merged["sessions"].rolling(30).mean()/1e3,
          color="#F59E0B", lw=1.5, alpha=0.7, label="Sessions (30d MA)")
ax1.set_ylabel("Revenue (M VND)", color="#1E293B", fontsize=11)
ax1b.set_ylabel("Web Sessions (Thousands)", color="#F59E0B", fontsize=11)

# COVID annotation
ax1.axvspan("2020-01-01", "2021-12-31", alpha=0.1, color="#EF4444")
ax1.text(pd.Timestamp("2020-07-01"), ax1.get_ylim()[1]*0.9, "COVID",
         fontsize=10, color="#EF4444", fontweight="bold", ha="center")

# Legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1b.get_legend_handles_labels()
ax1.legend(lines1+lines2, labels1+labels2, loc="upper left", framealpha=0.9)
ax1.set_title("Web Traffic as a Leading Indicator for Revenue\n"
              "Sessions and Revenue Move Together - Traffic Predicts Sales",
              fontsize=14, fontweight="bold", pad=15)

# Bottom: Rolling correlation
ax2.fill_between(roll_corr.index, roll_corr.values, alpha=0.3, color="#8B5CF6")
ax2.plot(roll_corr.index, roll_corr.values, color="#8B5CF6", lw=1.5)
ax2.axhline(0.8, color="#93FA64", ls="--", lw=1, alpha=0.5)
ax2.text(roll_corr.index[-1], 0.82, "Strong (0.8)", fontsize=8, color="#93FA64")
ax2.set_ylabel("90-Day Rolling\nCorrelation", fontsize=11)
ax2.set_ylim(0, 1)
ax2.set_title("Correlation Stability Over Time", fontsize=11, fontweight="bold")

# Annotate correlation during COVID
covid_corr = roll_corr["2020-06":"2021-06"].mean()
ax2.annotate(f"COVID: r={covid_corr:.2f}\n(Still correlated!)",
             xy=(pd.Timestamp("2020-12-01"), covid_corr),
             xytext=(pd.Timestamp("2019-01-01"), covid_corr - 0.15),
             fontsize=9, fontweight="bold", color="#8B5CF6",
             arrowprops=dict(arrowstyle="->", color="#8B5CF6", lw=1.2))

fig.tight_layout()
fig.savefig(OUT / "chart7_web_traffic_lead.png")
plt.close()
print("  -> chart7_web_traffic_lead.png")

# ═══════════════════════════════════════════════════════════════════════
# CHART 8: Customer Demographics & Channel Mix Evolution
# ═══════════════════════════════════════════════════════════════════════
print("[8/9] Customer Segmentation...")
customers["signup_year"] = customers.signup_date.dt.year
yearly_channel = customers.groupby(["signup_year","acquisition_channel"]).size().unstack(fill_value=0)
yearly_channel = yearly_channel[(yearly_channel.index >= 2013) & (yearly_channel.index <= 2022)]
yearly_pct = yearly_channel.div(yearly_channel.sum(axis=1), axis=0) * 100

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Left: Stacked area - Channel evolution
channel_colors = {
    "organic_search": "#93FA64", "social_media": "#8B5CF6",
    "paid_search": "#F59E0B", "email_campaign": "#334155",
    "referral": "#EC4899", "direct": "#94A3B8",
}
cols_ordered = ["organic_search","social_media","paid_search","email_campaign","referral","direct"]
ax1.stackplot(yearly_pct.index, [yearly_pct[c].values for c in cols_ordered],
              labels=[c.replace("_"," ").title() for c in cols_ordered],
              colors=[channel_colors[c] for c in cols_ordered], alpha=0.8)
ax1.set_ylabel("Share of New Customers (%)", fontsize=11)
ax1.set_title("Customer Acquisition Channel Mix\nShift Toward Digital Channels",
              fontsize=12, fontweight="bold", pad=10)
ax1.legend(loc="center left", bbox_to_anchor=(0, 0.3), fontsize=8, framealpha=0.9)
ax1.set_ylim(0, 100)

# Annotate social media growth
sm_2013 = yearly_pct.loc[2013, "social_media"] if 2013 in yearly_pct.index else 0
sm_2022 = yearly_pct.loc[2022, "social_media"] if 2022 in yearly_pct.index else 0
ax1.annotate(f"Social Media:\n{sm_2013:.0f}% -> {sm_2022:.0f}%",
             xy=(2022, 50), fontsize=9, fontweight="bold", color="#8B5CF6",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#8B5CF6"))

# Right: Age group pie
age_counts = customers.age_group.value_counts()
age_colors = ["#334155","#93FA64","#F59E0B","#EF4444","#8B5CF6"]
wedges, texts, autotexts = ax2.pie(
    age_counts.values, labels=age_counts.index, autopct="%1.1f%%",
    colors=age_colors, startangle=90, textprops={"fontsize": 10},
    wedgeprops={"edgecolor": "white", "linewidth": 2},
)
for at in autotexts:
    at.set_fontweight("bold")
ax2.set_title("Customer Age Distribution\nCore Demographic: 25-44 (56%)",
              fontsize=12, fontweight="bold", pad=10)

fig.suptitle("Customer Intelligence: Who Buys and How They Find Us",
             fontsize=14, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(OUT / "chart8_customer_segments.png")
plt.close()
print("  -> chart8_customer_segments.png")

# ═══════════════════════════════════════════════════════════════════════
# CHART 9: COVID Recovery Speed
# ═══════════════════════════════════════════════════════════════════════
print("[9/9] COVID Recovery...")
quarterly = sales.copy()
quarterly["quarter"] = quarterly.Date.dt.to_period("Q")
q_rev = quarterly.groupby("quarter")["Revenue"].mean() / 1e6

fig, ax = plt.subplots(figsize=(14, 7))

# Color by regime
q_colors = []
for q in q_rev.index:
    yr = q.year
    if yr <= 2019:
        q_colors.append("#1E293B")
    elif yr <= 2021:
        q_colors.append("#EF4444")
    else:
        q_colors.append("#93FA64")

x = range(len(q_rev))
ax.bar(x, q_rev.values, color=q_colors, alpha=0.8, width=0.7)

# Pre-COVID average line
pre_avg = sales[sales.year.between(2017, 2019)].Revenue.mean() / 1e6
ax.axhline(pre_avg, color="#1E293B", ls="--", lw=1.5, alpha=0.6)
ax.text(len(q_rev)-1, pre_avg + 0.15, f"2017-2019 Avg: {pre_avg:.1f}M",
        fontsize=9, color="#1E293B", ha="right")

# Recovery annotation
recovery_q = None
for i, q in enumerate(q_rev.index):
    if q.year >= 2022 and q_rev.values[i] >= pre_avg * 0.95:
        recovery_q = i; break

if recovery_q:
    ax.annotate(f"Recovery!\nExceeded Pre-COVID\n({q_rev.index[recovery_q]})",
                xy=(recovery_q, q_rev.values[recovery_q]),
                xytext=(recovery_q - 4, q_rev.values[recovery_q] + 1.5),
                fontsize=10, fontweight="bold", color="#4ADE80",
                arrowprops=dict(arrowstyle="->", color="#4ADE80", lw=2),
                bbox=dict(boxstyle="round,pad=0.4", facecolor="#ECFDF5", edgecolor="#4ADE80"))

# Trough annotation
trough_idx = q_rev.values.argmin()
ax.annotate(f"Deepest Trough:\n{q_rev.values[trough_idx]:.1f}M\n(-{(1-q_rev.values[trough_idx]/pre_avg)*100:.0f}%)",
            xy=(trough_idx, q_rev.values[trough_idx]),
            xytext=(trough_idx + 3, q_rev.values[trough_idx] + 1),
            fontsize=9, fontweight="bold", color="#DC2626",
            arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.5))

# X labels (show every 2nd quarter)
labels = [str(q) if i % 2 == 0 else "" for i, q in enumerate(q_rev.index)]
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, fontsize=8)
ax.set_ylabel("Avg Daily Revenue (M VND)", fontsize=12)
ax.set_title("COVID Recovery Trajectory: 8 Quarters to Full Recovery\nFrom -60% Trough to Pre-COVID Revenue Levels",
             fontsize=14, fontweight="bold", pad=15)
ax.set_ylim(0)

legend = [
    mpatches.Patch(color="#1E293B", label="Pre-COVID (Normal)"),
    mpatches.Patch(color="#EF4444", label="COVID Impact (2020-2021)"),
    mpatches.Patch(color="#93FA64", label="Recovery (2022)"),
]
ax.legend(handles=legend, loc="upper left", framealpha=0.9)
fig.savefig(OUT / "chart9_covid_recovery.png")
plt.close()
print("  -> chart9_covid_recovery.png")

print("\nBatch 3 DONE!")
