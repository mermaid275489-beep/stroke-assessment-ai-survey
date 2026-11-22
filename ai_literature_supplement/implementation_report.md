# AI motion-analysis literature search: implementation report

## Completed

- Four evidence streams were encoded: gait/mobility, upper-limb dexterity, trunk/balance/compensation, and strength/power.
- The legacy 274-record PubMed pool and 200-record factor-extraction pool were retained and rescreened as candidate sources.
- Four uncapped PubMed searches were executed without a starting-year restriction.
- Exact DOI/PMID known-item testing passed for Alt Murphy 2011, Tsai 2021, Abdollahi 2024, Geerars 2025 and Kristensen 2017.
- DOI, PMID and normalized title-year-first-author deduplication was applied.
- Machine-assisted title/abstract screening and component-level coding were generated for downstream full-text review.
- Excel workbooks, full-text extraction fields, search logs, BibTeX candidates and figure-source data were generated.

## Current counts

- New PubMed source records: 14,320.
- Legacy candidate records: 474.
- Combined source records before deduplication: 14,794.
- Unique records after deduplication: 10,084.
- Tier A title/abstract candidates: 245.
- Tier B title/abstract candidates: 812.
- Uncertain records: 4,245.
- Title/abstract exclusions: 4,782.
- Final full-text inclusions: 0 locked at this stage.

## Limitations requiring completion

- The strength/power PubMed query reported 3,928 records and returned 3,926 metadata records; this stream is marked incomplete and must not be used as a locked retrieval count until the two missing records are resolved.
- OpenAlex was attempted but returned HTTP 429. No OpenAlex records were merged.
- Embase, IEEE Xplore, Scopus/Web of Science and CINAHL exports have not been supplied.
- All Tier A and Tier B values remain title/abstract candidates until full texts are reviewed and disputed records are adjudicated.
- Figure 2 source data are deliberately marked ineligible for final plotting until full-text review is complete.
