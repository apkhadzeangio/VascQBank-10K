# VascQBank-10K — Clinical spot adjudication of 12 similarity pairs

**Date:** 2026-11-20. **Pinned question snapshot:** `9dd030de5d3be2b75226b58c78e7f77e56f1774b`. **Scope:** 12 flagged question pairs (24 source records) reviewed side by side; not an exhaustive clinical review of 10K. Dispositions are *editorial triage proposals*, not independent human sign-off. Production questions and explanations unchanged.

## High-priority overlapping assessments

| Pair | Triage decision | Reason | Priority |
|---|---|---|---|
| **PERIOPERATIVE #8 ↔ VGEI #34** | LIKELY_SEMANTIC_DUPLICATE | Nearly identical severe malnutrition scenario (13% weight loss, BMI 17.6, oral intake possible, elective vascular reconstruction), same question on delaying elective surgery and starting oral nutrition. Different bypass localization does not change the tested decision. | P1 |
| **ANATOMY_IMAGING #41 ↔ CAROTID_VERTEBRAL #839** | LIKELY_SEMANTIC_DUPLICATE | Both ask how to resolve pulsed-wave Doppler aliasing by increasing PRF and shifting baseline, with only vascular-bed differences. Same physics and decision. | P1 |
| **AAA_EVAR #1106 ↔ PERIOPERATIVE #227** | LIKELY_OVERLAPPING_DECISION; GUIDELINE_RECHECK | Both ask RBC transfusion for postoperative acute myocardial ischemia with ST depression, elevated troponin and Hb 76–81 g/L; keyed decision is transfusion rather than restrictive threshold. AAA #1106 specifies 80–90 g/L, potentially too rigid/low against 2025 ACS guidance. This is not automatically proof of wrong answer because exact indication and individualization matter. | **P0** |
| VGEI #363 ↔ VGEI #387 | OVERLAP_BUT_DISTINCT_ANATOMY | Emergency endovascular hemorrhage control for infected pseudoaneurysm; carotid patch versus femoropopliteal graft, different ESVS recommendation numbers, both involve urgent hemostasis. Review for educational diversity before removal. | P1 |

## Similarity candidates tentatively *not* duplicates

| Pair | Preliminary rationale |
|---|---|
| VGEI #271 ↔ #389 | Extra-anatomical thoracic vs lower-limb reconstruction; different anatomical alternatives and recommendation IDs |
| VGEI #316 ↔ #335 | Antimicrobial grafts in abdominal aorta vs lower extremity with different explicit evidence grades; contextual contrast is the test |
| PERIOPERATIVE #166 ↔ #168 | Neuraxial safety interval after therapeutic enoxaparin (24h) vs high-dose rivaroxaban (72h); differing pharmacology, both plausible ASRA cases |
| VENOUS #3 ↔ #17 | Great saphenous SVT 7cm long and 8cm from SFJ vs 4cm long and 1cm from SFJ, intentionally different anticoagulant dose strategy |
| VGEI #250 ↔ #275 | Graft preservation vs partial explantation, abdominal vs thoracic VGEI; different operation and recommendation |
| VASCULAR_TRAUMA #7 ↔ #97 | Adult vs pediatric grade-1-like blunt carotid injury; antiplatelet vs general early antithrombotic; population distinction needs pediatric-specific source |
| PAD_CLTI #1 ↔ #22 | Non-compressible ABI 1.54 in diabetes/CKD → TBI versus compressible normal resting ABI 1.08 with claudication → exercise ABI |
| VGEI #304 ↔ #316 | Cryopreserved arterial allografts in thoracic VGEI versus antimicrobial grafts in abdominal VGEI; distinct conduit and recommendation |

## Evidence audit notes — clinically significant, not mere pattern matching

1. **AMI/ACS transfusion threshold (P0 follow-up):** `AAA_EVAR #1106` says RBC transfusion with an Hb goal/range of 80–90 g/L for postoperative suspected ACS. The **2025 ACC/AHA multisociety ACS guideline** states that transfusion to maintain hemoglobin around 10 g/dL (100 g/L) **may be reasonable** in ACS with anemia and no active bleeding (class 2b, not a universal mandate); **AABB 2025** conditionally suggests a liberal strategy at Hb <10 g/dL in hospitalized AMI. Verify the intended test objective, question options and explanation against these sources; do not assert that 80–90 g/L is the single mandated target. Related `PERIOPERATIVE #227` is directionally compatible but nonspecific. Sources: https://professional.heart.org/en/science-news/2025-guideline-for-the-management-of-patients-with-acute-coronary-syndromes/top-things-to-know ; https://www.aabb.org/news-resources/news/article/2025/08/20/expert-panel-recommends-liberal-transfusion-strategy-for-hospitalized-patients-with-ami .
2. **Venous SVT distinction — supported:** `VENOUS #3` (≥5cm and >3cm from SFJ) matches SVS/AVF/AVLS 2023 prophylactic fondaparinux 2.5mg/day for 45 days; `VENOUS #17` (1cm from SFJ) calls for therapeutic anticoagulation. The duration for juxta-junctional SVT should be documented against a named guideline because duration differs across recommendations. Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC11523430/ .
3. **ASRA neuraxial interval distinction — supported in principle:** `PERIOPERATIVE #166` tests therapeutic enoxaparin 24h, `#168` high-dose rivaroxaban 72h. Check renal function, age and residual anti-Xa considerations per 2025 ASRA fifth edition rather than teaching fixed unconditional time intervals. Sources: https://rapm.bmj.com/content/early/2025/10/16/rapm-2024-105766 ; https://asra.com/the-asra-family/special-interest-groups/sig-article-item/legacy-b-blog-posts/2025/09/01/asra-pain-medicine-anticoagulation-pbld---regional-anesthesia-and-pain-procedures-in-anticoagulated-patients .
4. **Iliac threshold spot check — supported:** `AAA_EVAR #88` and `#264` correctly target consideration of intervention at 40mm for uncomplicated iliac artery aneurysm under ESVS 2024; this does not certify the other AAA items. Source: https://esvs.org/guideline/2024-abdominal-aorto-iliac-artery-aneurysms-guidelines/ .
5. **ESVS class IIIb is not intrinsically malformed.** Modern ESVS grading explicitly distinguishes class IIIa/IIIb in some 2025–26 documents. Any specific VGEI class/number claim still requires direct comparison to its original recommendation. Do not silently rewrite IIIb to III. Source: https://www.sciencedirect.com/science/article/pii/S107858842501319X .

## Other high-value QA corrections to queue

- `ANATOMY_IMAGING #62` explanation has exactly **two sentences**. The mechanical three-sentence warning was caused by the abbreviation `მაგ.`; mark **FALSE_POSITIVE** and optionally standardize to `მაგალითად` in a future reviewed edit.
- `AAA_EVAR #45/#149` and `AAA_EVAR explanation #149` contain `კოჭ-მხრის ინდექსი`. Prefer glossary-standard `გოჯ-მხრის ინდექსი` in context.
- Examples `DIALYSIS_ACCESS #152/#182/#643` of `სისხლძარღვოვანი წვდომა` need review for preferred `სისხლძარღვოვანი მიდგომა`.
- Flagged `დებრიდმენტი` in PAD_CLTI/VGEI explanations should be compared with preferred `ნეკრექტომია` where tissue excision is meant; avoid blind replacement in technical contexts.

## Next steps

- Expert adjudicator to approve each proposed duplicate and resolve the 2025 ACS target issue before production rewrite. Preserve original source and question IDs, create reviewed variant in separate QA output.
- Batchwise source-locked review under `QA/CLINICAL_REVIEW_PROTOCOL.md` and `QA/CLINICAL_REVIEW_BATCHES.csv`, with evidence at decision level and explicit status.
- No claim that more than these spot-reviewed pairs have been clinically verified. No final clinical approval is implied.
