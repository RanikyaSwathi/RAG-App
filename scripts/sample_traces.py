#!/usr/bin/env python3
"""
Sample 20 random traces with a documented seed.
Demonstrates provable, reproducible random sampling from data/traces.jsonl.
"""

import json
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
TRACES_PATH = BASE_DIR / "data" / "traces.jsonl"
SEED = 20261103  # Today's date: Nov 3, 2026

def get_sampled_traces(seed: int = SEED, k: int = 20):
    with open(TRACES_PATH, "r", encoding="utf-8") as f:
        traces = [json.loads(line) for line in f]
        
    rng = random.Random(seed)
    sampled_indices = rng.sample(range(len(traces)), k)
    sampled_traces = [traces[i] for i in sampled_indices]
    return sampled_traces, sampled_indices

if __name__ == "__main__":
    sampled, indices = get_sampled_traces()
    print(f"Seed: {SEED}")
    print(f"Total sampled traces: {len(sampled)}")
    print("\nSampled Trace IDs:")
    for idx, t in enumerate(sampled, 1):
        print(f"{idx:2d}. Index: {indices[idx-1]:4d} | Trace ID: {t['trace_id']} | Query: {t['user_query'][:60]}...")
