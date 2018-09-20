from pprint import pprint
from pycorenlp import StanfordCoreNLP
from wordnet import *
from SentMatch import struc_match

from efficiency.log import show_var
import pdb


# text = (
#     'I am healthy.')
# output = nlp.annotate(text, properties={
#     'annotators': 'depparse',
#     'outputFormat': 'json'
# })
# pprint(output['sentences'][0]['enhancedDependencies'])

# text = (
#     'I did well in something.'
# )
# output = nlp.annotate(text, properties={
#     'annotators': 'depparse',
#     'outputFormat': 'json'
# })
# pprint(output['sentences'][0]['enhancedDependencies'])


def parse_sent(sent, nlp, annot='depparse,ner'):
    # -annotators tokenize, ssplit, pos, lemma, ner, depparse, coref, natlog, openie
    output = nlp.annotate(sent, properties={
        'annotators': annot,
        'outputFormat': 'json'
    })
    # -annotators tokenize, ssplit, pos, lemma, ner, depparse, coref, natlog, openie

    return output['sentences'][0]


def compare(sent_model, sent_query, nlp):
    model = parse_sent(sent_model, nlp)['enhancedDependencies']
    query = parse_sent(sent_query, nlp)['enhancedDependencies']
    return struc_match(model, query)


def test():

    nlp = StanfordCoreNLP('http://localhost:9000')

    sent = (
        'I am healthy. '
        'I am healthier than others.')
    pprint(parse_sent(sent, nlp))

    sent = [
        'I won something.',
        'I won a game.']
    matched = compare(sent[0], sent[1], nlp)
    show_var(["matched"])

    sent = [
        'I did well in something.',
        'I did well in a test.']
    matched = compare(sent[0], sent[1], nlp)
    show_var(["matched"])


if __name__ == "__main__":
    test()
