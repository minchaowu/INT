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
# ids = [120, 40, 41, 42, 43]
# ids = range(1,19) #[101, 20, 21]
# ids = [121, 44, 45, 46]
ids = [122, 500]
# dup_states = set()
# dup_actions = set()

dup_states = {}
dup_actions = {} #set()

dataset = []
entity_ref = {}


with open("latent_dataset_pointer_repr_new_600.json") as f:
    new_dataset = json.load(f)


for t in new_dataset:
    step_dups = False
    for s in t:
        if s["state"] in dup_states or s["action"] in dup_actions:
            step_dups = True
            print("dup found")
            break
    if step_dups:
        continue
    else:
        dataset.append(t)
        dup_states.update({s["state"]:"" for s in t})
        dup_actions.update({s["action"]:"" for s in t})

print("removing dups done.")
print(len(dataset))
