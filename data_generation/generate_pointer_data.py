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

random.seed(213)
proof_parser = Parser()


def convert_proof_to_seq2seq(steps):
    sources, targets = list(), list()
    for i, step in enumerate(steps):
        source, target = proof_parser.parse_proof_step_to_seq(step)
        sources.append(source)
        targets.append(target)
    return sources, targets


def convert_proof_to_pointer_repr(steps):
    sources, targets = list(), list()
    for i, step in enumerate(steps):
        source, _ = proof_parser.parse_proof_step_to_seq(step)
        action = (step['lemma'].name, *step['input_entities'])
        target = ActionRepresentationPointer.proof_step_and_action_to_formula(step, action)
        sources.append(source)
        targets.append(target)
    return sources, targets


def generate_multiple_seq2seq(multiple_problems, all_sources_to_targets=None):
    if not all_sources_to_targets:
        all_sources_to_targets = dict()

    for problem in multiple_problems:
        sources, targets = convert_proof_to_seq2seq(problem)
        for source, target in zip(sources, targets):
            if source in all_sources_to_targets:
                continue
            all_sources_to_targets[source] = target
    return all_sources_to_targets


def generate_trajectories(multiple_problems, all_sources_to_targets=None):
    if not all_sources_to_targets:
        all_sources_to_targets = dict()

    trajectories = []
    for problem in multiple_problems:
        trajectory = []
        sources, targets = convert_proof_to_seq2seq(problem)

        zipped = list(zip(sources, targets))
        for i, (source, target) in enumerate(zipped):
            # if source in all_sources_to_targets:
            #     continue
            if i + 1 < len(zipped):
                next_state, next_action = zipped[i+1]
            else:
                next_state = "QED"

            trajectory.append({"state": source,
                               "action": target,
                               "next_state": next_state})

        trajectories.append(trajectory)

    return trajectories

def generate_pointer_trajectories(multiple_problems, all_sources_to_targets=None):
    if not all_sources_to_targets:
        all_sources_to_targets = dict()

    trajectories = []
    for problem in multiple_problems:
        trajectory = []
        sources, targets = convert_proof_to_pointer_repr(problem)

        zipped = list(zip(sources, targets))
        for i, (source, target) in enumerate(zipped):
            if i + 1 < len(zipped):
                next_state, next_action = zipped[i+1]
            else:
                next_state = "QED"

            trajectory.append({"state": source,
                               "action": target,
                               "next_state": next_state})
        # Note that there may still be same steps existing in the dataset
        if trajectory not in trajectories:
            trajectories.append(trajectory)
        # trajectories.append(trajectory)

    return trajectories


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Mode generator')
    parser.add_argument('--orders_path',
                        default="/home/minchao/proj/INT/data/benchmark/field")
    parser.add_argument('--dump_path', '-dp', default="/home/minchao/proj/INT/data/latent_actions")
    parser.add_argument('-k', type=int)
    parser.add_argument('-l', type=int)
    parser.add_argument('--degree', type=int, default=0)
    parser.add_argument('--num_probs', type=int, default=1)
    parser.add_argument('--use_combos', action='store_true')
    parser.add_argument('--num_order_or_combo', type=int, default=None)
    args = parser.parse_args()

    if not os.path.isdir(args.dump_path):
        os.makedirs(args.dump_path)

    combos = json.load(open(os.path.join(args.orders_path, "combinations.json"), "r"))
    orders = json.load(open(os.path.join(args.orders_path, "orders.json"), "r"))

    datasets, problems = generate_multiple_problems(num_axioms=args.k, length=args.l,
                                                    num_probs=args.num_probs, train_test="train",
                                                    orders=orders, degree=args.degree)
    trajectories = generate_pointer_trajectories(multiple_problems=problems)
    opts = jsbeautifier.default_options()
    opts.indent_size = 2
    latent_dataset = jsbeautifier.beautify(json.dumps(trajectories), opts)

    with open("latent_dataset_pointer_repr.json", "w") as f:
        f.write(latent_dataset)
