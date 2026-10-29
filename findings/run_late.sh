#!/bin/sh
# Experiments 22, 23b and 27-51, run the same way as the other scripts (about 3 hours on an M1 16GB; 30 alone is 80 min,
# 38 downloads Qwen3-1.7B).
cd "$(dirname "$0")/.."
lab() { name=$1; shift; echo "$(date +%H:%M) $name"; .venv/bin/python -u -m persona_lab.lab."$@" > "findings/logs/$name.log" 2>&1 || echo "  $name FAILED (see findings/logs/$name.log)"; }
lab 22-ordering ordering
lab 27-effect effect
lab 28-selfmodel selfmodel
lab 29-block block
lab 30-locate locate
lab 31-explain explain
lab 32-origin origin
lab 33-override override
lab 34-eastwest eastwest
lab 35-stance stance
lab 36-nation nation
lab 37-gate gate
lab 38-replicate replicate
lab 39-midsentence midsentence
lab 40-assemble assemble
lab 41-values values
lab 42-selfread selfread
lab 43-congruence congruence
lab 44-drift drift
lab 45-human human
lab 23b-cut cut Qwen/Qwen3-1.7B
lab 46-west west
lab 47-persona persona
lab 48-year year
lab 49-timetravel timetravel
lab 50-future future
lab 51-year17 year17
echo "$(date +%H:%M) late done"
