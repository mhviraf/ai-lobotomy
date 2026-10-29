#!/bin/sh
# Experiments added after run_all.sh started: waits for it to finish, then runs these the same way.
cd "$(dirname "$0")/.."
until grep -q "done" findings/logs/queue.log 2>/dev/null; do sleep 30; done
lab() { name=$1; shift; echo "$(date +%H:%M) $name"; .venv/bin/python -u -m persona_lab.lab."$@" > "findings/logs/$name.log" 2>&1 || echo "  $name FAILED (see findings/logs/$name.log)"; }
lab 14-language language
lab 15-identity identity
lab 16-crosslingual crosslingual
lab 17-behaviors behaviors
lab 18-compose compose
lab 19-index index
echo "$(date +%H:%M) more done"
