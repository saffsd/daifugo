PLAYERS_DIR = "./players"

def lists2ul(seq):
    retval = '<ul>'
    count = 0
    for s in seq:
        if isinstance(s, list):
            retval += lists2ul(s)
        else:
            retval += '<li>{0}</li>'.format(s)
        count += 1
    if count==0:
        retval += '<li>&nbsp;</li>'
    retval += '</ul>'
    return retval

def hand2html(hand):
    return sorted(hand)

