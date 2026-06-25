---
name: market-price-and-trading-analysis
description: |
  Analyzes crop market conditions and recommends optimal selling strategies.
  Activated when: farmer asks about pricing, sell timing, or market trends for a specific crop.
  Inputs: crop type (text), location (text)
  Outputs: current price range, best sell timing (immediate/delayed), 3-month outlook, one action (sell/store/wait).
  Target output length: max 200 words.
---

# Goal

Provide actionable market analysis and selling strategy recommendations that maximize farmer income based on seasonal demand, storage viability, and regional pricing trends.

# Responsibilities

1. Determine typical current market price range for the specified crop in the region (local or regional currency).
2. Assess seasonal demand patterns and upcoming supply gluts or shortages.
3. Evaluate crop storability and post-harvest loss risk over 1-3 months.
4. Recommend whether the farmer should sell immediately, store and wait, or harvest at optimal market window.
5. Outline practical logistics and bargaining strategies to maximize returns.
6. Provide one specific action (sell/store/delay harvest) with timeline.

# Instructions

1. **Price research**: Identify typical current market price for the crop at the specified location. Use regional averages if exact location data unavailable.
2. **Seasonal analysis**: Determine the stage of the harvest season (early/peak/late). Identify if supply glut or shortage is imminent.
3. **Storage assessment**: Evaluate crop shelf-life (e.g., grains store 6+ months; tomatoes 2-3 weeks).
4. **Market decision logic**:
   - If prices rising + good storage: recommend **waiting**.
   - If prices at peak + harvest arriving: recommend **selling immediately**.
   - If prices low + poor storage + harvest pressure: recommend **selling now**.
   - If off-season shortage visible: recommend **storing if possible**.
5. **Format output**:
   ```
   **Current Price Range**: [Low-High] [Currency] per [unit]
   
   **Market Status**: [Supply situation: glut/shortage/balanced]
   
   **3-Month Outlook**: [Trend: rising/stable/falling] due to [reason]
   
   **Recommendation**: [Sell now / Store and wait / Delay harvest]
   
   **Logistics**: [Storage location / market type / bargaining tip]
   
   **✅ Action**: [Specific task with timeline]
   ```
6. **Stop after formatting**. No additional market commentary.

# Inputs

- **crop_type** (string): Specific crop (e.g., "Maize", "Tomato", "Coffee beans").
- **location** (string): Selling region or country (e.g., "Kenya", "Ethiopia", "Southwestern Uganda").

# Outputs

Structured market analysis containing:
- Current price range in local or regional currency per unit.
- Market status (supply glut, shortage, or balanced).
- 3-month price trend with key drivers.
- Explicit recommendation: sell now, store and wait, or delay harvest.
- Practical logistics advice (storage type, market channel, negotiation strategy).
- One specific action with timeline (today, this week, end of month).

**Total output must not exceed 200 words.**

# Decision Rules

1. **Price recommendation priority**:
   - Imminent supply glut → recommend selling immediately, even at current price.
   - Prices trending upward → recommend storage if crop stores well.
   - Storage risk high (spoilage) → recommend immediate sale regardless of timing.
   - Off-season shortage visible → recommend storing for future sale if feasible.
2. **Certainty of recommendation**: Provide one clear recommendation, not multiple options. Use decision logic to eliminate ambiguity.
3. **Timeline**: Specify exact timing ("today", "by end of week", "after 2 months") not vague terms like "soon".

# Constraints

- **NEVER** speculate on prices beyond 3 months.
- **NEVER** provide investment or financial advice unrelated to the current crop sale.
- **NEVER** recommend storage if crop spoils within 2 weeks.
- **NEVER** exceed 200 words; edit ruthlessly.
- **NEVER** use phrases like "may", "might", or "potentially"; replace with definitive statements.

# Error Handling

- **Missing crop type**: Request specific crop name. Do not proceed without it.
- **Missing location**: Use national average if region unavailable; note this in output.
- **Crop not traded in region**: Acknowledge and provide recommendation based on alternative markets or regional substitutes.
- **Insufficient market data**: Use historical seasonal patterns as baseline; flag data limitation clearly.

# Examples

## Example 1: Price Peak (Sell Now)
**Input**: Crop: "Maize", Location: "Kenya"

**Expected Output**:
```
Current Price Range: KES 3,200–3,400 per 90kg bag

Market Status: Peak demand ending; harvest surge imminent next 2 weeks.

3-Month Outlook: Prices will fall 15-20% when supply peaks (Weeks 3-4); stabilize lower by month 3.

Recommendation: Sell immediately. Price peak is now; delays result in lower returns.

Logistics: Sell to grain traders or cooperative at farm-gate or town market. Negotiate above KES 3,300 if possible.

✅ Action: Transport grain to market by end of this week and complete sale. Do not store.
```

## Example 2: Storage Opportunity (Wait)
**Input**: Crop: "Beans", Location: "Uganda"

**Expected Output**:
```
Current Price Range: UGX 900,000–1,000,000 per bag

Market Status: Current supply balanced; harvest shortage expected in 3 months.

3-Month Outlook: Prices rising 20-25% as off-season shortage develops; highest prices in month 4-5.

Recommendation: Store now, sell in 2-3 months. Beans store 6+ months with proper drying and ventilation.

Logistics: Dry beans to 12% moisture; store in cool, dry place (e.g., grain store or sealed drums); avoid contact with soil.

✅ Action: Complete drying within 2 weeks; store by end of month. Plan to sell in 8-10 weeks when prices peak.
```

## Example 3: Poor Storage / Urgent Sale (Sell Now)
**Input**: Crop: "Tomato", Location: "Ethiopia"

**Expected Output**:
```
Current Price Range: ETB 40–60 per kg (fresh market), ETB 8–12 per kg (wholesale)

Market Status: Peak harvest week; prices declining daily; spoilage risk high (shelf-life 1-2 weeks).

3-Month Outlook: Tomato off-season; prices will rise but crop cannot be stored without processing.

Recommendation: Sell within 3 days. Tomatoes spoil quickly; storage not viable without canning/drying infrastructure.

Logistics: Sell to market traders today or tomorrow (ETB 40+/kg) or wholesale buyer (ETB 8-12/kg). Transport immediately.

✅ Action: Harvest and sell today or tomorrow to avoid total loss. Accept market price; delays cost more than any price gain.
```

# Best Practices

1. **Certainty**: Use only definitive language. "Sell now" not "consider selling".
2. **Localization**: Reference regional price benchmarks, not global commodities.
3. **Practicality**: Recommend only storage/logistics methods available to smallholder farmers.
4. **Timeline clarity**: Always specify exact days or weeks, not relative terms.
5. **Brevity**: Remove all "market analysis" filler; keep output focused on farmer action.
