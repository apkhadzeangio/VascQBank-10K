# VascQBank — 10K

სისხლძარღვთა ქირურგიის 10 000 პროფესიული ტესტის პროექტი.

- [AGENTS.md](AGENTS.md) — 12 თემატური ჩატის სამუშაო ინსტრუქციები.
- [GLOSSARY.md](GLOSSARY.md) — ერთიანი ქართული სამედიცინო გლოსარიუმი, დალაგებული თემების მიხედვით.

<!-- VASCQBANK_PROGRESS_START -->
## პროექტის მიმდინარე მდგომარეობა — 20 ნოემბერი 2026

**გენერაცია დასრულებულია: 10 000 / 10 000 კითხვა და 10 000 განმარტება.** მონაცემები დადასტურებულია `main` ბრენჩის 24 რეალური TXT ფაილით; საწყისი snapshot: [9dd030de5d3b](https://github.com/apkhadzeangio/VascQBank-10K/commit/9dd030de5d3be2b75226b58c78e7f77e56f1774b).

| თემა | შენახული კითხვები | სამიზნე | გენერაციის სტატუსი |
|---|---:|---:|---|
| [PAD_CLTI](PAD_CLTI_questions.txt) | 1500 | 1500 | დასრულებული |
| [ALI](ALI_questions.txt) | 900 | 900 | დასრულებული |
| [AAA_EVAR](AAA_EVAR_questions.txt) | 1200 | 1200 | დასრულებული |
| [THORACIC_AORTA](THORACIC_AORTA_questions.txt) | 700 | 700 | დასრულებული |
| [CAROTID_VERTEBRAL](CAROTID_VERTEBRAL_questions.txt) | 900 | 900 | დასრულებული |
| [VENOUS](VENOUS_questions.txt) | 900 | 900 | დასრულებული |
| [DIALYSIS_ACCESS](DIALYSIS_ACCESS_questions.txt) | 650 | 650 | დასრულებული |
| [MESENTERIC_RENAL](MESENTERIC_RENAL_questions.txt) | 600 | 600 | დასრულებული |
| [VASCULAR_TRAUMA](VASCULAR_TRAUMA_questions.txt) | 650 | 650 | დასრულებული |
| [VGEI](VGEI_questions.txt) | 500 | 500 | დასრულებული |
| [ANATOMY_IMAGING](ANATOMY_IMAGING_questions.txt) | 900 | 900 | დასრულებული |
| [PERIOPERATIVE](PERIOPERATIVE_questions.txt) | 600 | 600 | დასრულებული |
| **სულ** | **10 000** | **10 000** | **100%** |

**სტრუქტურული QA — PASS:** GitHub-ის [ბოლო დამტკიცებული ხარისხის შემოწმება](https://github.com/apkhadzeangio/VascQBank-10K/actions/runs/44682498400) დასრულდა წარმატებით. კითხვა/განმარტებების წყვილები, ნუმერაცია, ფორმატი და `AUTOMATION_CONTEXT.json` შეესაბამება ერთმანეთს.

**კლინიკური QA — სამუშაო პროცესში:** სტრუქტურული წარმატება არ ადასტურებს პასუხის სამეცნიერო სისწორეს, უნიკალურობას, თანამედროვე რეკომენდაციებთან შესაბამისობას ან დამოუკიდებელ ექსპერტულ დამტკიცებას. ისტორიული `ACADEMIC_REVIEW` მოიცავს მხოლოდ 400 ძველი კითხვიდან შეფასებულ ჩანაწერს და არ არის 10K-ზე სრული კლინიკური რევიზია.

- [10K კითხვა — ტექნიკური აუდიტი](QA/2026-11-20_MASS_AUDIT_QUESTIONS.md)
- [10K განმარტება — ტექნიკური აუდიტი](QA/2026-11-20_MASS_AUDIT_EXPLANATIONS.md)
- [სემანტიკური დამთხვევების კანდიდატები](QA/2026-11-20_SIMILARITY_REVIEW_CANDIDATES.md)
- [კლინიკური შერჩევითი შეფასება](QA/2026-11-20_CLINICAL_SPOT_ADJUDICATION.md)
- [რვადონიანი კლინიკური QA პროტოკოლი](QA/CLINICAL_REVIEW_PROTOCOL.md)
- [55 პარტია სრულ 10K კლინიკურ რევიზიაზე](QA/CLINICAL_REVIEW_BATCHES.csv)

**შენიშვნა:** ქვემოთ მოცემული ავტომატური მონიტორინგის ისტორიული ცხრილი შეიძლება განსხვავდებოდეს ამ მოგვიანო, უშუალოდ TXT-ით დადასტურებული რაოდენობებისგან.

<!-- VASCQBANK_PROGRESS_END -->

<!-- VASCQBANK_MONITORING_START -->
### აგენტების მონიტორინგი და ხარისხის კონტროლი

**შემოწმებულია:** 2026-11-20 14:36 (თბილისი). **Heartbeat-ით დადასტურებული მიმდინარე სამუშაო:** 0; **Heartbeat-ინტეგრირებული თემები:** 0/12. სხვა ChatGPT ანგარიშების ავტომატიზაციების მდგომარეობა მიუწვდომელია.

| თემა | კითხვები | ბოლო წარმატებული ატვირთვა | +24სთ | სტატუსი | Quality Gate | ინდექსი | შენიშვნა |
|---|---:|---|---:|---|---|---|---|
| PAD_CLTI | 1500/1500 | 2026-11-20 08:26 | +906 | COMPLETE | SUCCESS | OK | Heartbeat დასაკავშირებელია |
| ALI | 900/900 | 2026-11-20 09:01 | +773 | COMPLETE | SUCCESS | OK | Heartbeat დასაკავშირებელია |
| AAA_EVAR | 1200/1200 | 2026-11-19 08:29 | +0 | COMPLETE | SUCCESS | OK | Heartbeat დასაკავშირებელია |
| THORACIC_AORTA | 700/700 | 2026-11-19 09:17 | +0 | COMPLETE | SUCCESS | OK | Heartbeat დასაკავშირებელია |
| CAROTID_VERTEBRAL | 900/900 | 2026-11-19 04:40 | +0 | COMPLETE | SUCCESS | OK | Heartbeat დასაკავშირებელია |
| VENOUS | 900/900 | 2026-11-19 12:27 | +0 | COMPLETE | SUCCESS | OK | Heartbeat დასაკავშირებელია |
| DIALYSIS_ACCESS | 650/650 | 2026-11-19 10:35 | +0 | COMPLETE | SUCCESS | OK | Heartbeat დასაკავშირებელია |
| MESENTERIC_RENAL | 600/600 | 2026-11-20 08:54 | +543 | COMPLETE | SUCCESS | OK | Heartbeat დასაკავშირებელია |
| VASCULAR_TRAUMA | 650/650 | 2026-11-17 17:26 | +0 | COMPLETE | SUCCESS | OK | Heartbeat დასაკავშირებელია |
| VGEI | 500/500 | 2026-11-18 23:47 | +0 | COMPLETE | SUCCESS | OK | Heartbeat დასაკავშირებელია |
| ANATOMY_IMAGING | 900/900 | 2026-11-20 09:12 | +838 | COMPLETE | SUCCESS | OK | Heartbeat დასაკავშირებელია |
| PERIOPERATIVE | 600/600 | 2026-11-19 08:29 | +0 | COMPLETE | SUCCESS | OK | Heartbeat დასაკავშირებელია |

PRODUCING ნიშნავს ახლახან დადასტურებულ ატვირთვას და არა აქტიურ ჩატს. UNKNOWN არ ნიშნავს მუშაობის შეწყვეტას. Quality Gate ამოწმებს მხოლოდ სტრუქტურას, არა დამოუკიდებელ კლინიკურ ხარისხს. მონიტორი არ ცვლის კითხვებს, განმარტებებს ან საერთო ინდექსს.
<!-- VASCQBANK_MONITORING_END -->
