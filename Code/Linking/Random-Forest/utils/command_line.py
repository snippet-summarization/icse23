import sys
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
import os

class CommandLineHelper():

    def __init__(self):
        self.cmd = None
        self.output = None
        self.error = None


    def exec_command(self, cmd, cwd, timeout=600):
        '''
        This function execute the command @cmd using @cwd as working directory
        Then save the output in @self.output and the error in @self.error
        At the end return @output and @error
        '''
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True, cwd=cwd)

        try:
            output, error = p.communicate(timeout=timeout)
        except TimeoutExpired:
            p.kill()
            # output, error = p.communicate()
            return "", "TimeoutExpired"

        output = output.decode("UTF-8", errors="ignore")

        error = error.decode()
        self.output = output
        self.error = error

        return output, error

    def is_command_ok(self):
        '''
        This function check if previous command is OK, reading the content of @self.error
        Sometimes there are commands that use the std error in a wrong way (e.g. the message cloning from git clone come out from std error)
        '''
        if self.error == None:
            return True
        if len(self.error) == 0:
            return True

        return False
