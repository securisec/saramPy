import os
import sys
import re
import json
import requests
import delegator

__version__ = 0.1
__author__ = 'Hapsida @securisec'


class Paramduni(object):
    '''
    The Paramduni class

    :param token: Token for the URL. Provided in Slack
    :type token: str
    :param slack_user: Your Slack username
    :type slack_user: str
    :return: Paramduni object
    :rtype: object
    '''

    def __init__(self, token: str, slack_user: str) -> object:
        self.output = None
        self.command_run = None
        self.command_error = None
        self.file_path = None
        self.response = None
        self.slack_user = slack_user
        self.type = None
        self.token = token
        self.url =  self.__check_dev(self.token)
        print(self.url)

    def __check_dev(self, token):
        if os.environ.get('PARAMDUNI_ENV') == 'dev':
            return f'http://localhost:5001/{token}'
        else:
            return f'https://paramduni.securisec.com/{token}'

    def read_script(self) -> 'Paramduni':
        '''
        Read the contents of the file that this function is 
        called in and return the whole content

        :return: Returns Paramduni object. Access with ```output``` attribute
        :rtype: str
        '''

        path = sys.argv[0]
        with open(path, 'r') as f:
            data = f.read()
            self.file_path = path
            self.output = data
            self.type = 'script'
            self.command_run = 'Script'
            return self

    def file_content(self, file_path: str) -> 'Paramduni':
        '''
        Read a files content

        :param file_path: File path
        :type file_path: str
        :return: Paramduni object
        :rtype: object
        '''

        with open(file_path, 'r') as f:
            data = f.read()
            self.file_path = file_path
            self.output = data
            self.type = 'file'
            self.command_run = 'File'
            return self

    def script_output(self, var: any) -> 'Paramduni':
        '''
        Send any data like the output of a python script 
        to the server

        :param var: Variable
        :type var: any
        :return: Paramduni object
        :rtype: object
        '''

        self.type = 'script'
        self.command_run = 'Script'
        self.output = var
        return self

    def send_to_server(self) -> requests.Response:
        '''
        Sends a dict object to the server to save

        :return: response from request. access with ```response``` attribute
        :rtype: requests.Response
        '''

        json = {
            'type': self.type,
            'output': self.output,
            'command': self.command_run,
            'user': self.slack_user
        }
        r = requests.post(self.url, json=json)
        self.response = r
        print(r.text)
        return self

    def get_current_entries(self) -> dict:
        '''
        Get the current data from the server as an object

        :return: Data in server
        :rtype: dict
        '''

        self.response = requests.get(self.url + '/api')
        if self.response.status_code == 200:
            return self.response.json()

    def get_suggested_tools(self, parameter_list):
        # TODO get a list of suggested tools based on challenge category
        raise NotImplementedError('Work in progress')

    def run_command(self, command: str) -> 'Paramduni':
        '''
        Runs the command and gets the output of stdout

        :param command: Command to run. Could be string or an array
        :type command: str
        :return: Paramduni object. Access with ```command_output``` attribute
        :rtype: self
        '''

        output = delegator.run(command)
        self.type = 'stdout'
        self.output = output.out
        self.command_error = output.err
        self.command_run = command
        return self
