# Courtbeat
### *A modular, schema‑driven ingestion framework for courts, arrests, jails, and crime‑beat news media.*

`courtbeat` is a **federated retrieval and normalization system** designed to ingest public‑record data from:

- News media outlets  
- District courts  
- Justice courts  
- Jail systems  
- Sheriff booking logs  

It provides:

- **Source directories** (YAML)  
- **Source‑specific retrieval routines**  
- **Connectors** (retrievers)  
- **Transformers** (normalizers → unified schema)  
- **Unified data models**  
- **Dynamic registry**  
- **DAG‑based execution engine**  

The system is **atomic, modular, and extensible**, allowing new sources to be added with minimal effort.

---

# 



---

# **Features**

### **✔ Modular ingestion architecture**
Each source is defined by:

- A **directory entry** (YAML)
- A **retrieval routine** (source‑specific logic)
- A **connector** (retrieves raw events)
- A **transformer** (normalizes → unified schema)

### **✔ Unified schemas**
All sources normalize into consistent data models:

- `CourtEvent`
- `ArrestEvent`
- `ArticleEvent`
- `Person`

### **✔ Dynamic registry**
Loads sources from YAML and wires:

- Connectors  
- Retrieval routines  
- Transformers  

### **✔ DAG execution engine**
Runs all enabled sources and yields normalized events.

### **✔ Extensible**
Add a new source by creating:

1. A YAML entry  
2. A retrieval routine  
3. A connector  
4. A transformer  

No other code changes required.

---

# **Repository Structure**

```
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
│   ├── directories/
│   │   ├── news_media.yaml
│   │   ├── courts.yaml
│   │   ├── jails.yaml
│   │   └── sheriff_logs.yaml
│   │
│   ├── retrieval/
│   │   ├── news/
│   │   ├── courts/
│   │   ├── jails/
│   │   └── sheriff/
│   │
│   ├── connectors/
│   │   ├── news/
│   │   ├── courts/
│   │   ├── jails/
│   │   └── sheriff/
│   │
│   ├── transformers/
│   │   ├── news_media.py
│   │   ├── court_records.py
│   │   ├── jail_records.py
│   │   └── sheriff_logs.py
│   │
│   ├── schemas/
│   │   ├── court_event.py
│   │   ├── arrest_event.py
│   │   ├── article_event.py
│   │   └── person.py
│   │
│   ├── registry.py
│   ├── dag.py
│   │
│   └── utils/
│       ├── http.py
│       ├── text.py
│       └── logging.py
│
└── tests/
```

---

# **How It Works**

## 1. **Directories (YAML)**  
Define the ingestion universe.

Example: `news_media.yaml`

```yaml
fallon_post:
  type: news
  connector: courtbeat.connectors.news.fallon_post:FallonPostConnector
  retrieval: courtbeat.retrieval.news.fallon_post_routines:FallonPostRoutines
  transformer: courtbeat.transformers.news_media:NewsMediaTransformer
  enabled: true
  tags: [court_reports, sheriff_logs]
```

---

## 2. **Retrieval Routines**
Source‑specific logic:

- HTML selectors  
- Pagination  
- API endpoints  
- Rate limits  
- Parsing quirks  

Example:

```python
class FallonPostRoutines:
    def discover_articles(self): ...
    def fetch_article(self, url): ...
    def extract_lines(self, soup): ...
    def parse_line(self, line, context): ...
```

---

## 3. **Connectors**
Thin orchestrators that call retrieval routines.

```python
class FallonPostConnector(BaseConnector):
    def __init__(self):
        self.routines = FallonPostRoutines()

    def fetch(self):
        for article in self.routines.discover_articles():
            soup = self.routines.fetch_article(article.url)
            for line in self.routines.extract_lines(soup):
                yield self.routines.parse_line(line, context=article)
```

---

## 4. **Transformers**
Normalize → unified schema.

```python
class NewsMediaTransformer(BaseTransformer):
    def transform(self, raw):
        return CourtEventSchema.from_fallon_post(raw)
```

---

## 5. **Schemas**
Canonical data models for the entire system.

Example: `CourtEvent`

```python
@dataclass
class CourtEventRecord:
    source: str
    entity: str
    article_id: str
    article_url: str
    article_title: str
    article_date: datetime
    person: Person
    event: Event
```

---

## 6. **Registry**
Loads:

- Connectors  
- Retrieval routines  
- Transformers  

From YAML.

```python
registry = Registry(Path(__file__).parent)
registry.load_all()
sources = registry.enabled_sources()
```

---

## 7. **DAG Execution**

```python
dag = IngestionDAG(registry.enabled_sources())

for event in dag.run():
    process(event)
```

---

# **Adding a New Source**

To add a new news outlet, court, jail, or sheriff log:

### **1. Add a YAML entry**
`directories/news_media.yaml`

### **2. Create retrieval routine**
`retrieval/news/my_source_routines.py`

### **3. Create connector**
`connectors/news/my_source.py`

### **4. Create transformer**
`transformers/news_media.py` (or new transformer)

That’s it — the DAG will pick it up automatically.

---

# **Versioning**

- Global package version: `courtbeat/version.py`
- Component versions: `VERSION` files inside each subsystem

This allows:

- Independent upgrades  
- Component‑level rollback  
- Compatibility tracking  

---

# **Testing**

Tests live in `tests/`:

- `test_registry.py`
- `test_dag.py`
- `test_fallon_post_routines.py`
- `test_transformers.py`

Run with:

```
pytest
```

---

# **License**

MIT License

---

# **Roadmap**

- v0.4.0 — Add Nevada statewide court connectors  
- v0.5.0 — Add PDF ingestion for Justice Court  
- v0.6.0 — Add ML‑based charge normalization  
- v1.0.0 — Public release  

---

# **Contributing**

Pull requests welcome.  
Please follow:

- PEP8  
- Atomic module boundaries  
- Schema‑first design  
- Versioned components  

---
