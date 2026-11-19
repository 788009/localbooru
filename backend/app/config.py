import tomllib as tomli
from pathlib import Path
from pydantic import BaseModel

class StorageConfig(BaseModel):
    tags_file: str = "./data/tags.json"
    directories: list[str] = []
    default_selected: list[str] = []

class UIConfig(BaseModel):
    default_page_size: int = 50

class ServerConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000

class AppConfig(BaseModel):
    storage: StorageConfig = StorageConfig()
    ui: UIConfig = UIConfig()
    server: ServerConfig = ServerConfig()

def load_config(path: str) -> AppConfig:
    if not Path(path).exists():
        return AppConfig()
    with open(path, "rb") as f:
        data = tomli.load(f)
    return AppConfig(**data)

def get_shortest_unique_names(dirs: list[str]) -> dict[str, str]:
    parts_list = {d: [p for p in Path(d).parts if p not in ('/', '\\')] for d in dirs}
    names = {}
    for d in dirs:
        parts = parts_list[d]
        for i in range(1, len(parts) + 1):
            candidate = "/".join(parts[-i:])
            conflict = False
            for other_d in dirs:
                if other_d == d:
                    continue
                other_parts = parts_list[other_d]
                if len(other_parts) >= i and "/".join(other_parts[-i:]) == candidate:
                    conflict = True
                    break
            if not conflict:
                names[d] = candidate
                break
        if d not in names:
            names[d] = d
    return names
