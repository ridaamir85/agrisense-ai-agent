---
name: multilingual-report-compilation-and-simplification
description: |
  Compiles all weather, health, and market findings into a single, simple, multilingual advisory report.
  Activated when: all agent reports (weather, crop doctor, market price) are complete and ready for consolidation.
  Inputs: weather report (text), crop health report (text), market report (text), target language (string), location (string), crop type (string).
  Outputs: single unified advisory report in target language with 4 sections: weather, health, market, action checklist.
  Target output length: max 500 words in simple language (5th-grade reading level).
---

# Goal

Consolidate multi-agent findings into one clear, multilingual report written at a reading level accessible to smallholder farmers, eliminating technical jargon and emphasizing immediate actionable steps.

# Responsibilities

1. Translate all technical terms into simple, local language equivalents.
2. Consolidate three separate reports (weather, crop health, market) into four coherent sections.
3. Identify and highlight the most critical actions from all three domains (weather alerts, treatment urgency, market timing).
4. Structure the report for ease of reading: clear headers, short sentences, bullet points.
5. Generate a 4-step action checklist the farmer can execute this week.
6. Provide the output in the farmer's preferred language with 100% accuracy (no mixing of languages).

# Instructions

1. **Language preparation**: Confirm target language from input. If translation needed, translate ALL content consistently (no code-switching).
2. **Parse input reports**: Extract the essential information from each report:
   - Weather: alerts, best planting days, best harvesting days, primary action.
   - Crop health: primary diagnosis, organic treatment, chemical treatment, prevention, primary action.
   - Market: sell recommendation (now/wait/delay), price range, logistics, primary action.
3. **Jargon removal**: Create simple alternatives:
   - "Integrated Pest Management" → "using multiple safe methods to fight pests"
   - "Fungicide" → "medicine to stop fungal disease"
   - "Arbitrage" → "buying low, selling high"
   - "Systemic infection" → "disease throughout the plant"
   - "Microbial inoculant" → "beneficial microbes added to soil"
4. **Report structure**: Compile into this exact format (do not skip sections):
   ```
   # AgriSense Farming Advisory for [Crop] in [Location]
   
   [Date]
   
   ---
   
   ## ⛅ Weather Forecast (Next 7 Days)
   
   [1 sentence summary]
   
   **Watch out for**: [List hazards or "None"]
   
   **Best days to plant**: [Days]
   **Best days to harvest**: [Days]
   
   ---
   
   ## 🩺 Crop Health Report
   
   **Main problem**: [Diagnosis in simple terms]
   
   **Why it happened**: [1-2 sentences]
   
   **How to fix it**:
   
   - Safe methods: [Method 1], [Method 2]
   - If safe methods don't work: [Chemical option with dosage]
   
   **How to prevent next time**: [3-4 simple steps]
   
   ---
   
   ## 📊 Market Price Information
   
   **Current price**: [Price range in local currency]
   
   **Should you sell now?**: [Yes / No / Wait X days]
   
   **Why**: [1 sentence on market condition]
   
   **Where to sell**: [Market type]
   
   ---
   
   ## ✅ This Week's Action Plan
   
   1. [Immediate action from weather]
   2. [Immediate action from crop health]
   3. [Market action: sell/store/wait]
   4. [General preparation: cleanup, prevention]
   ```
5. **Simplification pass**: Read each section aloud. Replace any word a farmer unfamiliar with agriculture would not know.
6. **Language consistency**: Verify entire report is in target language only. No English or technical terms embedded.
7. **Verify output length**: Count words. If exceeds 500, trim non-essential descriptive phrases.

# Inputs

- **weather_report** (string): Output from Weather Agent (structured with alerts, best days, action).
- **crop_health_report** (string): Output from Crop Doctor Agent (diagnosis, treatment, prevention).
- **market_report** (string): Output from Market Price Agent (price, recommendation, logistics).
- **target_language** (string): Language name (e.g., "Spanish", "Swahili", "Hindi", "French").
- **location** (string): Farm location or region.
- **crop_type** (string): Crop name.

# Outputs

Single unified advisory report containing:
- **Section 1 (Weather)**: Forecast summary, hazards, best planting/harvesting days.
- **Section 2 (Health)**: Problem diagnosis, treatment (safe first, chemical if needed), prevention.
- **Section 3 (Market)**: Sell recommendation, price range, where to sell.
- **Section 4 (Action Checklist)**: 4 specific weekly tasks.

**Requirements**:
- Entire report in target language only (no code-switching).
- Reading level: 5th grade (ages 10-11); sentences ≤ 15 words; vocabulary accessible to non-literate farmers.
- Total output: 300–500 words.
- Format: Markdown with clear headers and bullet points.

# Decision Rules

1. **Jargon removal priority**: Any term not known to a farmer with primary-school education must be replaced or explained simply.
2. **Action priority**: Order the action checklist by time sensitivity:
   - Critical hazard actions first (e.g., frost, disease spread).
   - Market actions second (time-dependent pricing).
   - Prevention actions last (longer-term).
3. **Conflicting guidance**: If multiple agents recommend different urgent actions, list all and number by priority.
4. **Language selection**: If input specifies a language, output 100% in that language; do not mix.

# Constraints

- **NEVER** include technical terms, abbreviations, or jargon without explanation.
- **NEVER** use complex grammatical structures; prefer short, active sentences.
- **NEVER** add personal opinions or commentary beyond the consolidated facts from the three agents.
- **NEVER** exceed 500 words; prioritize clarity over detail.
- **NEVER** use conditional language ("may", "might", "possibly"); use definitive statements.
- **NEVER** include price predictions beyond the 3-month outlook provided.
- **NEVER** embed English words or acronyms in non-English reports.

# Error Handling

- **Missing input report**: Note which report is missing and request it. Proceed only if minimum 2 of 3 reports available.
- **Unsupported language**: Use English if target language cannot be properly translated; flag this clearly.
- **Conflicting recommendations**: Highlight the conflict explicitly (e.g., "Weather says harvest now; market says wait 2 weeks—choose based on condition").
- **Jargon persistence**: If unsure how to simplify a term, replace with analogy (e.g., "systemic fungicide" → "medicine that travels through the plant like water").

# Examples

## Example 1: Simplified Spanish Report
**Inputs**:
- Weather: Alerts on heat, best planting Day 4, no harvesting window.
- Health: Spider mites diagnosed, neem oil recommended, or chemical if needed.
- Market: Price rising in 2 months; store if possible.
- Language: Spanish
- Location: Southwestern Kenya
- Crop: Tomato

**Expected Output** (excerpt):
```
# Aviso Agrícola de AgriSense para Tomate en Kenya Sudoccidental

[Fecha]

---

## ⛅ Pronóstico del Clima (Próximos 7 Días)

Esta semana hace mucho calor. Cuidado: muy caluroso Días 3-5 (más de 40 grados).

**Cosas a vigilar**: Calor extremo. Riega las plantas dos veces cada día.

**Mejores días para plantar**: Día 4
**Mejores días para cosechar**: Ninguno esta semana.

---

## 🩺 Salud de las Plantas

**Problema principal**: Ácaros rojos (bichos pequeños).

**Por qué pasó**: Clima seco y caluroso ayuda a los ácaros.

**Cómo arreglarlo**:

- Formas seguras: Rocía aceite de neem cada 3 días. Aumenta agua en el suelo.
- Si no funciona: Usa spray acaricida (pregunta en la tienda agrícola).

**Cómo evitar otra vez**: Mantén el suelo húmedo. Limpia hojas muertas. Espacía plantas más.

---

## 📊 Precios en el Mercado

**Precio actual**: KES 1,200–1,500 por caja.

**¿Vender ahora?**: No. Espera 8 semanas.

**Por qué**: Los precios suben cuando hace frío y hay pocos tomates.

**Dónde vender**: Mercado cooperativo o negociante de verduras.

---

## ✅ Plan de Trabajo Esta Semana

1. Riega tomates DOS VECES cada día hasta que baje el calor (Días 3-5).
2. Rocía neem hoy y en 3 días más (para los ácaros).
3. NO vendas tomates esta semana. Guarda en lugar fresco si es posible.
4. Limpia hojas viejas o dañadas del suelo.
```

## Example 2: Simplified Swahili Report
**Inputs**:
- Weather: Frost warning Days 1-2, best planting Days 4-5.
- Health: Blight diagnosed, organic removal + copper spray.
- Market: Prices stable; sell now if ready.
- Language: Swahili
- Location: Uganda
- Crop: Maize

**Expected Output** (excerpt):
```
# Onyo wa AgriSense kwa Mahindi kiko Uganda

---

## ⛅ Hali ya Hewa (Siku 7 Ijayo)

Jumapili na Jumatatu itakuwa baridi sana. Tiki hadharani: Barafu inayoweza kunaribu mimea.

**Angalia**: Baridi kali Siku 1-2. Funika mimea ifuatayo kwa mitandao au mabati.

**Siku nzuri kupanda**: Siku 4, Siku 5
**Siku nzuri kukaata**: Hakuna siku nzuri wiki hii.

---

## 🩺 Afya ya Mimea

**Tatizo kuu**: Ugonjwa wa Leaf Blight (rangi hufa na kufa).

**Kwa nini**: Joto na unyevu husababisha ugonjwa huu.

**Jinsi ya kukamatia**:

- Kwa salama: Kata na choma majani yaliyoathiriwa. Okoa haraka harakati.
- Kama sio kutosha: Kumimina dawa ya copper kila siku 7.

**Kumzuia mara ijayo**: Kota mazao. Changia moto ya kufa. Simu mahindi ya kupinga.

---

## 📊 Bei ya Soko

**Bei sasa**: UGX 900,000 kwa gunia.

**Kuuza sasa?**: Ndiyo, tayari.

**Kwa nini**: Bei ni nzuri; utakapokufa hazitakuwa nzuri zaidi.

**Wapi kuuza**: Wageni wa nchi au sokoni.

---

## ✅ Kazi ya Wiki Hii

1. Funika mahindi siku 1-2 (barafu).
2. Kata majani yaliyoathiriwa leo.
3. Kumimina copper dawa wiki (anza Siku 3).
4. Uuza mahindi wiki hii au ijayo kwa bei nzuri.
```

# Best Practices

1. **Read-aloud test**: Mentally read each sentence aloud as if to a farmer with primary education.
2. **Active voice**: Use "you must do X" not "X should be done".
3. **Short sentences**: Max 12–15 words per sentence.
4. **Consistent terminology**: Use the same simple term throughout (e.g., "disease" not alternating with "illness").
5. **Cultural sensitivity**: Use local examples and references when replacing jargon.
6. **Verify completeness**: All four sections and all four action items must be present in every report.
