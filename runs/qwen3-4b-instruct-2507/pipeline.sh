#!/bin/sh
# Reproduces this directory: all traits, the demo characters, the demos, then the single-neuron search and
# demos (~75 min + ~100 min on an M1 16GB; close Chrome first or the single-neuron steps start swapping).
set -e
cd "$(dirname "$0")/../.."
pl() { .venv/bin/python -u -m persona_lab --model Qwen/Qwen3-4B-Instruct-2507 "$@"; }
pl extract
pl entity --name darth-vader --entity "Darth Vader" --keywords "Vader,Anakin"
pl entity --name paddington --entity "Paddington Bear" --keywords "Paddington,Padding,bear,marmalade"
.venv/bin/python -u -m persona_lab.experiments --run runs/qwen3-4b-instruct-2507
# characters for the single-neuron demos: villains that might have a single neuron, and a hero that does
pl entity --name dracula --entity "Count Dracula" --keywords "Dracula,vampire"
pl entity --name grinch --entity "the Grinch" --keywords "Grinch"
pl entity --name voldemort --entity "Lord Voldemort" --keywords "Voldemort,Dark Lord,He Who Must Not Be Named,Tom Riddle"
pl entity --name santa --entity "Santa Claus" --keywords "Santa,Saint Nick,Father Christmas,Kris Kringle,North Pole,reindeer"
pl single humor,formality,agreeableness,optimism,admiration,neuroticism,paddington,darth-vader,extraversion,sycophancy,openness,conscientiousness,confidence
pl single dracula,grinch,voldemort,santa --candidates 20
.venv/bin/python -u -m persona_lab.experiments --single --run runs/qwen3-4b-instruct-2507
