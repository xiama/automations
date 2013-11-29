#!/usr/bin/env python
import os,sys,re,time,subprocess,select,fcntl,signal
import Queue
import threading
import signal
import datetime

class Proc(object):
    def __init__(self, cmd, shell=True, stdin=subprocess.PIPE):
        self.cmd = cmd
        self.output = []
        self.lastoutput = []
        self.input = []
        self.proc = subprocess.Popen(cmd, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0, shell=shell)
            #preexec_fn=os.setsid
    def __read_output__(self, timeout=1):
        outfds, infds, errfds = select.select([self.proc.stdout], [], [], timeout)
        if len(outfds) != 0:
            flags = fcntl.fcntl(outfds[0], fcntl.F_GETFL, 0)
            fcntl.fcntl(outfds[0], fcntl.F_SETFL, flags | os.O_NONBLOCK)
            s = outfds[0].read()
            if s != '':
                self.lastoutput.append(s)
                self.output.append(s)
                return 0
            else:
                return 1
        else:
            return 1

    def __write_input__(self, input_data, timeout=1):
        outfds, infds, errfds = select.select([], [self.proc.stdin], [], timeout)
        if len(infds) != 0:
            flags = fcntl.fcntl(infds[0], fcntl.F_GETFL, 0)
            fcntl.fcntl(infds[0], fcntl.F_SETFL, flags | os.O_NONBLOCK)
            infds[0].write(input_data)
            return 0
        else:
            return 1

    def input_cmd(self, cmd, timeout=3):
        self.input.append(cmd)
        print "\nCommand: ", cmd
        return self.__write_input__(cmd, timeout)

    def kill(self, sig=signal.SIGTERM):
        self.proc.send_signal(sig)
        if sig == signal.SIGTERM or sig == signal.SIGKILL:
            time.sleep(1)
            if self.proc.poll() == None:
                return 1
            else:
                return 0
        return 0

    def wait(self, delay=2, count=5):
        '''Wait delay*count seconds for process to finish'''
        while count > 0:
            count -= 1
            retcode = self.proc.poll()
            if retcode != None:
                return retcode
            time.sleep(delay)
        return None

    def grep_output(self, regex, delay=3, count=5, flag=re.S, show_output=True):
        pattern = re.compile(regex)
        ret = 1
        while count > 0:
            count -= 1
            self.__read_output__(delay)
            match_lst = pattern.findall(''.join(self.output), flag)
            if match_lst != []:
                ret = 0
                print "According to regex '%s', found %s" % (regex, match_lst)
                break
            time.sleep(delay)
        if ret == 1:
            print "Regex '%s' didn't match any string in the output" % (regex)
        if show_output == True:
            self.print_lastoutput()
        return ret

    def get_full_output(self, delay=3, count=5):
        retry = count
        while count > 0:
            count -= 1
            if self.__read_output__(1) == 0:
                count = retry
            time.sleep(delay)
        return ''.join(self.output)

    def print_lastoutput(self, timeout=1):
        self.__read_output__(timeout)
        print '<***********last output of the proc************>'
        sys.stdout.write(''.join(self.lastoutput))
        print '<*************end of last output***************>'
        self.lastoutput = []

    def print_output(self, timeout=1):
        self.__read_output__(timeout)
        print '<***********full output of the proc************>'
        sys.stdout.write(''.join(self.output))
        print '<*************end of full output***************>'


class AsynchronousFileReader(threading.Thread):
    def __init__(self, fd, queue, quiet=False):
        threading.Thread.__init__(self)
        self.daemon = True
        self._fd = fd
        self._queue = queue
        self._stop = False
        self._quiet = quiet

    def stop(self):
        self._stop = True

    def run(self):
        for line in iter(self._fd.readline, ''):
            if not self._quiet:
                sys.stdout.write(line)
                self._queue.put(line, timeout=3)
            if self._stop == True:
                self._fd.close()
                return

    def eof(self):
        return not self.is_alive() and self._queue.empty()

class ProcNonBlock(object):
    def __init__(self, cmd, quiet=False):
        if not quiet:
            print "\nCommand: %s" % (cmd)
        self.cmd = cmd
        self._output = []
        self._queue = Queue.Queue()
        self._proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0, shell=True)
        self._reader = AsynchronousFileReader(self._proc.stdout, self._queue, quiet)
        self._reader.start()

    def __del__(self):
        try:
            self.kill()
        except OSError:
            pass

    def kill(self, sig=signal.SIGKILL):
        self._reader.stop()
        self._proc.terminate()

    def poll(self):
        return self._proc.poll()

    def wait(self, timeout=None):
        begin_time = datetime.datetime.now()
        if timeout == None:
            self._proc.wait()
            return self._proc.poll()
        while self._proc.poll() == None and (datetime.datetime.now() - begin_time).seconds < timeout:
            time.sleep(1)
        return self._proc.poll()

    # If no new output generated within 10 secs, kill the subprocess
    def wait_output(self, timeout=10):
        begin_time = datetime.datetime.now()
        prev_size = self._queue.qsize()
        while (datetime.datetime.now() - begin_time).seconds < timeout:
            time.sleep(1)
            cur_size = self._queue.qsize()
            if cur_size != prev_size:
                begin_time = datetime.datetime.now()
            prev_size = cur_size

    def output(self):
        while not self._queue.empty():
            self._output.append(self._queue.get(timeout=3))
        return ''.join(self._output)
