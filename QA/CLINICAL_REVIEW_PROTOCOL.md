# VascQBank-10K — Mass Clinical QA protocol and source-locked review batches

**Frozen question/explanation source snapshot:** `9dd030de5d3be2b75226b58c78e7f77e56f1774b` (20 Nov 2026). This version contains 12 topics and 10,000 paired question/explanation entries. The production source TXT files are read-only throughout review. Batches are pinned by topic question-blob SHA in `QA/CLINICAL_REVIEW_BATCHES.csv`; before evaluating any batch, also pin and record the explanation-file SHA. If sources change, compare original to current, then revalidate changed questions; never silently treat reviewed entries as unchanged.

## Verified baseline (not clinical approval)

- **10,000 questions:** structural validation of numbering, five options, exactly one asterisk, paired explanations and answer-letter matching passed in GitHub Actions on 20 Nov 2026.
- **10,000 explanations:** complete count and numbering verified; one automatic three-sentence warning in ANATOMY_IMAGING #62 is a false positive caused by the abbreviation `მაგ.` in an otherwise two-sentence rationale.
- **Exact normalized repeated stems and exact repeated explanations:** none found. Two-stage lexical similarity searches are only *candidate selection*, not proof of absence of semantic duplicates. TF–IDF selected 12 pairs with cosine ≥0.56, including clinically distinct cases and possible overlapping decisions, in `QA/2026-11-20_SIMILARITY_REVIEW_CANDIDATES.md`.
- **Legacy review is stale:** `ACADEMIC_REVIEW/REFINEMENT_STATE.json` last updated 16 Nov 2026, covering 400 of a historical 493-question source (384 AI-approved, 16 pending); these statuses cannot be inherited as independent approvals for the new 10K snapshot without fingerprints and guideline re-check.
- **No independent clinician has signed off on this 10K snapshot.** Structural success is *not* permission to publish the test bank as medically validated.

## Work allocation and audit coverage

- **55 source-locked topic-specific batches, ≤200 questions each**, total **10000**. Process P0 before P1 before P2, balancing all 12 topics; smaller flagged sub-batches (20–50) are appropriate when evidence is conflicting.
- P0: ALI, VGEI, vascular trauma, AAA/EVAR, perioperative care (urgent decisions, anticoagulation, infection, device safety).
- P1: PAD/CLTI, thoracic aorta, carotid/vertebral, mesenteric/renal, dialysis access.
- P2: venous diseases and anatomy/imaging. **P2 is an ordering priority, not a lower standard of correctness.**

## Mandatory eight gates, per question

1. **Identity / structural integrity.** Confirm source topic, number, Git blob fingerprint; preserve original question, five answer options, marked letter and 2-sentence rationale. Fail on sequence/answer mismatch.
2. **Clinical coherence.** Independently verify patient context, anatomy, urgency, diagnosis and classification; flag omitted clinical assumptions and impossible physiology or procedural steps.
3. **Guideline concordance.** Compare the *precise clinical decision* with an authentic primary guideline/review (prefer ESVS latest applicable edition; include SVS, AHA/ACC, KDOQI etc where indicated). Capture document title, version/year, recommendation ID, class/level if actually present, page/section, DOI/URL, and access date. **Never invent recommendation numbers or grades.** Check whether the recommendation applies to the stem's population and exception conditions.
4. **Answer-key uniqueness.** Independently solve *without seeing the asterisk first*, assess every distractor, verify exactly one best answer. Log potential alternate acceptable answers, not merely grammatical flaws. High-risk disagreement must be adjudicated, never silently changed.
5. **Explanation scientific audit.** Match the chosen answer and reasoning against evidence. No invented trial claims, numerical effects, arbitrary thresholds, guideline recommendations, drug doses or unjustified 'always/never'. Enforce clear two-sentence explanation after substantive correction.
6. **Deduplication.** Check exact/lexical candidate reports *and* semantics within/among 12 topics: same tested clinical decision despite different demographics, devices, numeric camouflage, or prose. Mark duplicate only after explicit side-by-side rationale; preserve both until adjudication.
7. **Academic Georgian.** Prefer `გოჯ-მხრის ინდექსი`, `ნეკრექტომია`, `სისხლძარღვოვანი მიდგომა` where clinically applicable; translate operative repair as `რეკონსტრუქცია` or specified treatment, not blanket `აღდგენა`. Do not replace legitimate physiologic `პერფუზიის აღდგენა` mechanically. Follow latest `GLOSSARY.md`, avoid literal calques, keep precise anatomy and correct Georgian declension.
8. **Independent decision and sign-off.** Output clinical score, evidence strength, severity, correction diff and reviewer note; second independent review for wrong-key, safety-critical, ambiguous or guideline-discordant items; clinician sign-off before any `HUMAN_APPROVED` classification.

## Severity and dispositions

- **P0/CRITICAL:** incorrect key, multiple clinically valid answers, harmful or contraindicated intervention selected as correct, misquoted guideline recommendation affecting treatment, dose/timing/threshold likely to change patient management.
- **P1/MAJOR:** materially wrong rationale, outdated recommendation, incomplete condition, misleading investigation/decision path, semantic duplicate of the same assessed decision.
- **P2/MINOR:** terminology, phrasing, punctuation, abbreviation, distractor style with unchanged clinical meaning.
- **REVIEW_REQUIRED:** evidence unavailable, conflict not resolved, uncertain duplicate, or review without independent source verification.

Permitted per-question statuses: `NOT_STARTED`, `AI_SCREENED`, `EVIDENCE_VERIFIED`, `NEEDS_REVISION`, `DUPLICATE_CANDIDATE`, `ADJUDICATION_REQUIRED`, `HUMAN_APPROVED`, `REJECTED`. An AI suggestion never sets `HUMAN_APPROVED`.

## Required per-question audit record

Store JSONL under `QA/CLINICAL_BATCHES/<batch_id>/decisions.jsonl`; each record must have `source_snapshot_sha`, `question_blob_sha`, `explanation_blob_sha`, `topic`, `number`, `source_text_fingerprint`, `clinical_verdict`, `answer_key_verdict`, `explanation_verdict`, `language_verdict`, `duplicate_candidates`, `evidence` (URLs/DOIs/page/recommendation ID/class/level/access date), `severity`, `proposed_revision`, `independent_review_status`, `human_reviewer`, `human_approval_at`. Each batch also requires a summary, source hashes, exact counts and reproducible commit SHA. Never claim clinical review on the basis of automated string scans alone.

## Atomic publication and quality conditions

1. Before each batch, fetch `main` source plus `AGENTS.md`, `GLOSSARY.md`, the pinned question/explanation files, prior batch decisions and candidate list. If source SHA differs, evaluate changed records explicitly.
2. Publish *QA output only* to its separate directory; don't overwrite original question/explanation files. Use GitHub atomic tree/commit/lease update to avoid lost updates. Keep one authoritative reviewed master after expert acceptance.
3. Mark a batch `COMPLETE` only if all expected question IDs have exactly one disposition, evidence and required review are recorded, failures are resolved or explicitly rejected, and counts/fingerprints match. Track total reviewed and human approved independently.
4. No release until 10,000/10,000 have a final disposition; all P0 critical issues resolved, all ambiguities adjudicated, duplicates intentionally resolved, terminology audited and a signed human acceptance log exists. **10K generated does not necessarily equal 10K approved** if poor items must be replaced.

## Authoritative reference starting points

- ESVS 2024 abdominal aorto-iliac aneurysm: https://esvs.org/guideline/2024-abdominal-aorto-iliac-artery-aneurysms-guidelines/
- ESVS 2025 vascular trauma: https://esvs.org/guideline/vascular-trauma-2/
- ESVS 2026 descending thoracic/thoracoabdominal aorta: https://esvs.org/guideline/2026-dta-guidelines/
- ESVS 2026 VGEI: https://esvs.org/esvs-vgei-guidelines/
- Other disease topics: locate the latest applicable authentic ESVS, SVS, KDOQI and AHA/ACC documents for the specific issue; do not assume a single year/version across topics.

## Existing diagnostic reports

- `QA/2026-11-20_MASS_AUDIT_QUESTIONS.md`
- `QA/2026-11-20_MASS_AUDIT_EXPLANATIONS.md`
- `QA/2026-11-20_SIMILARITY_REVIEW_CANDIDATES.md`

**Report status:** baseline and review workflow established; human-verified clinical QA remains pending. No automated claim of medical approval.
