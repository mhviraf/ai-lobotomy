#!/bin/sh
# Runs every lab experiment in order, one at a time (one 8 GB model at a time on a 16 GB Mac), each logging to
# findings/logs/<name>.log. A failure is logged and the queue moves on. About 4 hours on an M1 16GB.
# sh findings/run_all.sh [first-name]: start from that experiment (e.g. 05-sycophancy).
cd "$(dirname "$0")/.."
from=${1:-}
lab() {
    name=$1; shift
    if [ -n "$from" ] && [ "$name" != "$from" ]; then return; fi
    from=""
    echo "$(date +%H:%M) $name"
    .venv/bin/python -u -m persona_lab.lab."$@" > "findings/logs/$name.log" 2>&1 || echo "  $name FAILED (see findings/logs/$name.log)"
}
lab 01-weights weights
lab 01b-languages weights --only chinese,japanese,korean,russian,arabic,french,spanish,german --strict --per-band 3 --name 01b-languages
lab 01c-recheck recheck
lab 03-grader grader
lab 02-self-report selfreport
lab 04-momentum momentum
lab 05-sycophancy sycophancy
lab 06-tug-of-war tugofwar
lab 08-introspection introspection
lab 07-cost cost
lab 09-ladder ladder
lab 12-ablation ablation
lab 11-natural natural
lab 10-entangle entangle
lab 13-zoo zoo
echo "$(date +%H:%M) done"
