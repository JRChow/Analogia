from urllib.parse import urlencode, quote_plus
import requests
from urllib import request
import base64
import json
import copy

import argparse
import sys
import os

from itertools import permutations, combinations
from collections import Counter

from pprint import pprint
from pycorenlp import StanfordCoreNLP
from wordnet import *
import SentMatch
import corenlp
import p3

from utils import Constants
from utils.Loader import load_story

# from efficiency.log import show_var
import pdb


class Innerese(object):
    def __init__(self, sent=''):
        super(Innerese, self).__init__()

        self.sent = sent
        self.frame_list = []
        self.exist = False
        self.inner = ""
        self.parsed = {}

        self.username = 'start'
        self.password = 'startbegin'

        self.corenlp_parse()
        self.get_frames()

    def corenlp_parse(self, annot='depparse, ner'):
        nlp = StanfordCoreNLP('http://localhost:9000')
        self.parsed = corenlp.parse_sent(self.sent, nlp, annot=annot)
        # pprint(self.parsed)

    def get_frames(self):
        url = 'http://start.csail.mit.edu/api.php?'
        dic = {"server": "e-genesis",
               "action": "parse",
               "te": "formatted-text",
               "kb": "no",
               "query": self.sent
               }
        query = url + urlencode(dic)

        try:
            r = requests.get(url=query,
                             auth=requests.auth.HTTPBasicAuth(
                                 self.username,
                                 self.password))
        except HTTPError as e:
            content = e.read()
            print("[Error]", content)

        content = r.content.decode("utf-8", errors="ignore")
        result = content.strip().split('\n')
        success = len(result) > 1

        self.frame_list = result
        self.inner = "\n".join(result[1:])
        self.exist = success

        if not success:
            print("[Error] there is no Innerese for:", self.sent)

        return result, success

    def generate(self):

        url = 'http://start.csail.mit.edu/api.php'
        params = {"server": "e-genesis",
                  "action": "generate",
                  "te": "formatted-text",
                  "query": self.inner
                  }

        r = requests.post(url, params=params, auth=(self.username, self.password))
        content = r.content.decode("utf-8", errors="ignore")
        result = content.strip()
        self.generated = result

        return result

    def get_trunk(self):
        trunk_str = self.frame_list[1][1:-1]
        trunk_str = trunk_str.split()
        trunk_str = [s.split(Constants.WORD_IX_SEP, 1)[0] for s in trunk_str]
        trunk = {"subj": trunk_str[0],
                 "verb": trunk_str[1],
                 "obj": trunk_str[2]}
        self.trunk = trunk
        return trunk

    def repla_pers(self, from_pers='Alice', to_pers='Zoey'):
        self.inner = self.inner.replace(from_pers, to_pers)

    def update_tup(self):
        inner = self.inner
        start_tup = [triplet[1:-1].split()
                     for triplet in inner.split('\n')
                     ]
        start_tok = set([item for triplet in start_tup
                         for item in triplet
                         if '+' in item])
        start_tok = sorted(list(start_tok))
        self.start_tok = start_tok
        self.start_tup = start_tup

    def get_n_pers(self):
        return len(self.pers)
        # return sum(pers in self.inner for pers in Constants.PERSON)

    def get_pers(self):
        pers = set([token['originalText'] for token in self.parsed['tokens']
                    if token['ner'] == Constants.NER_PER])
        self.pers = list(pers)
        return self.pers

    def get_verbs(self):
        verbs = set([token['lemma'] for token in self.parsed['tokens']
                     if token['pos'][:2] == Constants.POS_VER])
        assert sum(v in self.inner for v in verbs) == len(verbs)
        self.verbs_set = verbs

        # to do: "John can project a project"
        return verbs

    def __eq__(self, other):
        return self.inner == other.inner

    def align_inner(self, other):
        for a_tok, b_tok in zip(self.start_tok, other.start_tok):
            self.inner.replace(a_tok, b_tok)


def sent_almost_equal(a, b):

    a_looklike = [[item.split('+')[0] for item in triplet]
                  for triplet in a.start_tup]
    b_looklike = [[item.split('+')[0] for item in triplet]
                  for triplet in b.start_tup]
    equal = (a_looklike == b_looklike)

    a_tok_list = [item.split('+')[0] for item in a.start_tok]
    b_tok_list = [item.split('+')[0] for item in b.start_tok]

    equal = equal and (a_tok_list == b_tok_list)

    return equal


def story_almost_equal(a, b):
    a_looklike = [[[item.split('+')[0] for item in triplet]
                   for triplet in sent] for sent in a.start_tup]
    b_looklike = [[[item.split('+')[0] for item in triplet]
                   for triplet in sent] for sent in b.start_tup]
    equal = (a_looklike == b_looklike)

    a_tok_list = [item.split('+')[0] for item in a.start_tok]
    b_tok_list = [item.split('+')[0] for item in b.start_tok]

    equal = equal and (a_tok_list == b_tok_list)

    return equal


class Story(object):
    """docstring for  Story"""

    def __init__(self, sent_list=[]):
        super(Story, self).__init__()
        inner_list = []
        for sent in sent_list:
            inner = Innerese(sent=sent)
            inner_list.append(inner)
        self.inner_list = inner_list
        self.inner_str = self.to_str()

    def generate(self):
        generated = ''
        for sent in self.inner_list:
            generated += sent.generate() + '\n'
        self.generated = generated
        return generated

    def get_pers(self):
        pers = set()
        for sent in self.inner_list:
            pers |= set(sent.get_pers())
        self.pers = list(pers)
        return self.pers

    def repla_pers(self, from_pers='Alice', to_pers='Zoey'):
        for i in range(len(self.inner_list)):
            self.inner_list[i].repla_pers(from_pers, to_pers)

    def update_tup(self):
        inner_list = self.inner_list
        start_tup = [[triplet[1:-1].split()
                      for triplet in sent.inner.split('\n')]
                     for sent in inner_list]
        start_tok = set([item for sent in start_tup
                         for triplet in sent
                         for item in triplet
                         if '+' in item])
        start_tok = sorted(list(start_tok))
        self.start_tok = start_tok
        self.start_tup = start_tup

    def to_str(self):
        return '\n\n'.join([sent.inner for sent in self.inner_list])

    def __eq__(self, other):
        return self.inner_list == other.inner_list

    def align_inner(self, other):
        for a_tok, b_tok in zip(self.start_tok, other.start_tok):
            for i in range(len(self.inner_list)):
                self.inner_list[i].inner = self.inner_list[i].inner.replace(a_tok, b_tok)


def total_match(model, query):
    '''
    I will win this match.
    Yesterday he won that match easily.
    '''
    pers_m = model.get_pers()
    pers_q = query.get_pers()
    match = False
    for pers_q_candi in permutations(pers_q):
        model_copy = copy.deepcopy(model)

        for i in range(len(pers_m)):
            model_copy.repla_pers(from_pers=pers_m[i], to_pers=pers_q_candi[i])

        model_copy.update_tup()
        query.update_tup()

        if story_almost_equal(model_copy, query):
            model_copy.align_inner(query)
            match = True
            binding = [(pers_m[i], pers_q_candi[i])
                       for i in range(len(pers_m))]
            if model_copy == query:
                return match, binding

    return match, None


def test_story_match(model_sto=[], query_sto_list=[]):
    model_sto = ['Mary did homework.', 'Mary is praised.'] if not model_sto else model_sto
    query_sto_list = [
        ['John did homework.', 'John is praised.'],
        ['John did not do homework.', 'John is scolded.']] if not query_sto_list else query_sto_list
    model = Story(model_sto)
    matched = 0
    matched_ix = []
    matched_bind = []
    for ix, query_sto in enumerate(query_sto_list):
        query = Story(query_sto)
        match, binding = total_match(model, query)
        if match:
            matched += 1
            matched_ix += [ix]
            matched_bind += [binding]
            # print("[Info] Match{} with {}th query:".format(matched, ix))
            # show_var(["model.generate()", "query.generate()"])
    return matched, matched_ix, matched_bind


def test_sent_match():
    sent = 'Alice likes animals.'
    sent = 'Alice likes Cathy.'
    model = Innerese(sent=sent)

    story = [
        "Bob likes David.",
        "Bob loves dogs.",
        "Bob loves animals."]
    for sent in story:
        inner = Innerese(sent=sent)
        show_var(["SentMatch.total_match(model, inner)"])

    return


def find_concept(concepts, story):
    story_titl, story_text = story
    underlying_conc = []
    for conc in concepts:
        conc_titl, conc_text = conc
        n_matched, _, _ = s_c_match(story_text, conc_text)
        if n_matched:
            underlying_conc.append(conc)

    return underlying_conc


def find_hist(history, story):
    story_titl, story_text = story
    matched_hist = []
    matched_bind = []
    for hist in history:
        hist_titl, hist_text = hist
        n_matched, _, binding = h_s_match(story_text, hist_text)
        if n_matched:
            matched_hist.append(hist)
            matched_bind.append(binding[0])

    return matched_hist, matched_bind


def apply_hist(story, matched_hist, matched_bind):

    sto_titl, sto_text = story
    sto_text = Story(sto_text).generate()
    sto_text = sto_text.strip().split('\n')

    hist_text = matched_hist[-1]
    pred = Story(hist_text)

    for from_pers, to_pers in matched_bind:
        pred.repla_pers(to_pers, from_pers)
    foretune_teller = pred.generate()
    foretune_teller = foretune_teller.strip().split('\n')
    # print("[Info] Prediction of story {}:{}".format(sto_titl, foretune_teller))

    sepa_ix = foretune_teller.index(sto_text[-1])
    past = foretune_teller[:sepa_ix]
    future = foretune_teller[sepa_ix + 1:]
    if past:
        print("[Info] Guess of what causes Story '{0}': {1}".format(sto_titl, '\n'.join(past)))
    if future:
        print("[Info] Prediction of Story '{0}': {1}".format(sto_titl, '\n'.join(future)))

    return pred


def h_s_match(story, history):
    n_sent = len(story)
    hist_candi = combinations(history, n_sent)
    return test_story_match(model_sto=story, query_sto_list=hist_candi)


def s_c_match(story, concept):
    n_sent = len(concept)
    story_candi = combinations(story, n_sent)
    return test_story_match(model_sto=concept, query_sto_list=story_candi)


def more_history(history):
    hist_text = [hist[-1] for hist in history]

    more_hist = hist_text[:]

    for one_hist in hist_text:
        noun_n_pos, poten_hyper = get_all_noun(one_hist)
        for (noun, pos), hyper in zip(noun_n_pos, poten_hyper):
            for p in pos:
                toks = word_tokenize(one_hist[p[0]])
                toks[p[1]] = hyper[0]
                one_hist[p[0]] = detokenize(toks)
        pdb.set_trace()
        more_hist.append(one_hist)
    return more_hist


def generalize(history):
    more_hist = more_history(history)
    more_hist = [tuple(one_hist) for one_hist in more_hist]
    more_hist_cnt = Counter(more_hist)
    repeated = [k for k, v in more_hist_cnt.items() if v >= 3]
    for i, r in enumerate(repeated):
        inner = Innerese(r)
        if not inner.exist:
            del repeated[i]
    pdb.set_trace()
    return repeated


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-file', type=str, default='')
    args = parser.parse_args()

    if args.file == '3p':
        file = '../../data/attribution/99_temp.story'
    elif args.file == 'condition':
        file = '../../data/attribution/3_condition.story'
    elif args.file == 'success':
        file = '../../data/attribution/01_success.story'

    json_save = '../../data/attribution/99_temp.json'
    data = load_story(file, json_save)

    concepts = data["concepts"]
    story = data["story"]
    history = data["history"]

    # generalize(history)
    # matched_conc = find_concept(concepts, story[0])

    # show_var(["data"])
    for sto in story:
        sto_titl, sto_text = sto
        print("\n\n")
        print("[Info] Let's talk about Story '{}': \n\t{}".format(sto_titl, '\n\t'.join(sto_text)))
        if history:
            matched_hist, matched_bind = find_hist(history, sto)
            if matched_hist:
                apply_hist(sto, matched_hist[0], matched_bind[0])
        else:
            sent = sto_text[0]
            if p3.perman(sent):
                pred = p3.perman(sent)
            elif p3.persona_neg(sent):
                pred = p3.persona_neg(sent)
            print("[Info] Prediction of Story '{0}': \n\t{1}".format(sto_titl, pred))
    print("\n\n")
