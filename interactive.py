import daifugo.game as game
import daifugo.sandbox as sandbox

game.DEBUG = True

players = [
  sandbox.as_module(open('players/interactive.py'))[0],
  sandbox.as_module(open('players/some_call_me'))[0],
  sandbox.as_module(open('players/mlui.py'))[0],
  sandbox.as_module(open('players/mlui_cost.py'))[0],
  ]

game.play_game([p.play for p in players])
