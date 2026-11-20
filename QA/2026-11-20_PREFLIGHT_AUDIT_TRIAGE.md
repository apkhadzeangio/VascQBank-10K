# VascQBank-10K — Pre-Flight High-Risk Triage for Final Audit

**Pinned question/explanation snapshot:** `9dd030de5d3be2b75226b58c78e7f77e56f1774b` (10,000 paired items). Supplements `QA/2026-11-20_MASS_AUDIT_QUESTIONS.md`, `QA/2026-11-20_MASS_AUDIT_EXPLANATIONS.md`, `QA/2026-11-20_SIMILARITY_REVIEW_CANDIDATES.md`, and `QA/2026-11-20_CLINICAL_SPOT_ADJUDICATION.md`.

## 1. Confirmed Unchanged Cross-Topic Semantic Overlaps (16 items)

Carried over from `ACADEMIC_REVIEW/REFINEMENT_ISSUES.jsonl` with identical SHA-256 fingerprints in the 10K snapshot (missed by pure lexical cosine):

| Global # | Topic # | Batch | Overlap / Issue Summary |
|---:|---|---|---|
| 1515 | ALI#15 | `ALI-0001-0200` | მთავარი გამოცდითი გადაწყვეტილება — ვარგისი დიდი საჩინო ვენის შერჩევა დისტალური შუნტისთვის — უკვე მოწმდება PAD_CLTI:4-ში. ანევრიზმის დამატება ამ კითხვაში სხვა გადაწყვეტილებას არ ქმნის. |
| 1521 | ALI#21 | `ALI-0001-0200` | წვივის ოთხივე კომპარტმენტის გადაუდებელი დეკომპრესიის გადაწყვეტილება უკვე სრულად მოწმდება VASCULAR_TRAUMA:4-ში; აქ ისევ იგივე ჩარევაა გამოსაცნობი. |
| 1535 | ALI#35 | `ALI-0001-0200` | ულტრაბგერითი კონტროლით ბარძაყის პუნქციის შერჩევა იმეორებს AAA_EVAR:28-ის მთავარ გადაწყვეტილებას; მხოლოდ ჩარევის დასახელებაა შეცვლილი. |
| 3605 | THORACIC_AORTA#5 | `THORACIC_AORTA-0001-0200` | პროქსიმალური ჰერმეტიზაციის დარღვევით IA ენდოლიკის ამოცნობა უკვე მოწმდება AAA_EVAR:4-ში; აორტის სეგმენტის შეცვლა დამოუკიდებელ საგამოცდო გადაწყვეტილებას არ ქმნის. |
| 3609 | THORACIC_AORTA#9 | `THORACIC_AORTA-0001-0200` | ახალგაზრდა დაბალი რისკის მარფანის პაციენტში საკუთარი აორტის ჰერმეტიზაციის ზონების გამო ღია რეკონსტრუქციის უპირატესობა იმეორებს AAA_EVAR:18-ის გადაწყვეტილებას. |
| 3617 | THORACIC_AORTA#17 | `THORACIC_AORTA-0001-0200` | დაკლაკნილ აორტაში ცენტრალური ხაზის პერპენდიკულარულად დიამეტრის გაზომვის გადაწყვეტილება იმეორებს AAA_EVAR:16-ს; გარეთა კიდეების დაზუსტება ცალკე დამოუკიდებელ სცენარს აქ არ ქმნის. |
| 3619 | THORACIC_AORTA#19 | `THORACIC_AORTA-0001-0200` | გამორიცხული I/III ენდოლიკის ფონზე სტაბილური ან შემცირებული ტომრის მქონე II ენდოლიკის დაკვირვების გადაწყვეტილება უკვე დაფარულია AAA_EVAR:7-ში. |
| 5223 | VENOUS#23 | `VENOUS-0001-0200` | ჰეპარინის შეწყვეტისა და არაჰეპარინული სამკურნალო ანტიკოაგულაციის დაწყების გადაწყვეტილება უკვე მოწმდება ALI:12-ში; ვენური საწყისი ეპიზოდი დამოუკიდებელ მთავარ გადაწყვეტილებას არ ამატებს. |
| 2445 | AAA_EVAR#45 | `AAA_EVAR-0001-0200` | რევასკულარიზაციის შემდეგ ახალი კოჭლობისა და ABI-ის დაქვეითებისას გამოსახულებითი შეფასების არჩევა უკვე მოწმდება ALI:30-ში; ამ ვარიანტში განსხვავებული მოწყობილობა დამოუკიდებელ მთავარ გადაწყვეტილებას არ ამატებს. |
| 2465 | AAA_EVAR#65 | `AAA_EVAR-0001-0200` | ზურგის ტვინის იშემიისას პერფუზიის გაძლიერებისა და გადაუდებელი CSF დრენირების გადაწყვეტილება უკვე დაფარულია THORACIC_AORTA:14-ში; რთული მუცლის ენდოპროთეზირება ამ ვარიანტში ახალ საგამოცდო გადაწყვეტილებას არ ქმნის. |
| 1548 | ALI#48 | `ALI-0001-0200` | ათეროემბოლიის დიაგნოსტიკური კომბინაცია — დაგვიანებული AKI, ლურჯი თითები, შენარჩუნებული პულსები და ეოზინოფილია — უკვე სრულად მოწმდება THORACIC_AORTA:33-ში. |
| 1559 | ALI#59 | `ALI-0001-0200` | მასიური ციანოზური შეშუპების, ფართო თეძო-ბარძაყის ვენური თრომბოზისა და შენარჩუნებული მთავარი არტერიების მიხედვით ლურჯი ფლეგმაზიის ამოცნობა იმეორებს VENOUS:28-ს. |
| 1561 | ALI#61 | `ALI-0001-0200` | არაფრაქცირებული ჰეპარინის დარჩენილი ეფექტის პროტამინით შებრუნების პრეპარატული არჩევანი უკვე მოწმდება CAROTID_VERTEBRAL:32-ში; ოპერაციის შეცვლა ამ ვარიანტში სხვა ძირითად ცოდნას არ ამოწმებს. |
| 1565 | ALI#65 | `ALI-0001-0200` | სამმაგად დადებითი APS-ისას ვარფარინის უპირატესობა DOAC-ებთან შედარებით უკვე მოწმდება VENOUS:6-ში; ამ ვარიანტში არტერიული ეპიზოდის დამატება სხვა პრეპარატულ გადაწყვეტილებას არ ცვლის. |
| 3654 | THORACIC_AORTA#54 | `THORACIC_AORTA-0001-0200` | ინფიცირებული მცირე ანევრიზმისას ზომითი ზღვრის ლოდინის ნაცვლად ანტიბიოტიკებისა და დროული რეკონსტრუქციის არჩევანი უკვე მოწმდება AAA_EVAR:26-ში; სეგმენტის შეცვლა ამ კითხვაში სხვა საგამოცდო გადაწყვეტილებას არ ქმნის. |
| 3662 | THORACIC_AORTA#62 | `THORACIC_AORTA-0001-0200` | ენდოგრაფტის იმპლანტაციის შემდეგ ადრეული სტერილური ანთებითი რეაქციის დიაგნოზი იმეორებს ამავე პარტიის AAA_EVAR:49-ს; აორტის სხვა სეგმენტი დამოუკიდებელ გადაწყვეტილებას არ ამატებს. |

## 2. Explicit Guideline Recommendation / Grade Citations (172 items)

Items explicitly citing recommendation numbers, Class (I/IIa/IIb/III), or Level (A/B/C) — mandatory line-by-line check against authentic guideline tables so no hallucinated or version-shifted grades survive:

| Topic | Explicit Grade/Number Citations |
|---|---:|
| PAD_CLTI | 8 |
| ALI | 0 |
| AAA_EVAR | 7 |
| THORACIC_AORTA | 17 |
| CAROTID_VERTEBRAL | 2 |
| VENOUS | 39 |
| DIALYSIS_ACCESS | 0 |
| MESENTERIC_RENAL | 0 |
| VASCULAR_TRAUMA | 5 |
| VGEI | 78 |
| ANATOMY_IMAGING | 0 |
| PERIOPERATIVE | 16 |

## 3. Psychometric Option-Length Cue Outliers (22 items)

Overall length balance is ideal (`1,970/10,000 = 19.7%` strictly longest correct option vs `20.0%` random expectation). Only these 22 items exceed `1.35×` and `+20` chars over the longest distractor (`AGENTS.md` §4.5):

| Global # | Topic # | Batch | Correct Chars | Max Distractor Chars |
|---:|---|---|---:|---:|
| 1577 | ALI#77 | `ALI-0001-0200` | 65 | 43 |
| 1609 | ALI#109 | `ALI-0001-0200` | 77 | 53 |
| 2517 | AAA_EVAR#117 | `AAA_EVAR-0001-0200` | 95 | 62 |
| 2540 | AAA_EVAR#140 | `AAA_EVAR-0001-0200` | 87 | 64 |
| 2555 | AAA_EVAR#155 | `AAA_EVAR-0001-0200` | 264 | 138 |
| 3456 | AAA_EVAR#1056 | `AAA_EVAR-1001-1200` | 65 | 42 |
| 3602 | THORACIC_AORTA#2 | `THORACIC_AORTA-0001-0200` | 79 | 55 |
| 3623 | THORACIC_AORTA#23 | `THORACIC_AORTA-0001-0200` | 69 | 36 |
| 4306 | CAROTID_VERTEBRAL#6 | `CAROTID_VERTEBRAL-0001-0200` | 99 | 54 |
| 4335 | CAROTID_VERTEBRAL#35 | `CAROTID_VERTEBRAL-0001-0200` | 75 | 49 |
| 4360 | CAROTID_VERTEBRAL#60 | `CAROTID_VERTEBRAL-0001-0200` | 79 | 55 |
| 4370 | CAROTID_VERTEBRAL#70 | `CAROTID_VERTEBRAL-0001-0200` | 65 | 30 |
| 5298 | VENOUS#98 | `VENOUS-0001-0200` | 72 | 46 |
| 7049 | MESENTERIC_RENAL#299 | `MESENTERIC_RENAL-0201-0400` | 75 | 54 |
| 7207 | MESENTERIC_RENAL#457 | `MESENTERIC_RENAL-0401-0600` | 108 | 79 |
| 7335 | MESENTERIC_RENAL#585 | `MESENTERIC_RENAL-0401-0600` | 69 | 49 |
| 8062 | VGEI#62 | `VGEI-0001-0200` | 92 | 67 |
| 9420 | PERIOPERATIVE#20 | `PERIOPERATIVE-0001-0200` | 95 | 69 |
| 9457 | PERIOPERATIVE#57 | `PERIOPERATIVE-0001-0200` | 88 | 59 |
| 9599 | PERIOPERATIVE#199 | `PERIOPERATIVE-0001-0200` | 118 | 82 |
| 9604 | PERIOPERATIVE#204 | `PERIOPERATIVE-0201-0400` | 103 | 73 |
| 9606 | PERIOPERATIVE#206 | `PERIOPERATIVE-0201-0400` | 109 | 75 |

## 4. Numeric-Start Non-Monotonic Option Candidates (51 items)

Candidates where all 5 options start with numbers that are neither ascending nor descending (verify whether mixed-parameter prose justifies order or reorder ascending per `AGENTS.md` §4.5):

`PAD_CLTI#937` (G#937), `PAD_CLTI#1288` (G#1288), `ALI#25` (G#1525), `ALI#84` (G#1584), `ALI#158` (G#1658), `ALI#181` (G#1681), `ALI#192` (G#1692), `ALI#346` (G#1846), `ALI#403` (G#1903), `ALI#676` (G#2176), `ALI#679` (G#2179), `AAA_EVAR#13` (G#2413), `AAA_EVAR#34` (G#2434), `AAA_EVAR#279` (G#2679), `AAA_EVAR#644` (G#3044), `AAA_EVAR#771` (G#3171), `AAA_EVAR#861` (G#3261), `AAA_EVAR#896` (G#3296), `AAA_EVAR#1062` (G#3462), `AAA_EVAR#1077` (G#3477), `AAA_EVAR#1100` (G#3500), `AAA_EVAR#1147` (G#3547), `THORACIC_AORTA#411` (G#4011), `CAROTID_VERTEBRAL#2` (G#4302), `CAROTID_VERTEBRAL#31` (G#4331), `CAROTID_VERTEBRAL#38` (G#4338), `CAROTID_VERTEBRAL#42` (G#4342), `VENOUS#12` (G#5212), `VENOUS#44` (G#5244), `VENOUS#52` (G#5252), `VENOUS#69` (G#5269), `VENOUS#368` (G#5568), `VENOUS#398` (G#5598), `VENOUS#497` (G#5697), `VENOUS#512` (G#5712), `VENOUS#630` (G#5830), `VENOUS#690` (G#5890), `VENOUS#864` (G#6064), `DIALYSIS_ACCESS#155` (G#6255), `DIALYSIS_ACCESS#182` (G#6282), `DIALYSIS_ACCESS#498` (G#6598), `DIALYSIS_ACCESS#580` (G#6680), `DIALYSIS_ACCESS#594` (G#6694), `DIALYSIS_ACCESS#601` (G#6701), `VGEI#302` (G#8302), `VGEI#311` (G#8311), `ANATOMY_IMAGING#45` (G#8545), `ANATOMY_IMAGING#582` (G#9082), `ANATOMY_IMAGING#666` (G#9166), `PERIOPERATIVE#62` (G#9462), `PERIOPERATIVE#171` (G#9571)

## 5. Source Internal Blank Lines & Legacy Import Terminology (5 items)

Normalized in `MASTER/VascQBank_10K_ALL_QUESTIONS.txt`, flagged for source/terminology cleanup during batch review (`თრომბოლიზისი` → `თრომბოლიზი`, `ქვედა ღრუ ვენა` → `ქვემო ღრუ ვენა`, ASCII quotes):

- `AAA_EVAR#154` (Global #2554, `AAA_EVAR-0001-0200`)
- `CAROTID_VERTEBRAL#174` (Global #4474, `CAROTID_VERTEBRAL-0001-0200`)
- `DIALYSIS_ACCESS#59` (Global #6159, `DIALYSIS_ACCESS-0001-0200`)
- `VASCULAR_TRAUMA#42` (Global #7392, `VASCULAR_TRAUMA-0001-0200`)
- `VGEI#62` (Global #8062, `VGEI-0001-0200`)
