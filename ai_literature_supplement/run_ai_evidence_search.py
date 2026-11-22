from __future__ import annotations

import argparse
import csv
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
RAW_DIR = ROOT / "raw"
OUTPUT_DIR = ROOT / "outputs"
TODAY = date.today().isoformat()
USER_AGENT = "StrokeComponentReview/1.0 (systematic-search; contact=local-user)"

PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
OPENALEX_BASE = "https://api.openalex.org/works"

POPULATION_PUBMED = r"""("Stroke"[Mesh] OR stroke*[tiab] OR poststroke[tiab]
OR post-stroke[tiab] OR hemipar*[tiab]
OR cerebrovascular accident*[tiab])"""

TECHNOLOGY_PUBMED = r"""("Motion Analysis, Computer-Assisted"[Mesh]
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
OR deep learning[tiab] OR algorithm*[tiab])"""

STREAMS = {
    "gait_mobility": {
        "pubmed": r"""("Gait"[Mesh] OR gait[tiab] OR walk*[tiab]
OR ambulation[tiab] OR locomot*[tiab] OR mobility[tiab]
OR step*[tiab] OR turning[tiab] OR sit-to-stand[tiab]
OR transfer*[tiab])""",
        "openalex": """(gait OR walking OR ambulation OR locomotion OR mobility
OR stepping OR turning OR "sit-to-stand" OR transfer)""",
    },
    "upper_limb_dexterity": {
        "pubmed": r"""("Upper Extremity"[Mesh] OR upper limb*[tiab]
OR upper extremit*[tiab] OR paretic arm[tiab]
OR hand[tiab] OR shoulder[tiab] OR elbow[tiab] OR wrist[tiab]
OR reach*[tiab] OR grasp*[tiab] OR dexter*[tiab]
OR hand-object interaction*[tiab] OR object manipulation[tiab]
OR drinking task*[tiab] OR block transfer*[tiab]
OR peg test*[tiab])""",
        "openalex": """("upper limb" OR "upper extremity" OR "paretic arm"
OR hand OR shoulder OR elbow OR wrist OR reaching OR grasping OR dexterity
OR "hand-object interaction" OR "object manipulation" OR "drinking task"
OR "block transfer" OR "peg test")""",
    },
    "trunk_balance_compensation": {
        "pubmed": r"""("Postural Balance"[Mesh] OR trunk[tiab] OR torso[tiab]
OR sitting balance[tiab] OR trunk control[tiab]
OR postural control[tiab] OR postural sway[tiab]
OR trunk displacement[tiab] OR sit-to-stand[tiab]
OR weight-bearing[tiab] OR compensat*[tiab]
OR movement quality[tiab] OR movement smoothness[tiab])""",
        "openalex": """(trunk OR torso OR "sitting balance" OR "trunk control"
OR "postural control" OR "postural sway" OR "trunk displacement"
OR "sit-to-stand" OR "weight bearing" OR compensation
OR "movement quality" OR "movement smoothness")""",
    },
    "strength_power": {
        "pubmed": r"""("Muscle Strength"[Mesh] OR "Muscle Strength Dynamometer"[Mesh]
OR muscle strength[tiab] OR muscle force[tiab]
OR joint torque[tiab] OR muscle power[tiab]
OR propulsion[tiab] OR dynamometr*[tiab]
OR isokinetic[tiab] OR electromyogra*[tiab] OR EMG[tiab])""",
        "openalex": """("muscle strength" OR "muscle force" OR "joint torque"
OR "muscle power" OR propulsion OR dynamometry OR dynamometer
OR isokinetic OR electromyography OR EMG)""",
    },
}

POPULATION_OPENALEX = """(stroke OR "post-stroke" OR poststroke OR hemiparesis
OR hemiparetic OR "cerebrovascular accident")"""

TECHNOLOGY_OPENALEX = """("motion capture" OR markerless OR kinematic
OR kinematics OR "movement analysis" OR "pose estimation"
OR "computer vision" OR video OR RGB OR "RGB-D" OR "depth camera" OR Kinect
OR "inertial sensor" OR "inertial measurement unit" OR IMU OR "wearable sensor"
OR "force plate" OR "pressure sensor" OR electromyography OR EMG
OR dynamometry OR dynamometer OR isokinetic
OR "instrumented device" OR "sensor fusion" OR "signal processing"
OR "machine learning" OR "deep learning" OR algorithm)"""

KNOWN_ITEMS = [
    {
        "name": "Alt Murphy 2011",
        "doi": "10.1177/1545968310370748",
        "pmid": "20829411",
        "title_terms": ["kinematic", "upper", "stroke"],
        "expected_stream": "upper_limb_dexterity",
    },
    {
        "name": "Tsai 2021",
        "doi": "10.1109/JTEHM.2021.3072347",
        "pmid": "33889453",
        "title_terms": ["hand", "stroke", "egocentric"],
        "expected_stream": "upper_limb_dexterity",
    },
    {
        "name": "Abdollahi 2024",
        "pmid": "38339529",
        "title_terms": ["fall risk", "stroke", "machine learning"],
        "expected_stream": "trunk_balance_compensation",
    },
    {
        "name": "Geerars 2025",
        "doi": "10.1093/ptj/pzaf021",
        "pmid": "39982424",
        "title_terms": ["postural sway", "stroke"],
        "expected_stream": "trunk_balance_compensation",
    },
    {
        "name": "Kristensen 2017",
        "doi": "10.1016/j.apmr.2016.05.023",
        "pmid": "27372002",
        "title_terms": ["strength", "stroke"],
        "expected_stream": "strength_power",
    },
]

COMPONENT_PATTERNS = {
    "range of motion": [
        r"\brange of motion\b", r"\bjoint angle", r"\bjoint excursion",
        r"\bkinematic", r"\bangular velocity", r"\bactive movement range",
    ],
    "muscle strength and power": [
        r"\bmuscle strength\b", r"\bmuscle force\b", r"\bjoint torque\b",
        r"\bmuscle power\b", r"\bpropulsion\b", r"\bdynamomet",
        r"\bground reaction force\b", r"\belectromyogra", r"\bemg\b",
    ],
    "coordination and selective motor control": [
        r"\bcoordination\b", r"\bselective motor", r"\binter[- ]?joint",
        r"\bsynerg", r"\bdysmetria\b", r"\bendpoint accuracy\b",
        r"\btrajectory smooth", r"\bmotor control\b",
    ],
    "balance and postural control": [
        r"\bbalance\b", r"\bpostural", r"\bsway\b", r"\bstability\b",
        r"\bcentre of pressure\b", r"\bcenter of pressure\b",
        r"\bweight[- ]bearing\b", r"\bsit[- ]to[- ]stand\b",
    ],
    "manual dexterity": [
        r"\bdexter", r"\bgrasp", r"\bgrip\b", r"\bpinch",
        r"\bhand[- ]object\b", r"\bobject manipulation\b", r"\bpeg\b",
        r"\bblock transfer\b", r"\bfinger",
    ],
    "gait and mobility": [
        r"\bgait\b", r"\bwalk", r"\bambulat", r"\blocomo",
        r"\bmobility\b", r"\bstep ", r"\bstepping\b", r"\bturning\b",
        r"\btransfer", r"\bsit[- ]to[- ]stand\b",
    ],
    "movement quality and compensation": [
        r"\bcompensat", r"\bmovement quality\b", r"\basymmetr",
        r"\bsymmetr", r"\btrunk displacement\b", r"\babnormal synergy\b",
        r"\btrajectory smooth", r"\bmovement smooth", r"\bstrategy\b",
    ],
}

MODALITY_PATTERNS = {
    "RGB video / pose": [
        r"\bvideo", r"\brgb\b", r"\bcamera", r"\bcomputer vision\b",
        r"\bpose estimation\b", r"\bmarkerless\b", r"\bsmartphone",
    ],
    "Depth / RGB-D": [r"\brgb[- ]?d\b", r"\bdepth camera\b", r"\bkinect\b"],
    "Marker-based motion capture": [
        r"\bmarker[- ]based\b", r"\boptoelectronic\b", r"\bvicon\b",
        r"\bmotion capture\b", r"\bmocap\b",
    ],
    "IMU / wearable": [
        r"\bimu\b", r"\binertial", r"\bacceleromet", r"\bgyroscope",
        r"\bwearable sensor",
    ],
    "Force / pressure / EMG": [
        r"\bforce plate\b", r"\bforce platform\b", r"\bpressure",
        r"\binsole", r"\belectromyogra", r"\bemg\b", r"\bdynamomet",
    ],
    "Instrumented / other": [
        r"\binstrumented", r"\brobot", r"\bexoskeleton",
        r"\bfunctional electrical stimulation\b", r"\bfes\b",
    ],
}

METHOD_PATTERNS = {
    "deep learning": [
        r"\bdeep learning\b", r"\bconvolutional neural", r"\bcnn\b",
        r"\brecurrent neural", r"\blstm\b", r"\btransformer\b",
        r"\bneural network\b", r"\bpose estimation\b",
    ],
    "machine learning": [
        r"\bmachine learning\b", r"\bsupport vector", r"\brandom forest",
        r"\bgradient boost", r"\bclassification\b", r"\bregression model",
        r"\bclustering\b", r"\bknowledge graph\b",
    ],
    "signal processing / deterministic algorithm": [
        r"\bsignal processing\b", r"\balgorithm", r"\bfiltering\b",
        r"\bsegmentation\b", r"\bevent detection\b", r"\bthreshold[- ]based\b",
        r"\bkalman\b",
    ],
}

VALIDATION_PATTERNS = {
    "technical accuracy": [
        r"\bmean absolute error\b", r"\bmae\b", r"\brmse\b",
        r"\broot mean square error\b", r"\baccuracy\b", r"\bprecision\b",
        r"\bsensitivity\b", r"\bspecificity\b", r"\bf1[- ]?score\b",
        r"\barea under the curve\b", r"\bauc\b", r"\bbland[- ]altman\b",
    ],
    "reliability": [
        r"\breliab", r"\bintraclass correlation\b", r"\bicc\b",
        r"\btest[- ]retest\b", r"\binter[- ]rater\b", r"\bagreement\b",
    ],
    "clinical validity": [
        r"\bvalidity\b", r"\bclinical scale\b", r"\bfugl", r"\bberg balance",
        r"\bfunctional ambulation", r"\bnihs", r"\bconstruct validity\b",
        r"\bcorrelat",
    ],
    "responsiveness / longitudinal": [
        r"\bresponsiv", r"\blongitudinal\b", r"\bfollow[- ]up\b",
        r"\bchange score\b", r"\brecovery\b", r"\bprogress\b",
    ],
    "external validation": [
        r"\bexternal validation\b", r"\bindependent cohort\b",
        r"\bmulticenter\b", r"\bmulti[- ]center\b",
    ],
}

STROKE_TERMS = [
    r"\bstroke\b", r"\bpost[- ]?stroke\b", r"\bhemipar",
    r"\bcerebrovascular accident",
]
NONSTROKE_TERMS = [
    r"\bcerebral palsy\b", r"\bparkinson", r"\bspinal cord injur",
    r"\bhuntington", r"\bsarcopen", r"\bdementia\b", r"\balzheimer",
    r"\bmultiple sclerosis\b", r"\bataxia\b", r"\bvestibular\b",
    r"\btennis\b", r"\bsquash\b", r"\bswimming\b", r"\bgolf\b",
    r"\bcricket\b", r"\bzebrafish\b", r"\bdystroph",
]
ANIMAL_TERMS = [
    r"\bzebrafish\b", r"\bmouse model\b", r"\bmice\b", r"\brat model\b",
    r"\banimal model\b", r"\bin vitro\b",
]
PAEDIATRIC_TERMS = [
    r"\bchild", r"\bpaediatric\b", r"\bpediatric\b", r"\badolescen",
    r"\bcerebral palsy\b",
]
REVIEW_TERMS = [
    r"\bsystematic review\b", r"\bscoping review\b", r"\bnarrative review\b",
    r"\bliterature review\b", r"\breview of\b", r"\bmeta-analysis\b",
]
PROTOCOL_TERMS = [r"\bstudy protocol\b", r"\bprotocol for\b"]
MOVEMENT_TASK_TERMS = [
    r"\bgait\b", r"\bwalk", r"\breach", r"\bgrasp", r"\bhand\b",
    r"\bupper limb\b", r"\bupper extremity\b", r"\bbalance\b",
    r"\bpostural", r"\btrunk\b", r"\bsit[- ]to[- ]stand\b",
    r"\bmovement\b", r"\bmobility\b", r"\bstrength\b", r"\btorque\b",
    r"\bpropulsion\b", r"\bcoordination\b",
]
QUANTITATIVE_TERMS = [
    r"\bquantif", r"\bmeasure", r"\bestimat", r"\bdetect", r"\bclassif",
    r"\brecogn", r"\bvalid", r"\breliab", r"\baccuracy\b", r"\bparameter",
    r"\bfeature", r"\bkinematic", r"\bkinetic", r"\btrajectory",
    r"\bangle", r"\bvelocity", r"\bdistance", r"\btiming\b",
]
PARTICIPANT_TERMS = [
    r"\bparticipants?\b", r"\bpatients?\b", r"\bsurvivors?\b",
    r"\bsubjects?\b", r"\badults?\b", r"\bcohort\b",
]
STROKE_POPULATION_PATTERNS = [
    r"\bpost[- ]?stroke\b",
    r"\bstroke (patients?|survivors?|participants?|subjects?)\b",
    r"\b(patients?|survivors?|participants?|subjects?|individuals|people)"
    r".{0,45}\b(with|after|following)\b.{0,20}\bstroke\b",
    r"\bstroke\b.{0,35}\b(patients?|survivors?|participants?|subjects?|"
    r"individuals|people)\b",
    r"\bhemiparetic\b",
    r"\bhemiparesis\b",
    r"\bstroke rehabilitation\b",
    r"\bstroke recovery\b",
]
NON_MOTION_STROKE_PATTERNS = [
    r"\bprehospital\b",
    r"\bacute stroke detection\b",
    r"\bstroke diagnosis\b",
    r"\bstroke categorization\b",
    r"\batrial fibrillation\b",
    r"\bmortality prediction\b",
    r"\bneurological deterioration\b",
    r"\bbrain imaging\b",
    r"\bmagnetic resonance imaging\b",
    r"\bcomputed tomography\b",
    r"\blesion segmentation\b",
]
COMPONENT_OUTPUT_PATTERNS = [
    r"\bjoint angle", r"\bjoint excursion", r"\brange of motion\b",
    r"\btrajectory", r"\bsmoothness\b", r"\bsymmetr", r"\bcoordination\b",
    r"\bpostural sway\b", r"\bcentre of pressure\b", r"\bcenter of pressure\b",
    r"\bgrasp", r"\bdexter", r"\bhand use\b", r"\bgait speed\b",
    r"\bcadence\b", r"\bstep length\b", r"\bstance time\b",
    r"\bswing time\b", r"\bturning\b", r"\bsit[- ]to[- ]stand\b",
    r"\bground reaction force\b", r"\bmuscle force\b", r"\bjoint torque\b",
    r"\bemg feature", r"\bkinematic", r"\bkinetic",
]


def clean_space(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", clean_space(value)).encode(
        "ascii", "ignore"
    ).decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return clean_space(text)


def normalize_doi(value: Any) -> str:
    text = clean_space(value).lower()
    text = re.sub(r"^https?://(dx\.)?doi\.org/", "", text)
    text = re.sub(r"^doi:\s*", "", text)
    return text.rstrip(" .;,")


def first_author(authors: Any) -> str:
    text = clean_space(authors)
    if not text:
        return ""
    return normalize_text(re.split(r";|\band\b|,", text, maxsplit=1)[0])


def request_json(url: str, retries: int = 4) -> dict[str, Any]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=90) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("unreachable")


def request_bytes(url: str, retries: int = 4) -> bytes:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/xml"}
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=120) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError):
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("unreachable")


def element_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return clean_space("".join(element.itertext()))


def pubmed_search(query: str) -> tuple[list[str], int, str]:
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": "10000",
        "sort": "pub date",
    }
    url = f"{PUBMED_BASE}/esearch.fcgi?{urllib.parse.urlencode(params)}"
    data = request_json(url)
    result = data["esearchresult"]
    count = int(result["count"])
    ids = [str(x) for x in result.get("idlist", [])]
    if count > 10000:
        raise RuntimeError(
            f"PubMed query returned {count} records; segment the query before retrieval."
        )
    return ids, count, url


def pubmed_fetch(pmids: list[str], batch_size: int = 200) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for start in range(0, len(pmids), batch_size):
        batch = pmids[start : start + batch_size]
        params = {
            "db": "pubmed",
            "id": ",".join(batch),
            "retmode": "xml",
        }
        url = f"{PUBMED_BASE}/efetch.fcgi?{urllib.parse.urlencode(params)}"
        root = ET.fromstring(request_bytes(url))
        for item in root.findall(".//PubmedArticle"):
            medline = item.find("MedlineCitation")
            article = item.find(".//Article")
            pmid = element_text(medline.find("PMID") if medline is not None else None)
            title = element_text(article.find("ArticleTitle") if article is not None else None)
            abstract_parts = []
            if article is not None:
                for node in article.findall(".//Abstract/AbstractText"):
                    label = clean_space(node.attrib.get("Label", ""))
                    value = element_text(node)
                    abstract_parts.append(f"{label}: {value}" if label else value)
            abstract = clean_space(" ".join(abstract_parts))
            journal = element_text(article.find(".//Journal/Title") if article is not None else None)
            year = ""
            for path in [
                ".//JournalIssue/PubDate/Year",
                ".//JournalIssue/PubDate/MedlineDate",
                ".//ArticleDate/Year",
            ]:
                candidate = element_text(article.find(path) if article is not None else None)
                match = re.search(r"\b(19|20)\d{2}\b", candidate)
                if match:
                    year = match.group(0)
                    break
            author_names = []
            if article is not None:
                for author in article.findall(".//AuthorList/Author"):
                    collective = element_text(author.find("CollectiveName"))
                    if collective:
                        author_names.append(collective)
                        continue
                    last = element_text(author.find("LastName"))
                    initials = element_text(author.find("Initials"))
                    name = clean_space(f"{last}, {initials}" if initials else last)
                    if name:
                        author_names.append(name)
            doi = ""
            pmcid = ""
            for identifier in item.findall(".//PubmedData/ArticleIdList/ArticleId"):
                id_type = identifier.attrib.get("IdType", "")
                if id_type == "doi":
                    doi = element_text(identifier)
                elif id_type == "pmc":
                    pmcid = element_text(identifier)
            publication_types = [
                element_text(x)
                for x in item.findall(".//PublicationTypeList/PublicationType")
            ]
            mesh_terms = [
                element_text(x)
                for x in item.findall(".//MeshHeadingList/MeshHeading/DescriptorName")
            ]
            languages = [
                element_text(x)
                for x in article.findall(".//Language")
            ] if article is not None else []
            records.append(
                {
                    "database": "PubMed",
                    "database_record_id": pmid,
                    "pmid": pmid,
                    "pmcid": pmcid,
                    "doi": normalize_doi(doi),
                    "title": title,
                    "abstract": abstract,
                    "journal": journal,
                    "year": year,
                    "authors": "; ".join(author_names),
                    "publication_type": "; ".join(publication_types),
                    "language": "; ".join(languages),
                    "mesh_terms": "; ".join(mesh_terms),
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
                    "open_access_url": f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/" if pmcid else "",
                    "retrieval_date": TODAY,
                }
            )
        time.sleep(0.35)
    return records


def invert_abstract(index: dict[str, list[int]] | None) -> str:
    if not index:
        return ""
    positions: list[tuple[int, str]] = []
    for word, indices in index.items():
        for pos in indices:
            positions.append((int(pos), word))
    return clean_space(" ".join(word for _, word in sorted(positions)))


def openalex_search(
    query: str, progress_label: str = ""
) -> tuple[list[dict[str, Any]], int, str]:
    cursor = "*"
    records: list[dict[str, Any]] = []
    meta_count = 0
    first_url = ""
    page = 0
    while cursor:
        filters = ",".join(
            [
                f"title_and_abstract.search:{query}",
                "type:article|proceedings-article",
                "is_retracted:false",
                "is_paratext:false",
            ]
        )
        params = {
            "filter": filters,
            "cursor": cursor,
            "per_page": "100",
            "select": ",".join(
                [
                    "id",
                    "doi",
                    "display_name",
                    "publication_year",
                    "publication_date",
                    "type",
                    "language",
                    "cited_by_count",
                    "authorships",
                    "primary_location",
                    "abstract_inverted_index",
                    "ids",
                ]
            ),
        }
        api_key = clean_space(os.environ.get("OPENALEX_API_KEY"))
        if api_key:
            params["api_key"] = api_key
        url = f"{OPENALEX_BASE}?{urllib.parse.urlencode(params)}"
        if not first_url:
            first_url = url
        data = request_json(url)
        if page == 0:
            meta_count = int(data.get("meta", {}).get("count", 0))
        items = data.get("results", [])
        for item in items:
            location = item.get("primary_location") or {}
            source = location.get("source") or {}
            authors = []
            for authorship in item.get("authorships") or []:
                author = authorship.get("author") or {}
                name = clean_space(author.get("display_name"))
                if name:
                    authors.append(name)
            ids = item.get("ids") or {}
            pmid_url = clean_space(ids.get("pmid"))
            pmid_match = re.search(r"/(\d+)/?$", pmid_url)
            doi = normalize_doi(item.get("doi"))
            records.append(
                {
                    "database": "OpenAlex",
                    "database_record_id": clean_space(item.get("id")),
                    "pmid": pmid_match.group(1) if pmid_match else "",
                    "pmcid": "",
                    "doi": doi,
                    "title": clean_space(item.get("display_name")),
                    "abstract": invert_abstract(item.get("abstract_inverted_index")),
                    "journal": clean_space(source.get("display_name")),
                    "year": item.get("publication_year") or "",
                    "authors": "; ".join(authors),
                    "publication_type": clean_space(item.get("type")),
                    "language": clean_space(item.get("language")),
                    "mesh_terms": "",
                    "url": clean_space(location.get("landing_page_url"))
                    or clean_space(item.get("id")),
                    "open_access_url": clean_space(location.get("pdf_url")),
                    "cited_by_count": item.get("cited_by_count") or 0,
                    "retrieval_date": TODAY,
                }
            )
        page += 1
        if page % 10 == 0:
            prefix = f"[{progress_label}] " if progress_label else ""
            print(
                f"{prefix}OpenAlex pages: {page}; records: {len(records)}",
                flush=True,
            )
        next_cursor = data.get("meta", {}).get("next_cursor")
        if not items or not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor
        time.sleep(0.2)
    return records, meta_count, first_url


def openalex_count(query: str) -> tuple[int, str]:
    filters = ",".join(
        [
            f"title_and_abstract.search:{query}",
            "type:article|proceedings-article",
            "is_retracted:false",
            "is_paratext:false",
        ]
    )
    params = {
        "filter": filters,
        "per_page": "1",
        "select": "id",
    }
    api_key = clean_space(os.environ.get("OPENALEX_API_KEY"))
    if api_key:
        params["api_key"] = api_key
    url = f"{OPENALEX_BASE}?{urllib.parse.urlencode(params)}"
    data = request_json(url)
    return int(data.get("meta", {}).get("count", 0)), url


def any_pattern(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(pattern, text, flags=re.I) for pattern in patterns)


def matched_labels(text: str, groups: dict[str, list[str]]) -> list[str]:
    return [
        label
        for label, patterns in groups.items()
        if any_pattern(text, patterns)
    ]


def screen_record(row: dict[str, Any]) -> dict[str, Any]:
    title = clean_space(row.get("title"))
    abstract = clean_space(row.get("abstract"))
    text = f"{title}. {abstract}".lower()
    title_lower = title.lower()
    pub_type = clean_space(row.get("publication_type")).lower()

    has_stroke = any_pattern(text, STROKE_TERMS)
    has_stroke_population = any_pattern(text, STROKE_POPULATION_PATTERNS)
    has_nonstroke = any_pattern(text, NONSTROKE_TERMS)
    has_animal = any_pattern(text, ANIMAL_TERMS)
    has_paediatric = any_pattern(text, PAEDIATRIC_TERMS)
    has_review = any_pattern(title_lower, REVIEW_TERMS) or "review" in pub_type
    has_protocol = any_pattern(title_lower, PROTOCOL_TERMS)
    has_task = any_pattern(text, MOVEMENT_TASK_TERMS)
    has_quant = any_pattern(text, QUANTITATIVE_TERMS)
    has_participants = any_pattern(text, PARTICIPANT_TERMS)
    has_component_output = any_pattern(text, COMPONENT_OUTPUT_PATTERNS)
    has_non_motion_stroke_focus = any_pattern(
        title_lower, NON_MOTION_STROKE_PATTERNS
    )
    components = matched_labels(text, COMPONENT_PATTERNS)
    modalities = matched_labels(text, MODALITY_PATTERNS)
    methods = matched_labels(text, METHOD_PATTERNS)
    validation = matched_labels(text, VALIDATION_PATTERNS)

    decision = "uncertain"
    tier = ""
    reason = ""

    if not title:
        decision = "exclude_title_abstract"
        reason = "missing bibliographic title"
    elif has_review:
        decision = "exclude_title_abstract"
        reason = "review or evidence-synthesis publication"
    elif has_protocol:
        decision = "exclude_title_abstract"
        reason = "protocol without completed results"
    elif has_animal and not has_participants:
        decision = "exclude_title_abstract"
        reason = "animal or non-human study"
    elif not has_stroke:
        decision = "exclude_title_abstract"
        reason = "no eligible stroke population"
    elif has_non_motion_stroke_focus and not has_component_output:
        decision = "exclude_title_abstract"
        reason = "stroke diagnosis or prognosis without component-level motion output"
    elif not has_stroke_population:
        decision = "exclude_title_abstract"
        reason = "stroke mentioned without evidence of an eligible stroke sample"
    elif has_paediatric and not re.search(r"\badult", text):
        decision = "uncertain"
        reason = "possible paediatric or mixed population"
    elif has_nonstroke and has_stroke:
        decision = "uncertain"
        reason = "mixed population; stroke data separability requires full text"
    elif not has_task:
        decision = "exclude_title_abstract"
        reason = "no explicit movement or functional task"
    elif not has_participants:
        decision = "uncertain"
        reason = "participant population is not sufficiently described"
    elif not modalities:
        decision = "uncertain"
        reason = "eligible task but sensing modality is unclear"
    elif not has_quant:
        decision = "uncertain"
        reason = "quantitative component-level output is unclear"
    elif not has_component_output:
        decision = "uncertain"
        reason = "component-level motion output is not explicit"
    elif methods and validation:
        decision = "include_candidate_tier_a"
        tier = "Tier A"
        reason = (
            "stroke-specific computational motion assessment with validation evidence"
        )
    elif methods:
        decision = "uncertain"
        reason = "computational motion assessment; validation evidence requires full text"
    elif validation:
        decision = "include_candidate_tier_b"
        tier = "Tier B"
        reason = "stroke measurement evidence without an explicit AI method"
    else:
        decision = "uncertain"
        reason = "measurement and validation status require full-text assessment"

    direct_status = ""
    if any_pattern(text, [
        r"\btime\b", r"\bdistance\b", r"\bcount\b", r"\bjoint angle\b",
        r"\bvelocity\b", r"\bcadence\b", r"\bstep length\b",
        r"\bcentre of pressure\b", r"\bcenter of pressure\b",
    ]):
        direct_status = "directly quantifiable"
    elif modalities and components:
        direct_status = "proxy-based or feature-dependent"

    return {
        "automated_screening_decision": decision,
        "provisional_evidence_tier": tier,
        "automated_primary_reason": reason,
        "movement_components": "; ".join(components),
        "sensing_modalities": "; ".join(modalities),
        "computational_method_family": "; ".join(methods),
        "validation_domains": "; ".join(validation),
        "direct_proxy_status": direct_status,
        "title_abstract_verification": "machine-assisted first pass",
        "full_text_status": "pending",
        "adjudication_status": "pending" if decision == "uncertain" else "",
    }


def merge_values(values: Iterable[Any]) -> str:
    unique = []
    seen = set()
    for value in values:
        for part in re.split(r"\s*;\s*", clean_space(value)):
            if not part:
                continue
            key = part.lower()
            if key not in seen:
                seen.add(key)
                unique.append(part)
    return "; ".join(unique)


def choose_best(group: pd.DataFrame) -> dict[str, Any]:
    group = group.copy()
    group["_score"] = (
        group["database"].eq("PubMed").astype(int) * 100000
        + group["abstract"].fillna("").str.len()
        + group["authors"].fillna("").str.len()
    )
    best = group.sort_values("_score", ascending=False).iloc[0].to_dict()
    best.pop("_score", None)
    for field in [
        "database",
        "database_record_id",
        "source_stream",
        "query_name",
        "legacy_source",
    ]:
        best[field] = merge_values(group[field].fillna("").tolist())
    for field in ["pmid", "pmcid", "doi", "url", "open_access_url"]:
        if not clean_space(best.get(field)):
            best[field] = next(
                (clean_space(v) for v in group[field].tolist() if clean_space(v)),
                "",
            )
    best["source_record_count"] = len(group)
    return best


def dedup_key(row: dict[str, Any]) -> str:
    doi = normalize_doi(row.get("doi"))
    if doi:
        return f"doi:{doi}"
    pmid = clean_space(row.get("pmid"))
    if pmid:
        return f"pmid:{pmid}"
    title = normalize_text(row.get("title"))
    year = clean_space(row.get("year"))
    author = first_author(row.get("authors"))
    return f"title:{title}|year:{year}|author:{author}"


def load_legacy() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    paths = [
        (
            PROJECT_ROOT / "ai_gait_literature_screened.csv",
            "legacy_pubmed_274",
        ),
        (
            PROJECT_ROOT
            / "ai_gait_factor_restart"
            / "06_tier1_factor_extraction_final.csv",
            "legacy_factor_pool_200",
        ),
    ]
    for path, label in paths:
        frame = pd.read_csv(path, dtype=str).fillna("")
        for _, row in frame.iterrows():
            item = row.to_dict()
            records.append(
                {
                    "database": clean_space(item.get("retrieval_source"))
                    or clean_space(item.get("source"))
                    or "PubMed",
                    "database_record_id": clean_space(item.get("pmid"))
                    or clean_space(item.get("dedup_key")),
                    "pmid": clean_space(item.get("pmid")),
                    "pmcid": "",
                    "doi": normalize_doi(item.get("doi")),
                    "title": clean_space(item.get("title")),
                    "abstract": clean_space(item.get("abstract")),
                    "journal": clean_space(item.get("journal")),
                    "year": clean_space(item.get("year")),
                    "authors": clean_space(item.get("authors")),
                    "publication_type": "",
                    "language": "",
                    "mesh_terms": "",
                    "url": clean_space(item.get("url")),
                    "open_access_url": "",
                    "retrieval_date": "2026-05-16",
                    "source_stream": "gait_mobility",
                    "query_name": clean_space(item.get("query_name")),
                    "legacy_source": label,
                    "legacy_screening_label": clean_space(
                        item.get("rule_screening_label_v2")
                    ),
                    "legacy_dedup_key": clean_space(item.get("dedup_key")),
                }
            )
    return records


def known_item_test(master: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for item in KNOWN_ITEMS:
        exact_found = pd.Series(False, index=master.index)
        if item.get("doi"):
            exact_found = exact_found | master["doi"].map(normalize_doi).eq(
                normalize_doi(item["doi"])
            )
        if item.get("pmid"):
            exact_found = exact_found | master["pmid"].astype(str).eq(str(item["pmid"]))
        title_norm = master["title"].map(normalize_text)
        term_match = pd.Series(True, index=master.index)
        for term in item.get("title_terms", []):
            term_match = term_match & title_norm.str.contains(
                normalize_text(term), regex=False, na=False
            )
        exact_hits = master.loc[exact_found]
        title_hits = master.loc[term_match]
        in_expected = exact_hits["source_stream"].fillna("").str.contains(
            item["expected_stream"], regex=False
        ).any()
        rows.append(
            {
                "known_item": item["name"],
                "expected_stream": item["expected_stream"],
                "doi": item.get("doi", ""),
                "pmid": item.get("pmid", ""),
                "retrieved_anywhere": bool(len(exact_hits)),
                "retrieved_in_expected_stream": bool(in_expected),
                "matched_records": len(exact_hits),
                "matched_titles": " | ".join(exact_hits["title"].head(5).tolist()),
                "title_term_hits_not_used_for_pass": len(title_hits),
            }
        )
    return pd.DataFrame(rows)


def write_bibtex(
    frame: pd.DataFrame,
    path: Path,
    allowed_decisions: set[str] | None = None,
) -> None:
    entries = []
    seen_keys = Counter()
    for _, row in frame.iterrows():
        decision = clean_space(row.get("automated_screening_decision"))
        if allowed_decisions is None:
            if clean_space(row.get("final_include")).lower() not in {"yes", "true", "1"}:
                continue
        elif decision not in allowed_decisions:
            continue
        authors = clean_space(row.get("authors"))
        first = first_author(authors).title().replace(" ", "")
        year = clean_space(row.get("year")) or "n.d."
        title = clean_space(row.get("title"))
        base_key = re.sub(r"[^A-Za-z0-9]", "", f"{first}{year}{normalize_text(title)[:24]}")
        if not base_key:
            base_key = f"Candidate{len(entries)+1}"
        seen_keys[base_key] += 1
        key = base_key if seen_keys[base_key] == 1 else f"{base_key}{seen_keys[base_key]}"
        bib_authors = " and ".join(
            clean_space(a) for a in authors.split(";") if clean_space(a)
        )
        fields = [
            f"  author = {{{bib_authors}}}",
            f"  title = {{{title}}}",
            f"  journal = {{{clean_space(row.get('journal'))}}}",
            f"  year = {{{year}}}",
        ]
        doi = normalize_doi(row.get("doi"))
        pmid = clean_space(row.get("pmid"))
        url = clean_space(row.get("url"))
        if doi:
            fields.append(f"  doi = {{{doi}}}")
        if pmid:
            fields.append(f"  pmid = {{{pmid}}}")
        if url:
            fields.append(f"  url = {{{url}}}")
        entries.append(f"@article{{{key},\n" + ",\n".join(fields) + "\n}")
    path.write_text("\n\n".join(entries) + "\n", encoding="utf-8")


def build_figure_source(master: pd.DataFrame) -> pd.DataFrame:
    rows = []
    candidates = master[
        master["automated_screening_decision"].eq("include_candidate_tier_a")
    ]
    for _, record in candidates.iterrows():
        components = [
            x.strip()
            for x in clean_space(record["movement_components"]).split(";")
            if x.strip()
        ]
        modalities = [
            x.strip()
            for x in clean_space(record["sensing_modalities"]).split(";")
            if x.strip()
        ]
        validations = [
            x.strip()
            for x in clean_space(record["validation_domains"]).split(";")
            if x.strip()
        ]
        for component in components:
            if modalities:
                for modality in modalities:
                    rows.append(
                        {
                            "study_id": record["study_id"],
                            "movement_component": component,
                            "sensing_modality": modality,
                            "validation_domain": "",
                            "count_basis": "title_abstract_candidate",
                            "figure_eligible": False,
                            "eligibility_note": (
                                "Not final: requires full-text and second-reviewer adjudication"
                            ),
                        }
                    )
            if validations:
                for validation in validations:
                    rows.append(
                        {
                            "study_id": record["study_id"],
                            "movement_component": component,
                            "sensing_modality": "",
                            "validation_domain": validation,
                            "count_basis": "title_abstract_candidate",
                            "figure_eligible": False,
                            "eligibility_note": (
                                "Not final: requires full-text and second-reviewer adjudication"
                            ),
                        }
                    )
    return pd.DataFrame(rows)


def run(
    skip_openalex: bool = False,
    count_only: bool = False,
    offline_rebuild: bool = False,
) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_records: list[dict[str, Any]] = load_legacy()
    log_rows = []

    for stream, blocks in STREAMS.items():
        print(f"[{stream}] PubMed search", flush=True)
        pubmed_query = (
            f"({POPULATION_PUBMED}) AND ({TECHNOLOGY_PUBMED}) "
            f"AND ({blocks['pubmed']})"
        )
        pubmed_cache = RAW_DIR / f"pubmed_{stream}.csv"
        pubmed_records = []
        if offline_rebuild:
            if not pubmed_cache.exists():
                raise FileNotFoundError(f"Missing cached search file: {pubmed_cache}")
            cached = pd.read_csv(pubmed_cache, dtype=str).fillna("")
            pubmed_records = cached.to_dict(orient="records")
            pmids = cached.get("pmid", pd.Series(dtype=str)).astype(str).tolist()
            meta_path = RAW_DIR / f"pubmed_{stream}.meta.json"
            metadata = {}
            if meta_path.exists():
                metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            count = int(metadata.get("reported_count", len(pubmed_records)))
            url = clean_space(metadata.get("request_url")) or "cached result"
            print(
                f"[{stream}] PubMed offline cache: {count} records",
                flush=True,
            )
        else:
            pmids, count, url = pubmed_search(pubmed_query)
        if count_only:
            print(f"[{stream}] PubMed count: {count}", flush=True)
            if not skip_openalex:
                openalex_query = (
                    f"({POPULATION_OPENALEX}) AND ({TECHNOLOGY_OPENALEX}) "
                    f"AND ({blocks['openalex']})"
                )
                oa_count, _ = openalex_count(openalex_query)
                print(f"[{stream}] OpenAlex count: {oa_count}", flush=True)
            continue
        if not pubmed_records and pubmed_cache.exists():
            cached = pd.read_csv(pubmed_cache, dtype=str).fillna("")
            cached_pmids = set(cached.get("pmid", pd.Series(dtype=str)).astype(str))
            if len(cached) == len(pmids) and cached_pmids == set(pmids):
                pubmed_records = cached.to_dict(orient="records")
                print(
                    f"[{stream}] PubMed cache reused: {len(pubmed_records)} records",
                    flush=True,
                )
        if not pubmed_records:
            print(f"[{stream}] PubMed fetch: {len(pmids)} records", flush=True)
            pubmed_records = pubmed_fetch(pmids)
        for record in pubmed_records:
            record["source_stream"] = stream
            record["query_name"] = f"pubmed_{stream}"
            record["legacy_source"] = ""
            record["legacy_screening_label"] = ""
            record["legacy_dedup_key"] = ""
        all_records.extend(pubmed_records)
        log_rows.append(
            {
                "database": "PubMed",
                "platform": "NCBI E-utilities",
                "source_stream": stream,
                "search_date": TODAY,
                "query": pubmed_query,
                "filters": "none",
                "reported_count": count,
                "retrieved_count": len(pubmed_records),
                "complete_retrieval": count == len(pubmed_records),
                "request_url": url,
                "status": "completed" if count == len(pubmed_records) else "incomplete_retrieval",
            }
        )
        pd.DataFrame(pubmed_records).to_csv(
            pubmed_cache, index=False, encoding="utf-8-sig"
        )
        (RAW_DIR / f"pubmed_{stream}.meta.json").write_text(
            json.dumps(
                {
                    "reported_count": count,
                    "retrieved_count": len(pubmed_records),
                    "complete_retrieval": count == len(pubmed_records),
                    "request_url": url,
                    "search_date": TODAY,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        if not skip_openalex and not offline_rebuild:
            print(f"[{stream}] OpenAlex search", flush=True)
            openalex_query = (
                f"({POPULATION_OPENALEX}) AND ({TECHNOLOGY_OPENALEX}) "
                f"AND ({blocks['openalex']})"
            )
            try:
                oa_count, oa_count_url = openalex_count(openalex_query)
                openalex_cache = RAW_DIR / f"openalex_{stream}.csv"
                oa_records = []
                oa_url = oa_count_url
                if openalex_cache.exists():
                    cached = pd.read_csv(openalex_cache, dtype=str).fillna("")
                    if len(cached) == oa_count:
                        oa_records = cached.to_dict(orient="records")
                        print(
                            f"[{stream}] OpenAlex cache reused: "
                            f"{len(oa_records)} records",
                            flush=True,
                        )
                if not oa_records:
                    oa_records, oa_count, oa_url = openalex_search(
                        openalex_query, progress_label=stream
                    )
                for record in oa_records:
                    record["source_stream"] = stream
                    record["query_name"] = f"openalex_{stream}"
                    record["legacy_source"] = ""
                    record["legacy_screening_label"] = ""
                    record["legacy_dedup_key"] = ""
                all_records.extend(oa_records)
                print(
                    f"[{stream}] OpenAlex fetch: {len(oa_records)} of {oa_count}",
                    flush=True,
                )
                pd.DataFrame(oa_records).to_csv(
                    openalex_cache,
                    index=False,
                    encoding="utf-8-sig",
                )
                log_rows.append(
                    {
                        "database": "OpenAlex",
                        "platform": "OpenAlex API",
                        "source_stream": stream,
                        "search_date": TODAY,
                        "query": openalex_query,
                        "filters": (
                            "title and abstract; article or proceedings-article; "
                            "not retracted; not paratext"
                        ),
                        "reported_count": oa_count,
                        "retrieved_count": len(oa_records),
                        "complete_retrieval": oa_count == len(oa_records),
                        "request_url": oa_url,
                        "status": "completed",
                    }
                )
            except Exception as exc:
                log_rows.append(
                    {
                        "database": "OpenAlex",
                        "platform": "OpenAlex API",
                        "source_stream": stream,
                        "search_date": TODAY,
                        "query": openalex_query,
                        "filters": (
                            "title and abstract; article or proceedings-article; "
                            "not retracted; not paratext"
                        ),
                        "reported_count": "",
                        "retrieved_count": 0,
                        "complete_retrieval": False,
                        "request_url": "",
                        "status": f"failed: {type(exc).__name__}: {exc}",
                    }
                )
        print(f"[{stream}] complete", flush=True)

    if count_only:
        return

    raw = pd.DataFrame(all_records).fillna("")
    required = [
        "database",
        "database_record_id",
        "pmid",
        "pmcid",
        "doi",
        "title",
        "abstract",
        "journal",
        "year",
        "authors",
        "publication_type",
        "language",
        "mesh_terms",
        "url",
        "open_access_url",
        "retrieval_date",
        "source_stream",
        "query_name",
        "legacy_source",
        "legacy_screening_label",
        "legacy_dedup_key",
    ]
    for field in required:
        if field not in raw:
            raw[field] = ""
    raw["doi"] = raw["doi"].map(normalize_doi)
    raw["dedup_key"] = [
        dedup_key(record) for record in raw.to_dict(orient="records")
    ]
    raw.to_csv(
        RAW_DIR / "all_records_before_dedup.csv",
        index=False,
        encoding="utf-8-sig",
    )

    merged_rows = [
        choose_best(group)
        for _, group in raw.groupby("dedup_key", sort=True, dropna=False)
    ]
    master = pd.DataFrame(merged_rows).fillna("")
    master = master.sort_values(
        ["year", "title"], ascending=[False, True], kind="stable"
    ).reset_index(drop=True)
    master.insert(
        0,
        "study_id",
        [f"AI-{index:04d}" for index in range(1, len(master) + 1)],
    )
    screen_rows = [
        screen_record(record) for record in master.to_dict(orient="records")
    ]
    screen = pd.DataFrame(screen_rows)
    master = pd.concat([master, screen], axis=1)
    master["reviewer_decision"] = ""
    master["reviewer_exclusion_reason"] = ""
    master["second_reviewer_status"] = "pending"
    master["final_evidence_tier"] = ""
    master["final_include"] = ""
    master["source_url"] = master["url"]

    master.to_csv(
        OUTPUT_DIR / "master_screening_library.csv",
        index=False,
        encoding="utf-8-sig",
    )
    extraction_columns = [
        "study_id",
        "source_stream",
        "database",
        "pmid",
        "doi",
        "title",
        "year",
        "authors",
        "journal",
        "provisional_evidence_tier",
        "automated_screening_decision",
        "automated_primary_reason",
        "movement_components",
        "sensing_modalities",
        "computational_method_family",
        "validation_domains",
        "direct_proxy_status",
        "population_and_stroke_stage",
        "sample_size",
        "assessment_task",
        "body_region",
        "sensor_placement_or_view",
        "machine_observable_features",
        "output_type",
        "reference_standard",
        "evaluation_metrics",
        "reliability",
        "clinical_validity",
        "responsiveness",
        "external_validation",
        "principal_limitation",
        "full_text_status",
        "reviewer_decision",
        "reviewer_exclusion_reason",
        "second_reviewer_status",
        "final_evidence_tier",
        "final_include",
        "source_url",
        "open_access_url",
    ]
    for column in extraction_columns:
        if column not in master:
            master[column] = ""
    extraction = master[extraction_columns].copy()
    extraction.to_csv(
        OUTPUT_DIR / "component_evidence_extraction.csv",
        index=False,
        encoding="utf-8-sig",
    )

    log = pd.DataFrame(log_rows)
    log.to_csv(
        OUTPUT_DIR / "search_log.csv", index=False, encoding="utf-8-sig"
    )
    known = known_item_test(master)
    known.to_csv(
        OUTPUT_DIR / "known_item_testing.csv",
        index=False,
        encoding="utf-8-sig",
    )
    figure_source = build_figure_source(master)
    figure_source.to_csv(
        OUTPUT_DIR / "figure2_source_data.csv",
        index=False,
        encoding="utf-8-sig",
    )
    write_bibtex(master, OUTPUT_DIR / "included_ai_studies.bib")
    write_bibtex(
        master,
        OUTPUT_DIR / "candidate_ai_studies.bib",
        allowed_decisions={"include_candidate_tier_a", "include_candidate_tier_b"},
    )

    decision_counts = (
        master["automated_screening_decision"]
        .value_counts(dropna=False)
        .rename_axis("decision")
        .reset_index(name="count")
    )
    stream_counts = (
        master.assign(
            source_stream=master["source_stream"].str.split(r"\s*;\s*")
        )
        .explode("source_stream")
        .groupby(
            ["source_stream", "automated_screening_decision"],
            dropna=False,
        )
        .size()
        .reset_index(name="count")
    )
    flow = pd.DataFrame(
        [
            {"metric": "raw source records", "count": len(raw)},
            {"metric": "unique records after deduplication", "count": len(master)},
            {
                "metric": "duplicate source records consolidated",
                "count": len(raw) - len(master),
            },
            {
                "metric": "Tier A title/abstract candidates",
                "count": int(
                    master["automated_screening_decision"]
                    .eq("include_candidate_tier_a")
                    .sum()
                ),
            },
            {
                "metric": "Tier B title/abstract candidates",
                "count": int(
                    master["automated_screening_decision"]
                    .eq("include_candidate_tier_b")
                    .sum()
                ),
            },
            {
                "metric": "uncertain records requiring adjudication",
                "count": int(
                    master["automated_screening_decision"].eq("uncertain").sum()
                ),
            },
            {
                "metric": "title/abstract exclusions",
                "count": int(
                    master["automated_screening_decision"]
                    .eq("exclude_title_abstract")
                    .sum()
                ),
            },
            {
                "metric": "full-text included Tier A studies",
                "count": 0,
                "note": "Not locked; requires full-text and second-reviewer adjudication",
            },
        ]
    )
    decision_counts.to_csv(
        OUTPUT_DIR / "decision_counts.csv",
        index=False,
        encoding="utf-8-sig",
    )
    stream_counts.to_csv(
        OUTPUT_DIR / "stream_decision_counts.csv",
        index=False,
        encoding="utf-8-sig",
    )
    flow.to_csv(
        OUTPUT_DIR / "prisma_flow_counts.csv",
        index=False,
        encoding="utf-8-sig",
    )

    summary = {
        "search_date": TODAY,
        "raw_source_records": len(raw),
        "unique_records": len(master),
        "duplicates_consolidated": len(raw) - len(master),
        "decisions": decision_counts.set_index("decision")["count"].to_dict(),
        "known_item_testing_passed": bool(
            known["retrieved_in_expected_stream"].all()
        ),
        "public_database_search_status": (
            "provisional; subscription-database exports not yet merged"
        ),
        "figure2_status": (
            "not locked; source file contains title/abstract candidates only"
        ),
    }
    (OUTPUT_DIR / "run_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def refresh_pubmed_stream(stream: str) -> None:
    """Refresh one PubMed stream cache without rebuilding downstream outputs."""
    blocks = STREAMS[stream]
    pubmed_query = (
        f"({POPULATION_PUBMED}) AND ({TECHNOLOGY_PUBMED}) "
        f"AND ({blocks['pubmed']})"
    )
    pmids, count, url = pubmed_search(pubmed_query)
    records = pubmed_fetch(pmids)
    for record in records:
        record["source_stream"] = stream
        record["query_name"] = f"pubmed_{stream}"
        record["legacy_source"] = ""
        record["legacy_screening_label"] = ""
        record["legacy_dedup_key"] = ""
    pd.DataFrame(records).to_csv(
        RAW_DIR / f"pubmed_{stream}.csv", index=False, encoding="utf-8-sig"
    )
    (RAW_DIR / f"pubmed_{stream}.meta.json").write_text(
        json.dumps(
            {
                "reported_count": count,
                "retrieved_count": len(records),
                "complete_retrieval": count == len(records),
                "request_url": url,
                "search_date": TODAY,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "stream": stream,
                "reported_count": count,
                "retrieved_count": len(records),
                "complete_retrieval": count == len(records),
                "request_url": url,
            },
            ensure_ascii=False,
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-openalex",
        action="store_true",
        help="Run PubMed and legacy-corpus processing only.",
    )
    parser.add_argument(
        "--count-only",
        action="store_true",
        help="Report PubMed and OpenAlex result counts without fetching records.",
    )
    parser.add_argument(
        "--offline-rebuild",
        action="store_true",
        help="Rebuild screening outputs from cached raw files without API calls.",
    )
    parser.add_argument(
        "--refresh-stream",
        choices=sorted(STREAMS),
        help="Refresh one PubMed stream cache and leave downstream outputs unchanged.",
    )
    args = parser.parse_args()
    if args.refresh_stream:
        refresh_pubmed_stream(args.refresh_stream)
        return 0
    run(
        skip_openalex=args.skip_openalex,
        count_only=args.count_only,
        offline_rebuild=args.offline_rebuild,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
