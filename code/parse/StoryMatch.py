"""StoryMatch.py: Input 2 stories. Output similarity (percentage of
intersection)."""

from pycorenlp import StanfordCoreNLP
import itertools
import copy


__author__ = "ZHOU, JINGRAN"

# Given story
STORY0 = ["Alice likes Bob.",
          "Alice sends a gift to Bob.",
          "Bob is happy.",
          "Bob invites Alice for dinner."]
# Natural (1)
STORY1 = ["John likes Mary.",
          "John sends a gift to Mary.",
          "Mary is happy.",
          "Mary invites John for dinner."]
# Natural but not 100% sure (0.666667)
STORY2 = ["John likes Mary.",
          "John sends a gift to Mary."]
# Natural but not 100% sure (0.666667)
STORY3 = ["Mary is happy.",
          "Mary invites John for dinner."]
# Strange (0.25)
STORY4 = ["John likes Mary.",
          "Mary sends a gift to John.",
          "Mary is happy.",
          "Mary invites John for dinner."]
# Strange (0.25)
STORY5 = ["John likes Mary.",
          "Mary sends a gift to Mary.",
          "John is happy.",
          "Mary invites John for dinner."]

NLP = StanfordCoreNLP('http://localhost:9000')
NLP_NER_PROPERTIES = {'annotators': 'ner',
                      'outputFormat': 'json'}
NLP_DEP_PARSE_PROPERTIES = {'annotators': 'depparse',
                            'outputFormat': 'json'}

NATURAL_THRESHOLD = 0.8335
DOUBTFUL_NATURAL_THRESHOLD = 0.4583


def get_story_ner(story_list):
    story_str = " ".join(story_list)
    return NLP.annotate(story_str, properties=NLP_NER_PROPERTIES)


def get_sentence_dep_parse(sentence):
    return NLP.annotate(sentence, properties=NLP_DEP_PARSE_PROPERTIES)


def get_named_entities(story_ner):
    """
    Get all named entities in a story.
    :param story_ner: raw NER output of a story.
    :return: a list of unique named entities where each unique entity is a
    dictionary containing its text and type.
    """
    named_entities = []
    sentence_list = story_ner['sentences']
    for sentence in sentence_list:
        entity_mentions = sentence['entitymentions']
        for named_entity in entity_mentions:
            entity = dict((k, named_entity[k]) for k in ['text', 'ner'])
            if entity not in named_entities:
                named_entities.append(entity)
    return named_entities


def number_named_entities(named_entities):
    """
    Assign numbers to named entities by type.
    :param named_entities: a list of named entities (each as a dictionary)
    :return: a list of named entities with numbered types
    """
    ne_list = [d['ner'] for d in named_entities]
    ne_count = dict((ner, 0) for ner in ne_list)
    for entity in named_entities:
        entity_type = entity['ner']
        entity['ner'] += str(ne_count[entity_type])
        ne_count[entity_type] += 1
    return named_entities


def get_all_permutations(input_list):
    """
    Get all possible permutations of a list
    :param input_list: a list
    (each as a dictionary).
    :return: a list of all the possible permutations of the input list.
    """
    permutation_list = list(itertools.permutations(input_list))
    result = list(map(lambda x: list(x), permutation_list))
    return result


def get_root_word(dependencies):
    for dep in dependencies:
        if dep['dep'] == 'ROOT':
            return dep['dependentGloss']
    return None


def get_top_level_dep(dependencies, root_word):
    top_level_dep_list = []
    for dep in dependencies:
        if dep['governorGloss'] == root_word:
            top_dep = dict((k, dep[k]) for k in ['dep', 'dependentGloss'])
            top_level_dep_list.append(top_dep)
    return top_level_dep_list


def is_sentences_similar(sentence0, sentence1):
    sentence0_dep = \
        get_sentence_dep_parse(sentence0)['sentences'][0]['basicDependencies']
    sentence1_dep = \
        get_sentence_dep_parse(sentence1)['sentences'][0]['basicDependencies']

    # Check if ROOT words are similar
    sentence0_root_word = get_root_word(sentence0_dep)
    sentence1_root_word = get_root_word(sentence1_dep)
    if sentence0_root_word == sentence1_root_word:
        # Finds every dependency with ROOT word as governor for both sentences
        sentence0_top_dep_list = get_top_level_dep(sentence0_dep,
                                                    sentence0_root_word)
        sentence1_top_dep_list = get_top_level_dep(sentence1_dep,
                                                    sentence1_root_word)
        # Check if all types of top level dependencies are the same
        sentence0_dep_type = set([d['dep'] for d in sentence0_top_dep_list])
        sentence1_dep_type = set([d['dep'] for d in sentence1_top_dep_list])
        if sentence0_dep_type == sentence1_dep_type:
            # Check if all dependents are similar
            for dep_type in sentence0_dep_type:
                sentence0_dep_gloss = next(
                    (item for item in sentence0_top_dep_list if
                     item["dep"] == dep_type))
                sentence1_dep_gloss = next(
                    (item for item in sentence1_top_dep_list if
                     item["dep"] == dep_type))
                if sentence0_dep_gloss != sentence1_dep_gloss:
                    return False
            return True
    return False


def generate_meta_story(original_story, numbered_entities):
    """
    Generate a "meta story" by replacing named entities in the original story
    with numbered entities.
    :param original_story: a list of sentences.
    :param numbered_entities: a list of dictionaries where each entry has an
    original piece of text and a numbered type.
    :return: a list of sentences.
    """
    meta_story = []
    for sentence in original_story:
        for numbered_entity in numbered_entities:
            sentence = sentence.replace(numbered_entity['text'],
                                        numbered_entity['ner'])
        meta_story.append(sentence)
    return meta_story


def get_one_meta_story(raw_story_list):
    ner_raw = get_story_ner(raw_story_list)
    named_entities = get_named_entities(ner_raw)
    numbered_entities = number_named_entities(named_entities)
    return generate_meta_story(raw_story_list, numbered_entities)


def get_all_meta_stories(raw_story_list):
    all_meta_stories = []
    ner_raw = get_story_ner(raw_story_list)
    named_entities = get_named_entities(ner_raw)
    all_named_entities = get_all_permutations(named_entities)
    for ne in all_named_entities:
        # MUST MAKE SURE IT'S A DEEP COPY!!! -- Jerome
        numbered_entities = number_named_entities(copy.deepcopy(ne))
        meta_story = generate_meta_story(raw_story_list, numbered_entities)
        all_meta_stories.append(meta_story)
    return all_meta_stories


def get_longest_match(story0, story1):
    meta_story0 = get_one_meta_story(story0)
    meta_story1_list = get_all_meta_stories(story1)
    return max(
        [get_similar_sentence_pairs(meta_story0, meta_story1) for meta_story1
         in meta_story1_list])


def get_similar_sentence_pairs(meta_story0, meta_story1):
    similar_sentence_pairs = []
    for idx0, story0_sentence in enumerate(meta_story0):
        for idx1, story1_sentence in enumerate(meta_story1):
            if is_sentences_similar(story0_sentence, story1_sentence):
                similar_sentence_pairs.append((idx0, idx1))
    return similar_sentence_pairs


def calc_similarity_score(story0_list, story1_list, longest_match):
    numerator = len(longest_match) * 2
    denominator = len(story0_list) + len(story1_list)
    return numerator/denominator


def judge_story(similarity_score):
    if similarity_score > NATURAL_THRESHOLD:
        return "Natural."
    elif similarity_score > DOUBTFUL_NATURAL_THRESHOLD:
        return "Natural (but not 100% sure)."
    else:
        return "Strange."


if __name__ == "__main__":
    # Modify here
    given_story = STORY0
    query_story = STORY1

    print("[Given]\n" + "\n".join(given_story) + "\n")
    print("[Query]\n" + "\n".join(query_story) + "\n")

    similar_sentences = get_longest_match(given_story, query_story)
    print("----- Similar Sentence Pairs -----")
    for pair in similar_sentences:
        print("\n%s\n%s\n" % (given_story[pair[0]], query_story[pair[1]]))
    score = calc_similarity_score(given_story, query_story, similar_sentences)
    print("----- Diagnosis -----")
    print("==> Similarity Score = %f" % score)
    print("==> Verdict = %s" % judge_story(score))
