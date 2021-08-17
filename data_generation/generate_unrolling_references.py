#!/usr/bin/env python

import argparse
import json
import os
import random
import pickle

# from data_generation.generate_problems import generate_multiple_problems
# from proof_system.graph_seq_conversion import Parser
# from representation.action_representation_pointer import ActionRepresentationPointer

import jsbeautifier

random.seed(213)
# proof_parser = Parser()

def generate_references(dataset):
    references = {}
    for t in dataset:
        for j,step in enumerate(t):
            references[step["state"]] = {"actions": [s["action"] for s in t[j:]], "next_states": [s["next_state"] for s in t[j:]]}

    return references

opts = jsbeautifier.default_options()
opts.indent_size = 2


with open("/home/minchao/proj/latent_actions_INT/latent_dataset_pointer_repr.json") as f:
    dataset = json.load(f)

references = generate_references(dataset)
references = jsbeautifier.beautify(json.dumps(references), opts)

with open("latent_dataset_pointer_references.json", "w") as f:
    f.write(references)


# if __name__ == "__main__":
#     opts = jsbeautifier.default_options()
#     opts.indent_size = 2


#     with open("latent_dataset_pointer_repr.json") as f:
#         dataset = json.load(f)

#     references = generate_references(dataset)
#     references = jsbeautifier.beautify(json.dumps(references), opts)

#     with open("latent_dataset_references.json", "w") as f:
#         f.write(references)
