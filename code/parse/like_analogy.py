"""like_analogy.py: Given that "I like hamburgers." and "I like hot dogs.",
should answer "Yes." to query "I like fries." and "Not sure." to
"I like apples.".
"""

from nltk.corpus import wordnet as wn
from pycorenlp import StanfordCoreNLP
from pprint import pprint

__author__ = "ZHOU, JINGRAN"

NLP = StanfordCoreNLP('http://localhost:9000')
NLP_ANNOTATE_PROPERTIES = {'annotators': 'openie',
                           'outputFormat': 'json'}


def extract_object_from(sentence):
    annotate_output = NLP.annotate(sentence,
                                   properties=NLP_ANNOTATE_PROPERTIES)
    return annotate_output['sentences'][0]['openie'][0]['object']


class LikeAnalogyModel:
    def __init__(self, train_example):
        self.train_example = train_example
        self.lowest_common_hypernyms = None
        self.train()

    def train(self):
        print("Training...")
        object_list = []

        # Extract objects
        print("Looking for objects...")
        for example in self.train_example:
            obj = extract_object_from(example)
            object_list.append(obj)

        # Find lowest common hypernym
        pprint(object_list)
        synset0 = wn.synsets(object_list[0])[0]
        synset1 = wn.synsets(object_list[1])[0]
        self.lowest_common_hypernyms = \
            synset0.lowest_common_hypernyms(synset1)[0]
        print("Found lowest common hypernym -> %s" %
              self.lowest_common_hypernyms)

    def process_query(self, query):
        # Extract object
        print("Extracting object from query...")
        query_obj = extract_object_from(query)
        query_synset = wn.synsets(query_obj)[0]
        if query_synset in self.lowest_common_hypernyms.hyponyms():
            return 'Yes.'
        else:
            return 'Not sure.'


if __name__ == "__main__":
    train_set = ["I like dogs.", "I like foxes."]
    model = LikeAnalogyModel(train_set)

    while True:
        query = input("\nPlease input query:\n=> ")  # Take input
        answer = model.process_query(query)  # Query model
        print(answer)
