import os
import sys
import re
import json
import requests
import delegator
from uuid import uuid1

__version__ = 0.1
__author__ = 'Hapsida @securisec'


class Saram(object):
    '''
    The Saram class

    :param token: Token for the URL. Provided in Slack
    :type token: str
    :param slack_user: Your Slack username
    :type slack_user: str
    :return: Saram object
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
        self.url = self._check_dev(self.token)
        print(self.url)

    def _check_dev(self, token, base_url: bool=False) -> str:
        if os.environ.get('SARAM_ENV') == 'dev':
            return 'http://localhost:5001/' if base_url else f'http://localhost:5001/{token}'
        else:
            return 'https://saram.securisec.com/' if base_url else f'https://saram.securisec.com/{token}'

    def _token_generator(self, title: str) -> str:
        u = str(uuid1())[0:8]
        t = '-'.join(re.sub(r'[^a-zA-Z0-9 ]', '', title).split())[0:25]
        return f'{u}-{t}'

    def read_script(self, script_name: str=None) -> 'Saram':
        '''
        Read the contents of the file that this function is 
        called in and return the whole content

        :return: Returns Saram object. Access with ```output``` attribute
        :rtype: str
        '''

        path = sys.argv[0]
        with open(path, 'r') as f:
            data = f.read()
            self.file_path = path
            self.output = data
            self.type = 'script'
            self.command_run = 'Script' if script_name is None else script_name
            return self

    def file_content(self, file_path: str, file_name: str=None) -> 'Saram':
        '''
        Read a files content

        :param file_path: File path
        :type file_path: str
        :param file_name: File path
        :type file_name: str
        :return: Saram object
        :rtype: object
        '''

        with open(file_path, 'r') as f:
            data = f.read()
            self.file_path = file_path
            self.output = data
            self.type = 'file'
            self.command_run = 'File' if file_name is None else file_name
            return self

    def variable_output(self, var: any, script_name: str=None) -> 'Saram':
        '''
        Send any data like the output of a python script 
        to the server

        :param var: Variable
        :type var: any
        :param script_name: Variable
        :type script_name: any
        :return: Saram object
        :rtype: object
        '''

        self.type = 'script'
        self.command_run = 'Script' if script_name is None else script_name
        self.output = var
        return self

    def send_to_server(self) -> requests.Response:
        '''
        Sends a dict object to the server to save

        :return: response from request. access with ```response``` attribute
        :rtype: requests.Response
        '''

        json = {
            'id': str(uuid1()),
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

    def run_command(self, command: str) -> 'Saram':
        '''
        Runs the command and gets the output of stdout

        :param command: Command to run. Could be string or an array
        :type command: str
        :return: Saram object. Access with ```command_output``` attribute
        :rtype: self
        '''

        output = delegator.run(command)
        self.type = 'stdout'
        self.output = output.out
        self.command_error = output.err
        self.command_run = command
        return self

    def create_entry(self, title: str, category: str,
                     slack_link: str, create_token: str) -> 'Saram':
        entry = {
            'title': title,
            'category': category,
            'slackLink': slack_link,
            'data': []
        }
        header = {
            'x-saram': create_token
        }
        token = self._token_generator(title)
        base_url = self._check_dev(None, True)
        url = f'{base_url}create/{token}'
        entry_url = f'{base_url}{token}'
        r = requests.post(url, json=entry, headers=header)
        print(r.status_code)
        print(entry_url)
        self.response = r
        self.url = url
        self.token = token
        return self
        