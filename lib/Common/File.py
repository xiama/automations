"""
"""
import re


def write(fpath, content, flags='w'):
    fp = open(fpath, flags)
    fp.write(content)
    fp.close()


def append(fpath, content):
    write(fpath, "\n"+content, 'a')


def read(fpath):
    f = open(fpath, 'r')
    c = f.read()
    f.close()
    return c


def sub(fpath, pattern2repl, count=0, flags=0):
    """
    Usage: 
        fpath - path to the file for substitution
        pattern2repl - dict of { 'pattern' : ' repl', ...} format
        count,flags  -see re.sub for more

      try:
          sub("/etc/passwd", {"^root.*":"#root", ".*pattern$","replacement",...})
      except:
          ...

    Throws exception if error.
    """
    c = read(fpath)
    for p in pattern2repl.keys():
        c = re.sub(p, pattern2repl[p], count, flags)
    write(fpath, c)
