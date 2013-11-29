#!/usr/bin/python
# -*- coding: ascii -*-
# vim:ts=4:sw=4
# License: LGPL
# Keith Dart <kdart@kdart.com>

"""
A library for scheduling callback functions using SIGALRM. When used,
this module "owns" SIGALRM, and all timing functions associated with it.
This means that you should not use the stock time.sleep() function when
using this module.	Instead, use get_scheduler().sleep(x) to sleep.

"""

import signal
from errno import EINTR
from nmsbuiltins import add_exception
try:
	import itimer
except ImportError:
	import sys
	print >>sys.stderr, """scheduler: Try installing the py-itimer package for more precise timing."""
	alarm = signal.alarm
	del sys
else:
	alarm = itimer.alarm # allows subsecond precision using floats

#import readline
#readline.set_event_hook(lambda:None)
#del readline

__all__ = ["get_scheduler"]


def insort(a, x, lo=0, hi=None):
	if hi is None:
		hi = len(a)
	while lo < hi:
		mid = (lo+hi) // 2
		if x < a[mid]: 
			hi = mid
		else: 
			lo = mid+1
	a.insert(lo, x)
	return lo

class TimeoutError(Exception):
	pass
add_exception(TimeoutError)

class _Event(object):
	def __init__(self, delay, callback, args, repeat):
		self.delay = delay # tracks actual delay needed
		self.interval = delay # set interval
		self.callback = callback
		self.args = args
		self.repeat = repeat

	def __str__(self):
		return "%s%r runs in %d seconds." % (self.callback.__name__, self.args, self.delay)

	def __repr__(self):
		return "%s(%r, %r, %r, %r)" % (self.__class__.__name__, self.interval, self.callback.__name__, self.args, self.repeat)

	def __lt__(self, other):
		return self.delay < other.delay

	def __gt__(self, other):
		return self.delay > other.delay

	# to match events exactly for index()
	def __eq__(self, other):
		return self is other

	def adjust(self, adj):
		self.delay -= adj

	def reset(self):
		self.delay = self.interval

	def stop(self):
		remove(self)

	def __call__(self):
		apply(self.callback, self.args)


NULL = lambda: None

# Probably a lot of race conditions here... but I hope it works most of the
# time.
class Scheduler(object):
	"""A Scheduler instance uses SIGALRM to schedule callback functions. It
	does too much work in the signal handler, so it should really only be used
	with infrequently scheduled events."""
	def __init__(self, alarm=alarm):
		self.eventq = []
		self.alarm = alarm
		self.timeremaining = self.alarm(0)
		self._oldhandler = signal.signal(signal.SIGALRM, self._alarm_handler)
		self._sleepflag = 0
		self._timeout_flags = {}
		self._running = True

	def _alarm_handler(self, signum, frame):
		d = self.eventq[0].delay
		self._adjust(d)
		self._run_event(self.eventq.pop(0))
		#self._runq()
		if self.eventq:
			self.alarm(self.eventq[0].delay)

	def _adjust(self, adj):
		map(lambda ev: ev.adjust(adj), self.eventq)

	def _runq(self):
		# run any events that would be due or past due
		while self.eventq:
			if self.eventq[0].delay <= 0:
				self._run_event(self.eventq.pop(0))
			else:
				break

	def _run_event(self, ev):
		ev()
		if ev.repeat:
			ev.reset()
			self.add_event(ev)

	def __str__(self):
		i = 0
		s = ["scheduled events:"]
		for ev in self.eventq:
			s.append("	%2d: %s" % (i, ev))
			i += 1
		return "\n".join(s)

	def __nonzero__(self):
		return len(self.eventq)

	def add_event(self, event):
		rem = self.alarm(0)
		if rem == 0:
			rem = 2147483646 # if zero it would disable the timer
		if self.eventq:
			self._adjust(self.eventq[0].delay - rem)
		insort(self.eventq, event)
		self.alarm(min(rem, self.eventq[0].delay)) # smallest delay

	def remove(self, event):
		"""remove(event)
Removes the event from the event queue. The event is an Event object as
returned by the add or getevents methods."""
		left = self.alarm(0)
		try:
			i = self.eventq.index(event)
		except ValueError:
			pass
		else:
			if i == 0: # currently scheduled event time
				ev = self.eventq.pop(0)
				self._adjust(ev.delay-left)
				self._runq()
				if self.eventq:
					self.alarm(self.eventq[0].delay)
			else:
				del self.eventq[i]
				self.alarm(left)

	def clear(self):
		self.alarm(0)
		del self.eventq[:]

	def __delitem__(self, ind):
		del self.eventq[ind]

	def __getitem__(self, ind):
		return self.eventq[ind]

	def getevents(self):
		return self.eventq[:]

	def stop(self):
		if self._running:
			self.timeremaining = self.alarm(0)
			signal.signal(signal.SIGALRM, self._oldhandler)
			self._running = False

	def start(self):
		if not self._running:
			self._oldhandler = signal.signal(signal.SIGALRM, self._alarm_handler)
			if self.eventq:
				self.alarm(self.timeremaining)
			self._running = True

	def add(self, delay, pri=0, callback=NULL, args=(), repeat=0):
		"""add(delay, priority, callbackfunction, callbackargs, [repeatflag])
Creates an Event object and adds it to the event queue. Returns the event
object. The callback will be run with the supplied arguments, after the elapsed
interval. If the repeat flag is given the job is rescheduled indefinitely."""
		assert delay > 0
		event = _Event(delay, callback, args, repeat) 
		self.add_event(event)
		return event

	def _sleep_cb(self):
		self._sleepflag = 1

	def sleep(self, delay):
		"""sleep(<secs>)
Pause the current thread of execution for <secs> seconds. Use this
instead of time.sleep() since it works with the scheduler, and allows
other events to run.  """
		self._sleepflag = 0
		self.add(delay, 0, self._sleep_cb)
		while 1:
			signal.pause()
			if self._sleepflag:
				return

	def _timeout_cb(self):
		raise TimeoutError, "timer expired"

	# An abstraction of basic timeout patterns. Perform functions that may
	# block, but with a timeout as a failsafe method to return control to the
	# caller. These functions will raise the TimeoutError exception when the
	# specified timout (in seconds) is reached.
	def timeout(self, function, args=(), kwargs={}, timeout=30):
		"""Wraps a normal thread of execution. Will raise TimeoutError when the
timeout value is reached."""
		to = self.add(timeout, 1, self._timeout_cb)
		try:
			return function(*args, **kwargs)
		finally:
			self.remove(to)
	
	def iotimeout(self, function, args=(), kwargs={}, timeout=30):
		"""Wraps an IO function that may block in the kernel. Provides a
timeout feature."""
		self._timed_out = 0
		ev = self.add(timeout, 1, self._timedio_cb)
		try:
			while 1:
				try:
					rv = function(*args, **kwargs)
				except EnvironmentError, val:
					if val.errno == EINTR:
						if self._timed_out:
							raise TimeoutError
						else:
							continue
					else:
						raise
				else:
					break
		finally:
			self.remove(ev)
		return rv

	def _timedio_cb(self):
		self._timed_out = 1


# alarm schedulers are singleton instances. Only use this factory function to
# get it.
def get_scheduler():
	global scheduler
	try:
		return scheduler
	except NameError:
		scheduler = Scheduler()
		return scheduler

def del_scheduler():
	global scheduler
	scheduler.stop()
	del scheduler

def sleep(secs):
	get_scheduler().sleep(secs)

def timeout(*args, **kwargs):
	return get_scheduler().timeout(*args, **kwargs)

def iotimeout(*args, **kwargs):
	return get_scheduler().iotimeout(*args, **kwargs)

def add(delay, pri=0, callback=NULL, args=(), repeat=0):
	return get_scheduler().add(delay, pri, callback, args, repeat)

def remove(event):
	# scheduler must already exist if you have an event to remove.
	scheduler.remove(event)

def repeat(interval, method, *args):
	s = get_scheduler()
	return s.add(interval, 0, method, args, 1)


if __name__ == "__main__":
	import os
	os.system("qaunittest test_scheduler")


