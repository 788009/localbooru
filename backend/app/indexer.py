import json
import os
from app.config import AppConfig, get_shortest_unique_names

class Indexer:
    def __init__(self):
        self.valid_images = {}
        self.tag_freq = {}
        self.total_images = 0
        self.config = None
        self.dir_names = {}

    def build(self, config: AppConfig):
        self.config = config
        self.dir_names = get_shortest_unique_names(config.storage.directories)

        image_paths = {}
        valid_exts = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
        
        for d in config.storage.directories:
            if os.path.exists(d):
                for file in os.listdir(d):
                    ext = os.path.splitext(file)[1].lower()
                    if ext in valid_exts:
                        name = os.path.splitext(file)[0]
                        if name not in image_paths:
                            image_paths[name] = {
                                "path": os.path.join(d, file),
                                "dir": d,
                                "filename": file
                            }

        if os.path.exists(config.storage.tags_file):
            with open(config.storage.tags_file, "r", encoding="utf-8") as f:
                tags_raw = json.load(f)
        else:
            tags_raw = {}

        for img_id, path_info in image_paths.items():
            if img_id in tags_raw:
                raw_data = tags_raw[img_id]
                flat_tags = {}
                categories = {}
                
                for cat, cat_tags in raw_data.items():
                    categories[cat] = list(cat_tags.keys())
                    for tag_name, conf in cat_tags.items():
                        flat_tags[tag_name] = conf

                self.valid_images[img_id] = {
                    "path": path_info["path"],
                    "dir": path_info["dir"],
                    "filename": path_info["filename"],
                    "categories": categories,
                    "flat_tags": flat_tags
                }
                
                for tag_name in flat_tags:
                    self.tag_freq[tag_name] = self.tag_freq.get(tag_name, 0) + 1

        self.total_images = len(self.valid_images)

    def autocomplete(self, query: str):
        is_neg = query.startswith("-")
        term = query[1:] if is_neg else query

        if not term:
            return []

        results = []
        for tag, count in self.tag_freq.items():
            if term in tag:
                display_count = self.total_images - count if is_neg else count
                results.append((tag, display_count, tag.startswith(term)))

        results.sort(key=lambda x: (not x[2], -x[1]))
        return [{"tag": ("-" if is_neg else "") + x[0], "count": x[1]} for x in results[:50]]

    def search(self, pos_tags: list[str], neg_tags: list[str], dirs: list[str], skip: int, limit: int):
        results = []
        dir_set = set(dirs)
        
        for img_id, img_data in self.valid_images.items():
            if img_data["dir"] not in dir_set:
                continue

            flat = img_data["flat_tags"]
            if any(nt in flat for nt in neg_tags):
                continue
            if pos_tags and not all(pt in flat for pt in pos_tags):
                continue

            score = sum(flat[pt] for pt in pos_tags) if pos_tags else 0
            results.append((score, img_id, img_data))

        results.sort(key=lambda x: x[0], reverse=True)
        total = len(results)
        
        items = []
        for score, img_id, img_data in results[skip:skip+limit]:
            items.append({
                "id": img_id,
                "path": img_data["path"],
                "dir": img_data["dir"]
            })
            
        return {"total": total, "items": items}

    def get_detail(self, img_id: str):
        if img_id not in self.valid_images:
            return None
        data = self.valid_images[img_id]
        return {
            "id": img_id,
            "path": data["path"],
            "filename": data["filename"],
            "tags": data["categories"]
        }

indexer = Indexer()
