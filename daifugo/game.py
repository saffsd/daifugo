"""
Daifugo player backend.
"""
import random
import copy
from itertools import product, cycle
#random.seed("COMP10001")
import time
random.seed(time.time())
import cgi
DEBUG=False
import common



def get_deck(shuffle=False):
    suits = 'CSDH'
    ranks = '34567890JQKA2'
    deck = [''.join(c) for c in product(ranks, suits)]
    if shuffle:
        random.shuffle(deck)
    return deck

def deal(players=4):
    deck = get_deck(shuffle=True)
    hands = tuple(set() for i in xrange(players))
    players = cycle(hands)
    for card in deck:
        player = players.next()
        player.add(card)
    return hands

class InvalidAction(Exception): 
    def __init__(self, reason, call):
        self.reason = reason
        self.call = call
    
    def __str__(self):
        return self.reason
    

def play_round(hands, players, discard=None, first_player=0, invalid_action='pass'):
    """
    Execute simulation of one round of gameplay.
    """
    if invalid_action not in ['pass', 'raise']:
        raise ValueError, "invalid_action cannot be '{0}'".format(invalid_action)
    num_players = len(players)
    assert len(hands) == num_players
    
    prev = None #last hand played
    if discard is None:
        # First round played
        discard = [[]]
    else:
        # add an empty list representing the start of a new round
        discard.append([])
    indices = range(num_players)
    pass_count = 0
    last_player=first_player
    index = first_player

    while True:
        player = players[index]
        hand = hands[index]
        holding = tuple(len(hands[(index+i)%num_players]) for i in range(1,num_players))
        args = [copy.deepcopy(prev), list(hand), copy.deepcopy(discard), holding]
        kwargs = dict(valid=common.get_valid_plays, generate=common.generate_plays, 
            is_valid=common.is_valid_play)
        call_str = "play({args[0]},{args[1]},{args[2]},{args[3]})".format(args=args)
        try:
            # TODO: Suppress stdout
            # TODO: impose timelimit
            play = player(*args, **kwargs)
               
        except Exception, e:
            if DEBUG: print "  {0} failed with exception: '{1}'".format(index, e)
            if invalid_action == 'pass':
                play = None
            elif invalid_action == 'raise':
                raise InvalidAction("player {0} raised {1}: '{2}'".format(index, cgi.escape(e.__class__.__name__), e), call_str)

        if DEBUG: 
          if play is None:
            print "  {0} ({2} cards) --> {1}".format(index, "pass", len(hands[index]))
          else:
            print "  {0} ({2} cards) --> {1}".format(index, play, len(hands[index])-len(play))

        # need to check a play is a valid play
        if play and frozenset(play) not in map(frozenset,common.generate_plays(hand)):
            if DEBUG: 
                print "  {0} invalid play {1}".format(index, play)
            # Force player to pass if their play is invalid
            if invalid_action=='pass':
                play = None
            elif invalid_action =='raise':
                raise InvalidAction("player {0} attempted invalid play {1}".format(index, play), call_str)
        
        if prev is None:
            if play is None:
                if DEBUG: 
                    print "  {0} passed as first player".format(index)
                if invalid_action=='pass':
                    play = None
                elif invalid_action =='raise':
                    raise InvalidAction("player {0} passed as first player".format(index), call_str)
            
        else:
            # need to check a play is valid in the context of the previous play
            if not common.is_valid_play(prev, play):
                if DEBUG: 
                    print "  {0} invalid play {1} -> {2}".format(index, prev, play)
                # Force player to pass if their play is invalid
                if invalid_action=='pass':
                    play = None
                elif invalid_action =='raise':
                    raise InvalidAction("player {0} attempted invalid play {1} -> {2}".format(index, prev, play), call_str)
        
        discard[-1].append(play)
        if play is None:
            pass_count += 1
        else:      
            hand -= set(play)
            prev = play
            pass_count = 0
            last_player = index

        # Assess end of round
        if len(hands[index]) == 0:
            if DEBUG: print "ROUND OVER: Player {0} wins".format(index)
            return hands, last_player, True, discard
        elif pass_count == num_players:
            if DEBUG: print "ROUND OVER: All passed - LP {0}".format(last_player)
            return hands, last_player, False, discard
        elif prev is not None and prev[-1][0] == '2':
            if DEBUG: print "ROUND OVER: 2 played - LP {0}".format(last_player)
            return hands, last_player, False, discard
        index = (index+1) % num_players

def play_game(players, invalid_action='raise', initial_deal=None):
    assert all(callable(p) for p in players)
    lp_hist = []
    hands_hist = []
    if initial_deal is None:
      initial_deal = deal()
    else:
      initial_deal = copy.deepcopy(initial_deal)

    hands_hist.append(copy.deepcopy(initial_deal))
    hands, lp, game_over, discard = play_round(initial_deal, players)
    hands_hist.append(copy.deepcopy(hands))
    lp_hist.append(lp)
    while not game_over:
        hands, lp, game_over, discard = play_round(hands, players, discard, lp)
        hands_hist.append(copy.deepcopy(hands))
        lp_hist.append(lp)
    return lp_hist, discard, hands_hist


