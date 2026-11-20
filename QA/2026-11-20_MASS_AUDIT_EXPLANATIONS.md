# VascQBank-10K — Massive QA / Pass 2: Explanations

**Snapshot:** `9dd030de5d3be2b75226b58c78e7f77e56f1774b`, 20 November 2026. **Scope:** all 12 production explanation TXT files, 10000 numbered explanations. **Method:** numbering/labels, heuristic two-sentence format, word-count outliers, exact repeated rationale, and targeted terminology patterns. **No AI clinical approval is implied.**

## Findings

- Retrieved 12/12 explanation files; missing 0.
- Numbered explanations 10000.
- Non-sequential numbering records: 0.
- Sentence review flags: 1.
- Explanations under 18 tokens: 1.
- Explanations above 130 tokens: 0.
- Identical rationales across questions: 0.
- Terminology substring occurrences: 15 (manual-context checks only).

| Topic | Count | Nonsequential | Sentence flags | Under 18 words | Over 130 | Repeated explanations | Terminology flags |
|---|---:|---:|---:|---:|---:|---:|---:|
| AAA_EVAR | 1200 | 0 | 0 | 0 | 0 | 0 | 1 |
| ALI | 900 | 0 | 0 | 1 | 0 | 0 | 1 |
| ANATOMY_IMAGING | 900 | 0 | 1 | 0 | 0 | 0 | 0 |
| CAROTID_VERTEBRAL | 900 | 0 | 0 | 0 | 0 | 0 | 1 |
| DIALYSIS_ACCESS | 650 | 0 | 0 | 0 | 0 | 0 | 3 |
| MESENTERIC_RENAL | 600 | 0 | 0 | 0 | 0 | 0 | 0 |
| PAD_CLTI | 1500 | 0 | 0 | 0 | 0 | 0 | 3 |
| PERIOPERATIVE | 600 | 0 | 0 | 0 | 0 | 0 | 0 |
| THORACIC_AORTA | 700 | 0 | 0 | 0 | 0 | 0 | 0 |
| VASCULAR_TRAUMA | 650 | 0 | 0 | 0 | 0 | 0 | 4 |
| VENOUS | 900 | 0 | 0 | 0 | 0 | 0 | 0 |
| VGEI | 500 | 0 | 0 | 0 | 0 | 0 | 2 |

## Actionable rationale review queue

### terminology: სამედიცინო რეკონსტრუქციის არაზუსტი ტერმინი: 5

- **ALI #97**:  კლინიკური აღწერებიც ადასტურებს ღია მოცილებისა და არტერიის აღდგენის შესაძლებლობას; ამ კონკრეტულ ანატომიაში მხოლოდ ჰეპარინიზაც 
- **VASCULAR_TRAUMA #37**: ექტის გაკერვა ერთდროულად ახდენს დეკომპრესიასაც და არტერიის აღდგენის გარეშე ანატომიურ ჰემოსტაზსაც. 
- **VASCULAR_TRAUMA #385**: ნირებით და გადაუდებელი ღია ქირურგიული დეკომპრესია არტერიის აღდგენით. 
- **VASCULAR_TRAUMA #400**: ი კონტროლის მოპოვების შემდეგ ტროაკარის ამოღება და არტერიის აღდგენა. 
- **VASCULAR_TRAUMA #608**: დან ხელისგულის რკალის რეტროგრადული შევსება სხივის არტერიის აღდგენის ან ლიგირების გადაწყვეტამდე. 

### terminology: დებრიდმენტი: 5

- **PAD_CLTI #1364**: კულარიზაციის სეპტიურ გართულებებს. გადაუდებელი ღია დებრიდმენტი და ინფიცირებული თითების მოცილება სწრაფად აჩერებს ინფექციას 
- **PAD_CLTI #1435**: ინფიცირებული საზარდული პროთეზის ექსპლანტაციისა და დებრიდმენტისთვის, რაც თავიდან იცილებს ახალი შუნტის ჯვარედინ კონტამინაც 
- **PAD_CLTI #1436**: ის სრულ ექსპლანტაციას, ნეკროზული კედლის რადიკალურ დებრიდმენტსა და აუტოლოგიურ ან ექსტრაანატომიურ რეკონსტრუქციას. 
- **VGEI #39**: ედო პროფილაქტიკა მოითხოვს აორტის კედლის რადიკალურ დებრიდმენტს ჯანსაღ ქსოვილამდე, დაჭიმულობის გარეშე არააბსორბირებადი მონ 
- **VGEI #44**:  პროთეზის სრული ექსპლანტაცია, ჭრილობის რადიკალური დებრიდმენტი, ბარძაყის არტერიის დეფექტის აუტოვენური ნაფლეთით პლასტიკა დ 

### terminology: სისხლძარღვოვანი წვდომის ტერმინი: 3

- **DIALYSIS_ACCESS #152**: იოვენური პროთეზი საიმედო და სწრაფად გამოსაყენებელ სისხლძარღვოვან წვდომას უზრუნველყოფს. ეს ტაქტიკა შეესაბამება ინდივიდუალიზებული მკ 
- **DIALYSIS_ACCESS #182**: დასვლა ტუნელირებულ, მანჟეტიან კათეტერზე ან მუდმივ სისხლძარღვოვან წვდომაზე. 
- **DIALYSIS_ACCESS #643**: ში 10–12 პუნქცია მაღალ მექანიკურ დატვირთვას ქმნის სისხლძარღვოვან წვდომაზე, რის გამოც კედლის რეგენერაციის უნარი და ინფექციური მდგრა 

### terminology: გოჯ-მხრის ალტერნატივა: 1

- **AAA_EVAR #149**: ვითარებული დუნდულოს გარდამავალი კოჭლობა ნორმალური კოჭ-მხრის ინდექსისა და გამავალი ენდოპროთეზის ფონზე განპირობებულია დუნ 

### short: 1

- **ALI #110**: ალტეპლაზა რეკომენდებული რეკომბინანტული ქსოვილოვანი პლაზმინოგენის აქტივატორია კიდურის კათეტერით მიმართული თრომბოლიზისთვის. იგი ამ ჩვენებისთვის უროკინაზის მიღებულ ალტერნატივას წარმოადგენს. 

### sentences: 1

- **ANATOMY_IMAGING #62**: ადამკევიჩის არტერია (დიდი წინა რადიკულომედულური არტერია) უზრუნველყოფს ზურგის ტვინის ქვედა თორაკოლუმბალური ნაწილის წინა ორი მესამედის ძირითად სისხლმომარაგებას ზურგის ტვინის წინა არტერიის გავლით და შემთხვევათა ~75–89%-ში გამოდის მარცხენა მხრიდან, T8–L2 (უხშირესად T8–L1) მალების დონეზე. TEVAR-ის ან ღია თორაკოაბდომინური ოპერაციის დაგეგმვისას მისი CTA-ით წინასწარი იდენტიფიცირება მნიშვნელოვანია ზურგის ტვინის იშემიის რისკის შესაფასებლად და ნეი (sentence markers 3)

### terminology: გაუმსკდარი: 1

- **CAROTID_VERTEBRAL #609**: ოებით 12–20%-ს აღენიშნება თავის ტვინის არტერიების გაუმსკდარი ტომრისებრი ანევრიზმა, რაც ზოგად პოპულაციაზე მნიშვნელოვნად  

## Repeated rationale candidates

None by exact normalized text.

## Caution

A perfectly formatted answer explanation may still be clinically wrong, out of date, non-evidence-based, or inconsistent with the stem. Automated two-sentence and terminology flags are triage, not final editorial judgments. The repository's structural QA compares explanation letters with marked answers; evidence-based review still requires source-by-source checks.
