"""
Tournament playing system. Takes as input a list of paths to
player agents on stdin and and an output file path. Randomly 
selects 4 players to play, and appends the result to the file. 
Does this a set number of times.  

Note that each game uses the exact same deck! This is to 
control for the effect of the deck in player comparisons.

Writes 5-tuples: p1, p2, p3, p4, winner.

Marco Lui, May 2012
"""

from optparse import OptionParser
import sys,os
import random
import copy

import daifugo.sandbox as sandbox
import daifugo.game as game

if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option('-o','--output',help='output to FILE', metavar='FILE')
  parser.add_option('-i','--input',help='read from FILE instead of stdin', metavar='FILE')
  parser.add_option('-n','--numiter',help='number of games', type=int, default=1000)
  parser.add_option('-s','--seed',help='seed for deck shuffling',default='daifugo')

  opts, args = parser.parse_args()

  if not opts.output:
    parser.error("Output directory must be specified")

  all_players = {}
  for i,path in enumerate(open(opts.input) if opts.input else sys.stdin):
    path = path.strip()
    with open(path) as f:
      all_players[i] = sandbox.as_module(f)[0]

  output = open(opts.output, 'a') if opts.output else sys.stdout
  
  random.seed(opts.seed)
  deck = game.deal()

  for i in xrange(opts.numiter):
    players = random.sample(all_players, 4)
    try:
      with sandbox.redirect_stdout(open('/dev/null','w')):
        game_trace = game.play_game([all_players[p].play for p in players], 'pass', initial_deal=deck)
      output.write(','.join(map(str,players)+[str(game_trace[0][-1])]) + '\n')
    except Exception, e:
      pass
        
       


