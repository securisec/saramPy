import os
import sys
import re
import json
import logging
import requests
import delegator
from inspect import currentframe
from pathlib import Path
from datetime import datetime
from uuid import uuid1

from .modules.exceptions import ServerError

__version__ = 0.1
__author__ = 'Hapsida @securisec'

class Saram(object):
    '''
    The Saram class

    >>> from saram import Saram
    >>> s = Saram(token='token value', user='username')

    :param token: Token for the URL. Provided in Slack
    :type token: str
    :param user: Your Slack username
    :type user: str
    :param local: Uses localhost as the host
    :type local: bool
    :param base_url: Set the base url
    :type base_url: str
    :return: Saram object
    :rtype: object
    '''

    def __init__(self, token: str, user: str, base_url: str=None, 
                local: bool=False) -> object:
        self.output: str = None
        self.command_run: str = None
        self.command_error: str = None
        self.comment = ''
        self.file_path: str = None
        self.response: object = None
        self.user: str = user
        self.type: str = None
        self.token: str = token
        self.local: bool = local
        self.self_file: str = sys.argv[0]
        self.base_url = base_url if base_url else self._check_dev()
        self.url: str = f'{self.base_url}{token}'

        # function alias
        self.send = self.send_to_server
        
        logging.basicConfig()

    def _get_file_name(self, path):
        return Path(path).parts[-1]

    def _verify_token(self):
        # TODO verify token again special chars
        pass

    def _check_dev(self) -> str:
        if self.local:
            return 'http://localhost:5001/'
        else:
            return 'https://saram.securisecctf.com/'

    def _token_generator(self, title: str) -> str:
        u = str(uuid1())[0:8]
        t = '-'.join(re.sub(r'[^a-zA-Z0-9 ]', '', title).split())[0:25]
        logging.debug(f'Token generated: {u}-{t}')
        return f'{u}-{t}'

    def script_read_self(self, comment: str='', script_name: str=None) -> 'Saram':
        '''
        Read the contents of the file that this function is 
        called in and return the whole content

        :param comment: Optional make a comment
        :type comment: str
        :param script_name: Optional name of the script being read
        :type script_name: str
        :return: Returns Saram object. Access with ```output``` attribute
        :rtype: str
        '''

        path = sys.argv[0]
        with open(path, 'r') as f:
            data = f.read()
            self.file_path = self._get_file_name(path)
            self.output = data
            self.type = 'script'
            self.comment = comment
            self.command_run = 'Script' if script_name is None else script_name
            return self

    def script_dump(self, script_name: str=None, comment='') -> 'Saram':
        """
        Reads a file till the point this method is called. 
        Can be used as many times as needed.
        
        :param script_name: Optional name of the script being read
        :type script_name: str
        :param comment: Optional make a comment
        :type comment: str
        :return: Saram object
        :rtype: object
        """

        cf = currentframe()
        line_number = cf.f_back.f_lineno
        print('Line', line_number)
        with open(self.self_file) as f:
            lines = []
            for i, line in enumerate(f):
                lines.append(line)
                if i == line_number - 2:
                    self.type = 'dump'
                    self.comment = comment
                    self.command_run = 'Script dump' if script_name is None else script_name
                    self.output = ''.join(lines)
                    return self

    def file_content(self, file_path: str, comment: str='', file_name: str=None) -> 'Saram':
        '''
        Read a files content

        :param file_path: File path
        :type file_path: str
        :param comment: Optional make a comment
        :type comment: str
        :param file_name: File path
        :type file_name: str
        :return: Saram object
        :rtype: object
        '''

        with open(file_path, 'r') as f:
            data = f.read()
            self.file_path = self._get_file_name(file_path)
            self.output = data
            self.type = 'file'
            self.comment = comment
            self.command_run = 'File' if file_name is None else file_name
            return self

    def variable_output(self, var: any, comment: str='', script_name: str=None) -> 'Saram':
        '''
        Send any data like the output of a python script 
        to the server

        :param var: Variable
        :type var: any
        :param comment: Optional make a comment
        :type comment: str
        :param script_name: Variable
        :type script_name: any
        :return: Saram object
        :rtype: object
        '''

        self.type = 'script'
        self.command_run = 'Script' if script_name is None else script_name
        self.output = var
        self.comment = ''
        return self

    def send_to_server(self) -> requests.Response:
        '''
        Sends a dict object to the server to save

        >>> s.run_command(command).send_to_server()

        :return: response from request. access with ```response``` attribute
        :rtype: requests.Response
        '''

        json = {
            'id': str(uuid1()),
            'type': self.type,
            'output': self.output,
            'command': self.command_run,
            'user': self.user,
            'comment': self.comment,
            'time': str(datetime.utcnow())
        }
        r = requests.patch(self.url, json=json)
        self.response = r
        if r.status_code != 200:
            logging.error(f'{r.status_code} {r.text}')
            raise ServerError('Could not add')
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

    def run_command(self, command: str, comment: str='') -> 'Saram':
        '''
        Runs the command and gets the output of stdout

        :param command: Command to run. Could be string or an array
        :type command: str
        :param comment: Optional make a comment
        :type comment: str
        :return: Saram object. Access with ```command_output``` attribute
        :rtype: self
        '''

        command = command if isinstance(command, str) else ' '.join(command)
        output = delegator.run(command)
        self.type = 'stdout'
        self.comment = comment
        self.output = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', output.out)
        self.command_error = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', output.err)
        self.command_run = command if isinstance(command, str) else ' '.join(command)
        print(output.out)
        return self


class SaramHelpers(Saram):
    """
    This class is used to create or delete items 
    that are already store
    
    :param local: Uses localhost as the host
    :type local: bool
    :param base_url: Set the base url
    :type base_url: str
    """

    def __init__(self, local: bool=False, base_url: str=None):
        super().__init__(None, None, local=local, base_url=base_url)
    
    def create(self, title: str, category: str, slack_link: str) -> 'Saram':
        """
        Create an entry in the Saram db
        
        :param title: Title of the entry
        :type title: str
        :param category: Category for the entry
        :type category: str
        :param slack_link: Link to references/slack
        :type slack_link: str
        :return: Saram object.
        :rtype: self
        """

        entry = {
            'title': title,
            'category': category,
            'slackLink': slack_link,
            'timeCreate': str(datetime.utcnow()),
            'data': []
        }
        # header = {
        #     'x-saram': create_token
        # }
        token = self._token_generator(title)
        url = f'{self.base_url}create/{token}'
        entry_url = f'{self.base_url}{token}'
        print(entry_url)
        r = requests.post(url, json=entry) #, headers=header)
        logging.info(r.status_code)
        logging.info(entry_url)
        self.response = r
        self.url = url
        self.token = token
        logging.info(f'Url for entry: {entry_url}')
        return self

    def delete_entry(self, token: str, object_id) -> 'Saram':
        """
        Delete an entry
        
        :param token: Token for the entry
        :type token: str
        :param object_id: Id of the object to be deleted
        :type object_id: str
        :return: Saram object
        :rtype: object
        """

        url = f'{self.base_url}{token}/{object_id}'
        r = requests.delete(url)
        if r.status_code != 200:
            logging.error(f'{r.status_code} {r.text}')
            return self
        self.response = r
        self.url = url
        print(r.text)
        return self
        