"""
This is the playground access point for students.
It allows students to upload a player script, which we
then run against other players.

The work is split into two main portions. The first part
is allowing a player to 

TODO: Limit file size
TODO: Allow players to choose opponents
TODO: Maintain player stats
"""
import cgi
import cgitb; cgitb.enable(format='text')
import os, sys, imp
import copy
import random, time
random.seed(time.time())
from itertools import cycle

import daifugo.game as game
import daifugo.sandbox as sandbox
from common import lists2ul, hand2html, PLAYERS_DIR
import logging
logger = logging.getLogger(__name__)
FORMAT = "%(asctime)-15s %(forwarded_for)s  %(message)s"    
env_info = dict(remote_addr=cgi.escape(os.environ["REMOTE_ADDR"]), forwarded_for=cgi.escape(os.environ["HTTP_X_FORWARDED_FOR"]))
logging.basicConfig(filename='play.py.log', level=logging.INFO, format=FORMAT,)

HTML_TEMPLATE = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html><head>
<title>COMP10001 Daifugo Playground</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
</head>
<body><h1>COMP10001 Daifugo Playground</h1>
{body}
</body>
</html>"""

PLAYER_SELECT_AREA="""
<form action="{script_name}" method="POST">
<table>
<tr>
<td>Player 1</td>
<td>Player 2</td>
<td>Player 3</td>
<td>Player 4</td>
</tr>
<tr>
<td>{select1}</td>
<td>{select2}</td>
<td>{select3}</td>
<td>{select4}</td>
</tr>
<tr>
<td>
<input name="submit" type="submit" value="Play!"/>
</td>
</tr>
</table>
</form>
"""

SELECT_TEMPLATE="""
<select name="{name}">
{options}
</select>
"""

OPTION_TEMPLATE="<option>{0}</option>"
OPTION_S_TEMPLATE="<option selected>{0}</option>"

def player_count():
    return len(os.listdir(PLAYERS_DIR))

def display_page(body):
    print 'Content-Type: text/html'
    print
    print HTML_TEMPLATE.format(body=body)

def generate_select(name, options, selected = None):
    opt_html = []
    for o in options:
        v = (OPTION_S_TEMPLATE if o == selected else OPTION_TEMPLATE).format(o)
        opt_html.append(v)

    retval = SELECT_TEMPLATE.format(name=name, options="\n".join(opt_html))
    return retval
           
    
template_values = {}
template_values['script_name'] = os.environ['SCRIPT_NAME']
template_values['player_count'] = len(os.listdir(PLAYERS_DIR))

body = ''
body += 'We currently have {player_count} players.<br/>'.format(**template_values)



form = cgi.FieldStorage()
player_choices = sorted(os.listdir(PLAYERS_DIR))
chosen = []
for key in ['player1','player2','player3','player4']:
    if form.has_key(key) and form[key].value in player_choices:
        chosen.append(form[key].value)
    else:
        chosen.append(random.choice(player_choices))
play_paths = [os.path.join(PLAYERS_DIR,p) for p in chosen]

d = dict(template_values)
d['select1'] = generate_select('player1', player_choices, chosen[0])
d['select2'] = generate_select('player2', player_choices, chosen[1])
d['select3'] = generate_select('player3', player_choices, chosen[2])
d['select4'] = generate_select('player4', player_choices, chosen[3])
body += PLAYER_SELECT_AREA.format(**d)

# actually run the game simulation
try:
    game_trace = sandbox.complete_game(play_paths)
    body += "<p>Winner: {0}</p>".format(chosen[game_trace[0][-1]])
    round_count = 0
    prev_winner = 0

    for winner, round, hands in zip(*game_trace):
        round_count += 1
        play_names = cycle(chosen[(i+prev_winner)%4] for i in xrange(4))
    
        body += lists2ul(['HANDS', ["{0}({2}): {1}".format(p,str(sorted(h)),len(h)) for p,h in zip(chosen,hands)]])
        body += lists2ul(['ROUND {0}'.format(round_count),["{0}: {1}".format(*x) for x in zip(play_names,round)]])
        body += lists2ul(['WINNER', [chosen[winner]]])
        prev_winner = winner
    logger.info('players: {0} winner {1}'.format(chosen, chosen[winner]), extra=env_info)

except game.InvalidAction,e :
    body += "<p>Invalid Action: {0}</p>".format(e)
    body += "<p>Please remain calm. This incident has been logged.</p>"
    logger.info('InvalidAction: {1} players:{0}'.format(chosen, str(e)), extra=env_info)
    
except Exception, e:
    body += "<p>Exception Occurred:</p>"
    body += "<p>{0}: {1}</p>".format(e.__class__.__name__, str(e))
    body += "<p>Please remain calm. This incident has been logged.</p>"
    logger.info('{0}: {1} players:{2}'.format(e.__class__.__name__, str(e), chosen), extra=env_info)

    
#body += str(map(len,game_trace))+'<br/>'
#body += lists2ul(game_trace)

 
                    
display_page(body)


