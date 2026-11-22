# AI motion-analysis screening report (verified public-database stage)

## Scope

The screening pool contained 10,084 unique records after automated cross-stream deduplication. The current public-database search log reports 14,794 raw records, 4,710 duplicates, 4,782 title/abstract exclusions, 245 provisional Tier-A candidates, 812 provisional Tier-B candidates and 4,245 uncertain records. These numbers describe the candidate-screening stage; they are not the final number of included studies.

The present evidence set contains 21 original studies whose PubMed record and/or accessible full text were checked for population, task, sensing modality, computational method, output and validation. The set includes adult post-stroke studies and explicitly identifies conventional motion-analysis support separately from AI/algorithmic evidence.

## Decisions

- Verified evidence set: **21 studies**.
- Tier A: **16 studies** with a post-stroke original study and a computational/algorithmic component-level or task-level output.
- Tier B: **5 studies** used as conventional motion-analysis or measurement support; these are not counted as validated AI studies.
- The verified set spans the seven movement components; assignments are non-exclusive.
- Records not in the verified set remain `pending full-text review` and are not used as final AI evidence in the compact table.

## Evidence boundary

The verified studies support feature families such as joint excursion, gait timing, speed, asymmetry, trajectory smoothness, task segmentation, trunk sway, task completion and movement-quality classification. They do not establish that ordinary video directly measures force, muscle activation, tone, reflexes, tactile sensation, assistance requirements or self-report. These constructs remain proxy-based or not derivable from motion alone.

## Search limitation

The current search is a public-database stage based on PubMed and local legacy records. Embase, IEEE Xplore, Scopus/Web of Science and CINAHL export files were not available in the workspace, and OpenAlex retrieval was incomplete. Therefore, the verified set is suitable for a conservative working table and feature-evidence audit, but it must not be reported as the final multi-database systematic-review count until those sources are merged and the remaining candidates undergo full-text adjudication.

## Reproducibility files

- `verified_ai_evidence_set.csv`: the checked evidence set and extracted fields.
- `component_evidence_extraction_screened.csv`: the original 10,084-row extraction pool with verified rows updated; all other rows remain pending.
- `search_log.xlsx`, `prisma_flow_counts.csv` and `screening_status.md`: public-stage search and screening metadata.
