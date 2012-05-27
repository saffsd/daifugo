"""
Display the current ranking of players.
"""
import re
import os
import trueskill
from collections import defaultdict
from filelock import FileLock
from itertools import islice
import shelve
from contextlib import closing

class Player(object): 
    def __init__(self):
        self.skill = (25.0, 25.0/3.0)

P_LC = '.rankings_linecount'
P_LOCK = '.rankings_lock'
P_ESTIM = '.rankings_players'

def reset():
    for p in [P_LC, P_LOCK, P_ESTIM]:
        if os.path.isfile(p):
            os.unlink(p)
#reset();raise ValueError

BATCH_SIZE=500
CGI_HEADER = """Content-Type: text/html

"""

PAGE_TEMPLATE="""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html><head>
<title>COMP10001 Daifugo Playground Rankings</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
</head>
<body><h1>COMP10001 Daifugo Playground Rankings</h1>
{body}
</body>
</html>"""

RE_LOGLINE=re.compile("\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} (\d|\.)+  players: \['(?P<player1>\w+)', '(?P<player2>\w+)', '(?P<player3>\w+)', '(?P<player4>\w+)'\] winner (?P<winner>\w+)")
play_log = 'play.py.log'


        
player_index = defaultdict(Player)

with FileLock(P_LOCK, timeout=1):
    if not os.path.isfile(P_LC):
        with open(P_LC,'w') as f:
            f.write('0')
    with closing(shelve.open(P_ESTIM)) as p:
        player_index.update(p)
    with open(P_LC) as f:
        line_count = int(f.read())
    with open(play_log) as f:
        history = islice(f, line_count, line_count+BATCH_SIZE)
                         
        i = 0
        for row in history:
            i += 1
            m = RE_LOGLINE.match(row)
            if m:
                winner = m.group('winner')
                players= []
                for p_name in ['player1','player2','player3','player4']:
                    p_obj = player_index[m.group(p_name)]
                    p_obj.rank = 1 if m.group(p_name) == winner else 2
                    players.append(p_obj)
                trueskill.AdjustPlayers(players)
    
    with open(P_LC,'w') as f:
        f.write(str(line_count+i))
    with closing(shelve.open(P_ESTIM)) as p:
        p.update(player_index)
    
body = ''
body += '<p>Previously processed {0} games. Now processed {1} new games. We have {2} players.</p>'.format(line_count,i,len(player_index))
for p in sorted(player_index, key=lambda l:player_index[l].skill, reverse=True):
    pl = player_index[p]
    body += "<p>{0}: mu={1[0]:.3f} sigma={1[1]:.3f}</p>".format(p, pl.skill)
                    
                
                


            
print CGI_HEADER
print PAGE_TEMPLATE.format(body=body)

