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

insert_before("output/figures_living/04_financial_payment_dynamics/DA.md", "## 🎯 Comprehensive Financial Recommendations", content_04)
