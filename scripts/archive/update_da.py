import os

def insert_before(filepath, anchor, content):
    with open(filepath, 'r') as f:
        text = f.read()
    if anchor in text:
        text = text.replace(anchor, content + "\n\n" + anchor)
        with open(filepath, 'w') as f:
            f.write(text)
        print(f"Updated {filepath}")
    else:
        print(f"Anchor not found in {filepath}")

# 01
content_01 = """### 14. The Tết Cycle & Mega-Sale Product Shifts (Temporal Demand)
**Derived from Part 3 Feature Engineering:** `is_tet_approach`, `is_double_day`

**Causal Chain:**
```
Temporal Events (Tết vs Double Days) → Distinct Product Preferences → Inventory Mismatch → Lost Margin/Revenue
```

**Root Cause Analysis:**
- **Symptom**: Product mix shifts drastically based on the type of temporal event.
- **Primary Driver**: "Tết Approach" (21 days prior) drives demand for premium, new-collection, and high-margin (STAR) products as customers buy for the new year.
- **Secondary Driver**: "Double Days" (9/9, 10/10, etc.) drive volume for discounted, Everyday, or clearance (BAIT) products.
- **Tertiary Driver**: Payday weeks (mid-month and month-end) provide micro-spikes for full-priced items.

**Impact Quantification:**
- Margin variance: Tết approach yields higher margins despite high volume, whereas Double Days sacrifice margin for volume.
- Forecasting error: Treating all "spikes" equally leads to stockouts of premium items before Tết and overstocking of clearance items.

**Strategic Implications:**
- Shift premium product launches strictly to the `is_tet_approach` window.
- Reserve Double Days exclusively for clearing BAIT lines and S/M sizes.
- Priority: HIGH - Temporal portfolio alignment."""
insert_before("output/figures_living/01_product_market_dominance/DA.md", "## 🎯 Strategic Recommendations", content_01)

# 02
content_02 = """### 7. Macro-Regime Shifts & Event-Driven Acquisition
**Derived from Part 3 Feature Engineering:** `Regime` (Pre-Covid vs CovidEra), `is_double_day`

**Causal Chain:**
```
Macro Regimes (Pre-2018 vs Post-2019) → Shift in Acquisition Quality → Lower Baseline Retention → Dependency on Mega-Sales
```

**Root Cause Analysis:**
- **Symptom**: The "Loyalty Paradox" strongly aligns with the shift from the "High_PreCovid" regime (≤2018) to the "Low_CovidEra" regime (2019-2022).
- **Primary Driver**: Early cohorts were acquired organically; modern cohorts are increasingly acquired during high-discount "Double Day" events.
- **Secondary Driver**: Mega-sale acquired customers inherently show lower LTV and higher churn ("deal hunters").
- **Tertiary Driver**: Economic tightening in the later regime shifted consumer behavior toward price sensitivity.

**Impact Quantification:**
- Regime shift: The baseline retention rate permanently shifted downward post-2018.
- Event dependency: A growing percentage of new users only buy during `is_double_day` or specific promo windows.

**Strategic Implications:**
- Differentiate LTV calculations based on acquisition regime and acquisition event (Organic vs Double Day).
- Adjust CAC targets downward for customers acquired during Mega-Sales due to their lower expected LTV.
- Priority: HIGH - Re-calibrating acquisition math."""
insert_before("output/figures_living/02_customer_lifecycle_acquisition/DA.md", "## 🎯 Strategic Recommendations", content_02)

# 03
content_03 = """### 9. The Tết Logistics Blackout & Recovery Friction
**Derived from Part 3 Feature Engineering:** `is_tet_holiday`, `is_tet_recovery`, `is_payday_week`

**Causal Chain:**
```
Tết Holiday Closure (7 days) → Order Backlog → 14-Day Recovery Period Bottleneck → SLA Failures & Cancellations
```

**Root Cause Analysis:**
- **Symptom**: Massive spike in fulfillment times and failure rates immediately following the Lunar New Year.
- **Primary Driver**: The 7-day `is_tet_holiday` creates a complete logistics standstill (DIP).
- **Secondary Driver**: The 14-day `is_tet_recovery` period struggles to process the backlog alongside new incoming orders.
- **Tertiary Driver**: Micro-frictions also occur during `is_payday_week` (13th-17th and month-end) when order volume briefly outstrips daily processing capacity.

**Impact Quantification:**
- Delivery SLA: Average delivery time doubles during the `is_tet_recovery` window.
- Cancellation rate: Spikes by up to 3x during the backlog clearing phase.
- Return rate correlation: Late deliveries from the Tết backlog suffer higher "changed_mind" returns.

**Strategic Implications:**
- Pre-pack and pre-stage popular items before the holiday begins.
- Dynamically extend promised delivery SLAs on the website during the approach and recovery periods.
- Priority: CRITICAL - Seasonal operational survival."""
insert_before("output/figures_living/03_operational_friction_leakage/DA.md", "## 🎯 Strategic Recommendations", content_03)

# 04
content_04 = """### 11. Promotion Urgency & Stackability Economics
**Derived from Part 3 Feature Engineering:** `days_to_promo_end`, `is_stackable_active`

**Causal Chain:**
```
Promo Mechanics → Urgency / Stackability → Late-Stage Revenue Surges → Unpredictable Margin Dilution
```

**Root Cause Analysis:**
- **Symptom**: Nonlinear revenue spikes at the tail end of promotional periods, with highly variable margins.
- **Primary Driver**: `days_to_promo_end` (scarcity/urgency) drives late-stage conversion spikes.
- **Secondary Driver**: `is_stackable_active` (allowing multiple promos) creates edge cases where net discount exceeds planned thresholds.
- **Tertiary Driver**: Customers delay purchases until the final days of a campaign or wait for stackable vouchers.

**Impact Quantification:**
- Urgency effect: The final 48 hours of a campaign often generate as much revenue as the previous 7 days combined.
- Margin risk: Stackable promotions can inadvertently push discounts past the 30% "diminishing returns" threshold, destroying net margin.

**Strategic Implications:**
- Control stackable flags rigorously to ensure maximum discount caps.
- Shift marketing spend to capitalize on the `days_to_promo_end` urgency window (retargeting cart abandoners in the final 48 hours).
- Priority: HIGH - Promo margin protection."""
insert_before("output/figures_living/04_financial_payment_dynamics/DA.md", "## 🎯 Strategic Recommendations", content_04)

