#!/usr/bin/python
# ********************************************************************************
#
#             COPYRIGHT 2013-2018 MOTOROLA SOLUTIONS INC. ALL RIGHTS RESERVED.
#                    MOTOROLA SOLUTIONS CONFIDENTIAL RESTRICTED
#                            TEMPLATE VERSION R01.03
#
# *******************************************************************************

from subprocess import Popen, PIPE, STDOUT
import os, errno
import logging
from threading import Timer, Lock
import signal


class CommandRunner:
    """ Supports running command line commands and gathering of results. """

    NO_LOG = -1
    DEFAULT_TIMEOUT_IN_SECONDS = 180

    def __init__(self, stderr=STDOUT, stdout=PIPE, echoCommand=False):
        self.logDecorator = self.NO_LOG
        self.stderr = stderr
        self.stdout = stdout
        self.echoCommand = echoCommand
        self.processTreeKiller = None
        self.processHandler = None
        self.processLock = Lock()

    def runCommand(self, command, logDecorator, env=None, timeout=DEFAULT_TIMEOUT_IN_SECONDS):
        """
        Passes command to the system and returns a data structure containing the return code of the command
        ran in the shell and the output stream containing both stdout and stderr.


            command - command to pass to the shell to run
            logDecorator - string to prefix each logging.info log entry with or
                           CommandRunner.NO_LOG to run command without logging
            env - dictionary with environment variables to be added to shell
                  environment before running command
            timeout - max time in seconds to allow for shell command to run.

        """
        self.processLock.acquire()
        try:
            if env is None:
                env = {}

            self.logDecorator = logDecorator

            if self.echoCommand:
                print("runCommand(%s %s)" % (command, env))
            logging.info("runCommand(%s %s)" % (command, env))

            self.processHandler = ProcessHandler(self.stderr, self.stdout, self.processTreeKiller)
            out, returnCode = self.processHandler.createProcessAndRun(command, self.__getLocalEnvironment(command, env), timeout)
        finally:
            self.processLock.release()

        return self.__createCommandRunnerResults(out, returnCode)

    def __createCommandRunnerResults(self, out, returnCode):
        # split the output into list of strings without LF's
        commandResult = CommandResult()
        if out is None:
            out = ""
        try:
            commandResult.out = out.decode('utf8').rstrip().splitlines()  # for python2
        except Exception as e:
            commandResult.out = out.rstrip().splitlines()   # for python 3

        commandResult.returnCode = returnCode

        # log the output
        if self.logDecorator != self.NO_LOG:
            for line in commandResult.out:
                logging.info("%s: %s" % (self.logDecorator, line))
        return commandResult

    def __getLocalEnvironment(self, command, env):
        newEnv = dict(os.environ)
        keyText = ""
        for key in env:
            newEnv[key] = env[key]  # store the new key into the environment
            keyText += " %s=%s" % (key, env[key])

        # log command if desired
        if self.logDecorator != self.NO_LOG:
            logging.info("%s: %s" % (self.logDecorator + keyText, command))

        return newEnv

    def stop_process(self, options=None):
        if self.processHandler:
            self.processHandler.stop_process(options)

class ProcessHandler:
    """
    CommandRunner delegates to this class to handle the subprocess command and the error handling for
    timeouts.
    """
    popen_lock = Lock()

    def __init__(self, stderr, stdout, processTreeKiller=None):
        self.currentCommandTimedOut = False
        self.stopProcessNotCalled = True
        self.actualTimeout = False
        self.pipe = None
        self.env = {}
        self.command = ""
        self.timeout = 0
        self.stderr = stderr
        self.stdout = stdout
        self.pidKillList = []
        self.processTreeKiller = processTreeKiller
        self.platform_type = ""

    def createProcessAndRun(self, command, env, timeout):
        """
        Actually handles the subprocess command to run, returning stdout and stderr in the same stream along
        with the shell return code.
        """
        self.env = env
        self.command = command
        self.timeout = timeout
        # ~ logging.info("CommandRunner: createProcessAndRun for command %s" % command)

        self.platform_type = os.name
        if self.platform_type == "nt":
            self.platform_type = "Windows"

        self.__createPipeWithCombinedOutAndErrStreams(self.stderr, self.stdout)
        out = self.__runCommandWithTimeout()

        if self.currentCommandTimedOut and self.stopProcessNotCalled:
            logging.critical("Command '" + command + "' timed out")

        if self.actualTimeout:
            logging.critical("Command '" + command + "' actually timed out")

        return out, self.pipe.returncode

    def __runCommandWithTimeout(self):
        if self.processTreeKiller:
            errorTimer = Timer(self.timeout, self._timeoutProcessFamilyTree)
        elif self.platform_type == "Windows":
            errorTimer = Timer(self.timeout, self.__killProcess, [self.pipe])
        else:
            errorTimer = Timer(self.timeout, self._timeoutProcessTree)

        try:
            errorTimer.start()
            out, err = self.pipe.communicate()
        finally:
            errorTimer.cancel()
        return out

    def _timeoutProcessFamilyTree(self):
        self.processTreeKiller.timeoutProcessFamilyTree()
        self.currentCommandTimedOut = True
        self.actualTimeout = True

    def _timeoutProcessTree(self):
        parentPid = self.pipe.pid
        logging.warn('CommandRunner: _timeoutProcessTree - process timing out pid is %s' % parentPid)
        self.pidKillList.append(parentPid)

        self._findAllChildren(parentPid)

        for processToKill in self.pidKillList:
            logging.warn('CommandRunner: _timeoutProcessTree - timing out child, pid is %s' % int(processToKill))

            os.kill(int(processToKill), signal.SIGKILL)
            self.currentCommandTimedOut = True
            self.actualTimeout = True

    def _findAllChildren(self, startPid):
        checkIfParentList = []
        childrenList = self._getChildrenOfPid(startPid)

        if childrenList:
            for child in childrenList:
                checkIfParentList.append(child)

            while checkIfParentList:
                currentPidToCheck = checkIfParentList.pop(0)
                self.pidKillList.append(currentPidToCheck)
                tmpChildrenList = self._getChildrenOfPid(currentPidToCheck)

                if tmpChildrenList:
                    for tmpChild in tmpChildrenList:
                        checkIfParentList.append(tmpChild)

    def _getChildrenOfPid(self, topPid):
        childProcessList = []
        getChildrenPipe = Popen("pgrep -P " + str(topPid), shell=True, stdout=PIPE, env=self.env)
        childProcesses, err = getChildrenPipe.communicate()

        if childProcesses:
            childProcessList = childProcesses.rstrip().split('\n')

            for child in childProcessList:
                print("CommandRunner: childProcessList of %s is %s" % (topPid, child))
                logging.debug("CommandRunner: childProcessList of %s is %s" % (topPid, child))

        return childProcessList

    def __pidExists(self, pid):
        "Check whether pid exists in the current process table. UNIX only."
        pidExists = False

        try:
            # Sending signal 0 to a pid will raise an OSError exception
            # if the pid is not running, and do nothing otherwise
            os.kill(pid, 0)
        except OSError as err:
            if err.errno == errno.ESRCH:
                # ESRCH == No such process
                pidExists = False
            elif err.errno == errno.EPERM:
                # EPERM clearly means there's a process to deny access to
                pidExists = True
            else:
                # According to "man 2 kill" possible error values are
                # (EINVAL, EPERM, ESRCH)
                raise
        else:
            pidExists = True

        return pidExists

    # On Windows, kill() is still an alias for terminate().  Posix OSs send SIGKILL.
    def _sigkillProcess(self, subprocessPipe):
        self.currentCommandTimedOut = True

        if (self.platform_type == "Windows"):
            self.__sigkillChildProcesses(subprocessPipe.pid)
            subprocessPipe.kill()
        else:
            logging.warn("CommandRunner: sigKillProcess using SIGKILL, parent pid is %s" % self.pipe.pid)
            if self.__pidExists(self.pipe.pid):
                os.killpg(os.getpgid(self.pipe.pid), signal.SIGKILL)
            else:
                logging.warn("CommandRunner: sigKillProcess using SIGKILL, parent pid %s does not exist" % self.pipe.pid)

    def __killProcess(self, subprocessPipe):
        self.currentCommandTimedOut = True

        if (self.platform_type == "Windows"):
            logging.warn("CommandRunner: killProcess using SIGTERM, parent pid is %s" % subprocessPipe.pid)

            self.__killChildProcesses(subprocessPipe.pid)
            subprocessPipe.terminate()
        else:
            logging.warn("CommandRunner: killProcess using SIGTERM, parent pid is %s" % self.pipe.pid)
            os.killpg(os.getpgid(self.pipe.pid), signal.SIGTERM)

    def _sigIntProcess(self, subprocessPipe):
        if (self.platform_type == "Windows"):
            self._sigIntChildProcesses(subprocessPipe.pid)
        else:
            logging.warn("CommandRunner: sigIntProcess using SIGINT, parent pid is %s" % self.pipe.pid)
            os.killpg(os.getpgid(self.pipe.pid), signal.SIGINT)

    def __createPipeWithCombinedOutAndErrStreams(self, stderr, stdout):
        with ProcessHandler.popen_lock:
            if (self.platform_type == "Windows"):
                self.pipe = Popen(self.command, shell=True, stdout=stdout, stderr=stderr, env=self.env)
            else:
                self.pipe = Popen(self.command, shell=True, stdout=stdout, stderr=stderr, env=self.env, preexec_fn=os.setsid)
            # ~ logging.debug("CommandRunner: created pipe with pid %s for command %s" % (self.pipe.pid, self.command))

    def __sigkillChildProcesses(self, parentPID):
        getChildrenPipe = Popen("pgrep -P " + str(parentPID), shell=True, stdout=PIPE, env=self.env)
        childProcesses, err = getChildrenPipe.communicate()

        if childProcesses:
            childProcessList = childProcesses.rstrip().split('\n')
            for child in childProcessList:
                os.kill(int(child), signal.SIGKILL)

    def __killChildProcesses(self, parentPID):
        getChildrenPipe = Popen("pgrep -P " + str(parentPID), shell=True, stdout=PIPE, env=self.env)
        childProcesses, err = getChildrenPipe.communicate()

        if childProcesses:
            childProcessList = childProcesses.rstrip().split('\n')
            for child in childProcessList:
                logging.warn("CommandRunner: __killChildProcesses sending SIGTERM to %s" % child)
                os.kill(int(child), signal.SIGTERM)

    def _sigIntChildProcesses(self, parentPID):
        getChildrenPipe = Popen("pgrep -P " + str(parentPID), shell=True, stdout=PIPE, env=self.env)
        childProcesses, err = getChildrenPipe.communicate()

        if childProcesses:
            childProcessList = childProcesses.rstrip().split('\n')
            for child in childProcessList:
                os.kill(int(child), signal.SIGINT)

    def stop_process(self, options=None):
        self.stopProcessNotCalled = False

        if self.pipe:
            if options == 'SIGINT':
                self._sigIntProcess(self.pipe)
            elif (options == 'KILL') or (options == 'SIGKILL'):
                self._sigkillProcess(self.pipe)
            else:
                self.__killProcess(self.pipe)
        else:
            print("ProcessHandler - stop_process - self.pipe does not exist!")

class CommandResult:
    def __init__(self):
        self.out = []
        self.returnCode = 0
