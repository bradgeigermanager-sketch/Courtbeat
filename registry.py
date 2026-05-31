"""
courtbeat.registry
v0.3.0

Dynamic registry for:
- Source directories (YAML)
- Connectors
- Retrieval routines
- Transformers

Each source entry defines:
  type: news | court | jail | sheriff
  connector: module:Class
  retrieval: module:Class
  transformer: module:Class
  enabled: bool
"""

import yaml
import importlib
from pathlib import Path


class SourceSpec:
    """
    Represents a single source entry loaded from YAML.
    """

    def __init__(self, name, cfg):
        self.name = name
        self.type = cfg.get("type")
        self.connector_spec = cfg.get("connector")
        self.retrieval_spec = cfg.get("retrieval")
        self.transformer_spec = cfg.get("transformer")
        self.enabled = cfg.get("enabled", True)
        self.tags = cfg.get("tags", [])

    def load_connector(self):
        return _load_class(self.connector_spec)

    def load_retrieval(self):
        return _load_class(self.retrieval_spec)

    def load_transformer(self):
        return _load_class(self.transformer_spec)


def _load_class(spec: str):
    """
    Load a class from a string like:
        "courtbeat.connectors.news.fallon_post:FallonPostConnector"
    """
    module_name, class_name = spec.split(":")
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


class Registry:
    """
    Loads all source directories and exposes them as SourceSpec objects.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.sources = {}

    def load_directory(self, filename: str):
        path = self.base_dir / "directories" / filename
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        for name, cfg in data.items():
            self.sources[name] = SourceSpec(name, cfg)

    def load_all(self):
        """
        Loads all YAML directories:
        - news_media.yaml
        - courts.yaml
        - jails.yaml
        - sheriff_logs.yaml
        """
        for filename in [
            "news_media.yaml",
            "courts.yaml",
            "jails.yaml",
            "sheriff_logs.yaml",
        ]:
            self.load_directory(filename)

    def enabled_sources(self):
        return {name: spec for name, spec in self.sources.items() if spec.enabled}

    def get(self, name: str) -> SourceSpec:
        return self.sources[name]
