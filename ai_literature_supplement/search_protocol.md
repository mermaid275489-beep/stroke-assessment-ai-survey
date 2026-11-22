# Component-specific supplementary search protocol

Protocol version: 1.0  
Search date: 2026-07-28  
Review topic: Objective, component-level AI and computational motion assessment after adult stroke

## Review question

Which sensing modalities, machine-observable features, computational methods, and validation approaches have been used to quantify clinically meaningful movement components after adult stroke?

The seven analytic components are:

1. range of motion;
2. muscle strength and power;
3. coordination and selective motor control;
4. balance and postural control;
5. manual dexterity;
6. gait and mobility; and
7. movement quality and compensation.

These components are an analytic synthesis derived from the assessment-tool item review. They are not presented as an externally validated taxonomy.

## Evidence streams

| Stream code | Scope |
|---|---|
| `gait_mobility` | Gait, walking, stepping, turning, transfers, and transitional mobility |
| `upper_limb_dexterity` | Upper-limb motor capacity, reaching, grasping, object manipulation, and manual dexterity |
| `trunk_balance_compensation` | Trunk control, sitting or standing balance, postural sway, weight bearing, movement quality, and compensation |
| `strength_power` | Muscle force, joint torque, power, propulsion, dynamometry, force measurement, and electromyography |

The existing 274-record PubMed pool and 200-record factor-extraction pool are retained as legacy candidate sources. Neither is treated as a set of included studies without rescreening.

## Sources

### Sources searched directly

- PubMed/MEDLINE through NCBI E-utilities.
- OpenAlex as a public cross-disciplinary index. OpenAlex searches are restricted to titles and abstracts and include journal articles and proceedings articles.

### Sources awaiting user or institutional export

- Embase;
- IEEE Xplore;
- Scopus or Web of Science; and
- CINAHL.

RIS, BibTeX, NBIB, or CSV exports from these sources will be merged into the same deduplication and screening pipeline. Until those exports are available, the search is reported as a public-database supplementary search rather than a complete subscription-database search.

## PubMed search blocks

### Population

```text
("Stroke"[Mesh] OR stroke*[tiab] OR poststroke[tiab]
OR post-stroke[tiab] OR hemipar*[tiab]
OR cerebrovascular accident*[tiab])
```

### Technology and quantitative measurement

```text
("Motion Analysis, Computer-Assisted"[Mesh]
OR "Artificial Intelligence"[Mesh]
OR "Machine Learning"[Mesh]
OR "Wearable Electronic Devices"[Mesh]
OR motion captur*[tiab] OR markerless[tiab]
OR kinematic*[tiab] OR "movement analysis"[tiab]
OR pose estimat*[tiab] OR computer vision[tiab]
OR video-based[tiab] OR RGB[tiab] OR RGB-D[tiab]
OR depth camera*[tiab] OR Kinect[tiab]
OR inertial sensor*[tiab] OR inertial measurement unit*[tiab]
OR IMU[tiab] OR wearable sensor*[tiab]
OR force plate*[tiab] OR pressure sensor*[tiab]
OR electromyogra*[tiab] OR EMG[tiab]
OR dynamometr*[tiab] OR isokinetic[tiab] OR force transducer*[tiab]
OR instrumented device*[tiab] OR sensor fusion[tiab]
OR signal processing[tiab] OR machine learning[tiab]
OR deep learning[tiab] OR algorithm*[tiab])
```

### Gait and mobility

```text
("Gait"[Mesh] OR gait[tiab] OR walk*[tiab]
OR ambulation[tiab] OR locomot*[tiab] OR mobility[tiab]
OR step*[tiab] OR turning[tiab] OR sit-to-stand[tiab]
OR transfer*[tiab])
```

### Upper limb and manual dexterity

```text
("Upper Extremity"[Mesh] OR upper limb*[tiab]
OR upper extremit*[tiab] OR paretic arm[tiab]
OR hand[tiab] OR shoulder[tiab] OR elbow[tiab] OR wrist[tiab]
OR reach*[tiab] OR grasp*[tiab] OR dexter*[tiab]
OR hand-object interaction*[tiab] OR object manipulation[tiab]
OR drinking task*[tiab] OR block transfer*[tiab]
OR peg test*[tiab])
```

### Trunk, balance, and compensation

```text
("Postural Balance"[Mesh] OR trunk[tiab] OR torso[tiab]
OR sitting balance[tiab] OR trunk control[tiab]
OR postural control[tiab] OR postural sway[tiab]
OR trunk displacement[tiab] OR sit-to-stand[tiab]
OR weight-bearing[tiab] OR compensat*[tiab]
OR movement quality[tiab] OR movement smoothness[tiab])
```

### Strength and power

```text
("Muscle Strength"[Mesh] OR "Muscle Strength Dynamometer"[Mesh]
OR muscle strength[tiab] OR muscle force[tiab]
OR joint torque[tiab] OR muscle power[tiab]
OR propulsion[tiab] OR dynamometr*[tiab]
OR isokinetic[tiab] OR electromyogra*[tiab] OR EMG[tiab])
```

Each complete PubMed query is:

```text
Population AND Technology AND stream-specific block
```

No publication-date or language restriction is applied at retrieval.

## OpenAlex strategy

OpenAlex uses an equivalent Boolean query over the `title_and_abstract.search` field. The technology block includes motion capture, kinematics, movement analysis, pose estimation, video, inertial sensors, force or pressure sensing, electromyography, dynamometry, isokinetic testing and computational methods. Wildcards are expanded to explicit variants because OpenAlex Boolean search does not support wildcard characters. Records are restricted to `article` and `proceedings-article`, and retracted or paratext records are excluded. In the current run, OpenAlex returned HTTP 429 and no records were merged.

## Translation for subscription databases

### Embase

```text
('cerebrovascular accident'/exp OR stroke*:ti,ab,kw OR poststroke:ti,ab,kw
OR 'post-stroke':ti,ab,kw OR hemipar*:ti,ab,kw)
AND
('motion analysis'/exp OR 'artificial intelligence'/exp OR 'machine learning'/exp
OR 'wearable device'/exp OR 'motion capture':ti,ab,kw OR markerless:ti,ab,kw
OR 'pose estimation':ti,ab,kw OR 'computer vision':ti,ab,kw
OR video:ti,ab,kw OR 'inertial sensor':ti,ab,kw OR imu:ti,ab,kw
OR 'force plate':ti,ab,kw OR 'pressure sensor':ti,ab,kw
OR electromyography:ti,ab,kw OR emg:ti,ab,kw)
AND
(STREAM_BLOCK)
```

### IEEE Xplore

```text
("All Metadata":stroke OR "All Metadata":"post-stroke"
OR "All Metadata":poststroke OR "All Metadata":hemiparesis)
AND
("All Metadata":"motion capture" OR "All Metadata":markerless
OR "All Metadata":"pose estimation" OR "All Metadata":"computer vision"
OR "All Metadata":video OR "All Metadata":"inertial sensor"
OR "All Metadata":IMU OR "All Metadata":"wearable sensor"
OR "All Metadata":"force plate" OR "All Metadata":"pressure sensor"
OR "All Metadata":electromyography OR "All Metadata":EMG
OR "All Metadata":"machine learning" OR "All Metadata":"deep learning")
AND
(STREAM_BLOCK)
```

### Scopus

```text
TITLE-ABS-KEY(stroke* OR poststroke OR "post-stroke" OR hemipar*
OR "cerebrovascular accident")
AND TITLE-ABS-KEY("motion capture" OR markerless OR "pose estimation"
OR "computer vision" OR video OR RGB OR RGB-D OR "depth camera"
OR Kinect OR "inertial sensor" OR "inertial measurement unit" OR IMU
OR "wearable sensor" OR "force plate" OR "pressure sensor"
OR electromyograph* OR EMG OR "instrumented device"
OR "signal processing" OR "machine learning" OR "deep learning")
AND TITLE-ABS-KEY(STREAM_BLOCK)
```

### Web of Science

```text
TS=(stroke* OR poststroke OR "post-stroke" OR hemipar*
OR "cerebrovascular accident")
AND TS=("motion capture" OR markerless OR "pose estimation"
OR "computer vision" OR video OR RGB OR RGB-D OR "depth camera"
OR Kinect OR "inertial sensor" OR "inertial measurement unit" OR IMU
OR "wearable sensor" OR "force plate" OR "pressure sensor"
OR electromyograph* OR EMG OR "instrumented device"
OR "signal processing" OR "machine learning" OR "deep learning")
AND TS=(STREAM_BLOCK)
```

### CINAHL

```text
(MH "Stroke+" OR TI(stroke* OR poststroke OR "post-stroke" OR hemipar*)
OR AB(stroke* OR poststroke OR "post-stroke" OR hemipar*))
AND
(MH "Artificial Intelligence+" OR MH "Wearable Sensors+"
OR TI("motion capture" OR markerless OR "pose estimation" OR "computer vision"
OR video OR "inertial sensor" OR IMU OR "force plate" OR electromyography)
OR AB("motion capture" OR markerless OR "pose estimation" OR "computer vision"
OR video OR "inertial sensor" OR IMU OR "force plate" OR electromyography))
AND
(STREAM_BLOCK)
```

`STREAM_BLOCK` is replaced with the corresponding component-specific terms above.

## Known-item testing

The search is checked against:

- Alt Murphy et al. (2011), three-dimensional upper-limb kinematics after stroke;
- Tsai et al. (2021), egocentric video and hand use after stroke;
- Abdollahi et al. (2024), wearable-sensor balance or fall-risk assessment;
- Geerars et al. (2025), postural-sway responsiveness after stroke; and
- Kristensen et al. (2017), post-stroke strength measurement.

Failure to retrieve a known item triggers query review. A known item is not manually inserted into the search results unless it is separately identified through citation chasing and labelled as such.

## Eligibility

### Tier A: core clinical evidence

All of the following are required:

- adult participants with stroke;
- original peer-reviewed full article or full proceedings paper;
- an explicit movement or functional task;
- video, motion capture, inertial, pressure, force, electromyographic, or instrumented-device signals;
- at least one quantitative output mapped to a movement component;
- a computational procedure for detection, segmentation, estimation, classification, regression, clustering, or monitoring; and
- technical performance, reliability, clinical validity, responsiveness, or external validation.

Mixed-population studies enter Tier A only when stroke data are separately extractable.

### Tier B: supporting evidence

- stroke-specific measurement or biomechanical studies that establish a feature or measurement boundary but are not AI studies; or
- healthy-participant technical-validation studies directly supporting a sensing or feature-extraction method.

Tier B records do not contribute to the core stroke-AI study count.

### Exclusions

- paediatric or non-stroke populations without separately extractable stroke data;
- animal or in-vitro studies;
- intervention-only studies without quantitative movement assessment;
- neuroimaging-only studies;
- devices without participant data or validation;
- reviews, editorials, protocols, conference abstracts, or papers without complete data;
- prediction of a clinical total score without component-level motion information; and
- self-report only.

## Screening and adjudication

1. Deduplicate by DOI, then PMID, then normalized title plus year and first author.
2. Screen titles and abstracts.
3. Retrieve full text where available and record a single primary exclusion reason.
4. Retain uncertain records in an adjudication queue.
5. Conduct backward and forward citation chasing for included studies.
6. Update the search before submission.

The automated pipeline performs first-pass title/abstract screening and records the rule evidence. It does not replace the required second-reviewer or author adjudication. Final study counts are locked only after that review.

## Data extraction

```text
Study ID
Source stream
Database
Population and stroke stage
Sample size
Assessment task
Body region
Movement component
Sensing modality
Sensor placement or camera view
Machine-observable feature
Computational method family
Output type
Reference standard
Evaluation metric
Direct, proxy, or not-derivable status
Reliability
Clinical validity
Responsiveness
External validation
Evidence tier
Screening decision
Primary exclusion reason
Verification status
Principal limitation
```

A study may contribute to multiple movement components, but it is counted once in the total number of included studies. Component counts are therefore not mutually exclusive.

## Reporting standards

- JBI evidence-synthesis search guidance;
- PRISMA-S for search reporting; and
- PRESS for peer review of electronic search strategies.
