"""
Run the test suite against a single player, to check if they qualify.

Marco Lui, May 2012
"""

from optparse import OptionParser

import daifugo.sandbox as sandbox


if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option("-i","--input", help="Read from FILE", metavar="FILE")
  parser.add_option("-d","--disq", action="store_true", default=False, help="echo disqualified")
  parser.add_option("-q","--qual", action="store_true", default=False, help="echo qualified")
  parser.add_option("-r","--reason", action="store_true", default=False, help="show reason")

  opts, args = parser.parse_args()
  if not opts.input:
    parser.error("Must specify input file")

  t_pass = True    
  fail_reason = None
  try:
    with open(opts.input) as f:
      student_code, student_output = sandbox.as_module(f)
    # Run the actual test suite
    for t, t_fn in sandbox.TEST_SUITE:
        if hasattr(student_code, t):
            #t_result = t_fn(getattr(student_code,t))
            t_ran, t_result, t_out = sandbox.timeout(t_fn, args=(getattr(student_code,t),), timeout_duration=30)
            if t_ran:
              t_pass = t_pass and t_result[0]
              if not t_result[0]:
                fail_reason = "failed {0}".format(t)
            else:
              t_pass = False
              e = t_result[1]
              fail_reason = "{0}: {1}".format(e.__class__.__name__, str(e))
        else:
            t_pass = False
            fail_reason = "missing {0}".format(t)
        if not t_pass:
          # Already disqualified, no point proceeding
          break
  except Exception, e:
    t_pass = False
    fail_reason = "{0}: {1}".format(e.__class__.__name__, str(e))

  if opts.reason:
    if opts.qual and t_pass:
      print "{0}: {1}".format(opts.input, "qualified")
    elif opts.disq and not t_pass:
      print "{0}: {1}".format(opts.input, fail_reason)
    else:
      print "{0}: {1}".format(opts.input, "WTF")
  else:
    if opts.qual and t_pass:
      print opts.input
    elif opts.disq and not t_pass:
      print opts.input
    else:
      print "{0}: {1}".format(opts.input, "WTF")

