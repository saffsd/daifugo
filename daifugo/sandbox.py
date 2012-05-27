"""
This is the playground sandbox. 
"""

import imp
import sys, os, tempfile, shutil
import resource
import contextlib
import threading
import random
import copy
from cStringIO import StringIO

import game
import check
import common

# adapted from http://code.activestate.com/recipes/473878/
class TimeOutExceeded(Exception): pass

class KThread(threading.Thread):
  """A subclass of threading.Thread, with a kill() method."""
  def __init__(self, *args, **keywords):
    threading.Thread.__init__(self, *args, **keywords)
    self.killed = False
    self.result = None 

  def start(self):
    """Start the thread."""
    self.__run_backup = self.run
    self.run = self.__run      # Force the Thread to install our trace.
    threading.Thread.start(self)

  def run(self):
    # TODO: Capture STDOUT, STDERR
    success = True
    outstream = StringIO()
    try:
      with redirect_stdout(outstream):
        val = self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
    except Exception, e:
      val = sys.exc_info()
      success = False
    output = outstream.getvalue()
    self.result = success, val, output

  def __run(self):
    """Hacked run function, which installs the trace."""
    sys.settrace(self.globaltrace)
    self.__run_backup()
    self.run = self.__run_backup

  def globaltrace(self, frame, why, arg):
    if why == 'call':
      return self.localtrace
    else:
      return None

  def localtrace(self, frame, why, arg):
    if self.killed:
      if why == 'line':
        raise SystemExit()
    return self.localtrace

  def kill(self):
    self.killed = True

def timeout(func, args=(), kwargs={}, timeout_duration=10, default=None):
    """This function will spawn a thread and run the given function
    using the args, kwargs and return the given default value if the
    timeout_duration is exceeded.
    """ 
    if isinstance(args, basestring):
      args = eval(args)
    if isinstance(kwargs, basestring):
      kwargs = eval(kwargs)
    t = KThread(target=func, args=args, kwargs=kwargs)
    t.start()
    t.join(timeout_duration)
    if t.isAlive():
        t.kill()
        raise TimeOutExceeded()
    else:
        return t.result

@contextlib.contextmanager
def redirect_stdout(target):
    __stdout__ = sys.stdout
    sys.stdout = target
    try:
        yield target
    finally:    
        sys.stdout = __stdout__

@contextlib.contextmanager
def working_directory(path=None):
    prev_cwd = os.getcwd()
    deldir = False
    
    if path is None:
        path = tempfile.mkdtemp()
        deldir = True
    elif not os.path.isdir(path):
        os.mkdir(path)
        
    os.chdir(path)
    try:
        yield path
    finally:
        if deldir:
            shutil.rmtree(path)
        os.chdir(prev_cwd)

@contextlib.contextmanager    
def limit_resource(r, softlimit):
    soft, hard = resource.getrlimit(r)
    resource.setrlimit(r, (softlimit, hard))
    yield
    resource.setrlimit(r, (soft, hard))



def as_module(source, name='module'):
    resource_cm = [
    limit_resource(resource.RLIMIT_NOFILE, 10), 
    limit_resource(resource.RLIMIT_FSIZE, 0), 
    limit_resource(resource.RLIMIT_NPROC, 0),
    ]
    module = imp.new_module(name)
    output = StringIO()
    with contextlib.nested(redirect_stdout(output), working_directory()):
        with contextlib.nested(*resource_cm):
            exec source in module.__dict__
    return module, output.getvalue()

def get_player(path):
    with open(path) as f:
            module, _ = as_module(f)
    player_id = os.path.splitext(os.path.basename(path))[0]
    return player_id, module


def complete_game(player_paths):
    ids, players = zip(*[get_player(p) for p in player_paths])
    with redirect_stdout(open('/dev/null','w')):
        outcome = game.play_game([p.play for p in players])
    return outcome
       
def list2frozenset(seq):
    if not isinstance(seq, list):
        #raise ValueError, "argument is not a list"
        return seq
    
    def process_items(seq):
        for item in seq:
            try:
                yield list2frozenset(item)
            except ValueError:
                yield item
    return frozenset(process_items(seq))

def checkresult2list(result):
    if result[0]:
        return ['PASS']
    else:
        retval = ['<b>FAIL</b>']
        if isinstance(result[1], Exception):
            retval.append(['exception raised', [result[1].__class__.__name__, str(result[1])]])
        else:
            try:
                retval.append(['expected', map(str,result[2])])
                retval.append(['got', map(str,result[1])])
            except TypeError:
                retval.append(['expected', [str(result[2])]])
                retval.append(['got', [str(result[1])]])

        return retval

def test_generate_plays(student):
    hands = game.deal()
    retval = []
    t_pass = True
    for hand in hands:
        hand = list(hand)
        x = check.compare_solutions(common.generate_plays,student, t_args=[hand], transform=list2frozenset)
        t_pass = t_pass and x[0]   
        retval.append("hand = {0}".format(hand))
        retval.append("sorted(hand) = {0}".format(sorted(hand)))
        # convert away from frozenset so that doesn't get displayed
        y = x[0], map(list, x[1]), map(list, x[2])
        retval.append(checkresult2list(y))
    return t_pass, (retval)

def test_is_valid_play(student):
    hands = game.deal()
    prev = random.choice(common.generate_plays(hands[0]))
    retval = []
    t_pass = True
    retval.append('prev = {0}'.format(sorted(prev)))
    for play in common.generate_plays(hands[1]):
        x = check.compare_solutions(common.is_valid_play, student, t_args=[prev, play])
        t_pass = t_pass and x[0]
        retval.append(['play = {0}'.format(sorted(play)), checkresult2list(x)])
    return t_pass, (retval)


def test_get_valid_plays(student):
    hands = game.deal()
    retval = []
    t_pass = True
    for prev in common.generate_plays(hands[0]):
        retval.append('prev = {0}'.format(sorted(prev)))
        for hand in hands[1:]:
            x = check.compare_solutions(common.get_valid_plays, student, t_args=[prev, list(hand)], t_kwargs=dict(generate=common.generate_plays, is_valid=common.is_valid_play), transform=list2frozenset)
            t_pass = t_pass and x[0]
            retval.append(['hand = {0}'.format(sorted(hand)),checkresult2list(x)])
    return t_pass, (retval)
    


def test_play(student):
    hands = game.deal()
    players = (student, student, student, student)
    discard = []
    lp = 0
    game_over = False
    
    retval = []
    round = 0
    t_pass = True
    
    while not game_over:
        round += 1
        retval.append('Round {0}'.format(round))
        retval.append( ['HANDS', ['player{0}: {1}'.format(i,sorted(h)) for i,h in enumerate(hands)]] )
        prev_hands = copy.deepcopy(hands)
        prev_lp = lp
        try:
            hands, lp, game_over, discard = game.play_round(hands, players, discard, lp, 'raise')
        except game.InvalidAction, e:
            retval.append(['INVALID ACTION', [e, e.call]])
            t_pass = False
            break
        retval.append( ['PLAYS',['player{0}: {1}'.format((prev_lp + i) % len(players) ,str(p)) for i,p in enumerate(discard[-1])] ] )
        
        if prev_hands == hands:
            # Nobody played, so we break out or we would be stuck
            game_over=True
            retval.append("GAME OVER: Nobody played")
                    
        else:
            retval.append( ['WINNER', ['player{0}'.format(lp)]] )
        
        
    return t_pass, retval
    


TEST_SUITE = [
    ("generate_plays", test_generate_plays),
    ("is_valid_play", test_is_valid_play),
    ("get_valid_plays", test_get_valid_plays),
    ("play", test_play),
    ]

