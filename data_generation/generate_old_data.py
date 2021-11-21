#!/usr/bin/env python

import argparse
import json
import os
import random
import pickle

from INT.data_generation.generate_problems import generate_multiple_problems
from INT.proof_system.graph_seq_conversion import Parser
from INT.representation.action_representation_pointer import ActionRepresentationPointer

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

def convert_proof_to_pointer_repr_with_objectives(steps):
    sources, targets = list(), list()
    objective = ""
    for i, step in enumerate(steps):
        source, _ = proof_parser.parse_proof_step_to_seq(step)
        action = (step['lemma'].name, *step['input_entities'])
        target = ActionRepresentationPointer.proof_step_and_action_to_formula(step, action)
        sources.append(source)
        targets.append(target)
        if i == 0:
            objective = steps["objectives"][0]
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
    dup_state = []
    dup_action = []

    if not all_sources_to_targets:
        all_sources_to_targets = dict()

    trajectories = []
    for problem in multiple_problems:
        flag = False        
        trajectory = []
        sources, targets = convert_proof_to_seq2seq(problem)

        zipped = list(zip(sources, targets))
        for i, (source, target) in enumerate(zipped):
            # if source in all_sources_to_targets:
            #     continue
            if source not in dup_state:
                dup_state.append(source)
            else:
                flag = True
                break
            if target not in dup_action:
                dup_action.append(target)
            else:
                flag = True
                break
            
            if i + 1 < len(zipped):
                next_state, next_action = zipped[i+1]
            else:
                next_state = "QED"

            trajectory.append({"state": source,
                               "action": target,
                               "next_state": next_state})
        if not flag:
            trajectories.append(trajectory)

    return trajectories

def generate_pointer_trajectories(multiple_problems, all_sources_to_targets=None):
    dup_state = []
    dup_action = []
    if not all_sources_to_targets:
        all_sources_to_targets = dict()

    trajectories = []
    for problem in multiple_problems:
        flag = False
        trajectory = []
        sources, targets = convert_proof_to_pointer_repr(problem)

        zipped = list(zip(sources, targets))
        for i, (source, target) in enumerate(zipped):
            if source not in dup_state:
                dup_state.append(source)
            else:
                flag = True
                break
            if target not in dup_action:
                dup_action.append(target)
            else:
                flag = True
                break
            
            if i + 1 < len(zipped):
                next_state, next_action = zipped[i+1]
            else:
                next_state = "QED"

            trajectory.append({"state": source,
                               "action": target,
                               "next_state": next_state})
        # Note that there may still be same steps existing in the dataset
        # if trajectory not in trajectories:
        #     trajectories.append(trajectory)
        if not flag:
            trajectories.append(trajectory)

    return trajectories


def generate_pointer_trajectories_new(dataset, multiple_problems, all_sources_to_targets=None, max_len=120):

    entity_ref = {}
    existing_states = {} # set()
    print("start building")
    for t in dataset:
        step_states = {s["state"]:"" for s in t}
        existing_states.update(step_states)
    print(len(existing_states))
    print("done building set")

    dup_state = {} # set()
    dup_action = {} # set()
    if not all_sources_to_targets:
        all_sources_to_targets = dict()

    trajectories = []
    for problem in multiple_problems:
        flag = False
        trajectory = []
        sources, targets = convert_proof_to_pointer_repr(problem)

        zipped = list(zip(sources, targets))
        for i, (source, target) in enumerate(zipped):
            if source in existing_states:
                flag = True
                break
            if source not in dup_state:
                # dup_state.add(source)
                dup_state.update({source:""})
            else:
                flag = True
                break
            if target not in dup_action:
                # dup_action.add(target)
                dup_action.update({target:""})
            else:
                flag = True
                break

            if i + 1 < len(zipped):
                next_state, next_action = zipped[i+1]
            else:
                next_state = "QED"

            if len(source) > max_len or len(target) > max_len or len(next_state) > max_len:
                flag = True
                break

            trajectory.append({"state": source,
                               "action": target,
                               "next_state": next_state})

            entity_ref[source] = {"objective": problem[i]["observation"]["objectives"][0].name,
                                  "ground_truth": [g.name for g in problem[i]["observation"]["ground_truth"]]}
        # Note that there may still be same steps existing in the dataset
        # if trajectory not in trajectories:
        #     trajectories.append(trajectory)
        if not flag:
            trajectories.append(trajectory)
    print(len(trajectories))
    return trajectories, entity_ref


def generate_old_trajectories_new(dataset, multiple_problems, all_sources_to_targets=None, max_len=120):

    state_dup_c = 0
    action_dup_c = 0
    len_c = 0

    entity_ref = {}
    existing_states = {} # set()
    print("start building")
    for t in dataset:
        step_states = {s["state"]:"" for s in t}
        existing_states.update(step_states)
    print(len(existing_states))
    print("done building set")

    dup_state = {} # set()
    dup_action = {} # set()
    if not all_sources_to_targets:
        all_sources_to_targets = dict()

    trajectories = []
    for problem in multiple_problems:
        flag = False
        trajectory = []
        sources, targets = convert_proof_to_seq2seq(problem)

        zipped = list(zip(sources, targets))
        for i, (source, target) in enumerate(zipped):
            if source in existing_states:
                flag = True
                break
            if source not in dup_state:
                # dup_state.add(source)
                dup_state.update({source:""})
            else:
                state_dup_c += 1
                flag = True
                break
            # if target not in dup_action:
            #     # dup_action.add(target)
            #     dup_action.update({target:""})
            # else:
            #     action_dup_c += 1
            #     flag = True
            #     break

            if i + 1 < len(zipped):
                next_state, next_action = zipped[i+1]
            else:
                next_state = "QED"

            if len(source) > max_len or len(target) > max_len or len(next_state) > max_len:
                len_c += 1
                flag = True
                break

            trajectory.append({"state": source,
                               "action": target,
                               "next_state": next_state})

            entity_ref[source] = {"objective": problem[i]["observation"]["objectives"][0].name,
                                  "ground_truth": [g.name for g in problem[i]["observation"]["ground_truth"]]}
        # Note that there may still be same steps existing in the dataset
        # if trajectory not in trajectories:
        #     trajectories.append(trajectory)
        if not flag:
            trajectories.append(trajectory)
    print(len(trajectories))
    print("state dup:{}".format(state_dup_c))
    print("action dup:{}".format(action_dup_c))
    print("len c:{}".format(len_c))
    return trajectories, entity_ref


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
    parser.add_argument('--id', type=int, default=0)
    
    args = parser.parse_args()

    if not os.path.isdir(args.dump_path):
        os.makedirs(args.dump_path)

    combos = json.load(open(os.path.join(args.orders_path, "combinations.json"), "r"))
    orders = json.load(open(os.path.join(args.orders_path, "orders.json"), "r"))

    datasets, problems = generate_multiple_problems(num_axioms=args.k, length=args.l,
                                                    num_probs=args.num_probs, train_test="train",
                                                    orders=orders, degree=args.degree)
    # trajectories = generate_pointer_trajectories(multiple_problems=problems)
    # with open("latent_dataset_pointer_repr.json") as f:
    #     dataset = json.load(f)
    trajectories, entity_ref = generate_old_trajectories_new([], multiple_problems=problems)

    opts = jsbeautifier.default_options()
    opts.indent_size = 2
    latent_dataset = jsbeautifier.beautify(json.dumps(trajectories), opts)
    entity_ref = jsbeautifier.beautify(json.dumps(entity_ref), opts)

    with open("latent_dataset_old_repr_new_{}.json".format(args.id), "w") as f:
        f.write(latent_dataset)
    with open("entity_ref_{}.json".format(args.id), "w") as f:
        f.write(entity_ref)
