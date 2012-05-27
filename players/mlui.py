"""
Sample solution for project 3.
"""
from collections import defaultdict
from itertools import combinations
import random

def cards_by_index(cardset, index):
  """
  Organize cards by rank (index 0) or suit (index 1)
  """
  retval = defaultdict(list)
  for card in cardset:
    rank = card[index]
    retval[rank].append(card)
  return retval

def card_value(card):
  """
  Return an index value that can be used for comparing cards
  """
  ranks = '34567890JQKA2'
  return ranks.index(card[0])

def straights(cards):
  """
  Generate all possible staights from a group of cards
  """
  cards = sorted(cards, key=card_value)
  num_cards = len(cards)
  retval = []
  for i in range(3,6): # straights of len 3 to 5
    if num_cards < i:
      # Can't have a straight of length i or more: not enough cards
      break 
    for j in range(num_cards-i+1):
      # We check that the difference in values is the same as the
      # length of the straight. NB this only works if cards are unique
      gap = card_value(cards[j+i-1]) - card_value(cards[j]) + 1
      if gap == i:
        retval.append(cards[j:j+i])
  return retval

def generate_plays(hand):
  ranked = cards_by_index(hand,0)
  plays = []
  # Generate rank combinations
  for rank in ranked:
    cards = ranked[rank]
    for n in range(1,5):
      plays.extend(combinations(cards, n))
  # Generate straights
  suited = cards_by_index(hand,1)
  for suit in suited:
    plays.extend(straights(suited[suit]))
  retval = [list(p) for p in plays]
  return retval

def is_valid_play(prev, play, debug=False):
  if card_value(prev[0]) != card_value(prev[-1]):
    # Previous play is a straight
    s = straights(play)
    if len(s) == 0:
      # Proposed play is not a straight
      if debug: print "INVALID: {0} is not a straight".format(play)
      return False
    if card_value(max(prev, key=card_value)) >= card_value(max(play, key=card_value)):
      # Proposed play does not have a higher max card
      if debug: 
        print "INVALID: {0} does not have higher max card".format(play)
        print "prev:{0} play:{1}".format(max(prev, key=card_value), max(play, key=card_value))
      return False
    else:
      return True
  else:
    # Previous play is a rankset
    if len(play) != len(prev):
      # Wrong number of cards
      if debug: print "INVALID: {0} has wrong number of cards".format(play)
      return False
    elif len(set(p[0] for p in play)) != 1:
      # Proposed play has cards of mixed rank
      if debug: print "INVALID: {0} of mixed rank".format(play)
      return False
    elif card_value(play[0]) <= card_value(prev[0]):
      # Proposed play is not worth more than prev
      if debug: print "INVALID: {0} not worth more".format(play)
      return False
    else:
      return True

def get_valid_plays(prev, hand, generate=generate_plays, is_valid=is_valid_play):
  retval = [ p for p in generate(hand) if is_valid(prev, p) ]
  return retval

def long_low(play):
  score = len(play) * 13
  top_card = max(play, key=card_value)
  score += 12-card_value(top_card)
  return score

def endgame(play):
  score = len(play) * 13
  if len(play) == 1:
    score += card_value(play[0])
  else:
    top_card = max(play, key=card_value)
    score += 12-card_value(top_card)
  return score
  
def play(prev, hand, discard, holding, valid=get_valid_plays, generate=generate_plays, is_valid=is_valid_play):
  try:
    if len(discard[-1]) >= 3 and all(p is None for p in discard[-1][-3:]):
      # Pass if all 3 passed, to gain control of the game
      return None
  except IndexError:
    pass

  if prev is None:
    plays = generate_plays(hand)
  else:
    if len(prev) == 1:
      # single card played
      # compute all the single cards not in hands longer than 1
      singles = set(hand) - reduce(set.union, (set(x) for x in valid(prev,hand) if len(x) > 1), set())
      if singles:
        #if we have any
        plays = [ [c] for c in singles if card_value(c) > card_value(prev[0])]
    else:
      plays = valid(prev, hand)

  if (card_value(min(hand, key=card_value)) > card_value('8')) or any(h < 3 for h in holding):
    # endgame behaviour
    try:
      return max(plays, key=endgame)
    except ValueError:
      return None

  try:
    return max(plays, key=long_low)
  except ValueError:
    return None
