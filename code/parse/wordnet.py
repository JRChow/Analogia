from pprint import pprint
from pycorenlp import StanfordCoreNLP

import nltk
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.tokenize import word_tokenize

import itertools
import string
from collections import OrderedDict

from efficiency.log import show_var
import pdb


def if_hypo(fruit, apple, part_of_sp='n', verbose=False):
    if fruit == apple:
        return True
    if fruit == 'perform':
        assert part_of_sp == 'v'
        if_apple_is_verb = sum(syn.name().split('.')[1] == part_of_sp for syn in wn.synsets(apple)) > 0
        assert if_apple_is_verb
        return True

    if fruit == 'something':
        assert part_of_sp == 'n'
        if_apple_is_noun = sum(syn.name().split('.')[1] == part_of_sp for syn in wn.synsets(apple)) > 0
        assert if_apple_is_noun
        return True

    fruit_syn = set(syn for syn in wn.synsets(fruit) if syn.name().split('.')[1] == part_of_sp)
    types_of_fruits = set([w for syn in fruit_syn for s in syn.closure(lambda s:s.hyponyms()) for w in s.lemma_names()])
    if verbose and (apple not in types_of_fruits):
        show_var(["types_of_fruits"])
    return apple in types_of_fruits


def get_hyper(apple, part_of_sp='n'):
    apple_syn = set(syn for syn in wn.synsets(apple) if syn.name().split('.')[1] == part_of_sp)
    apple_is_a_ = set([w for syn in apple_syn for s in syn.closure(lambda s:s.hypernyms()) for w in s.lemma_names()])
    return apple_is_a_


def detokenize(tokens):
    return "".join([" " + i if not i.startswith("'") and i not in string.punctuation else i for i in tokens]).strip()


def get_all_noun(sent_list, hyper=True):
    nouns = []
    nouns_dict = {}
    for i_sent, sent in enumerate(sent_list):
        sent_tok = word_tokenize(sent)
        tok_tag = nltk.pos_tag(sent_tok)
        nouns += [[tok, (i_sent, tok_i)] for tok_i, (tok, tag) in enumerate(tok_tag) if tag[:2] == 'NN']
    for n, (i_sent, tok_i) in nouns:
        if n in nouns_dict:
            nouns_dict[n].append((i_sent, tok_i))
        else:
            nouns_dict[n] = [(i_sent, tok_i)]
    nouns_dict = sorted(nouns_dict.items(), key=lambda t: t[0])

    if hyper:

        noun_hyper = [list(get_hyper(n)) for n, _ in nouns_dict]

        poten_gener = list(itertools.product(*noun_hyper))
        return nouns_dict, poten_gener

    return nouns_dict,


def if_same_stem(word_list, pos='n', verbose=False):
    wnl = WordNetLemmatizer()
    word_list = [wnl.lemmatize(word, pos=pos) for word in word_list]
    if verbose and len(set(word_list)) != 1:
        show_var(["word_list"])

    return len(set(word_list)) == 1


if __name__ == "__main__":
    sent_list = ["I got up from bed.", "I like peas."]

    show_var(["get_all_noun(sent_list)",
              "get_hyper('apple')",
              "if_hypo('like', 'love', part_of_sp='v', verbose=True)"])
    pdb.set_trace()

    show_var(["if_same_stem(['good','better', 'best'], 'a', verbose=True)"])

'''
POS tag list:

CC  coordinating conjunction
CD  cardinal digit
DT  determiner
EX  existential there (like: "there is" ... think of it like "there exists")
FW  foreign word
IN  preposition/subordinating conjunction
JJ  adjective   'big'
JJR adjective, comparative  'bigger'
JJS adjective, superlative  'biggest'
LS  list marker 1)
MD  modal   could, will
NN  noun, singular 'desk'
NNS noun plural 'desks'
NNP proper noun, singular   'Harrison'
NNPS    proper noun, plural 'Americans'
PDT predeterminer   'all the kids'
POS possessive ending   parent's
PRP personal pronoun    I, he, she
PRP$    possessive pronoun  my, his, hers
RB  adverb  very, silently,
RBR adverb, comparative better
RBS adverb, superlative best
RP  particle    give up
TO  to  go 'to' the store.
UH  interjection    errrrrrrrm
VB  verb, base form take
VBD verb, past tense    took
VBG verb, gerund/present participle taking
VBN verb, past participle   taken
VBP verb, sing. present, non-3d take
VBZ verb, 3rd person sing. present  takes
WDT wh-determiner   which
WP  wh-pronoun  who, what
WP$ possessive wh-pronoun   whose
WRB wh-abverb   where, when

-----------------------------------------
WordNet has those simplified pos tags:

n    NOUN 
v    VERB 
a    ADJECTIVE 
s    ADJECTIVE SATELLITE 
r    ADVERB 
'''
