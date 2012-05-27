"""
Compute statistics for the tournament.

Marco Lui, May 2012
"""
import os, sys
import csv
from optparse import OptionParser
from collections import defaultdict

if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option("-i","--input")
  opts, args = parser.parse_args()

  if not opts.input or not os.path.isdir(opts.input):
    parser.error("Must supply an input directory")

  playcount = defaultdict(int)
  wincount = defaultdict(int)

  for path in os.listdir(opts.input):
    with open(os.path.join(opts.input, path)) as f:
      reader = csv.reader(f)
      for row in reader:
        try:
          players = row[:4]
          winner = players[int(row[4])]
          for player in players:
            playcount[player] += 1
          wincount[winner] += 1
        except IndexError:
          import pdb;pdb.post_mortem()

  for key in sorted(playcount, key=wincount.get):
    played = playcount[key]
    won = wincount[key]

    print "Player {0}: {1}/{2} ({3:.1f}%)".format(key, won, played, float(won)/played*100)




