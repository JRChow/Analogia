from collections import OrderedDict
import re

WORD_IX_SEP = '+'
PERSON = ['Alice', 'Bob', 'Cathy', 'David']
NER_PER = 'PERSON'
POS_VER = 'VB'


EXPERIMENT_START = 'Start experiment.'

CONCEPT_START = 'Start description of "".'

HISTORY_START = 'Start history titled "".'

STORY_START = 'Start story titled "".'

COMMENT = '// '

END_SENT = 'The end.'

RULE_PATT = OrderedDict({
    "explanation": "^If .*, then .* may .*\.",
    "presumption": "^If .*, then .* can be .*\.",
    "abduction": "^If .*, then .* must be .*\.",
    "prediction": "^If .*, then .*\.",
    "enablement": ".* enables .*\."})
RULE_SEPA = OrderedDict({
    "explanation": "^If |, then |",
    "presumption": "^If |, then |",
    "abduction": "^If |, then |",
    "prediction": "^If |, then |",
    "enablement": "\."})
RULE_PATT = {key: re.compile(val) for key, val in RULE_PATT.items()}


# formatting
class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    # print (color.BOLD + 'Hello World !' + color.END)
