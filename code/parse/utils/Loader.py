import json
import re
from utils.Constants import *


def get_content(file):
    with open(file, 'r') as f:
        return [line.strip() for line in f
                if line.strip() and line[:len(COMMENT)] != COMMENT]


def load_story(file, json_save=''):
    content = get_content(file)
    data = parse_content(content)
    if json_save:
        with open(json_save, 'w') as f:
            json.dump(data, f)

    return data


def detect(content, ix, line, length, patt):
    titl = line[len(patt):-2]
    detected = [titl, []]
    for det_i in range(ix + 1, length):
        det_line = content[det_i]
        if det_line == END_SENT:
            break
        else:
            detected[-1].append(det_line)
    return detected


def get_rules(line):
    rule = ["type", "statement"]
    for rule_type, rule_exp in RULE_PATT.items():
        if re.match(rule_exp, line):
            rule = [rule_type, line]
            return rule


def parse_content(content):
    patt_c = CONCEPT_START[:-2]
    patt_h = HISTORY_START[:-2]
    patt_s = STORY_START[:-2]

    length = len(content)
    concepts = []
    history = []
    story = []

    assert content[0] == EXPERIMENT_START

    for ix, line in enumerate(content):

        if line[:len(patt_c)] == patt_c:
            elem = detect(content, ix, line, length, patt_c)
            concepts.append(elem)
        elif line[:len(patt_h)] == patt_h:
            elem = detect(content, ix, line, length, patt_h)
            history.append(elem)
        elif line[:len(patt_s)] == patt_s:
            elem = detect(content, ix, line, length, patt_s)
            story.append(elem)

    return {"concepts": concepts,
            "history": history,
            "story": story
            }


if __name__ == "__main__":
    load_story('../../../data/attribu_story/1_fail.story')
