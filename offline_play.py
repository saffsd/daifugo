"""
Play an offline game using four instances of a single player
agent, and report win statistics from each position.

Marco Lui, May 2012
"""

from collections import defaultdict
import sys
import daifugo.game as game
from daifugo.sandbox import as_module
from optparse import OptionParser

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-i','--input',help='Read player from FILE', metavar='FILE')
    parser.add_option('-n','--niter',help='Number of iterations', type=int, default=100)
    parser.add_option('-t','--trace',help='Show game trace', action='store_true', default=False)
    opts, args = parse.parse_args()

    game.DEBUG = opts.trace

    if not opts.input:
      parser.error("must specify input file")

    with open(opts.input) as f:
      module, _ = as_module(f)
    p1 = module.play
    p2 = module.play
    p3 = module.play
    p4 = module.play

    win_count = defaultdict(int)
    players=(p1,p2,p3,p4)
    for i in range(opts.niter):
        print i
        winner, _, _ = game.play_game(players)
        win_count[winner[-1]] += 1
    print win_count
    
