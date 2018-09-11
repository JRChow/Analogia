from pprint import pprint
from pycorenlp import StanfordCoreNLP
from wordnet import *


from efficiency.log import show_var
import pdb


def trunk_match(model, query, verbose=True):
    '''
    I will win this match.
    Yesterday he won that match easily.
    '''
    trunk_m, trunk_q = model.get_trunk(), query.get_trunk()
    match = if_hypo(trunk_m["verb"], trunk_q["verb"], 'v', verbose=verbose)
    match = match and if_hypo(trunk_m["obj"], trunk_q["obj"], verbose=verbose)
    pdb.set_trace()
    return match


def total_match(model, query):
    '''
    Alice loves Bob. 
    Carrie loves John.
    # to do: Alice likes animals. & Bob loves dogs. 
    # to do: Alice likes Bob & Alice likes a person.
    '''
    pers_m = model.get_pers()
    pers_q = query.get_pers()
    match = False
    for pers_q_candi in permutations(pers_q):
        for i in range(len(pers_m)):
            model.repla_pers(from_pers=i, to_pers=pers_q_candi[i])
        if model.inner == query.inner:
            match = True
    return match


def struc_match(model, query, verbose=True):
    '''
    criteria for a match:
        - the center verb should be same or subword
        - all links with center verb should have the same attr
    example:
        - I am healthy. <-> You are healthy.
        - I won a game. <-> He won a competition.
        - I won it once. <-> I won that once.
    '''
    pdb.set_trace()
    model_trunk = [token for token in model if token['dep'] == 'ROOT' or token['governor'] == model[0]['dependent']]
    query_trunk = [token for token in query if token['dep'] == 'ROOT' or token['governor'] == model[0]['dependent']]

    if model_trunk[0] != query_trunk[0]:
        if not if_hypo(model_trunk[0]['dependentGloss'], query_trunk[0]['dependentGloss'], verbose=verbose):
            return False
    for m, q in zip(model_trunk[1:], query_trunk[1:]):
        if m['dep'] != q['dep']:
            return False

    return True


if __name__ == "__main__":

    show_var(["if_same_stem(['good','better', 'best'], 'a', verbose=True)"])
