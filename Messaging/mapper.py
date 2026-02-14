#!/usr/bin/env python3
import sys
import json

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    try:
        record = json.loads(line)

        # Optional safety check (already low severity, but good practice)
        if record.get("fuzzy_severity", "").lower() != "normal":
            continue

        timestamp = record["timestamp"]   # "2023-03-10 00:00:00"
        date = timestamp.split(" ")[0]    # YYYY-MM-DD

        print(f"{date}\t1")

    except Exception:
        # Never crash the mapper
        continue

