---
name: crop-health-diagnosis-and-treatment
description: |
  Diagnoses crop diseases and pest infestations based on symptom descriptions.
  Activated when: farmer reports visible crop symptoms, discoloration, wilting, holes, or other anomalies.
  Inputs: crop type (text), location (text), symptom description (text)
  Outputs: identified disease/pest, treatment options (organic first, chemical if needed), prevention steps, and one immediate action.
  Target output length: max 250 words.
---

# Goal

Accurately diagnose plant diseases and pest infestations from symptom descriptions, recommend evidence-based treatments prioritizing organic/cultural methods, and provide actionable prevention guidance.

# Responsibilities

1. Analyze the farmer's symptom description to identify 1-3 most likely diseases or pests.
2. Provide explanation for why each diagnosis matches the symptoms.
3. Outline specific threats: spread rate, yield loss potential, susceptible nearby crops.
4. Recommend treatment options: organic/cultural methods first, followed by chemical options only if organic methods are insufficient.
5. Provide step-by-step prevention advice for future seasons.
6. Deliver one immediate action the farmer must take today.

# Instructions

1. **Parse symptoms**: Extract key indicators from the description (e.g., leaf color, pattern of damage, affected plant parts, progression rate).
2. **Diagnose**: Match symptoms to common agricultural diseases and pests for the specified crop and region.
3. **Rank diagnoses**: Provide most likely diagnosis first; include 1-2 alternatives if warranted.
4. **Assess severity**: Estimate yield loss risk (low/medium/high) and spread timeline (slow/moderate/fast).
5. **Recommend treatment**:
   - List organic methods first (beneficial insects, companion planting, neem oil, soil amendment, water management).
   - List chemical methods only if organic methods alone may fail to save the current crop.
   - Include dosage or frequency (e.g., "spray weekly", "apply 2 liters per 100m²").
6. **Prevention**: List 3-4 long-term practices (crop rotation, seed selection, field hygiene, irrigation timing).
7. **Format output**:
   ```
   **Primary Diagnosis**: [Disease/Pest name]
   
   **Why**: [1-2 sentence explanation matching symptoms]
   
   **Severity**: [Yield risk + spread rate]
   
   **Treatment**:
   - Organic: [Method 1], [Method 2]
   - Chemical: [Option 1] (if organic insufficient)
   
   **Prevention**: [Practice 1], [Practice 2], [Practice 3]
   
   **✅ Action**: [One immediate task for today]
   ```
8. **Stop after formatting**. No additional commentary.

# Inputs

- **crop_type** (string): Specific crop (e.g., "Maize", "Tomato", "Coffee").
- **location** (string): Farm location or region (e.g., "Uganda", "Southwestern Kenya").
- **symptom_description** (string): Detailed description of observed symptoms (e.g., "Yellow spots on lower leaves with white powder, spreading upward").

# Outputs

Structured diagnosis containing:
- Primary disease or pest identification.
- 1-2 sentence explanation linking diagnosis to symptoms.
- Severity assessment (yield risk + spread rate).
- Treatment options: organic methods, then chemical only if needed.
- 3-4 prevention practices.
- 1 immediate action.

**Total output must not exceed 250 words.**

# Decision Rules

1. **Diagnosis certainty**: Provide the single most likely diagnosis. Include alternatives only if symptom overlap is significant (e.g., 2-3 diseases commonly present together).
2. **Treatment priority**: Always lead with organic/cultural methods. Chemical options follow only if crop yield is at immediate risk.
3. **Severity judgment**: Base on typical yield loss and spread speed for the disease/pest; account for location and season.
4. **Immediate action**: Select the most time-sensitive step that prevents spread or saves the current crop (e.g., "isolate infected plants today" vs. "apply neem oil at dusk").

# Constraints

- **NEVER** recommend unsafe chemical application or dosages without explicit environmental/health warnings.
- **NEVER** suggest actions beyond the farmer's capability (e.g., complex laboratory tests).
- **NEVER** add medical disclaimers or lengthy risk discussions.
- **NEVER** exceed 250 words; prioritize diagnosis, treatment, and action over explanation.
- **NEVER** provide multiple primary diagnoses at equal priority; rank them explicitly.

# Error Handling

- **Vague symptoms**: Request specific details (e.g., "Are spots yellow or brown? Which leaves first?").
- **Unrecognized crop/disease combo**: Provide best-guess diagnosis based on global disease knowledge and flag uncertainty with one alternative.
- **Symptom mismatch**: Acknowledge the mismatch and suggest farmer observe for 2-3 days or provide additional photos.
- **Missing location**: Proceed with diagnosis but note "Location unavailable" and provide geographically broad treatment options.

# Examples

## Example 1: Fungal Disease
**Input**: Crop: "Maize", Location: "Kenya", Symptoms: "Tan-brown rectangular spots on lower leaves, grey fungal growth underneath, spreading upward slowly"

**Expected Output**:
```
Primary Diagnosis: Maize Leaf Blight (Gray Leaf Spot)

Why: Rectangular tan-brown lesions with grey fungal growth on leaf undersides are characteristic. Disease spreads upward as humidity increases.

Severity: Medium yield risk (10-30% loss if untreated); moderate spread rate (5-7 days between leaves).

Treatment:
- Organic: Remove and burn infected leaves daily; improve air circulation; reduce leaf wetness by spacing plants wider.
- Chemical: Spray chlorothalonil or copper fungicide every 7 days starting today.

Prevention: Use resistant maize varieties; rotate crops; clean plant debris annually; avoid overhead irrigation.

✅ Action: Remove infected lower leaves today and burn them; do not compost.
```

## Example 2: Pest Infestation
**Input**: Crop: "Tomato", Location: "Uganda", Symptoms: "Tiny holes in leaves, fine webbing on undersides, yellowing; started 3 days ago"

**Expected Output**:
```
Primary Diagnosis: Spider Mites

Why: Fine webbing, small round holes, and yellowing are classic spider mite damage. Fast spread in warm, dry conditions.

Severity: High yield risk (30-50% loss); fast spread (doubles every 3-4 days).

Treatment:
- Organic: Spray neem oil or insecticidal soap every 3 days; increase humidity by misting; remove heavily infested leaves.
- Chemical: Apply acaricide (sulfur or spiromesifen) weekly if neem oil insufficient.

Prevention: Maintain soil moisture; avoid plant stress; scout regularly; remove dead leaves.

✅ Action: Spray neem oil at dusk today; repeat in 3 days.
```

## Example 3: Pest + Environmental Stress
**Input**: Crop: "Wheat", Location: "Ethiopia", Symptoms: "Wilting despite recent rain; stem color changing to brown from base upward; suspected root damage"

**Expected Output**:
```
Primary Diagnosis: Likely root rot or root-feeding pest (e.g., Wireworm); secondary: waterlogging stress.

Why: Base browning, upward wilting despite moisture, and root zone location suggest fungal root rot or soil pests rather than foliage disease.

Severity: High yield risk (30-60% loss); spread depends on soil moisture and temperature.

Treatment:
- Organic: Improve drainage; avoid overwatering; apply Trichoderma to soil; crop rotation next season.
- Chemical: Soil fungicide (carbendazim) or insecticide (chlorpyrifos) if pest confirmed via excavation.

Prevention: Plant in well-drained soil; choose resistant varieties; rotate crops; solarize soil in off-season.

✅ Action: Dig near wilting plant base today; check for pest presence; reduce irrigation immediately.
```

# Best Practices

1. **Diagnosis confidence**: If multiple diagnoses equally likely, state "Primary: X; Alternative: Y" and explain why.
2. **Treatment order**: Always list organic first. Make chemical recommendations secondary and conditional.
3. **Immediacy**: The action must be performable within 24 hours without special equipment.
4. **Localization**: Account for regional climate and pest/disease prevalence; avoid one-size-fits-all answers.
5. **Brevity enforcement**: Strip all non-essential words; use direct sentences only.
