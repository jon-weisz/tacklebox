#!/usr/bin/env python
import sys
import argparse
import inspect
import collections
import logging


from components import rendering_component
from components import host_x_component
from tools import docker_subprocess
from tools import subcommand

reload(rendering_component)
reload(host_x_component)
reload(docker_subprocess)


class TackleBox(subcommand.CLICommands):
    def __init__(self, inputs):
        self.components = [rendering_component.RenderingComponent(),
                           host_x_component.HostXComponent()]
        self.main_description = "command line interface to TackleBox Docker toolkit"
        self.main_usage = "tackle <command> [<args>]"
        #self.parser.add_argument(version="0.1")        
        self.sub_description="The available commands and usage is described below. Use tackle <command> -h for more information on each"
        self.sub_help="Descriptions:"
        super(TackleBox,self).__init__()
        self._parse(inputs)

    
    def __get_component_arguments(self):
        argument_strings = []
        for component in self.components:
            argument_strings.extend(self.__get_arguments_from_dict(component.update_arguments()))
        
        return argument_strings

    def __get_arguments_from_dict(self, argument_dict):
        argument_strings =[]
        for key,value in argument_dict.get('volumes',{}).iteritems():
            argument_strings.append('--volume={}:{}'.format(key, value))
        for key,value in argument_dict.get('devices',{}).iteritems():
            argument_strings.append('--device={}:{}'.format(key, value))
        for key,value in argument_dict.get('environment',{}).iteritems():
            argument_strings.append('--env={}={}'.format(key, value))
        return argument_strings

    def run(self, image="ubuntu:trusty", rm=True, 
            interactive=False, options="", command="/bin/bash"):
        """
        docker run with automatic hardware library and device flags automatically derived and passed to docker run.

        :param image: The name of the docker image to run
        :type image: str
        :param rm: Specify whether to remove the container after running the image. This option is redundant with the standard docker operation, but is promoted here for the purpose of highlighting the change in default behavior with respect to the standard docker command. 
        :type rm: bool
        :param interactive: Whether to run the docker container with the interactive option enabled. Equivalent of -ti in docker command. 
        :type interactive: bool
        :param options: comma seperated list of docker options. See Docker for more information
        :type options: str
        :param command: The command to run in the docker container. 
        :type command: str
        """
        
        docker_runner = docker_subprocess.DockerRunPopen(image, interactive=interactive, dockerargs=self.__get_component_arguments(),rm=rm)
        process = docker_runner(command)
        (stdout,stderr) = process.communicate()

    def component_test(self, image="ubuntu:trusty"):
        """
        Run the component tests to make sure that the image is correctly configured for the hardware components to work correctly.

        :param image: The name of the docker image to run
        :type image: str
        """
        docker_runner = docker_subprocess.DockerRunPopen(image, interactive=False, dockerargs=self.__get_component_arguments(),rm=True)
        passed = True
        for component in self.components:
            if component.test_component(docker_runner):
                logging.warn("Component: {} Passed ".format(component.name))
            else:
                logging.error("Component: {} Failed ".format(component.name))
                passed = False
        return passed

    def component_demo(self, image="ubuntu:trusty"):
        """
        Run the component demo to allow a human user to verify the function of a component

        :param image: The name of the docker image to run
        :type image: str
        """
        docker_runner = docker_subprocess.DockerRunPopen(image, interactive=True, dockerargs=self.__get_component_arguments(),rm=True)
        dockerargs=self.__get_component_arguments()


        print(dockerargs)
    
        # for component in self.components:
        #     print(component)
        #     # component.demo_component(docker_runner)

        passed = True
        for component in self.components:
            component.demo_component(docker_runner)





if __name__=="__main__":
    t = TackleBox(sys.argv[1:])
    
