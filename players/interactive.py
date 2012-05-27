"""
Interactive player.
"""
import daifugo.common as common
import sys
from collections import defaultdict

def play(prev, hand, discard, holding, valid=None, generate=None, is_valid=None):
  if prev is None:
    plays = generate(hand)
  else:
    plays = valid(prev,hand)

  # Just pass straight away if we dont actually have a choice
  if not plays:
    return None

  plays.sort(key=lambda p: (len(p), max(map(common.card_value,p))))
  print "PLAYS", plays

  discard_summary = defaultdict(list)
  for round in discard:
    for play in round:
      if play is not None:
        for card in play:
          discard_summary[card[1]].append(card)

  if discard_summary:
    print "    Discard Summary:"
    for suit in sorted(discard_summary):
      cards = sorted(discard_summary[suit], key=common.card_value)
      ranks = [c[0] for c in cards]
      disp = ''.join( c if c in ranks else ' ' for c in common.RANKS)
      print "      {0}: {1}".format(suit, disp)

  print "    Hand: {0}".format(sorted(hand, key=common.card_value))
  if prev is not None:
    print "    Prev: {0}".format(sorted(prev, key=common.card_value))
  print "    [0] Pass"
  for i, play in enumerate(plays):
    print "    [{0}] {1}".format(i+1, play)

  try:
    c = input("    CHOICE: ")
  except KeyboardInterrupt:
    sys.exit(0)


  if c == 0:
    return None
  else:
    return plays[c-1]
