
# =============================================================================
# TASK BLOCK 2 — FEATURE ENGINEERING
# Datathon 2026 | VinUni Sales Forecasting
# [ARCHITECT] spec → [AGENT] implementation
# RANDOM_SEED = 42
# =============================================================================

import os, random, json, warnings
import numpy as np
import pandas as pd
from pathlib import Path

warnings.filterwarnings("ignore")
random.seed(42)
np.random.seed(42)

# =============================================================================
# CONFIG
# =============================================================================
DATA_DIR   = Path("/content/drive/MyDrive/Colab Notebooks/vinuni/raw")
OUTPUT_DIR = Path("/content/drive/MyDrive/Colab Notebooks/vinuni/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_START = "2012-07-04"
TRAIN_END   = "2022-12-31"
TEST_START  = "2023-01-01"
TEST_END    = "2024-07-01"   # 548 ngày

# =============================================================================
# BLOCK 0 — LOAD DATA (chạy trước Block 2)
# =============================================================================
def load_all_data(data_dir: Path) -> dict:
    files = [
        "products", "customers", "geography", "promotions",
        "orders", "order_items", "payments", "shipments",
        "returns", "reviews", "sales", "sample_submission",
        "inventory", "web_traffic",
    ]
    data = {}
    for name in files:
        path = data_dir / f"{name}.csv"
        if path.exists():
            df = pd.read_csv(path, low_memory=False)
            # Auto-parse date columns
            for col in df.columns:
                if any(kw in col.lower() for kw in ["date", "snapshot"]):
                    try:
                        df[col] = pd.to_datetime(df[col])
                    except Exception:
                        pass
            data[name] = df
            print(f"  ✅ {name}: {df.shape}")
        else:
            print(f"  ⚠️  {name}: NOT FOUND")
    return data

print("Loading data...")
data = load_all_data(DATA_DIR)

df_sales    = data["sales"].copy()
df_sub      = data["sample_submission"].copy()
df_promo    = data["promotions"].copy()
df_web      = data["web_traffic"].copy()
df_orders   = data["orders"].copy()
df_items    = data["order_items"].copy()
df_returns  = data["returns"].copy()
df_reviews  = data["reviews"].copy()
df_inv      = data["inventory"].copy()

# =============================================================================
# BLOCK 1 — BUILD MASTER DATE SPINE
# Tạo date index liên tục từ TRAIN_START → TEST_END
# =============================================================================
print("\n[Block 1] Building master date spine...")

all_dates = pd.date_range(TRAIN_START, TEST_END, freq="D")
df_master = pd.DataFrame({"Date": all_dates})
df_master["is_test"] = (df_master["Date"] >= TEST_START).astype(int)

# Merge target (Revenue, COGS) từ sales.csv
df_sales["Date"] = pd.to_datetime(df_sales["Date"])
df_master = df_master.merge(df_sales[["Date", "Revenue", "COGS"]], on="Date", how="left")

# ✅ QA
assert df_master["Date"].nunique() == len(df_master), "Duplicate dates in spine!"
print(f"  Spine: {df_master.shape} | Train rows: {(df_master['is_test']==0).sum()} | Test rows: {(df_master['is_test']==1).sum()}")


# =============================================================================
# BLOCK 2A — TEMPORAL FEATURES
# =============================================================================
print("\n[Block 2A] Temporal features...")

def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    d = df["Date"]

    # --- Basic ---
    df["year"]        = d.dt.year
    df["month"]       = d.dt.month
    df["day"]         = d.dt.day
    df["day_of_week"] = d.dt.dayofweek          # 0=Mon, 6=Sun
    df["day_of_year"] = d.dt.dayofyear
    df["week_of_year"]= d.dt.isocalendar().week.astype(int)
    df["quarter"]     = d.dt.quarter
    df["is_weekend"]  = (d.dt.dayofweek >= 5).astype(int)
    df["is_month_end"]= d.dt.is_month_end.astype(int)
    df["is_month_start"] = d.dt.is_month_start.astype(int)
    df["days_in_month"] = d.dt.days_in_month

    # --- Cyclical encoding (sin/cos — không dùng raw integer) ---
    df["sin_doy"]   = np.sin(2 * np.pi * df["day_of_year"] / 365.25)
    df["cos_doy"]   = np.cos(2 * np.pi * df["day_of_year"] / 365.25)
    df["sin_dow"]   = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["cos_dow"]   = np.cos(2 * np.pi * df["day_of_week"] / 7)
    df["sin_month"] = np.sin(2 * np.pi * df["month"] / 12)
    df["cos_month"] = np.cos(2 * np.pi * df["month"] / 12)
    df["sin_woy"]   = np.sin(2 * np.pi * df["week_of_year"] / 52)
    df["cos_woy"]   = np.cos(2 * np.pi * df["week_of_year"] / 52)

    # --- Payday week (ngày lương VN: 15 và cuối tháng) ---
    df["is_payday_week"] = (
        ((df["day"] >= 13) & (df["day"] <= 17)) |   # quanh ngày 15
        (df["is_month_end"] == 1) |
        ((df["day"] >= 28))                          # những ngày cuối tháng
    ).astype(int)

    # --- Double Day sales events (9/9, 10/10, 11/11, 12/12) ---
    df["is_double_day"] = (
        ((df["month"] == 9)  & (df["day"] == 9))  |
        ((df["month"] == 10) & (df["day"] == 10)) |
        ((df["month"] == 11) & (df["day"] == 11)) |
        ((df["month"] == 12) & (df["day"] == 12))
    ).astype(int)

    # --- Vietnam special days ---
    df["is_womens_day_intl"]  = ((df["month"] == 3)  & (df["day"] == 8)).astype(int)
    df["is_womens_day_vn"]    = ((df["month"] == 10) & (df["day"] == 20)).astype(int)
    df["is_teachers_day"]     = ((df["month"] == 11) & (df["day"] == 20)).astype(int)
    df["is_national_day"]     = ((df["month"] == 9)  & (df["day"] == 2)).astype(int)
    df["is_liberation_day"]   = ((df["month"] == 4)  & (df["day"] == 30)).astype(int)
    df["is_labor_day"]        = ((df["month"] == 5)  & (df["day"] == 1)).astype(int)

    # --- Window approach cho "days before/after" major events ---
    for col, window in [
        ("is_double_day", 3),
        ("is_womens_day_intl", 5),
        ("is_womens_day_vn", 5),
        ("is_national_day", 3),
    ]:
        df[f"{col}_window{window}"] = (
            df[col].rolling(window*2+1, center=True, min_periods=1).max()
        ).astype(int)

    return df

df_master = add_temporal_features(df_master)
print(f"  Temporal features added. Shape: {df_master.shape}")


# =============================================================================
# BLOCK 2A.2 — TẾT NGUYÊN ĐÁN FEATURES
# Hardcode Tết dates 2013–2024 (Lunar New Year first day in Gregorian)
# =============================================================================
print("\n[Block 2A.2] Tet features...")

TET_DATES = {
    2013: "2013-02-10",
    2014: "2014-01-31",
    2015: "2015-02-19",
    2016: "2016-02-08",
    2017: "2017-01-28",
    2018: "2018-02-16",
    2019: "2019-02-05",
    2020: "2020-01-25",
    2021: "2021-02-12",
    2022: "2022-02-01",
    2023: "2023-01-22",
    2024: "2024-02-10",
}

def add_tet_features(df: pd.DataFrame, tet_dates: dict) -> pd.DataFrame:
    df = df.copy()
    df["is_tet_approach"]  = 0   # 21 ngày trước Tết: nhu cầu tăng mạnh
    df["is_tet_holiday"]   = 0   # 7 ngày Tết: DIP (kho đóng)
    df["is_tet_recovery"]  = 0   # 14 ngày sau Tết: recovery
    df["days_to_tet"]      = 999  # khoảng cách đến Tết gần nhất

    for year, tet_str in tet_dates.items():
        tet = pd.Timestamp(tet_str)
        mask_approach = (df["Date"] >= tet - pd.Timedelta(days=21)) & (df["Date"] < tet)
        mask_holiday  = (df["Date"] >= tet) & (df["Date"] < tet + pd.Timedelta(days=7))
        mask_recovery = (df["Date"] >= tet + pd.Timedelta(days=7)) & (df["Date"] < tet + pd.Timedelta(days=21))

        df.loc[mask_approach, "is_tet_approach"] = 1
        df.loc[mask_holiday,  "is_tet_holiday"]  = 1
        df.loc[mask_recovery, "is_tet_recovery"] = 1

        # days_to_tet: số ngày đến Tết (âm = đã qua, dương = chưa đến)
        diff = (tet - df["Date"]).dt.days
        df["days_to_tet"] = np.where(
            np.abs(diff) < np.abs(df["days_to_tet"]),
            diff,
            df["days_to_tet"]
        )

    # Cyclical encoding của days_to_tet (clip to ±60 days window)
    df["days_to_tet_clipped"] = df["days_to_tet"].clip(-60, 60)
    df["tet_proximity"] = np.exp(-np.abs(df["days_to_tet_clipped"]) / 15)  # Gaussian-like proximity

    return df

df_master = add_tet_features(df_master, TET_DATES)
print(f"  Tet features added. is_tet_approach sum: {df_master['is_tet_approach'].sum()}")


# =============================================================================
# BLOCK 2B — PROMOTION CALENDAR FEATURES
# Bao gồm lịch thật (2013–2022) + Synthetic (2023–2024)
# =============================================================================
print("\n[Block 2B] Promotion calendar features...")

# --- Synthetic promotions 2023-2024 (từ [ARCHITECT] spec) ---
SYNTHETIC_PROMOS = [
    # (promo_name, start, end, promo_type, discount_value, applicable_category, promo_channel, stackable)
    ("Spring Sale 2023",   "2023-03-18", "2023-04-17", "percentage", 12.0, None, "email",        1),
    ("Mid-Year Sale 2023", "2023-06-23", "2023-07-22", "percentage", 18.0, None, "online",       0),
    ("Urban Blowout 2023", "2023-07-30", "2023-09-02", "fixed",      50.0, "Streetwear", "online", 0),
    ("Fall Launch 2023",   "2023-08-30", "2023-10-01", "percentage", 10.0, None, "email",        0),
    ("Rural Special 2023", "2023-09-01", "2023-09-30", "percentage", 15.0, None, "in_store",     0),
    ("Year-End Sale 2023", "2023-11-18", "2023-12-31", "percentage", 20.0, None, "all_channels", 0),
    ("Spring Sale 2024",   "2024-03-18", "2024-04-17", "percentage", 12.0, None, "email",        1),
    ("Mid-Year Sale 2024", "2024-06-23", "2024-07-22", "percentage", 18.0, None, "online",       0),
    ("Fall Launch 2024",   "2024-08-30", "2024-10-01", "percentage", 10.0, None, "email",        0),
    ("Year-End Sale 2024", "2024-11-18", "2024-12-31", "percentage", 20.0, None, "all_channels", 0),
]

syn_rows = []
for row in SYNTHETIC_PROMOS:
    syn_rows.append({
        "promo_name": row[0], "start_date": pd.Timestamp(row[1]),
        "end_date": pd.Timestamp(row[2]), "promo_type": row[3],
        "discount_value": row[4], "applicable_category": row[5],
        "promo_channel": row[6], "stackable_flag": row[7],
        "is_synthetic": 1,
    })
df_syn = pd.DataFrame(syn_rows)

# Standardise real promo table
df_promo_std = df_promo.rename(columns={"start_date": "start_date", "end_date": "end_date"}).copy()
df_promo_std["is_synthetic"] = 0
df_promo_std["applicable_category"] = df_promo_std["applicable_category"].fillna("All")

# Merge cả hai
PROMO_COLS = ["promo_name", "start_date", "end_date", "promo_type",
              "discount_value", "applicable_category", "promo_channel",
              "stackable_flag", "is_synthetic"]
df_all_promos = pd.concat([
    df_promo_std[PROMO_COLS],
    df_syn[PROMO_COLS]
], ignore_index=True)

# Phân loại campaign type
campaign_map = {
    "Spring Sale":   "spring",
    "Mid-Year Sale": "midyear",
    "Fall Launch":   "fall",
    "Year-End Sale": "yearend",
    "Urban Blowout": "urban",
    "Rural Special": "rural",
}
def get_campaign_type(name):
    for k, v in campaign_map.items():
        if k in name:
            return v
    return "other"
df_all_promos["campaign_type"] = df_all_promos["promo_name"].apply(get_campaign_type)

def build_promo_daily_features(df_spine: pd.DataFrame, df_promos: pd.DataFrame) -> pd.DataFrame:
    """
    Với mỗi ngày trong spine, tính:
    - is_in_any_promo
    - max_discount_pct (quy về %, fixed→estimate)
    - n_active_promos
    - is_stackable_active
    - is_all_channel_promo
    - days_to_next_promo_start
    - days_since_promo_start
    - days_to_promo_end (urgency)
    - Per-campaign binary flags
    """
    df = df_spine.copy()
    n = len(df)

    # Init columns
    df["is_in_any_promo"]       = 0
    df["n_active_promos"]       = 0
    df["max_discount_pct"]      = 0.0
    df["is_stackable_active"]   = 0
    df["is_all_channel_promo"]  = 0
    df["days_to_promo_end"]     = 999
    df["days_since_promo_start"]= 999

    for ct in campaign_map.values():
        df[f"promo_{ct}"] = 0

    for _, promo in df_promos.iterrows():
        start = promo["start_date"]
        end   = promo["end_date"]
        dtype = promo["promo_type"]
        dval  = float(promo["discount_value"])
        stack = int(promo["stackable_flag"])
        chan  = str(promo["promo_channel"])
        ctype = promo["campaign_type"]

        # Convert fixed discount to rough % (avg basket ~2M VND)
        if dtype == "fixed":
            disc_pct = min(dval / 20000 * 100, 50)  # rough normalization
        else:
            disc_pct = dval

        mask = (df["Date"] >= start) & (df["Date"] <= end)
        df.loc[mask, "is_in_any_promo"]      = 1
        df.loc[mask, "n_active_promos"]     += 1
        df.loc[mask, "max_discount_pct"]     = df.loc[mask, "max_discount_pct"].clip(lower=disc_pct)
        if stack:
            df.loc[mask, "is_stackable_active"] = 1
        if "all" in chan.lower():
            df.loc[mask, "is_all_channel_promo"] = 1
        if ctype in campaign_map.values():
            df.loc[mask, f"promo_{ctype}"] = 1

        # Days to end (urgency): within promo period
        end_diff = (end - df.loc[mask, "Date"]).dt.days
        df.loc[mask, "days_to_promo_end"] = np.minimum(
            df.loc[mask, "days_to_promo_end"].values, end_diff.values
        )
        # Days since start
        start_diff = (df.loc[mask, "Date"] - start).dt.days
        df.loc[mask, "days_since_promo_start"] = np.minimum(
            df.loc[mask, "days_since_promo_start"].values, start_diff.values
        )

    # days_to_next_promo_start (forward-looking — OK vì promo calendar known)
    df["days_to_next_promo_start"] = 999
    for _, promo in df_promos.iterrows():
        start = promo["start_date"]
        diff = (start - df["Date"]).dt.days
        future_mask = diff >= 0
        df.loc[future_mask, "days_to_next_promo_start"] = np.minimum(
            df.loc[future_mask, "days_to_next_promo_start"].values,
            diff[future_mask].values
        )

    # Clip outliers
    df["days_to_promo_end"]       = df["days_to_promo_end"].clip(0, 60)
    df["days_since_promo_start"]  = df["days_since_promo_start"].clip(0, 60)
    df["days_to_next_promo_start"]= df["days_to_next_promo_start"].clip(0, 90)

    # Log-transform urgency features (diminishing returns)
    df["log_days_to_promo_end"]        = np.log1p(df["days_to_promo_end"])
    df["log_days_to_next_promo_start"] = np.log1p(df["days_to_next_promo_start"])

    return df

df_master = build_promo_daily_features(df_master, df_all_promos)

# ✅ QA
assert df_master["promo_yearend"].sum() > 0, "Year-End promo not mapped!"
assert df_master.loc[df_master["Date"] >= "2023-01-01", "is_in_any_promo"].sum() > 0, \
    "Synthetic promos 2023 not active!"
print(f"  Promo features added. Active promo days 2023+: "
      f"{df_master.loc[df_master['Date']>='2023-01-01','is_in_any_promo'].sum()}")


# =============================================================================
# BLOCK 2H — FINAL ASSEMBLY & SAVE
# =============================================================================
print("\n[Block 2H] Final assembly...")

# --- Build final feature list (exclude target, metadata) ---
EXCLUDE_COLS = [
    "Date", "Revenue", "COGS", "is_test",
    "year", "time_linear", "time_quadratic", "time_log", "business_year",
    "regime_growth", "regime_maturity", "regime_covid", "regime_recovery", "regime_postnorm",
    "is_lockdown_q1_2020", "is_delta_wave", "is_v_recovery_2020"
]

# Create explicit categorical Regime feature
def get_regime(yr):
    if yr <= 2018: return 0 # High_PreCovid
    elif yr <= 2022: return 1 # Low_CovidEra
    return 0 # Test set (2023-2024) -> force back to High_PreCovid

df_master["Regime"] = df_master["year"].apply(get_regime)

FEATURE_COLS = [c for c in df_master.columns if c not in EXCLUDE_COLS]

# --- Separate train / test ---
df_train = df_master[df_master["is_test"] == 0].copy()
df_test  = df_master[df_master["is_test"] == 1].copy()

# --- Drop warmup rows if needed ---
# We MUST keep 2012-2018 because that is the 'High_PreCovid' regime!
df_train = df_train[df_train["Date"] >= "2013-01-01"].copy() # Drop 2012 for lag warmup, but keep 2013+
print(f"  Train rows after warmup drop: {len(df_train)}")
print(f"  Test rows: {len(df_test)}")

# Drop any column where train NaN rate > 30%
nan_rates = df_train[FEATURE_COLS].isna().mean()
high_nan = nan_rates[nan_rates > 0.30].index.tolist()
if high_nan:
    print(f"  ⚠️ Dropping {len(high_nan)} features with >30% NaN: {high_nan[:5]}...")
    FEATURE_COLS = [c for c in FEATURE_COLS if c not in high_nan]

# Final fill: remaining NaN → median per column (if any still exist in early train rows)
for col in FEATURE_COLS:
    fill_val = df_train[col].median()
    # Always fill both train and test to guarantee no NaNs
    df_train[col] = df_train[col].fillna(fill_val)
    df_test[col]  = df_test[col].fillna(fill_val)

print(f"  Final feature count: {len(FEATURE_COLS)}")

# --- Save ---
df_master.to_parquet(OUTPUT_DIR / "master_features.parquet", index=False)
df_train.to_parquet(OUTPUT_DIR  / "train_features.parquet",  index=False)
df_test.to_parquet(OUTPUT_DIR   / "test_features.parquet",   index=False)
json.dump(FEATURE_COLS, open(OUTPUT_DIR / "feature_cols.json", "w"), indent=2)

print(f"\n✅ ALL BLOCKS COMPLETE")
print(f"   master_features.parquet : {df_master.shape}")
print(f"   train_features.parquet  : {df_train.shape}")
print(f"   test_features.parquet   : {df_test.shape}")
print(f"   feature_cols.json       : {len(FEATURE_COLS)} features")

# --- Final QA ---
assert len(df_test) == 548, f"Test set wrong size: {len(df_test)}"
assert df_train["Revenue"].isna().sum() == 0, "NaN in train Revenue!"
assert df_test["Revenue"].isna().all(), "Test Revenue should all be NaN!"
for col in FEATURE_COLS:
    assert df_train[col].isna().sum() == 0, f"NaN remaining in train[{col}]!"
    assert df_test[col].isna().sum()  == 0, f"NaN remaining in test[{col}]!"

print("\n✅ QA PASSED — Feature matrix is clean and ready for modeling.")
print("   Next step: Task Block 3 (Validation) → Task Block 4 (LightGBM)")
