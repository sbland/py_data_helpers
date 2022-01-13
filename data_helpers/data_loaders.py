from pathlib import Path
import json
import csv
from .cls_parsing import dict_to_cls


def load_json_to_cls(file_path: Path, cls):
    with open(file_path) as file_raw:
        json_data = json.load(file_raw)
        cls_obj = dict_to_cls(json_data, cls)
        return cls_obj

def json_loader(fp):
    with open(fp) as f:
        return json.load(f)

def csv_loader(fp):
    with open(fp) as f:
        spamreader = csv.reader(f)
        header = next(spamreader)
        out = []
        for row in spamreader:
            out.append({k:v for k, v in zip(header, row)})
        return out
