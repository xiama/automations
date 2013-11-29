#!/usr/bin/python
# -*- coding: ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
# License: LGPL
# Keith Dart <kdart@kdart.com>

"""
Special getopt function. It returns long options as a dictionary. Any
name-value pair may be given on the command line.

"""
import nmsbuiltins

class GetoptError(Exception):
    opt = ''
    msg = ''
    def __init__(self, msg, opt):
        self.msg = msg
        self.opt = opt
        Exception.__init__(self, msg, opt)

    def __str__(self):
        return self.msg

add_exception(GetoptError)

#def nmsgetopt(argv):
#    """nmsgetopt(argv)
#Parses the argument list and returns an nms configuration object initialized
#with command-line arguments.  """
#    import config
#    try:
#        optlist, extraopts, args = getopt(argv[1:], "hdvc:f:")
#    except GetoptError, err:
#        print >>sys.stderr, err
#        sys.exit(2)
#    cf = config.get_config(initdict=extraopts)
#    for opt, optarg in optlist:
#        if opt == "-h":
#            print __doc__
#            sys.exit(2)
#        if opt == "-d":
#            cf.flags.DEBUG += 1
#        if opt == "-v":
#            cf.flags.VERBOSE += 1
#        if opt == "-c" or opt == "-f":
#            cf.mergefile(optarg)
#    cf.argv = args
#    return cf


# special getopt processing for tests. long-form options get placed in
# a dictionary of name-value pairs.

def getopt(args, shortopts):
    """getopt(args, options) -> opts, long_opts, args 
Returns options as list of tuples, long options as entries in a dictionary, and
the remaining arguments."""
    opts = []
    longopts = {}
    while args and args[0].startswith('-') and args[0] != '-':
        if args[0] == '--':
            args = args[1:]
            break
        if args[0].startswith('--'):
            arg = args.pop(0)
            _do_longs(longopts, arg)
        else:
            opts, args = _do_shorts(opts, args[0][1:], shortopts, args[1:])

    return opts, longopts, args

def _do_longs(longopts, opt):
    try:
        i = opt.index('=')
    except ValueError:
        raise GetoptError('long options require arguments in the form opt=arg.', opt)
    opt, optarg = opt[2:i], opt[i+1:]
    longopts[opt] = optarg
    return longopts

def _do_shorts(opts, optstring, shortopts, args):
    while optstring != '':
        opt, optstring = optstring[0], optstring[1:]
        if _short_has_arg(opt, shortopts):
            if optstring == '':
                if not args:
                    raise GetoptError('option -%s requires argument' % opt,
                                      opt)
                optstring, args = args[0], args[1:]
            optarg, optstring = optstring, ''
        else:
            optarg = ''
        opts.append(('-' + opt, optarg))
    return opts, args

def _short_has_arg(opt, shortopts):
    for i in range(len(shortopts)):
        if opt == shortopts[i] != ':':
            return shortopts.startswith(':', i+1)
    raise GetoptError('option -%s not recognized' % opt, opt)


# XXX
class Arguments(object):
    def __init__(self, optlist=""):
        self._optlist = optlist
        self._opts = None
        self._longopts = None
        self._args = None
    
    def parse(args):
        optlist, self._longopts, self._args = getopt(args, self._optlist)
        for opt, optarg in optlist:
            self._opts[opt] = optarg

    def __getitem__(self, idx):
        try:
            i = int(idx)
        except (ValueError, TypeError):
            return self._opts[idx]
        else:
            return self._args[i]

    def __iter__(self):
        return iter(self._args)


# self test
def _test():
    import sys
    dopt = 0
    try:
        optlist, extraopts, args = getopt([ "-d", "--opt1=1", "arg1", "arg2"], "d")
    except GetoptError, err:
        print >>sys.stderr, "ERR:", err
    for opt, optarg in optlist:
        if opt == "-d":
            dopt = 1
    print extraopts
    print dopt
    print args

if __name__ == "__main__":
    _test()
