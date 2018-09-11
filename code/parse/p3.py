from collections import OrderedDict
perman_pairs = OrderedDict([(" once ", " always "),
                            (" one ", " all ")])
pos_words = ["good", "well"]


def perman(sent):
    for temp, perm in perman_pairs.items():
        if temp in sent:
            pred = sent.replace(temp, perm)
            return pred
    return None


def persona_neg(sent, good_sent=True):
    good_sent = sum(1 for word in pos_words if word in sent) > 0
    pred = None
    if good_sent:
        if " against " in sent:
            other = sent.split(" against ")[1][:-1]
            pred = "{} is too weak.".format(other)

        elif " according to " in sent:
            other = sent.split(" according to ")[1][:-1]
            pred = "{} is pretending.".format(other)
        elif " together with " in sent:
            other = sent.split(" together with ")[1][:-1]
            pred = "{} made the most contribution.".format(other)
    else:
        if " against " in sent:
            other = sent.split(" against ")[1][:-1]
            pred = "I am too weak.".format(other)

        elif " according to " in sent:
            opinion = sent.split(" according to ")[0]
            pred = opinion
        elif " together with " in sent:
            other = sent.split(" together with ")[1][:-1]
            pred = "I made the most mistakes."

    return pred


def test():
    sent = 'I did well in the competition against other students.'
    sent = 'I did badly in the competition against other students.'
    sent = 'I did a good job according to my manager.'
    sent = 'I did a bad job according to my manager.'
    sent = 'I did well in a project together with colleagues.'
    sent = 'I did badly in a project together with colleagues.'

    sent = 'I once did well in the test.'
    sent = 'My parents once had a fight.'
    sent = 'My mom once scolded me.'
    sent = 'I once spilled the milk.'

    if perman(sent):
        pred = perman(sent)
    elif persona_neg(sent):
        pred = persona_neg(sent)
    print(pred)


if __name__ == "__main__":
    test()
