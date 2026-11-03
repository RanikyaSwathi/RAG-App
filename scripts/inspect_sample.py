#!/usr/bin/env python3
"""
Inspect all 20 sampled traces in detail.
"""

import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

import json
from scripts.sample_traces import get_sampled_traces, SEED

def main():
    sampled, indices = get_sampled_traces(SEED, 20)
    print(f"=== INSPECTION OF 20 SAMPLED TRACES (Seed: {SEED}) ===\n")
    for i, t in enumerate(sampled, 1):
        print(f"--------------------------------------------------------------------------------")
        print(f"Sample #{i:02d} | Index: {indices[i-1]} | Trace ID: {t['trace_id']}")
        print(f"Timestamp: {t['timestamp']}")
        print(f"Query: {t['user_query']}")
        print(f"Retrieved Chunks:")
        for c in t['retrieved_chunks']:
            print(f"  - [{c['chunk_id']}] {c['policy_id']} §{c['section']} (Region: {c['region']}, Date: {c['effective_date']}, Score: {c['score']})")
        print(f"Raw Output:\n{t['raw_output']}")
        print(f"Status: {t['status']}")
        print()

if __name__ == "__main__":
    main()
