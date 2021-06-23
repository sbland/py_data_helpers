from pathlib import Path
import json
from .cls_parsing import dict_to_cls


def load_json_to_cls(file_path: Path, cls):
    with open(file_path) as file_raw:
        json_data = json.load(file_raw)
        cls_obj = dict_to_cls(json_data, cls)
        return cls_obj
