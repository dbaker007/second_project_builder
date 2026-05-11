#!/bin/bash

# 1. Clean Environment
echo "🧹 Cleaning Sentinel state..."
rm -rf targets
rm -rf workspaces 
rm -rf snapshots/*

ollama ps | awk "NR>1 {print \$1}" | xargs -L1 ollama stop

echo "🚀 Starting Sentinel Engine..."
uv run src/main.py > sentinel_debug.log 2>&1