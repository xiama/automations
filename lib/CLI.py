#!/usr/bin/python2.3
# -*- coding: ascii -*-
# vim:ts=4:sw=4:softtabstop=0:smarttab
# License: LGPL
# Keith Dart <kdart@kdart.com>
"""
Provides a standard command line interpreter for programs needing one.
Supports different command contexts, customizable user interface, generic
object CLI's, and other neat stuff.

"""
from __future__ import generators

__all__ = ['CommandQuit', 'NewCommand', 'BaseCommands',
'DictCLI', 'GenericCLI', 'FileCLI', 'Completer', 'Shell', 'ConsoleIO', 'Theme',
'DefaultTheme', 'UserInterface', 'CommandParser', 'globargv', 'breakout_args',
'clieval', 'get_generic_cmd', 'get_generic_clone', 'get_generic_cli',
'run_cli_wrapper', 'run_cli', 'run_generic_cli', 'get_cli']

import sys, os, time
from cStringIO import StringIO

try:
	import readline # readline is very, very important to us...
	PROMPT_START_IGNORE = '\001'
	PROMPT_END_IGNORE = '\002'
except ImportError:
	readline = None # ...but try to live without it if it is not available.
	PROMPT_START_IGNORE = ''
	PROMPT_END_IGNORE = ''

import nmsgetopt
import termtools
import cliutils
import environ
from fsm import FSM, ANY

# global timer for timing methods
import scheduler
timer = scheduler.get_scheduler()
del scheduler

MethodType = type(timer.sleep) # cheat
_DEBUG = False


class CLIException(Exception):
	def __init__(self, value=None):
		self.value = value

class CommandQuit(CLIException):
	"""An exception that is used to signal quiting from a command object. """
	pass
class CommandExit(CLIException):
	"""An exception that is used to signal exiting from the command object. The
	command is not popped.  """
	pass
class NewCommand(CLIException):
	"""Used to signal the parser to push a new command object.
Raise this with an instance of BaseCommands as a value."""
	pass
add_exception(CommandQuit)
add_exception(CommandExit)
add_exception(NewCommand)

class BaseCLI(object):
	"""A base class that defines a holder object for command methods. It dispatches
the methods when you call it with an argv-style list of arguments. The first
argument must match a name of a method.
"""
	def __init__(self, ui, aliases=None):
		# initialize local variables
		self._aliases = aliases or {}
		self._command_list = None
		self._repeater = None
		self._completion_scopes = {}
		self._completers = []
		self._obj = None # may be in instance of some interface commands may use.
		self.set_userinterface(ui)
		self.initialize()

	# optional extra initialization. Override in subclass if desired.
	def initialize(self):
		pass

	# optional finalize method. called when CLI quits.
	def finalize(self):
		pass

	def set_userinterface(self, ui):
		self._ui = ui
		# map in user interface input and output for speed
		self._user_input = ui.user_input
		self._more_user_input = ui.more_user_input
		self._print = ui.Print
		self._printf = ui.printf
		self._pprint = ui.pprint
		self._format = ui.format
		self._print_list = ui.print_list
		self._set_theme = ui.set_theme
		self._environ = ui._env

	# override this and call it for command sets the need post-instantiation setup.
	def _setup(self, obj, prompt=""):
		self._obj = obj # an object to call methods on, if needed
		self._environ["PS1"] = "%s> " % (prompt,)
		self._reset_scopes()

	def _reset_scopes(self):
		pass

	# overrideable exception hook method - do something with command exceptions.
    def except_hook(self, ex, val, tb):
		global _DEBUG
		if _DEBUG:
			import debugger
			debugger.post_mortem(ex, val, tb)
		else:
        	self._ui.error("%s (%s)" % (ex, val))

	# override this if your subcommand passes something useful back
	# via a parameter to the CommandQuit exception. 
	def handle_subcommand(self, value):
		pass

	# override this for default actions
	def default_command(self, argv):
		self._ui.error("unknown command: %r" % (argv[0]))
		return 2

	# completer management methods
	def add_completion_scope(self, name, complist):
		self._completion_scopes[name] = list(complist)

	def get_completion_scope(self, name="commands"):
		return self._completion_scopes.get(name, [])

	def remove_completion_scope(self, name):
		del self._completion_scopes[name]

	def push_completer(self, namespace):
		if readline:
			orig = readline.get_completer()
			if orig is not None:
				self._completers.append(orig)
			readline.set_completer(Completer(namespace).complete)

	def pop_completer(self):
		if readline:
			if self._completers:
				c = self._completers.pop()
				readline.set_completer(c)

	# convenient access to option parsing.
	def getopt(self, argv, shortopts):
		return nmsgetopt.getopt(argv[1:], shortopts)
		# returns: optlist, longoptdict, args

	# dispatch commands by calling the instance
	def __call__(self, argv):
		if not argv or not argv[0] or argv[0].startswith("_"):
			return 2
		argv = self._expand_aliases(argv)
		# special escape characters...
		if argv[0].startswith("#"): # comment
			return 0
		try:
			meth = getattr(self, argv[0])
		except AttributeError:
			return self.default_command(argv)
		# ...and exec it.
		try:
			rv = meth(argv) # call the method
		except (NewCommand, CommandQuit, CommandExit, KeyboardInterrupt):
			raise # pass these through to parser
		except IndexError: # tried to get non-existent argv value
			self._print(meth.__doc__)
		except GetoptError, err:
			self._print("option %r: %s" % (err.opt, err.msg))
		except:
			ex, val, tb = sys.exc_info()
			self.except_hook(ex, val, tb)
		else:
			try:
				self._environ["?"] = int(rv)
			except (ValueError, TypeError, AttributeError):
				self._environ["?"] = 99
			self._environ["_"] = rv
			return rv

	def _expand_aliases(self, argv):
		seen = {}
		while 1:
			alias = self._aliases.get(argv[0], None)
			if alias:
				if alias[0] in seen:
					break # alias loop
				seen[alias[0]] = True
				# do the substitution
				del argv[0]
				rl = alias[:]
				rl.reverse()
				for arg in rl:
					argv.insert(0, arg)
			else:
				break
		return argv

	def _export(self, name, val):
		"""put a name-value pair in the environment."""
		self._environ[name] = val

	# Start a new BaseCommands (or subclass), with the same environment.
	# The new command object gets a copy of the environment, but the same aliases.
	def clone(self, cliclass=None, theme=None):
		if cliclass is None:
			cliclass = self.__class__
		newui = self._ui.clone(theme)
		return cliclass(newui, self._aliases)

	def subshell(self, io, env=None, aliases=None, theme=None):
		cliclass = self.__class__
		newui = UserInterface(io, env or self._environ.copy(), theme)
		aliases = aliases or self._aliases
		return cliclass(newui, aliases)

	def get_commands(self):
		if self._command_list is None:
			hashfilter = {}
			for name in filter(self._command_filt, dir(self)):
				## this filters out aliases (same function id)
				meth = getattr(self, name)
				hashfilter[id(meth.im_func)] = meth.im_func.func_name
			self._command_list = hashfilter.values()
			self._command_list.sort()
		return self._command_list

	# user visible commands are methods that don't have a leading underscore,
	# and do have a docstring.
	def _command_filt(self, objname):
		if objname.startswith("_"):
			return 0
		obj = getattr(self, objname)
		if type(obj) is MethodType and obj.__doc__:
			return 1
		else:
			return 0

	def commandlist(self, argv):
		self._print_list(self.get_commands())

	# most basic standard commands follow
	def unset(self, argv):
		"""unset <envar>
    Unsets the environment variable."""
		try:
			del self._environ[argv[1]]
		except:
			return 1

	def setenv(self, argv):
		"""setenv NAME VALUE
    Sets the environment variable NAME to VALUE, ala C shell.  """
		if len(argv) < 3:
			self._print(self.setenv.__doc__)
			return
		self._environ[argv[1]] = argv[2]
		return self._environ["_"]

	def echo(self, argv):
		"""echo ...
    Echoes arguments back.	"""
		self._print(" ".join(argv[1:]))
		return self._environ["_"]

	def printf(self, argv):
		"""printf [<format>] <args>....
    Print the arguments according to the format, 
    or all arguments if first is not a format string."""
		if argv[1].find("%") >= 0:
			try:
				ns = vars(self._obj)
			except:
				ns = globals()
			args, kwargs = breakout_args(argv[2:], ns)
			self._print(str(argv[1]) % args)
		else:
			self._print(" ".join(argv[1:]))

	def exit(self, argv):
		"""exit
    Exits this command interpreter instance.  """
		raise CommandQuit
	quit = exit

	def printenv(self, argv):
		"""printenv [name ...]
    Shows the shell environment that processes will run with.  """
		if len(argv) == 1:
			names = self._environ.keys()
			names.sort()
			ms = reduce(max, map(len, names))
			for name in names:
				value = self._environ[name]
				self._print("%*s = %s" % (ms, name, _safe_repr(value, {}, None, 0)))
		else:
			s = []
			for name in argv[1:]:
				try:
					s.append("%s=%s" % (name, _safe_repr(self._environ[name], {}, None, 0)))
				except KeyError:
					pass
			self._print("\n".join(s))

	def history(self, argv):
		"""history [<index>]
    Display the current readline history buffer."""
		if not readline:
			self._print("The readline library is not available.")
			return
		if len(argv) > 1:
			idx = int(argv[1])
			self._print(readline.get_history_item(idx))
		else:
			for i in xrange(readline.get_current_history_length()):
				self._print(readline.get_history_item(i))

	def export(self, argv):
		"""export NAME=VAL
    Sets environment variable that new processes will inherit.
	"""
		for arg in argv[1:]:
			try:
				self._environ.export(arg)
			except:
				ex, val = sys.exc_info()[:2]
				self._print("** could not set value: %s (%s)" % (ex, val))
	
	def help(self, argv):
		"""help [-lLcia] [<commandname>]...
    Print a list of available commands, or information about a command,
    if the name is given.  Options:
        -l Shows only local (object specific) commands.
        -c Shows only the dynamic commands.
        -L shows only local and dynamic commands.
        -i Shows only the inherited commands from the parent context.
        -a Shows all commands (default)
		"""
		local=True ; created=True ; inherited=True
		opts, longs, args = self.getopt(argv, "lLcia")
		for opt, optarg in opts:
			if opt =="-i":
				local=False ; created=False ; inherited=True
			elif opt == "-c":
				local=False ; created=True ; inherited=False
			elif opt == "-l":
				local=True ; created=False ; inherited=False
			elif opt == "-a":
				local=True ; created=True ; inherited=True
			elif opt == "-L":
				local=True ; created=True ; inherited=False
		if not args:
			args = self.get_commands()
		for name in args:
			try:
				doc = getattr(self, name).__doc__
			except AttributeError:
				self._print("No command named %r found." % (name,))
				continue
			if not doc:
				self._print("No docs for %r." % (name,))
			elif local and self.__class__.__dict__.has_key(name):
				self._ui.help_local(doc)
			elif created and "*" in doc: # dynamic method from generic_cli
				self._ui.help_created(doc)
			elif inherited:
				self._ui.help_inherited(doc)

	def unalias(self, argv):
		"""unalias <alias>
    Remove the named alias from the alias list."""
		if len(argv) < 2:
			self._print(self.unalias.__doc__)
			return
		try:
			del self._aliases[argv[1]]
		except:
			self._print("unalias: %s: not found" % argv[1])

	def alias(self, argv):
		"""alias [newalias]
    With no argument prints the current set of aliases. With an argument of the
    form alias ..., sets a new alias.  """
		if len(argv) == 1:
			for name, val in self._aliases.items():
				self._print("alias %s='%s'" % (name, " ".join(val)))
			return 0
		elif len(argv) == 2 and '=' not in argv[1]:
			name = argv[1]
			try:
				self._print("%s=%s" % (name, " ".join(self._aliases[name])))
			except KeyError:
				self._print("undefined alias.")
			return 0
		# else
		try: # this icky code to handle different permutations of where the '=' is.
			argv.pop(0) # discard 'alias'
			name = argv.pop(0)
			if "=" in name:
				name, rh = name.split("=", 1)
				argv.insert(0,rh)
			elif argv[0].startswith("="):
				if len(argv[0]) > 1: # if argv[1] is '=something'
					argv[0] = argv[0][1:]
				else:
					del argv[0] # remove the '='
			self._aliases[name] = argv
		except:
			ex, val = sys.exc_info()[:2]
			self._print("alias: Could not set alias. Usage: alias name=value")
			self._print("%s (%s)" % (ex, val))
			return 1

	def sleep(self, argv):
		"""sleep <secs>
    Sleeps for <secs> seconds."""
		secs = int(argv[1])
		timer.sleep(secs)
	delay = sleep # alias

	def stty(self, argv):
		"""stty <args>
    Sets or clears tty flags. May also use "clear", "reset", "sane". """
		self._print(termtools.stty(self._ui._io.fileno(), *tuple(argv[1:])))

	def debug(self, argv):
		"""debug ["on"|"off"]
	Enables debugging for CLI code. Enters debugger is an exception occurs."""
		global _DEBUG
		if len(argv) > 1:
			cmd = argv[1]
			if cmd == "on":
				_DEBUG = True
			else:
				_DEBUG = False
		else:
			self._print("Debugging is currently ", IF(_DEBUG, "on", "off"), ".")
		
	def python(self, argv):
		import code
		ns = self._get_ns()
		console = code.InteractiveConsole(ns)
		console.raw_input = self._ui.user_input
		try:
			saveps1, saveps2 = sys.ps1, sys.ps2
		except AttributeError:
			saveps1, saveps2 = ">>> ", "... "
		sys.ps1, sys.ps2 = "%%GPython%%N:%s> " % (self._obj.__class__.__name__,), "more> "
		if readline:
			oc = readline.get_completer()
			readline.set_completer(Completer(ns).complete)
		console.interact("You are now in Python. ^D exits.")
		if readline:
			readline.set_completer(oc)
		sys.ps1, sys.ps2 = saveps1, saveps2
		self._reset_scopes()

	def _get_ns(self):
		try:
			name = self._obj.__class__.__name__.lower()
		except:
			name = "object"
		return {name:self._obj, "environ":self._environ}


class BaseCommands(BaseCLI):
	"""Extends the BaseCLI with common commands that enable calling other
	programs, repeating commands, etc."""
	def __del__(self):
		self._stop()

	def __call__(self, argv):
		if argv[0].startswith("#"): # comment
			return 0
		elif argv[0].startswith("!"): # bang-escape reads pipe
			argv[0] = argv[0][1:]
			argv.insert(0, "pipe")
		elif argv[0].startswith("%"): # percent-escape spawns pty
			argv[0] = argv[0][1:]
			argv.insert(0, "spawn")
		elif argv[0].startswith("@"): # python exec escape
			argv[0] = argv[0][1:]
			argv.insert(0, "pyexec")
		elif argv[0].startswith("="): # python eval escape
			argv[0] = argv[0][1:]
			argv.insert(0, "pyeval")
		super(BaseCommands, self).__call__(argv)


	################################
	# actual commands follow (no leading '_' and has a docstring.)
	#
	def pipe(self, argv):
		"""pipe <command>
    Runs a shell command via a pipe, and prints its stdout and stderr. You may
    also prefix the command with "!" to run "pipe". """
		import proctools
		argv = globargv(argv)
		proc = proctools.spawnpipe(" ".join(argv))
		text = proc.read()
		self._print(text)
		proc.close()
		return proc.wait()

	def spawn(self, argv):
		"""spawn <command>...
    Spawn another process (uses a pty). You may also prefix the command
    with "%" to run spawn."""
		import proctools
		argv = globargv(argv)
		proc = proctools.spawnpty(" ".join(argv))
		cmd = self.clone(FileCLI)
		cmd._setup(proc, "Process:%s> " % (proc.cmdline.split()[0],))
		raise NewCommand, cmd

	def repeat_command(self, argv):
		"""repeat_command <interval> <command> [<args>...]
    Repeats a command every <interval> seconds. If <interval> is zero then
    loop forever (or until interrupted). If <interval> is negative then loop
    with a count of the absolute value of <interval>."""
		if self._repeater:
			self._print("Repeat command already defined. Run 'stop' first.")
			return
		argv.pop(0) # eat name
		interval = int(argv.pop(0))
		argv = self._expand_aliases(argv)
		meth = getattr(self, argv[0])
		if interval > 0:
			wr = _RepeatWrapper(self._ui._io, meth, (argv,))
			self._repeater = timer.add(interval, 0, wr, repeat=1)
		elif interval == 0:
			try:
				while 1:
					apply(meth, (argv,))
					# OOO cheat a little. This is need to keep PagedIO
					# from asking to press a key.
					self._ui._io.read(0)
			except KeyboardInterrupt:
				pass
		else:
			for i in xrange(-interval):
				apply(meth, (argv,))

	def stop_repeater(self, argv):
		"""stop_repeater
    Stops a repeating command."""
		self._stop()

	def _stop(self):
		if self._repeater:
			timer.remove(self._repeater)
			self._repeater = None

	def schedule(self, argv):
		"""schedule <delay> <command> [<args>...]
    Schedules a command to run <delay> seconds from now."""
		argv.pop(0) # eat name
		delay = int(argv.pop(0))
		argv = self._expand_aliases(argv)
		meth = getattr(self, argv[0])
		timer.add(delay, 0, meth, (argv,), repeat=0)

	# 'hidden' commands (no doc string) follow
	def pyeval(self, argv):
		snippet = " ".join(argv[1:]).strip()+"\n"
		ns = self._get_ns()
		try:
			code = compile(snippet, '<CLI>', 'eval')
			rv = eval(code, globals(), ns)
		except:
			t, v, tb = sys.exc_info()
			self._print('*** %s (%s)' % (t, v))
		else:
			self._print(rv)
			return rv

	def pyexec(self, argv):
		snippet = " ".join(argv[1:]).strip()+"\n"
		ns = self._get_ns()
		try:
			code = compile(snippet, '<CLI>', 'exec')
			exec code in globals(), ns
		except:
			t, v, tb = sys.exc_info()
			self._print('*** %s (%s)' % (t, v))


# This is needed to reset PagedIO so background events don't cause the pager to activate.
class _RepeatWrapper(object):
	def __init__(self, io, meth, args):
		self.io = io
		self.meth = meth
		self.args = args
	def __call__(self):
		apply(self.meth, self.args)
		self.io.read(0) 

def globargv(argv):
	if len(argv) > 2:
		import glob
		l = []
		map(lambda gl: l.extend(gl), map(lambda arg: glob.has_magic(arg) and glob.glob(arg) or [arg], argv[2:]))
		argv = argv[0:2] + l
	return argv[1:]

# TODO: should be able to specify value's object type
def breakout_args(argv, namespace=None):
	"""convert a list of string arguments (with possible keyword=arg pairs) to
	the most likely objects."""
	args = []
	kwargs = {}
	if namespace:
		if not isinstance(namespace, dict):
			raise ValueError, "namespace must be dict"
	else:
		namespace = locals()
	for argv_arg in argv:
		if argv_arg.find("=") > 0:
			[kw, kwarg] = argv_arg.split("=")
			kwargs[kw.strip()] = _convert(kwarg, namespace)
		else:
			args.append(_convert(argv_arg, namespace))
	return tuple(args), kwargs

def _convert(val, namespace):
	try:
		return eval(val, globals(), namespace)
	except:
		return val

# public "safe" evaluator
def clieval(val):
	try:
		return eval(val)
	except:
		return val # just assume some string otherwise

###### Specialized, but generally useful, command sets follow

class DictCLI(BaseCommands):
	"""Wrap a dictionary-like object and edit it."""
	def _setup(self, obj, prompt=""):
		self._obj = obj # the dictionary object
		self._environ["PS1"] = "%s(dict)> " % (prompt,)
		self._reset_scopes()

	def _reset_scopes(self):
		names = map(str, self._obj.keys())
		self.add_completion_scope("get", names)
		self.add_completion_scope("set", names)
		self.add_completion_scope("pop", names)
		self.add_completion_scope("delete", names)
	
	def set(self, argv):
		"""set [-t <type>] <name> <value>
    Set the mapping key to value. Specify a type of the value with the -t
    option. If not provided the value is simply evaluated."""
		t = clieval
		optlist, longoptdict, args = self.getopt(argv, "t:")
		name = args[0]
		for opt, optarg in optlist:
			if opt == "-t":
				t = eval(optarg, globals(), globals())
				if type(t) is not type:
					raise ValueError, "Argument to -t is not a type"
		value = t(*tuple(args[1:]))
		self._obj[name] = value
		self._reset_scopes()

	def get(self, argv):
		"""get <key>
    Gets and prints the named value."""
		name = argv[1]
		v = self._obj.get(name)
		self._print(repr(v))
		return v

	def delete(self, argv):
		"""delete <key>
    Deletes the given key from the mapping."""
		key = argv[1]
		del self._obj[key]
		self._reset_scopes()

	def clear(self, argv):
		"""clear
    Clears the mapping."""
		self._obj.clear()
		self._reset_scopes()
	
	def has_key(self, argv):
		"""has_key <key>
    Report whether or not the mapping has the given key."""
		if self._obj.has_key(argv[1]):
			self._print("Mapping does contain the key %r." % (argv[1],))
		else:
			self._print("Mapping does NOT contain the key %r." % (argv[1],))

	def keys(self, argv):
		"""keys
    Show all mapping keys."""
		self._print_list(map(repr, self._obj.keys()))

	def values(self, argv):
		"""values
    Show all mapping values."""
		self._print_list(self._obj.values())

	def items(self, argv):
		"""items
    Show mapping items."""
		for name, val in self._obj.items():
			self._print("%25.25r: %r" % (name, val))
		
	def pop(self, argv):
		"""pop <key>
	Pops the given key from the mapping."""
		name = argv[1]
		obj = self._obj.pop(name)
		self._print("Popped: ", repr(obj))
		self._reset_scopes()
		return obj
	
	def length(self, argv):
		"""length
	Display the length of this mapping object."""
		self._print(len(self._obj))

# edit list objects
class ListCLI(BaseCommands):
	"""Wrap a list object and edit it."""
	def _setup(self, obj, prompt=""):
		self._obj = obj # the list object
		self._environ["PS1"] = "%s(list)> " % (prompt,)
		self._reset_scopes()

	def _get_object(self, name):
		return eval(name, globals(), self._environ)

	def show(self, argv):
		"""show [<index>]
	Show the list, or a particular index."""
		if len(argv) > 1:
			for s_idx in argv[1:]:
				index = int(s_idx)
				self._print("%3d: %r" % (index, self._obj[index]))
		else:
			for index, obj in enumerate(self._obj):
				self._print("%3d: %r" % (index, obj))

	def delete(self, argv):
		"""delete <index>
	Delete the entry at <index>."""
		index = int(argv[1])
		del self._obj[index]
	
	def append(self, argv):
		"""append [-t <type>] <obj>
	Appends the <obj> to the list. Beware that <obj> may not evaluate as you
	expect, but simple objects should work."""
		optlist, longoptdict, args = self.getopt(argv, "t:")
		name = args[0]
		for opt, optarg in optlist:
			if opt == "-t":
				t = eval(optarg, globals(), globals())
				if type(t) is not type:
					raise ValueError, "Argument to -t is not a type"
				self._obj.append(t(name))
				return
		else:
			obj = self._get_object(name)
			self._obj.append(obj)

	def extend(self, argv):
		"""extend [-t type] <object>...
	Extends the list with the argument list of converted objects."""
		argtype = self._get_object
		new = []
		optlist, longoptdict, args = self.getopt(argv, "t:")
		for opt, optarg in optlist:
			if opt == "-t":
				argtype = eval(optarg, globals(), globals())
				if type(argtype) is not type:
					raise ValueError, "Argument to -t is not a type"
		for name in args:
			new.append(argtype(name))
		self._obj.extend(new)

	def count(self, argv):
		"""count <object>
	Counts number of <object> in list."""
		obj = self._get_object(argv[1])
		count = self._obj.count(obj)
		self._print(count)
		return count
	
	def index(self, argv):
		"""index <object>
	Returns the index number of <object> in the list."""
		obj = self._get_object(argv[1])
		i = self._obj.index(obj)
		self._print(i)
		return i
	
	def insert(self, argv):
		"""insert <index> <object>
	Inserts the <object> at <index>."""
		argtype = self._get_object
		optlist, longoptdict, args = self.getopt(argv, "t:")
		for opt, optarg in optlist:
			if opt == "-t":
				argtype = eval(optarg, globals(), globals())
				if type(argtype) is not type:
					raise ValueError, "Argument to -t is not a type"
		index = int(args[0])
		obj = argtype(args[1])
		self._obj.insert(index, obj)
	
	def pop(self, argv):
		"""pop [<index>]
	Pops the <index>'th item from the list. If <index> not given then pop the last item."""
		if len(argv) > 1:
			i = int(argv[1])
			obj = self._obj.pop(i)
		else:
			obj = self._obj.pop()
		self._print("Popped: %r" % (obj,))
		return obj
	
	def remove(self, argv):
		"""remove <object>
	Remove the <object> from the list."""
		obj = self._get_object(argv[1])
		return self._obj.remove(obj)
	
	def reverse(self, argv):
		"""reverse
	Reverses the order of the list."""
		self._obj.reverse()
	
	def sort(self, argv):
		"""sort
	Sorts, in place, the list."""
		self._obj.sort()


### objects for creating quick and dirty (generic) CLI objects that let
#you interact with another object's methods.
class GenericCLI(BaseCommands):
	"""GenericCLI() Generic Object editor commands.
Wraps any object and allows inspecting and altering it. Use the
get_generic_cli() factory function to get one of these with extra
methods/commands that correspond to the wrapped objects methods.  """

	def _generic_call(self, argv):
		meth = getattr(self._obj, argv[0])
		args, kwargs = breakout_args(argv[1:], vars(self._obj))
		rv = apply(meth, args, kwargs)
		self._print(rv)
	
	def _reset_scopes(self):
		names = filter(lambda n: not n.startswith("__"), dir(self._obj))
		self.add_completion_scope("show", names)
		self.add_completion_scope("call", [n for n in names if callable(getattr(self._obj, n))])
		self.add_completion_scope("set", names)
		self.add_completion_scope("get", names)
		self.add_completion_scope("delete", names)

	def subshell(self, io, env=None, aliases=None, theme=None):
		cliclass = self.__class__
		newui = UserInterface(io, env or self._environ.copy(), theme)
		aliases = aliases or self._aliases
		cmd  = cliclass(newui, aliases)
		cmd._obj = self._obj
		return cmd

	def call(self, argv):
		"""call <name> <arg1>...
	Calls the named method with the following arguments converted to "likely types"."""
		self._generic_call(argv[1:])

	def show(self, argv):
		"""show [<name>]
    Shows a named attribute of the object, or the object itself if no argument given."""
		if len(argv) > 1:
			v = getattr(self._obj, argv[1])
			self._print(v)
			return v
		else:
			self._print(self._obj)

	def ls(self, argv):
		"""ls
    Display a list of the wrapped objects attributes and their types."""
		d = dir(self._obj)
		s = []
		ms = []
		for name in d:
			if name.startswith("__") or name.startswith("_p_"): # hide class-private and persistence overhead objects.
				continue
			attr = getattr(self._obj, name)
			if type(attr) is MethodType:
				ms.append("%22.22s : %s" % (name, method_repr(attr)))
			else:
				s.append("%22.22s : %r" % (name, attr))
		self._print("Methods:")
		self._print("\n".join(ms))
		self._print("Attributes:")
		self._print("\n".join(s))
		return d
	dir = ls # alias

	def set(self, argv):
		"""set [-t <type>] <name> <value>
    Sets the named attribute to a new value. The value will be converted into a
    likely suspect, but you can specify a type with the -t flag.  """
		t = clieval
		optlist, longoptdict, args = self.getopt(argv, "t:")
		name = args[0]
		for opt, optarg in optlist:
			if opt == "-t":
				t = eval(optarg, globals(), vars(self._obj))
				assert type(t) is type, "Argument to -t is not a type"
		value = t(*tuple(args[1:]))
		setattr(self._obj, name, value)
		self._reset_scopes()

	def get(self, argv):
		"""get <name>
    Gets and prints the named attribute."""
		name = argv[1]
		v = getattr(self._obj, name)
		self._print(v)
		return v

	def delete(self, argv):
		"""delete <name>
    Delete the named attribute."""
		name = argv[1]
		delattr(self._obj, name)
		self._reset_scopes()


# used to interact with file-like objects.
class FileCLI(GenericCLI):
	"""Commands for file-like objects."""
	def read(self, argv):
		"""read [amt]
    Read <amt> bytes of data."""
		args, kwargs = breakout_args(argv[1:], vars(self._obj))
		data = self._obj.read(*args)
		self._print(data)
		return data

	def write(self, argv):
		"""write <data>
    Writes the arguments to the file."""
		writ = self._obj.write(" ".join(argv[1:]))
		writ += self._obj.write("\r")
		self._print("wrote %d bytes." % (writ,))
		return writ
	
	def interact(self, argv):
		"""interact
    Read and write to the file object. Works best with Process objects."""
		io = self._ui._io
		import select
		from errno import EINTR
		escape = chr(29) # ^]
		self._print("\nEntering interactive mode.")
		self._print("Type ^%s to stop interacting." % (chr(ord(escape) | 0x40)))
		# save tty state and set to raw mode
		stdin_fd = io.fileno()
		fo_fd = self._obj.fileno()
		ttystate = termtools.tcgetattr(stdin_fd)
		termtools.setraw(stdin_fd)
		while 1:
			try:
				rfd, wfd, xfd = select.select([fo_fd, stdin_fd], [], [])
			except select.error, errno:
				if errno[0] == EINTR:
					continue
			if fo_fd in rfd:
				try:
					text = self._obj.read(1)
				except (OSError, EOFError), err:
					termtools.tcsetattr(stdin_fd, termtools.TCSAFLUSH, ttystate)
					self._print( '*** EOF ***' )
					self._print( err)
					break
				if text:
					io.write(text)
					io.flush()
				else:
					break
			if stdin_fd in rfd:
				char = io.read(1)
				if char == escape: 
					break
				else:
					try:
						self._obj.write(char)
					except:
						termtools.tcsetattr(stdin_fd, termtools.TCSAFLUSH, ttystate)
						extype, exvalue, tb = sys.exc_info()
						io.errlog("%s: %s\n" % (extype, exvalue))
						termtools.setraw(stdin_fd)
		termtools.tcsetattr(stdin_fd, termtools.TCSAFLUSH, ttystate)

# The object's public interface is defined to be the methods that don't
# have a leading underscore, and do have a docstring.
def _get_methodnames(obj):
	cls = obj.__class__
	for name in dir(cls):
		if name[0] == "_":
			continue
		cls_obj = getattr(cls, name)
		if type(cls_obj) is MethodType and cls_obj.__doc__:
			yield name, cls_obj


# a completer object for readline and python method. Safer than the stock one (no eval).
class Completer(object):
	def __init__(self, namespace):
		assert type(namespace) is dict, "namespace must be a dict type"
		self.namespace = namespace
		self.globalNamespace = Completer.get_globals()
		self.globalNamespace.extend(map(str, namespace.keys()))
		self.matches = []

	def complete(self, text, state):
		if state == 0:
			self.matches = []
			if "." in text:
				for name, obj in self.namespace.items():
					for key in dir(obj):
						if key.startswith("__"):
							continue
						lname = "%s.%s" % (name, key)
						if lname.startswith(text):
							self.matches.append(lname)
			else:
				for key in self.globalNamespace:
					if key.startswith(text):
						self.matches.append(key)
		try:
			return self.matches[state]
		except IndexError:
			return None

	def get_globals():
		import keyword, __builtin__
		rv = keyword.kwlist + dir(__builtin__)
		rv = removedups(rv)
		return rv
	get_globals = staticmethod(get_globals)

	def get_class_members(klass, rv=None):
		if rv is None:
			rv = dir(klass)
		else:
			rv.extend(dir(klass))
		if hasattr(klass, '__bases__'):
			for base in klass.__bases__:
				Completer.get_class_members(base, rv)
		return rv
	get_class_members = staticmethod(get_class_members)

def get_generic_cmd(obj, ui, cliclass=GenericCLI, aliases=None, gbl=None):
	"""get a GenericCLI (or other) command set wrapping any class instance
	object. The wrapped objects public methods have CLI command counterparts
	automatically created."""
	import new
	from basicconfig import MethodHolder
	cmd = cliclass(ui, aliases)
	if gbl is None:
		gbl = globals()
	hashfilter = {}
	for name, obj_meth in _get_methodnames(obj):
		if hasattr(cmd, name):
			continue # don't override already defined methods
		# all this mess does is introspect the object methods and map it to a CLI
		# object method of the same name, with a docstring showing the attributes
		# and their default values, and the actual code mirroring the
		# _generic_call method in the GenericCLI class.
		else:
			if id(obj_meth.im_func) in hashfilter: # filter out aliases
				continue
			else:
				hashfilter[id(obj_meth.im_func)] = True
			mh = MethodHolder(obj_meth)
			doc = "%s  *\n%s" % (mh, obj_meth.__doc__ or "")
			code = cliclass._generic_call.func_code
			nc = new.code(code.co_argcount, code.co_nlocals, code.co_stacksize, 
				code.co_flags, code.co_code, 
				(doc,)+code.co_consts[1:], # replace docstring
				code.co_names, code.co_varnames, code.co_filename, 
				code.co_name, code.co_firstlineno, code.co_lnotab)
			f = new.function(nc, gbl, name)
			m = new.instancemethod(f, cmd, cliclass)
			setattr(cmd, name, m)
	cmd._setup(obj, "%s:%s" % (cliclass.__name__, obj.__class__.__name__))
	return cmd

def get_generic_clone(obj, cli, cliclass=GenericCLI, theme=None):
	"Return a generic clone of an existing Command object."
	newui = cli._ui.clone(theme)
	return get_generic_cmd(obj, newui, cliclass, aliases=cli._aliases)

def get_generic_cli(obj, cliclass=GenericCLI, env=None, aliases=None, theme=None, logfile=None, historyfile=None):
	""" get_generic_cli(obj, cliclass=GenericCLI, env=None, aliases=None)
Returns a generic CLI object with command methods mirroring the public
methods in the supplied object.  Ready to interact() with! """
	io = ConsoleIO()
	ui = UserInterface(io, env, theme)
	cmd = get_generic_cmd(obj, ui, cliclass, aliases)
	cmd._export("PS1", "%s> " % (obj.__class__.__name__,))
	cli = CommandParser(cmd, logfile, historyfile)
	return cli

# this class is indended to be wrapped by GenericCLI as a general Python CLI.
# It does nothing but allow GenericCLI to pass through its basic functionality.
class Shell(object):
	"""A simple class for testing object wrappers."""
	def __init__(self, *iargs, **ikwargs):
		self.initargs = iargs
		self.initkwargs = ikwargs

	def callme(self, *args, **kwargs):
		Print("args:", args)
		Print("kwargs:", kwargs)


# wraps stdio to look like a single read-write object. Also provides additional io methods.
# The termtools.PagedIO object should have all the same methods as this class.
class ConsoleIO(object):
	def __init__(self):
		self.stdin = sys.stdin
		self.stdout = sys.stdout
		self.stderr = sys.stderr
		self.mode = "rw"
		self.closed = 0
		self.softspace = 0
		# reading methods
		self.read = self.stdin.read
		self.readline = self.stdin.readline
		self.readlines = self.stdin.readlines
		self.xreadlines = self.stdin.xreadlines
		# writing methods
		self.write = self.stdout.write
		self.flush = self.stdout.flush
		self.writelines = self.stdout.writelines
	
	def raw_input(self, prompt=""):
		return raw_input(prompt)

	def close(self):
		self.stdout = None
		self.stdin = None
		self.closed = 1
		del self.read, self.readlines, self.xreadlines, self.write
		del self.flush, self.writelines

	def fileno(self): # ??? punt, since mostly used by readers
		return self.stdin.fileno()

	def isatty(self):
		return self.stdin.isatty() and self.stdout.isatty()

	def errlog(self, text):
		self.stderr.write("%s\n" % (text,))
		self.stderr.flush()

class ConsoleErrorIO(object):
	def __init__(self):
		self.stdin = sys.stdin
		self.stdout = sys.stderr
		self.stderr = sys.stderr
		self.mode = "rw"
		self.closed = 0
		self.softspace = 0
		# reading methods
		self.read = self.stdin.read
		self.readline = self.stdin.readline
		self.readlines = self.stdin.readlines
		self.xreadlines = self.stdin.xreadlines
		# writing methods
		self.write = self.stderr.write
		self.flush = self.stderr.flush
		self.writelines = self.stderr.writelines
	
	def raw_input(self, prompt=""):
		return raw_input(prompt)

	def close(self):
		self.stdout = None
		self.stdin = None
		self.closed = 1
		del self.read, self.readlines, self.xreadlines, self.write
		del self.flush, self.writelines

	def fileno(self): # ??? punt, since mostly used by readers
		return self.stdin.fileno()

	def isatty(self):
		return self.stdin.isatty() and self.stdout.isatty()

	def errlog(self, text):
		self.stderr.write("%s\n" % (text,))
		self.stderr.flush()


# themes define some basic "look and feel" for a CLI. This includes prompt srtrings and color set.
class Theme(object):
	NORMAL = RESET = ""
	BOLD = BRIGHT = ""
	BLACK = ""
	RED = ""
	GREEN = ""
	YELLOW = ""
	BLUE = ""
	MAGENTA = ""
	CYAN = ""
	WHITE = ""
	DEFAULT = ""
	GREY = ""
	BRIGHTRED = ""
	BRIGHTGREEN = ""
	BRIGHTYELLOW = ""
	BRIGHTBLUE = ""
	BRIGHTMAGENTA = ""
	BRIGHTCYAN = ""
	BRIGHTWHITE = ""
	UNDERSCORE = ""
	BLINK = ""
	help_local = WHITE
	help_inherited = YELLOW
	help_created = GREEN
	def __init__(self, ps1="> ", ps2="more> ", ps3="choose", ps4="-> "):
		self._ps1 = ps1 # main prompt
		self._ps2 = ps2 # more input needed
		self._ps3 = ps3 # choose prompt
		self._ps4 = ps4 # input prompt
		self._setcolors()
	def _set_ps1(self, new):
		self._ps1 = str(new)
	def _set_ps2(self, new):
		self._ps2 = str(new)
	def _set_ps3(self, new):
		self._ps3 = str(new)
	def _set_ps4(self, new):
		self._ps4 = str(new)
	ps1 = property(lambda s: s._ps1, _set_ps1, None, "primary prompt")
	ps2 = property(lambda s: s._ps2, _set_ps2, None, "more input needed")
	ps3 = property(lambda s: s._ps3, _set_ps3, None, "choose prompt")
	ps4 = property(lambda s: s._ps4, _set_ps4, None, "text input prompt")

class BasicTheme(Theme):
	def _setcolors(cls):
		"Base class for themes. Defines interface."
		cls.NORMAL = cls.RESET = "\x1b[0m"
		cls.BOLD = cls.BRIGHT = "\x1b[1m"
		cls.BLACK = ""
		cls.RED = ""
		cls.GREEN = ""
		cls.YELLOW = ""
		cls.BLUE = ""
		cls.MAGENTA = ""
		cls.CYAN = ""
		cls.WHITE = ""
		cls.DEFAULT = ""
		cls.GREY = ""
		cls.BRIGHTRED = ""
		cls.BRIGHTGREEN = ""
		cls.BRIGHTYELLOW = ""
		cls.BRIGHTBLUE = ""
		cls.BRIGHTMAGENTA = ""
		cls.BRIGHTCYAN = ""
		cls.BRIGHTWHITE = ""
		cls.UNDERSCORE = "\x1b[4m"
		cls.BLINK = "\x1b[5m"
		cls.help_local = cls.WHITE
		cls.help_inherited = cls.YELLOW
		cls.help_created = cls.GREEN
	_setcolors = classmethod(_setcolors)

class ANSITheme(BasicTheme):
	"""Defines tunable parameters for the UserInterface, to provide different color schemes and prompts."""
	def _setcolors(cls):
		# ANSI escapes for color terminals
		cls.NORMAL = cls.RESET = "\x1b[0m"
		cls.BOLD = cls.BRIGHT = "\x1b[01m"
		cls.BLACK = "\x1b[30m"
		cls.RED = "\x1b[31m"
		cls.GREEN = "\x1b[32m"
		cls.YELLOW = "\x1b[33m"
		cls.BLUE = "\x1b[34m"
		cls.MAGENTA = "\x1b[35m"
		cls.CYAN = "\x1b[36m"
		cls.WHITE = "\x1b[37m"
		cls.GREY = "\x1b[30;01m"
		cls.BRIGHTRED = "\x1b[31;01m"
		cls.BRIGHTGREEN = "\x1b[32;01m"
		cls.BRIGHTYELLOW = "\x1b[33;01m"
		cls.BRIGHTBLUE = "\x1b[34;01m"
		cls.BRIGHTMAGENTA = "\x1b[35;01m"
		cls.BRIGHTCYAN = "\x1b[36;01m"
		cls.BRIGHTWHITE = "\x1b[37;01m"
		cls.DEFAULT = "\x1b[39;49m"
		cls.UNDERSCORE = "\x1b[4m"
		cls.BLINK = "\x1b[5m"
		cls.help_local = cls.BRIGHTWHITE
		cls.help_inherited = cls.YELLOW
		cls.help_created = cls.GREEN
	_setcolors = classmethod(_setcolors)

DefaultTheme = ANSITheme

class UserInterface(object):
	"""An ANSI terminal user interface for CLIs.  """
	def __init__(self, io, env=None, theme=None):
		self._io = io
		self._env = env or environ.Environ()
		assert hasattr(self._env, "get")
		self._env["_"] = None
		self._cache = {}
		if io.isatty():
			self._termlen, self._termwidth, x, y = termtools.get_winsize(io.fileno())
		else:
			self._termlen, self._termwidth = 24, 80
		self.set_theme(theme)
		self._initfsm()
		self.initialize()

	winsize = property(lambda s: (s._termwidth, s._termlen), None, None, "Terminal size, if available")

	def __del__(self):
		try:
			self.finalize()
		except:
			pass

	def initialize(self, *args):
		pass

	def finalize(self):
		pass
	
	def close(self):
		if self._io is not None:
			self._io.close()
			self._io = None

	def set_environ(self, env):
		assert hasattr(env, "get")
		self._env = env
		self._env["_"] = None

	def set_theme(self, theme):
		self._theme = theme or DefaultTheme()
		assert isinstance(self._theme, Theme), "must supply a Theme object."
		self._env.setdefault("PS1", self._theme.ps1)
		self._env.setdefault("PS2", self._theme.ps2)
		self._env.setdefault("PS3", self._theme.ps3)
		self._env.setdefault("PS4", self._theme.ps4)

	def clone(self, theme=None):
		return self.__class__(self._io, self._env.copy(), theme or self._theme) 
	
	# output methods
	def Print(self, *objs):
		wr = self._io.write
		if objs:
			try:
				for obj in objs[:-1]:
					wr(str(obj))
					wr(" ")
				last = objs[-1]
				if last is not None: # don't NL if last value is None (works like trailing comma).
					wr(str(last))
					wr("\n")
			except PageQuitError:
				return
		else:
			wr("\n")
		self._io.flush()

	def pprint(self, obj):
		self._format(obj, 0, 0, {}, 0)
		self._io.write("\n")
		self._io.flush()
	
	def printf(self, text):
		"Print text run through the prompt formatter."
		self.Print(self.format(text))
	
	def print_obj(self, obj, nl=1):
		if nl:
			self._io.write("%s\n" % (obj,))
		else:
			self._io.write(str(obj))
		self._io.flush()

	def print_list(self, clist, indent=0):
		if clist:
			width = self._termwidth - 9
			indent = min(max(indent,0),width)
			ps = " " * indent
			try:
				for c in clist[:-1]:
					cs = "%s, " % (c,)
					if len(ps) + len(cs) > width:
						self.print_obj(ps)
						ps = "%s%s" % (" " * indent, cs)
					else:
						ps += cs
				self.print_obj("%s%s" % (ps, clist[-1]))
			except PageQuitError:
				pass

	def error(self, text):
		self.printf("%%R%s%%N" % (text,))

	# report-like methods for test framework
	def write(self, text):
		self._io.write(text)
	def writeline(self, text=""):
		self._io.writeline(text)
	def writelines(self, lines):
		self._io.writelines(lines)

	def add_heading(self, text, level=1):
		s = ["\n"]
		s.append("%s%s" % ("  "*(level-1), text))
		s.append("%s%s" % ("  "*(level-1), "-"*len(text)))
		self.Print("\n".join(s))

	def add_title(self, title):
		self.add_heading(title, 0)

	# called with the name of a logfile to report
	def logfile(self, filename):
		self._io.write("LOGFILE: <%s>\n" % (filename,))

	def add_message(self, msgtype, msg, level=1):
		self._io.write("%s%s: %s\n" % ("  "*(level-1), msgtype, msg))

	def add_summary(self, text):
		self._io.write(text)

	def add_text(self, text):
		self._io.write(text)

	def add_url(self, text, url):
		self._io.write("%s: <%s>\n" % (text, url))

	def passed(self, msg="", level=1):
		return self.add_message(self.format("%GPASSED%N"), msg, level)

	def failed(self, msg="", level=1):
		return self.add_message(self.format("%RFAILED%N"), msg, level)
	
    # XXX: new message type introduced for multiple UUTs	
    def completed(self, msg="", level=1):
		return self.add_message(self.format("%GCOMPLETED%N"), msg, level)

	def incomplete(self, msg="", level=1):
		return self.add_message(self.format("%yINCOMPLETE%N"), msg, level)

	def abort(self, msg="", level=1):
		return self.add_message(self.format("%YABORT%N"), msg, level)

	def info(self, msg, level=1):
        msg_type = "INFO [%s]" %  time.strftime('%H:%M:%S') 
		return self.add_message(msg_type, msg, level)

	def diagnostic(self, msg, level=1):
		return self.add_message(self.format("%yDIAGNOSTIC%N"), msg, level)
	
    def debug(self, msg, level=1):
		return self.add_message(self.format("%yDEBUG%N"), msg, level)


	def newpage(self):
		self._io.write("\x0c") # FF

	def newsection(self):
		self._io.write("\x0c") # FF
    
	# user input
	def _get_prompt(self, name, prompt=None):
		return PROMPT_START_IGNORE+self.format(prompt or self._env[name])+PROMPT_END_IGNORE

	def user_input(self, prompt=None):
		return self._io.raw_input(self._get_prompt("PS1", prompt))

	def more_user_input(self):
		return self._io.raw_input(self._get_prompt("PS2"))

	def choose(self, somelist, defidx=0, prompt=None):
		return cliutils.choose(somelist, defidx, self._get_prompt("PS3", prompt), input=self._io.raw_input)
	
	def get_text(self, msg=None):
		return cliutils.get_text(self._get_prompt("PS4"), msg, input=self._io.raw_input)

	def get_value(self, prompt, default=None):
		return cliutils.get_input(self.format(prompt), default, self._io.raw_input)

	def yes_no(self, prompt, default=True):
		yesno = cliutils.get_input(self.format(prompt), IF(default, "Y", "N"), self._io.raw_input)
		return yesno.upper().startswith("Y")

	def get_key(self, prompt=None, timeout=None, default=""):
		io = self._io
		if prompt:
			clear = "\b"*len(prompt)+" "*len(prompt)+"\b"*len(prompt)
			io.write(prompt)
			io.flush()
		if timeout is not None:
			try:
				c = timer.iotimeout(get_key, (io.fileno(),), timeout=timeout)
			except TimeoutError:
				c = default
		else:
			c = termtools.get_key(io.fileno())
		if prompt:
			io.write(clear) ; io.flush()
		return c
	
	def display(self, line):
		"""display a line of text, overwriting the old line."""
		self._io.write("\r"+str(line).strip())

	# docstring/help formatters
	def _format_doc(self, s, color):
		i = s.find("\n")
		if i > 0:
			return color+s[:i]+self._theme.NORMAL+s[i:]+"\n"
		else:
			return color+s+self._theme.NORMAL+"\n"

	def help_local(self, text):
		self.Print(self._format_doc(text, self._theme.help_local))

	def help_inherited(self, text):
		self.Print(self._format_doc(text, self._theme.help_inherited))
	
	def help_created(self, text):
		self.Print(self._format_doc(text, self._theme.help_created))

	def format(self, ps):
		"Expand percent-exansions in a string and return the result."
		self._fsm.process_string(ps)
		return self._getarg()

	def register_expansion(self, key, func):
		"""Register a percent-expansion function for the format method. The
		function must take one argument, and return a string. The argument is
		the character expanded on."""
		key = str(key)[0]
		if not self._EXPANSIONS.has_key(key):
			self._EXPANSIONS[key] = func
		else:
			raise ValueError, "expansion key %r already exists." % (key, )
	
	# FSM for prompt expansion
	def _initfsm(self):
		# maps percent-expansion items to some value.
		self._EXPANSIONS = {
					"I":self._theme.BRIGHT, 
					"N":self._theme.NORMAL, 
					"D":self._theme.DEFAULT,
					"R":self._theme.BRIGHTRED, 
					"G":self._theme.BRIGHTGREEN, 
					"Y":self._theme.BRIGHTYELLOW,
					"B":self._theme.BRIGHTBLUE, 
					"M":self._theme.BRIGHTMAGENTA, 
					"C":self._theme.BRIGHTCYAN, 
					"W":self._theme.BRIGHTWHITE, 
					"r":self._theme.RED, 
					"g":self._theme.GREEN, 
					"y":self._theme.YELLOW,
					"b":self._theme.BLUE, 
					"m":self._theme.MAGENTA, 
					"c":self._theme.CYAN, 
					"w":self._theme.WHITE, 
					"n":"\n", "l":self._tty, "h":self._hostname, "u":self._username, 
					"$": self._priv, "d":self._cwd, "L": self._shlvl, "t":self._time, 
					"T":self._date}
		f = FSM(0)
		f.add_default_transition(self._error, 0)
		# add text to args
		f.add_transition(ANY, 0, self._addtext, 0)
		# percent escapes
		f.add_transition("%", 0, None, 1)
		f.add_transition("%", 1, self._addtext, 0)
		f.add_transition("{", 1, self._startvar, 2)
		f.add_transition("}", 2, self._endvar, 0)
		f.add_transition(ANY, 2, self._vartext, 2)
		f.add_transition(ANY, 1, self._expand, 0)
		f.arg = ''
		self._fsm = f
	
	def _startvar(self, c, fsm):
		fsm.varname = ""

	def _vartext(self, c, fsm):
		fsm.varname += c

	def _endvar(self, c, fsm):
		fsm.arg += str(self._env.get(fsm.varname, fsm.varname))

	def _expand(self, c, fsm):
		try:
			arg = self._cache[c]
		except KeyError:
			try:
				arg = self._EXPANSIONS[c]
			except KeyError:
				arg = c
			else:
				if callable(arg):
					arg = str(arg(c))
		fsm.arg += arg

	def _username(self, c):
		un = os.environ.get("USERNAME") or os.environ.get("USER")
		if un:
			self._cache[c] = un
		return un
	
	def _shlvl(self, c):
		return str(self._env.get("SHLVL", ""))
	
	def _hostname(self, c):
		hn = os.uname()[1]
		self._cache[c] = hn
		return hn
	
	def _priv(self, c):
		if os.getuid() == 0:
			arg = "#"
		else:
			arg = ">"
		self._cache[c] = arg
		return arg
	
	def _tty(self, c):
		n = os.ttyname(self._io.fileno())
		self._cache[c] = n
		return n
	
	def _cwd(self, c):
		return os.getcwd()
	
	def _time(self, c):
		return time.strftime("%H:%M:%S", time.localtime())
	
	def _date(self, c):
		return time.strftime("%m/%d/%Y", time.localtime())

	def _error(self, input_symbol, fsm):
		self._io.errlog('Prompt string error: %s\n%r' % (input_symbol, fsm.stack))
		fsm.reset()

	def _addtext(self, c, fsm):
		fsm.arg += c

	def _getarg(self):
		if self._fsm.arg:
			arg = self._fsm.arg
			self._fsm.arg = ''
			return arg
		else:
			return None
	
	# pretty printing
	def _format(self, obj, indent, allowance, context, level):
		level = level + 1
		objid = id(obj)
		if objid in context:
			self._io.write(_recursion(obj))
			return
		rep = self._repr(obj, context, level - 1)
		typ = type(obj)
		sepLines = len(rep) > (self._termwidth - 1 - indent - allowance)
		write = self._io.write

		if sepLines:
			if typ is dict:
				write('{\n  ')
				length = len(obj)
				if length:
					context[objid] = 1
					indent = indent + 2
					items  = obj.items()
					items.sort()
					key, ent = items[0]
					rep = self._repr(key, context, level)
					write(rep)
					write(': ')
					self._format(ent, indent + len(rep) + 2, allowance + 1, context, level)
					if length > 1:
						for key, ent in items[1:]:
							rep = self._repr(key, context, level)
							write(',\n%s%s: ' % (' '*indent, rep))
							self._format(ent, indent + len(rep) + 2, allowance + 1, context, level)
					indent = indent - 2
					del context[objid]
				write('\n}')
				return

			if typ is list:
				write('[\n')
				self.print_list(obj, 2)
				write(']')
				return

			if typ is tuple:
				write('(\n')
				self.print_list(obj, 2)
				if len(obj) == 1:
					write(',')
				write(')')
				return

		write(rep)

	def _repr(self, obj, context, level):
		return self._safe_repr(obj, context.copy(), None, level)

	def _safe_repr(self, obj, context, maxlevels, level):
		return _safe_repr(obj, context, maxlevels, level)

# Return repr_string
def _safe_repr(obj, context, maxlevels, level):
	typ = type(obj)
	if typ is str:
		if 'locale' not in sys.modules:
			return repr(obj)
		if "'" in obj and '"' not in obj:
			closure = '"'
			quotes = {'"': '\\"'}
		else:
			closure = "'"
			quotes = {"'": "\\'"}
		qget = quotes.get
		sio = StringIO()
		write = sio.write
		for char in obj:
			if char.isalpha():
				write(char)
			else:
				write(qget(char, `char`[1:-1]))
		return ("%s%s%s" % (closure, sio.getvalue(), closure))

	if typ is dict:
		if not obj:
			return "{}"
		objid = id(obj)
		if maxlevels and level > maxlevels:
			return "{...}"
		if objid in context:
			return _recursion(obj)
		context[objid] = 1
		components = []
		append = components.append
		level += 1
		saferepr = _safe_repr
		for k, v in obj.iteritems():
			krepr = saferepr(k, context, maxlevels, level)
			vrepr = saferepr(v, context, maxlevels, level)
			append("%s: %s" % (krepr, vrepr))
		del context[objid]
		return "{%s}" % ", ".join(components)

	if typ is list or typ is tuple:
		if typ is list:
			if not obj:
				return "[]"
			format = "[%s]"
		elif len(obj) == 1:
			format = "(%s,)"
		else:
			if not obj:
				return "()"
			format = "(%s)"
		objid = id(obj)
		if maxlevels and level > maxlevels:
			return format % "..."
		if objid in context:
			return _recursion(obj)
		context[objid] = 1
		components = []
		append = components.append
		level += 1
		for o in obj:
			orepr = _safe_repr(o, context, maxlevels, level)
			append(orepr)
		del context[objid]
		return format % ", ".join(components)

	if typ is MethodType:
		return method_repr(obj)

	rep = repr(obj)
	return rep

def _recursion(obj):
	return ("<Recursion on %s with id=%s>" % (type(obj).__name__, id(obj)))

def safe_repr(value):
	return _safe_repr(value, {}, None, 0)

def method_repr(method):
	methname = method.im_func.func_name
	# formal names
	varnames = list(method.im_func.func_code.co_varnames)[1:method.im_func.func_code.co_argcount]
	if method.im_func.func_defaults:
		ld = len(method.im_func.func_defaults)
		varlist = [", ".join(varnames[:-ld]), 
				   ", ".join(["%s=%r" % (n, v) for n, v in zip(varnames[-ld:], method.im_func.func_defaults)])]
		return "%s(%s)" % (methname, ", ".join(varlist))
	else:
		return "%s(%s)" % (methname, ", ".join(varnames))

def _reset_readline():
	if readline:
		readline.parse_and_bind("tab: complete")
		readline.parse_and_bind("?: possible-completions")
		readline.parse_and_bind("set horizontal-scroll-mode on")
		readline.parse_and_bind("set page-completions on")
		readline.set_history_length(500)

def get_history_file(obj):
	"Utility to form a useful history file name from an object instance."
	return os.path.join(os.environ["HOME"], ".hist_%s" % (obj.__class__.__name__,))

class CommandParser(object):
	"""Reads an IO stream and parses input similar to Bourne shell syntax.
	Calls command methods for each line. Handles readline completer."""
	VARCHARS = r'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_?'
	_SPECIAL = {"r":"\r", "n":"\n", "t":"\t", "b":"\b"}
	def __init__(self, cmdobj=None, logfile=None, historyfile=None):
		self.reset(cmdobj)
		self._logfile = logfile
		if historyfile:
			self._historyfile = os.path.expanduser(os.path.expandvars(str(historyfile)))
		else:
			self._historyfile = None
		self._init()
		if readline:
			if self._historyfile:
				try:
					readline.read_history_file(self._historyfile)
				except:
					pass

	def _rl_completer(self, text, state):
		if state == 0:
			curr = readline.get_line_buffer()
			b = readline.get_begidx()
			if b == 0:
				complist = self._cmd.get_completion_scope("commands")
			else: # complete based on scope keyed on previous word
				word = curr[:b].split()[-1]
				complist = self._cmd.get_completion_scope(word)
			self._complist = filter(lambda s: s.startswith(text), complist)
		try:
			return self._complist[state]
		except IndexError:
			return None

	def close(self):
		self.reset()

	def __del__(self):
		if readline:
			if self._historyfile:
				try:
					readline.write_history_file(self._historyfile)
				except:
					pass

	def reset(self, newcmd=None):
		self._cmds = []
		self._cmd = None
		self.arg_list = []
		self._buf = ""
		if newcmd:
			self.push_command(newcmd)
	
	commands = property(lambda s: s._cmd, None, None)

	def push_command(self, newcmd):
		lvl = int(newcmd._environ.setdefault("SHLVL", 0))
		newcmd._environ["SHLVL"] = lvl+1
		self._cmds.append(newcmd)
		self._cmd = newcmd # current command holder
		cmdlist = newcmd.get_commands()
		newcmd.add_completion_scope("commands", cmdlist )
		newcmd.add_completion_scope("help", cmdlist )

	def pop_command(self, returnval=None):
		cmd = self._cmds.pop()
		cmd.finalize()
		if self._cmds:
			self._cmd = self._cmds[-1]
			if returnval:
				self._cmd.handle_subcommand(returnval)
		else:
			raise CommandQuit, "last command object quit."

	def command_setup(self, obj, prompt=None):
		if self._cmd:
			self._cmd._setup(obj, prompt)

	def parse(self, url):
		import urllib
		fo = urllib.urlopen(url)
		self.parseFile(fo)
		fo.close()

	def parseFile(self, fo):
		data = fo.read(4096)
		while data:
			self.feed(data)
			data = fo.read(4096)

	def interact(self, cmd=None):
		_reset_readline()
		if cmd and isinstance(cmd, BaseCommands):
			self.push_command(cmd)
		if readline:
			oc = readline.get_completer()
			readline.set_completer(self._rl_completer)
		try:
			try:
				while 1:
					ui = self._cmd._ui
					try:
						line = ui.user_input()
						if not line:
							continue
						while self.feed(line+"\n"):
							line = ui.more_user_input()
					except EOFError:
						self._cmd._print()
						self.pop_command()
			except (CommandQuit, CommandExit): # last command does this
				pass
		finally:
			if readline:
				readline.set_completer(oc)
				if self._historyfile:
					try:
						readline.write_history_file(self._historyfile)
					except:
						pass

	def feed(self, text):
		if self._logfile:
			self._logfile.write(text)
		text = self._buf + text
		i = 0 
		for c in text:
			i += 1
			try:
				self._fsm.process(c)
				while self._fsm.stack:
					self._fsm.process(self._fsm.pop())
			except EOFError:
				self.pop_command()
			except CommandQuit:
				val = sys.exc_info()[1]
				self.pop_command(val.value)
			except NewCommand, cmdex:
				self.push_command(cmdex.value)
		if self._fsm.current_state: # non-zero, stuff left
			self._buf = text[i:]
		return self._fsm.current_state

	def _init(self):
		f = FSM(0)
		f.arg = ""
		f.add_default_transition(self._error, 0)
		# normally add text to args
		f.add_transition(ANY, 0, self._addtext, 0)
		f.add_transition_list(" \t", 0, self._wordbreak, 0)
		f.add_transition_list(";\n", 0, self._doit, 0)
		# slashes
		f.add_transition("\\", 0, None, 1)
		f.add_transition("\\", 3, None, 6)
		f.add_transition(ANY, 1, self._slashescape, 0)
		f.add_transition(ANY, 6, self._slashescape, 3)
		# vars 
		f.add_transition("$", 0, self._startvar, 7)
		f.add_transition("{", 7, self._vartext, 9)
		f.add_transition_list(self.VARCHARS, 7, self._vartext, 7)
		f.add_transition(ANY, 7, self._endvar, 0)
		f.add_transition("}", 9, self._endvar, 0)
		f.add_transition(ANY, 9, self._vartext, 9)
		# vars in singlequote
		f.add_transition("$", 3, self._startvar, 8)
		f.add_transition("{", 8, self._vartext, 10)
		f.add_transition_list(self.VARCHARS, 8, self._vartext, 8)
		f.add_transition(ANY, 8, self._endvar, 3)
		f.add_transition("}", 10, self._endvar, 3)
		f.add_transition(ANY, 10, self._vartext, 10)

		# single quotes quote all
		f.add_transition("'", 0, None, 2)
		f.add_transition("'", 2, self._singlequote, 0)
		f.add_transition(ANY, 2, self._addtext, 2)
		# double quotes allow embedding word breaks and such
		f.add_transition('"', 0, None, 3)
		f.add_transition('"', 3, self._doublequote, 0)
		f.add_transition(ANY, 3, self._addtext, 3)
		# single-quotes withing double quotes
		f.add_transition("'", 3, None, 5)
		f.add_transition("'", 5, self._singlequote, 3)
		f.add_transition(ANY, 5, self._addtext, 5)
		# back-tick substitution
		f.add_transition("`", 0, None, 12)
		f.add_transition(ANY, 12, self._addtext, 12)
		f.add_transition("`", 12, self._do_backtick, 0)
		self._fsm = f

	def _startvar(self, c, fsm):
		fsm.varname = c

	def _vartext(self, c, fsm):
		fsm.varname += c

	def _endvar(self, c, fsm):
		if c == "}":
			fsm.varname += c
		else:
			fsm.push(c)
		try:
			fsm.arg += self._cmd._environ.expand(fsm.varname)
		except:
			ex, val, tb = sys.exc_info()
			self._cmd._ui.error("Could not expand variable %r: %s (%s)" % (fsm.varname, ex, val))

	def _error(self, input_symbol, fsm):
		self._cmd._ui.error('Syntax error: %s\n%r' % (input_symbol, fsm.stack))
		fsm.reset()

	def _addtext(self, c, fsm):
		fsm.arg += c

	def _wordbreak(self, c, fsm):
		if fsm.arg:
			self.arg_list.append(fsm.arg)
			fsm.arg = ''

	def _slashescape(self, c, fsm):
		fsm.arg += CommandParser._SPECIAL.get(c, c)

	def _singlequote(self, c, fsm):
		self.arg_list.append(fsm.arg)
		fsm.arg = ''

	def _doublequote(self, c, fsm):
		self.arg_list.append(fsm.arg)
		fsm.arg = ''

	def _doit(self, c, fsm):
		if fsm.arg:
			self.arg_list.append(fsm.arg)
			fsm.arg = ''
		args = self.arg_list
		self.arg_list = []
		self._cmd(args) # call command object with argv

	def _do_backtick(self, c, fsm):
		if fsm.arg:
			self.arg_list.append(fsm.arg)
			fsm.arg = ''
		io = StringIO()
		sys.stdout.flush()
		sys.stdout = sys.stdin = io
		try:
			subcmd = self._cmd.subshell(io)
			subparser = CommandParser(subcmd, self._logfile)
			try:
				subparser.feed(self.arg_list.pop()+"\n")
			except:
				ex, val, tb = sys.exc_info()
				print >>sys.stderr, "  *** %s (%s)" % (ex, val)
		finally:
			sys.stdout = sys.__stdout__
			sys.stdin = sys.__stdin__
		fsm.arg += io.getvalue().strip()

# get a cli built from sys.argv
def run_cli_wrapper(argv, wrappedclass=Shell, cliclass=GenericCLI, theme=None):
	"""Instantiate a class object (the wrappedclass), and run a CLI wrapper on it."""
	import getopt
	logfile = sourcefile = None
	paged = False
	try:
		optlist, args = getopt.getopt(argv[1:], "?hgs:", ["help", "script="])
	except getopt.GetoptError:
			print wrappedclass.__doc__
			return
	for opt, val in optlist:
		if opt in ("-?", "-h", "--help"):
			print run_cli_wrapper.__doc__
			return
		elif opt == "-s" or opt == "--script":
			sourcefile = val
		elif opt == "-g":
			paged = True
		elif opt == "-l" or opt == "--logfile":
			logfile = file(val, "w")
	if args:
		targs, kwargs = breakout_args(args)
	else:
		targs, kwargs = (), {}
	try:
		obj = apply(wrappedclass, targs, kwargs)
	except (ValueError, TypeError):
		print "Bad parameters."
		print wrappedclass.__doc__
		return
	if paged:
		io = termtools.PagedIO()
	else:
		io = ConsoleIO()
	ui = UserInterface(io, None, theme)
	cmd = get_generic_cmd(obj, ui, cliclass)
	cmd._export("PS1", "%%I%s%%N(%s%s%s)> " % (wrappedclass.__name__,
				", ".join(map(repr, targs)),  IF(kwargs, ", ", ""),
				", ".join(map(lambda t: "%s=%r" % t, kwargs.items()))) )
	cli = CommandParser(cmd, logfile)
	if sourcefile:
		cli.parse(sourcefile)
	else:
		cli.interact()


def run_cli(cmdclass, io, env=None, logfile=None, theme=None, historyfile=None):
	ui = UserInterface(io, env, theme)
	cmd = cmdclass(ui)
	parser = CommandParser(cmd, logfile, historyfile)
	parser.interact()

def run_generic_cli(cmdclass=BaseCommands):
	env = environ.Environ()
	env.inherit()
	io = ConsoleIO()
	run_cli(cmdclass, io, env)

# factory for Command classes. Returns a parser.
def get_cli(cmdclass, env=None, aliases=None, logfile=None, paged=False, theme=None, historyfile=None):
	if paged:
		io = termtools.PagedIO()
	else:
		io = ConsoleIO()
	ui = UserInterface(io, env, theme)
	cmd = cmdclass(ui, aliases)
	parser = CommandParser(cmd, logfile, historyfile)
	return parser

def get_terminal_ui(env=None, paged=False, theme=None):
	if paged:
		io = termtools.PagedIO()
	else:
		io = ConsoleIO()
	return UserInterface(io, env, theme)

def get_ui(ioc=ConsoleIO, uic=UserInterface, themec=DefaultTheme, env=None):
	io = ioc()
	theme = themec()
	return uic(io, env, theme)

def get_key(fd):
	savestate = termtools.tcgetattr(fd)
	try:
		termtools.setraw(fd)
		return os.read(fd, 1)
	finally:
		termtools.tcsetattr(fd, termtools.TCSAFLUSH, savestate)


#### self test

# models a BaseCommands class, but only prints argv (used to test parser)
class _CmdTest(BaseCommands):

	def __call__(self, argv):
		self._print("argv: ")
		self._print(str(argv))
		self._print("\n")
		return 0


if __name__ == "__main__":
	env = environ.Environ()
	env.inherit()
	io = ConsoleIO()
	#io = termtools.PagedIO()
	print "======================="
	run_cli(_CmdTest, io, env)
	print "======================="
	env["PS1"] = "CLItest> "
	ui = UserInterface(io, env, DefaultTheme())
	cmd = BaseCommands(ui)
	cmd = cmd.clone(DictCLI)
	cmd._setup({"testkey":"testvalue"}, "dicttest> ")
	parser = CommandParser(cmd)
	parser.interact()


	f = UserInterface(ConsoleIO(), env, DefaultTheme())
	print f.format("%T %t")
	print f.format("%Ibright%N")

	print f.format("%rred%N")
	print f.format("%ggreen%N")
	print f.format("%yyellow%N")
	print f.format("%bblue%N")
	print f.format("%mmagenta%N")
	print f.format("%ccyan%N")
	print f.format("%wwhite%N")

	print f.format("%Rred%N")
	print f.format("%Ggreen%N")
	print f.format("%Yyellow%N")
	print f.format("%Bblue%N")
	print f.format("%Mmagenta%N")
	print f.format("%Ccyan%N")
	print f.format("%Wwhite%N")

	print f.format("%Ddefault%N")
	print f.format("wrapped%ntext")
	print f.format("%l tty %l")
	print f.format("%h hostname %h")
	print f.format("%u username %u")
	print f.format("%$ priv %$")
	print f.format("%d cwd %d")
	print f.format("%L SHLVL %L")
	print f.format("%{PS4}")

