#!/bin/sh
# Third batch of experiments: waits for run_more.sh to finish, then runs these the same way.
cd "$(dirname "$0")/.."
until grep -q "more done" findings/logs/queue-more.log 2>/dev/null; do sleep 30; done
lab() { name=$1; shift; echo "$(date +%H:%M) $name"; .venv/bin/python -u -m persona_lab.lab."$@" > "findings/logs/$name.log" 2>&1 || echo "  $name FAILED (see findings/logs/$name.log)"; }
lab 20-whoami whoami
lab 21-census census
lab 23-cut cut
lab 24-switch switch
lab 25-chatgpt chatgpt
lab 26-front front
echo "$(date +%H:%M) next done"
