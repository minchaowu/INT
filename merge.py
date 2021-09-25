#!/usr/bin/env python

import argparse
import json
import os
import random
import pickle

from data_generation.generate_problems import generate_multiple_problems
from proof_system.graph_seq_conversion import Parser
from representation.action_representation_pointer import ActionRepresentationPointer

import jsbeautifier


# ids = [1, 2, 3, 4, 5, 6]
# ids = [7, 8, 9, 10, 11, 12, 99]
ids = [101, 20, 21]


dup_states = set()
dup_actions = set()
dataset = []
entity_ref = {}

for i in ids:
    with open("latent_dataset_pointer_repr_new_{}.json".format(i)) as f:
        new_dataset = json.load(f)
        # print(len(new_dataset))
    for t in new_dataset:
        step_dups = False
        for s in t:
            if s["state"] in dup_states or s["action"] in dup_actions:
                step_dups = True
                break
        if step_dups:
            continue
        else:
            dataset.append(t)
            dup_states = dup_states | {s["state"] for s in t}
            dup_actions = dup_actions | {s["action"] for s in t}
    

for i in ids:
    with open("entity_ref_{}.json".format(i)) as f:
        new_entity_ref = json.load(f)
        # print("en")
        # print(len(new_entity_ref))
    entity_ref.update(new_entity_ref)


for t in dataset:
    for s in t:
        if s["state"] not in entity_ref:
            print("not found")

print(len(dataset))
print(len(entity_ref))


opts = jsbeautifier.default_options()
opts.indent_size = 2
latent_dataset = jsbeautifier.beautify(json.dumps(dataset), opts)
entity_ref = jsbeautifier.beautify(json.dumps(entity_ref), opts)

with open("latent_dataset_pointer_repr_new_{}.json".format(102), "w") as f:
    f.write(latent_dataset)
with open("entity_ref_{}.json".format(102), "w") as f:
    f.write(entity_ref)
