from INT.proof_system.prover import Prover
from INT.proof_system.all_axioms import all_axioms
from INT.visualization.seq_parse import name_to_ls
from INT.representation.action_representation_pointer import ActionRepresentationPointer, thm2index
import json
import sys

# with open("test_proof/entity_ref_2000.json") as f:
#     entity_ref = json.load(f)

# with open("test_proof/latent_dataset_pointer_repr_new_2000.json") as f:
#     dataset = json.load(f)

# with open("predicted_actions_CE.json") as f:
#     predictions = json.load(f)


with open("test_proof/entity_ref_test.json") as f:
    entity_ref = json.load(f)

# with open("predicted_actions_MSE.json") as f:
#     predictions = json.load(f)

with open("latent_BFS_proofs.json") as f:
    predictions = json.load(f)


# test_objectives = ["Equivalent ( mul ( add ( a , add ( c , f ) ) , add ( a , c ) ) , mul ( add ( a , add ( c , f ) ) , add ( a , add ( c , f ) ) ) )"]

# test_objectives = ["Equivalent ( mul ( add ( a , add ( c , f ) ) , add ( a , c ) ) , sqr ( add ( a , add ( c , f ) ) ) )"]
# test_ground_truth = ["Equivalent ( add ( c , f ) , c )", "Equivalent ( add ( sqr ( 1 ) , f ) , 1 )"]

# raw_action1 = "@K((a+(c+f))*(a+c))=((a+(c+f))^2~)$"

# raw_action2 = "@L((a+(c+f))*(a+;c))=((a+(c+f))*(a~+(c+!f)))$"


# input_objectives = [name_to_ls(test_objectives[0])]
# input_ground_truth = [name_to_ls(g) for g in test_ground_truth]

# decoded_action = ActionRepresentationPointer.pointer_str_to_action(input_objectives[0], raw_action1, mode="mc")

# prover = Prover(all_axioms, input_ground_truth, input_objectives, prove_direction="backward")

# lemma = decoded_action[0]
# operands = decoded_action[1:]
# prover.apply_theorem(lemma, operands)


# decoded_action = ActionRepresentationPointer.pointer_str_to_action(prover.get_objectives()[0], raw_action2, mode="mc")
# lemma = decoded_action[0]
# operands = decoded_action[1:]
# prover.apply_theorem(lemma, operands)

# objective = "(c+f)=c & ((1^2)+f)=1 to ((a+(c+f))*(a+c))=((a+(c+f))^2)"
# actions = [raw_action1, raw_action2]

# objective = "to (((b*a)*c)*((a*c)+c))=(((b*(c*a))*(a*c))+((b*(c*a))*c))"

# objective = "to ((((a*b)*c)*(a*c))+(((b*a)*c)*c))=(((b*(c*a))*(a*c))+((a*(b*c))*c))"
# actions = ["@E((((a*b)*c)*(a*c))+(((b*a)*c)*c))=(((b*(c*a))*(a*c))+((a*~(b*c))*c))$",
#            "@E((((a*~b)*c)*(a*c))+(((b*a)*c)*c))=(((b*(c*a))*(a*c))+(((b*c)*a)*c))$",
#            "@J((((b*a)*c)*(a*c))+~(((b*a)*c)*c))=(((b*(c*a))*(a*c))+(((b*c)*a)*c))$",
#            "@F(((b*a)*c)*((a*c)+c))=(((b*(c*a))*(a*c))+(((b*c)*~a)*c))$",
#            "@J(((b*a)*c)*((a*c)+c))=(((b*(c*a))*(a*c))+~((b*(c*a))*c))$",
#            "@E(((b*a)*c)*((a*c)+c))=((b*(c*~a))*((a*c)+c))$",
#            "@F(((b*a)*~c)*((a*c)+c))=((b*(a*c))*((a*c)+c))$"]


# objective = "to (((b*a)*c)*((a*c)+c))=(((b*(c*a))*(a*c))+((b*(c*a))*c))"
# actions = ["@J(((b*a)*c)*((a*c)+c))=(((b*(c*a))*(a*c))+~((b*(c*a))*c))$",
#            "@E(((b*a)*c)*((a*c)+c))=((b*(c*~a))*((a*c)+c))$",
#            "@F(((b*a)*~c)*((a*c)+c))=((b*(a*c))*((a*c)+c))$"]

def run_proof(objective, actions, entity_ref):
    ground_truth = entity_ref[objective]["ground_truth"]
    goal = entity_ref[objective]["objective"]
    objectives = [name_to_ls(goal)]
    ground_truth = [name_to_ls(g) for g in ground_truth]
    # print(objectives)
    # print(ground_truth)
    prover = Prover(all_axioms, ground_truth, objectives, prove_direction="backward")
    for a in actions:
        objectives = prover.get_objectives()
        try:
            decoded_action = ActionRepresentationPointer.pointer_str_to_action(objectives[0], a, mode="mc")
        except ValueError:
            print("Action decoding error")
            return False
        except AssertionError:
            print("Assertion error when decoding actions.")
            return False
        lemma = decoded_action[0]
        operands = decoded_action[1:]
        prover.apply_theorem(lemma, operands)
        # print(prover.get_observation())
        if prover.is_proved():
            print("Valid proof")
            return True
        # objectives = prover.get_objectives()

    print("Invalid proof")
    return False


def run_proof_with_steps(objective, actions, entity_ref):
    ground_truth = entity_ref[objective]["ground_truth"]
    goal = entity_ref[objective]["objective"]
    objectives = [name_to_ls(goal)]
    ground_truth = [name_to_ls(g) for g in ground_truth]
    # print(objectives)
    # print(ground_truth)
    prover = Prover(all_axioms, ground_truth, objectives, prove_direction="backward")
    for s,a in enumerate(actions):
        objectives = prover.get_objectives()
        try:
            decoded_action = ActionRepresentationPointer.pointer_str_to_action(objectives[0], a, mode="mc")
        except ValueError:
            print("Action decoding error")
            return False,-1
        except AssertionError:
            print("Assertion error when decoding actions.")
            return False,-1
        lemma = decoded_action[0]
        operands = decoded_action[1:]
        prover.apply_theorem(lemma, operands)
        # print(prover.get_observation())
        if prover.is_proved():
            print("Valid proof")
            return True,s
        # objectives = prover.get_objectives()

    print("Invalid proof")
    return False,-1

# c =0
# metrics = {}
# for i in range(7):
#     metrics[i+1] = 0
# for t in dataset:
#     c += 1
#     for j,s in enumerate(t):
#         objective = s["state"]
#         try:
#             actions = predictions[objective]
#         except KeyError:
#             print("Missing keys: {}".format(objective))
#             continue
#         result = run_proof(objective, actions, entity_ref)
#         if result:
#             print("Proved")
#             metrics[j+1] += 1
#     print(c)
# print(metrics)


c =0
metrics = {}

lens_metrics = {}

eq_count = 0
for i in range(7):
    metrics[i+1] = 0
    lens_metrics[i+1] = 0
    
for t in predictions:
    # objective = t s["state"]
    actions = predictions[t]
    lens_metrics[len(actions)] += 1

    if len(actions) > 1:
        if actions[0] == actions[1]:
            eq_count += 1 
        
    result,s = run_proof_with_steps(t, actions, entity_ref)
    if result:
        print("Proved")
        
        metrics[s+1] += 1

print(metrics)
print("lens stats: {}".format(lens_metrics))
print("eq:{}".format(eq_count))
