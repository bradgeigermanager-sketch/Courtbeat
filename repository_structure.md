courtbeat/
│
├── README.md
├── pyproject.toml
├── LICENSE
│
├── courtbeat/
│   ├── __init__.py
│   ├── version.py
│   │
│   ├── directories/                     # Source registries (YAML)
│   │   ├── __init__.py
│   │   ├── news_media.yaml
│   │   ├── courts.yaml
│   │   ├── jails.yaml
│   │   └── sheriff_logs.yaml
│   │
│   ├── retrieval/                       # Source-specific routines
│   │   ├── __init__.py
│   │   ├── news/
│   │   │   ├── __init__.py
│   │   │   ├── fallon_post_routines.py
│   │   │   ├── reno_gazette_routines.py
│   │   │   └── las_vegas_review_routines.py
│   │   ├── courts/
│   │   │   ├── __init__.py
│   │   │   ├── churchill_district_routines.py
│   │   │   ├── washoe_district_routines.py
│   │   │   └── clark_district_routines.py
│   │   ├── jails/
│   │   │   ├── __init__.py
│   │   │   ├── washoe_jail_routines.py
│   │   │   └── clark_jail_routines.py
│   │   └── sheriff/
│   │       ├── __init__.py
│   │       └── churchill_sheriff_routines.py
│   │
│   ├── connectors/                      # Connectors call retrieval routines
│   │   ├── __init__.py
│   │   ├── news/
│   │   │   ├── __init__.py
│   │   │   ├── fallon_post.py
│   │   │   ├── reno_gazette.py
│   │   │   └── las_vegas_review.py
│   │   ├── courts/
│   │   │   ├── __init__.py
│   │   │   ├── churchill_district.py
│   │   │   ├── washoe_district.py
│   │   │   └── clark_district.py
│   │   ├── jails/
│   │   │   ├── __init__.py
│   │   │   ├── washoe_jail.py
│   │   │   └── clark_jail.py
│   │   └── sheriff/
│   │       ├── __init__.py
│   │       └── churchill_sheriff.py
│   │
│   ├── transformers/                    # Normalizers → unified schema
│   │   ├── __init__.py
│   │   ├── news_media.py
│   │   ├── court_records.py
│   │   ├── jail_records.py
│   │   └── sheriff_logs.py
│   │
│   ├── schemas/                         # Unified data models
│   │   ├── __init__.py
│   │   ├── court_event.py
│   │   ├── arrest_event.py
│   │   ├── article_event.py
│   │   └── person.py
│   │
│   ├── registry.py                      # Dynamic loader for connectors + routines
│   ├── dag.py                           # Execution graph
│   │
│   └── utils/                           # Shared utilities
│       ├── __init__.py
│       ├── http.py
│       ├── text.py
│       └── logging.py
│
└── tests/
    ├── test_registry.py
    ├── test_dag.py
    ├── test_fallon_post_routines.py
    ├── test_fallon_post_connector.py
    └── test_transformers.py
