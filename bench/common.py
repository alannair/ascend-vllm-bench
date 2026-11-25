from __future__ import annotations
import csv
import datetime
import hashlib
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'state'
LOGS = ROOT / 'logs'
GIB = 1024**3


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds')


def load(path, default=None):
    return json.loads(Path(path).read_text()) if Path(path).exists() else default


def atomic(path, item):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.write-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(item, f, indent=2, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def slug(name):
    return name.replace('/', '__')


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')


def csv_open(path, cols):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    f = path.open('a', newline='', buffering=1)
    writer = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
    if path.stat().st_size == 0:
        writer.writeheader()
    return f, writer


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()[:12]
