"""
Compute tournament ranking based on TrueSkill
given the tournament output

Marco Lui, May 2012
"""
import sys
import trueskill
import shelve
import csv
from optparse import OptionParser
from contextlib import closing
from collections import defaultdict

trueskill.SetParameters(draw_probability=0.00001, gamma=0.00001)

class Player(object): 
  def __init__(self):
    self.skill = (25.0, 25.0/3.0)


if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option("-i","--input")
  parser.add_option("-s","--shelf")
  opts, args = parser.parse_args()

  player_index = defaultdict(Player)

  if opts.shelf:
    with closing(shelve.open(opts.shelf)) as p:
        player_index.update(p)

  if opts.input:
    with open(opts.input) as f:
      reader = csv.reader(f)
      for row in reader:
        winner = int(row[4])
        p_objs = []
        for i,p in enumerate(row[:4]):
          p_obj = player_index[p]
          p_obj.rank = 1 if i == winner else 2
          p_objs.append(p_obj)
        trueskill.AdjustPlayers(p_objs)

    if opts.shelf: 
      with closing(shelve.open(opts.shelf)) as p:
          p.update(player_index)

  for p in sorted(player_index, key=lambda l:player_index[l].skill, reverse=True):
    pl = player_index[p]
    print "{0}: mu={1[0]:.3f} sigma={1[1]:.3f}".format(p, pl.skill)

