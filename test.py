## Based on http://code.activestate.com/recipes/273844/ (r3)
#!/usr/local/bin/python
"""
This is a test suite, which accepts a student upload and gives back
feedback on the correctness of the solution.

TODO: Limit file size

Marco Lui, May 2012
"""
import cgi
import cgitb; cgitb.enable(format='text')
import os, sys
import imp
import resource
import copy
import logging
logger = logging.getLogger(__name__)

from common import PLAYERS_DIR
 

import daifugo.common as common
import daifugo.check as check
import daifugo.game as game
import daifugo.sandbox as sandbox

game.DEBUG=False

import random, time
random.seed(time.time())

HTML_TEMPLATE = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html><head>
<title>COMP10001 Project 3 Tester/Playground Entry</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
</head>
<body>
<h1>COMP10001 Project 3 Tester/Playground Entry</h1>
%(BODY)s
</body>
</html>"""

NO_SUBMISSION_TEMPLATE="""
<p>Upload your submission here to have it tested. If the testing passes and you have selected the checkbox,
your player will be added to the playground. You will be given a player ID, which you can use to choose
your player to play against other players (once the playground itself is ready!).</p>

<p>The testing for play is done by playing a game between four copies of your player. Your player will only
be added to the playground if it passes all testing, and if it successfully plays a game against itself.
</p>

<form action="%(SCRIPT_NAME)s" method="POST" enctype="multipart/form-data">
File name: <input name="file_1" type="file"><br/>
<input name="add_player" type="checkbox" value="AddPlayer"/> Add player to playground. <br/>
<input name="submit" type="submit">
</form>
"""

# TODO: Make a nicer cut-pasteable player id field
QUALIFY_MSG="""
Congratulations! Your player has qualified for the playground. Your player id is: {player_id}
"""

from common import lists2ul, hand2htm, 

def generate_id(source):
    """
    Generate an identifier for an object based on its hash.
    Call with the source code of the player.
    """
    return "p{0:0>8x}".format(hash(source) % 16**8)



FORMAT = "%(asctime)-15s %(forwarded_for)s  %(message)s"    
env_info = dict(remote_addr=cgi.escape(os.environ["REMOTE_ADDR"]), forwarded_for=cgi.escape(os.environ["HTTP_X_FORWARDED_FOR"]))
logging.basicConfig(filename='test.py.log', level=logging.INFO, format=FORMAT,)


def get_python_source(form, form_field):
    """
    TODO: Limit filesize
    """
    if not form.has_key(form_field):
        return None
    fileitem = form[form_field]
    if not fileitem.file:
        raise ValueError, "field is not a file"
    if not fileitem.filename:
        raise ValueError, "no file specified"
    ext = os.path.splitext(fileitem.filename)[1]
    if ext.lower() != '.py':
        raise ValueError, "filename did not end in .py"
        
    source = fileitem.file.read().replace('\r\n','\n')
    try:
        compile(source, '', 'exec')
    except SyntaxError, e:
        etype = e.__class__.__name__
        raise ValueError, "{0} : {1} {2}".format(etype, str(e), (e.filename, e.lineno, e.offset, e.text))
    except Exception, e:
        etype = e.__class__.__name__
        raise ValueError, "file is not valid python code ({0}: {1})".format(etype, str(e))
        
    return source
    


######
#MAIN#
######


logging.info('request', extra=env_info)
form = cgi.FieldStorage()

body = ""
try:
    source = get_python_source(form, "file_1")
except ValueError, e:
    source = None
    body += "<h2>{0}: {1}</h2><br>".format(e.__class__.__name__,e) 

if source is None:
    logging.info('upload page served', extra=env_info)
    template_values = {}
    template_values['SCRIPT_NAME'] = os.environ['SCRIPT_NAME']
    body += NO_SUBMISSION_TEMPLATE % template_values
else:
    # Submission Received
    add_player = form.has_key('add_player')
    if not add_player:
        body += "<p>Not adding player, testing only.</p>"
    try:
        student_code, student_output = sandbox.as_module(source)
    except Exception, e:
        body += "<p>The following exception was raised when importing your code:</p>"
        body += "<h2>{0}: {1}</h2><br>".format(e.__class__.__name__,e) 
        student_code = None
        
    t_pass = True    
    for t, t_fn in sandbox.TEST_SUITE:
        if hasattr(student_code, t):
            t_result = t_fn(getattr(student_code,t))
            t_pass = t_pass and t_result[0]
            
            body += "<p>Testing: {0}</p>".format(t)
            if add_player:
                body += "<p>{0}</p>".format("Pass" if t_result[0] else "Fail")
            else:
                body += lists2ul(t_result[1])
        else:
            body += "<p>No implementation of {0}!</p>".format(t)
            t_pass = False
    
    if add_player:
        if t_pass:
            # player qualifies for playground
            player_id = generate_id(source)

            if not os.path.isdir(PLAYERS_DIR):
                os.mkdir(PLAYERS_DIR)

            path = os.path.join(PLAYERS_DIR, player_id)
            with open(path,'w') as f:
                f.write(source)
            body += QUALIFY_MSG.format(player_id=player_id)
        else:
            body += "<p>Sorry, your player did not qualify. Run testcases without the upload option for detailed output.</p>"
            
    
    

template_values = {}
template_values['BODY'] = body

print 'Content-Type: text/html'
print
print HTML_TEMPLATE % template_values

