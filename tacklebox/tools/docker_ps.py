from __future__ import print_function
import subprocess
import logging
import shlex


class DockerRunPS(object):
    def __init__(self):
        pass

    def __call__(self, command_args=[], **kwargs):
        args = ["docker", "ps"] + shlex.split(' '.join(command_args))
        return subprocess.Popen(args=args,  **kwargs)

    def read(self, command_args=[]):
        process = self.__call__(command_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = process.communicate()
        return stdout.split('\n')

    def container_names(self):
        return [line.split()[-1] for line in self.read(['-a'])[1:-1]]


