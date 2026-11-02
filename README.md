# Coal Fly Ash Valorization Knowledge Graph

Python source code for the study:

**Knowledge graph-based stratification of coal fly ash valorization pathways for waste management and resource recovery**

Repository: https://github.com/jy-craes/Code-Coal-Fly-Ash-Knowledge-Graph

## 1. Overview

This repository contains seven Python scripts used for literature preprocessing, entity matching, candidate triple extraction, author-review auditing, final knowledge-graph aggregation, Louvain community analysis, and pathway evaluation.

The underlying bibliographic records were retrieved from **Web of Science Core Collection** and **Scopus** under institutional access. Because redistribution of database-exported records and abstract-bearing bibliographic datasets is subject to database licensing and third-party rights, the complete source corpus is not deposited in this public repository.

Researchers with authorized access to Web of Science and Scopus can reconstruct the literature corpus by following the search strategy and screening rules reported in the article's **Supporting Information (SI)**. The public scripts can then be used to reproduce the main data-processing, candidate-extraction, network-aggregation, and analysis procedures. Author review is treated as a documented quality-control step in the workflow.

The SI is the primary methodological reference for database retrieval, screening, pathway classification, maturity coding, evidence-density definitions, relation schemas, and robustness analyses.

## 2. Software environment

The scripts were developed for **Python 3.10**.

Main Python packages:

- pandas
- NumPy
- NetworkX
- Matplotlib

A minimal environment can be installed with:

```bash
python -m pip install pandas numpy networkx matplotlib
```

Several scripts also use Python standard-library modules for CSV/JSON processing, regular expressions, hashing, text normalization, and file handling.

## 3. Reconstructing the literature corpus

The formal searches were conducted in Web of Science Core Collection and Scopus for publications from **2000 to 2025**. The detailed database queries, search fields, document types, language restrictions, and exclusion terms are provided in **Supplementary Table S1**.

The final frozen study corpus was constructed as follows:

| Step | Records retained | Records removed |
|---|---:|---:|
| Web of Science refined records | 2,581 | — |
| Scopus refined records | 2,357 | — |
| Combined records before deduplication | 4,938 | — |
| After DOI and normalized-title deduplication | 3,478 | 1,460 |
| After eligibility and scope screening | 3,422 | 56 |
| After publication-year filtering to 2000–2025 | **3,075** | 347 |

The 56 records removed during eligibility and scope screening consisted of 14 records that were outside the study scope or lacked sufficient classification evidence and 42 records removed after author review. Fuzzy-title similarity of **0.95 or higher** was used to flag candidate pairs for manual checking. The detailed workflow is reported in **Supplementary Table S2**, and the exported bibliographic fields and their analytical roles are summarized in **Supplementary Table S3**.

To reconstruct the corpus:

1. Retrieve records from Web of Science Core Collection and Scopus using the SI search strategy.
2. Export the permitted bibliographic fields locally.
3. Harmonize field names and normalize DOI, title, and publication year.
4. Remove duplicate records by DOI and normalized title, and manually inspect ambiguous title matches.
5. Apply the study-object and valorization-scope criteria reported in the SI.
6. Restrict the final corpus to publications from 2000 to 2025.
7. Assign stable local `Paper_ID` values for downstream processing.
8. Retain the reconstructed bibliographic records locally and run the relevant scripts below.

The final corpus used in the study contained **3,075 publications**, of which **2,859** were assigned to one of eight dominant valorization pathways and **216** remained unclear for dominant-pathway classification.

## 4. Knowledge extraction and graph construction

The workflow uses six main entity classes:

1. material properties;
2. technical pathways;
3. application scenarios;
4. limiting factors;
5. external synergies; and
6. evaluation indicators.

The main semantic relations include:

- `prepare`
- `use for`
- `remove`
- `recover`
- `improve`
- `limit`
- `synergize with`
- `associate with`
- `include`
- `evaluate`

Detailed pathway definitions, maturity rules, evidence-density indicators, and relation schemas are provided in **Supplementary Tables S4–S7**.

The workflow proceeds from dictionary-based matching and rule-based candidate extraction to author review and final relation aggregation. Each retained relation is linked to a `Paper_ID`, which preserves traceability to the corresponding publication record.

For the authors' final frozen dataset:

- 3,075 publications were retained;
- 2,904 publications contributed at least one retained relation;
- 19,177 paper-linked relation supports were retained;
- these relation supports were aggregated into 198 directed relation edges across 44 nodes.

The external association network used for Louvain analysis contains:

- 39 nodes;
- 104 weighted edges;
- 5 communities;
- modularity `Q ≈ 0.4684` with seed 42.

Robustness analyses for maturity coding, edge-weight sensitivity, Louvain community stability, and literature-reporting rates are documented in **Supplementary Tables S8–S11**.

## 5. Code 1–7: inputs and outputs

The table below summarizes the role, principal inputs, and outputs of each public script.

| Code | Main purpose | Principal input(s) | Main output(s) |
|---|---|---|---|
| **Code1 Preprocessing.py** | Field normalization, DOI/title duplicate screening, and publication-year checks | `Author Frozen Corpus 3075.csv`, or user-supplied WoS/Scopus CSV exports with `--raw` | `Papers Preprocessed.csv`; `Potential Duplicates for Review.csv`; `Preprocessing Report.json` |
| **Code2 Entity Matching.py** | Dictionary-based matching of properties, pathways, limiting factors, and external synergy factors | `Author Frozen Corpus 3075.csv`; local dictionary files: `KG Original 5 Entity Dictionaries.json`, `Property Pathway Dictionaries.json`, `Limiting Factors Dictionary.json`, `External Synergy Dictionaries.json` | `Code2 Candidate Entity Matches.csv` |
| **Code3 Triple Extraction.py** | Rule-based generation of candidate Source–Relation–Target triples | `Author Frozen Corpus 3075.csv` with title, abstract, keyword, pathway, and classification fields | `Code3 Initial Candidate Triples.csv` |
| **Code4 Author Review.py** | Audit of recorded V2/V3 author-review decisions and consistency of the final reviewed relation set | `V2 Author Approved Graph 21269.csv`; `V3 Author Revised Graph 21204.csv`; `V3 3422 Papers 20858 Relations.csv`; `Author Confirmed Exclusions 42 Papers.csv`; `Final Graph Triples 19177.csv`; `Author Frozen Corpus 3075.csv`; `Input1 Knowledge Graph Edges 198.csv` | `V3 Held Candidate Relation Index 5.csv`; `Final Reviewed Relation Index 3075 Papers.csv`; `V2 V3 Audit Trail.json` |
| **Code5 Final Knowledge Graph.py** | Reaggregation and validation of the final directed knowledge graph | `Author Frozen Corpus 3075.csv`; `Final Graph Triples 19177.csv`; `Input1 Knowledge Graph Edges 198.csv` | `KG 3075 Edges Recomputed.csv`; `KG 3075 Nodes Recomputed.csv`; `KG 3075 Relation Stats.csv`; `Knowledge Graph 3075 Multirelational.graphml`; `Audit 3075.json` |
| **Code6 Louvain Community Analysis.py** | Construction and Louvain analysis of the external association network | `Input3 Evidence Filtered Edges.csv` | `Nodes Community.csv`; `Edges Community.csv`; `Louvain Audit.json`; `Louvain Network Community.png` |
| **Code7 Pathway Evaluation Figures.py** | Pathway/maturity checks and reproduction of selected Fig. 2 and Fig. 3 analytical outputs | `Author Frozen Corpus 3075.csv`; `Input2 Pathway Evaluation.csv`; `Fig3 Paper Level Keyword Flags 2610.csv` | `Fig2b Category Counts.png`; `Fig2d Maturity Distribution.png`; `Fig3b Literature Proxy Scatter.png`; `Fig3c Evidence Reporting Heatmap.png`; `Reported Statistics.json` |

The file names above correspond to the authors' frozen analysis workflow. Researchers reconstructing the dataset independently can create locally equivalent input tables using the definitions and field descriptions in the SI.

## 6. Script details

### Code 1 — Preprocessing

`Code1 Preprocessing.py` performs bibliographic field normalization, exact DOI duplicate screening, normalized-title duplicate screening, and publication-year checks.

Default frozen-corpus audit:

```bash
python "Code1 Preprocessing.py"
```

Raw-export mode:

```bash
python "Code1 Preprocessing.py" --raw WOS_export.csv Scopus_export.csv
```

Code1 is also useful for checking whether a locally reconstructed corpus has unique `Paper_ID` values and publication years within the 2000–2025 analysis window.

### Code 2 — Entity Matching

`Code2 Entity Matching.py` applies predefined terminology dictionaries to titles, abstracts, and keywords and records candidate lexical matches linked to `Paper_ID`.

```bash
python "Code2 Entity Matching.py"
```

The script expects the required dictionary JSON files in a local `dict/` directory. The resulting CSV records candidate entity matches for subsequent review and relation processing.

### Code 3 — Triple Extraction

`Code3 Triple Extraction.py` applies the rule set to the reconstructed corpus and generates candidate Source–Relation–Target records linked to individual papers.

```bash
python "Code3 Triple Extraction.py"
```

The candidate relations cover pathway preparation, applications, evaluation indicators, pollutant removal, element recovery, property–pathway associations, multi-solid-waste synergy, and pathway classification relations.

### Code 4 — Author Review Audit

`Code4 Author Review.py` audits the saved author-review trajectory and verifies consistency among the recorded V2/V3 relation tables, the 42 scope exclusions, the final 3,075-paper corpus, the 19,177 retained relation supports, and the 198 aggregated edges.

```bash
python "Code4 Author Review.py"
```

This step represents the recorded quality-control stage used in the study. The required review tables are maintained locally because they contain intermediate author-review records and bibliographic information.

### Code 5 — Final Knowledge Graph

`Code5 Final Knowledge Graph.py` aggregates retained paper-linked relation supports into the final directed knowledge graph and produces edge, node, relation, GraphML, and audit outputs.

```bash
python "Code5 Final Knowledge Graph.py"
```

With the authors' frozen inputs, the principal validation targets are:

- publications: 3,075;
- publications contributing retained relations: 2,904;
- paper-linked relation supports: 19,177;
- directed aggregate edges: 198;
- graph nodes: 44.

### Code 6 — Louvain Community Analysis

`Code6 Louvain Community Analysis.py` reconstructs the weighted external association network and applies Louvain community detection using seed 42.

```bash
python "Code6 Louvain Community Analysis.py"
```

With the authors' frozen external-network input, the expected network contains 39 nodes, 104 edges, five communities, and modularity `Q ≈ 0.4684`.

### Code 7 — Pathway Evaluation Figures

`Code7 Pathway Evaluation Figures.py` checks pathway counts, maturity-stage counts, evidence-reporting values, and selected analytical outputs associated with Figs. 2 and 3.

```bash
python "Code7 Pathway Evaluation Figures.py"
```

Research heat, maturity, scale reporting, value reporting, and evidence-density indicators are bibliographic proxies derived from the literature corpus. Their definitions and interpretation are provided in the SI.

## 7. Recommended workflow

For a reconstructed local dataset, the recommended sequence is:

```text
Database retrieval and screening
        ↓
Code1: preprocessing and duplicate audit
        ↓
Code2: candidate entity matching
        ↓
Code3: candidate triple extraction
        ↓
Documented author review and quality control
        ↓
Code4: review-record audit
        ↓
Code5: final graph aggregation
        ↓
Code6: external-network community analysis
Code7: pathway and maturity evaluation
```

The individual scripts can also be run separately when only a specific analytical component is required.

## 8. Data availability and reproducibility

The original WoS and Scopus bibliographic records are not redistributed in this repository because they were obtained through institutional database access and remain subject to the applicable database licenses and third-party rights.

Researchers with lawful access to Web of Science Core Collection and Scopus can follow the SI search and screening protocol to reconstruct the literature corpus locally. The seven public Python scripts provide the computational procedures for preprocessing, candidate extraction, graph aggregation, community analysis, and pathway evaluation. The documented author-review stage provides the quality-control link between candidate relations and the final frozen relation set.

This repository therefore supports methodological and computational reproducibility while respecting the access and redistribution conditions of the source bibliographic databases.

## 9. Citation

When using or adapting this code, please cite the associated article and this repository.

**Associated manuscript**

Ji, Y., Shen, Y., Yang, J., Zhang, Y., Huang, Q., Yang, Y.  
*Knowledge graph-based stratification of coal fly ash valorization pathways for waste management and resource recovery.*

**Repository**

https://github.com/jy-craes/Code-Coal-Fly-Ash-Knowledge-Graph

Web of Science Core Collection and Scopus should also be acknowledged as the source bibliographic databases where appropriate.
