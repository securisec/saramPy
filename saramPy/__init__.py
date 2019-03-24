from __future__ import annotations
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
from pkg_resources import get_distribution

from .modules.exceptions import ServerError

__version__ = get_distribution('saramPy').version

class Saram(object):
    '''
    The Saram class

    >>> # import and instantiate Saram
    >>> from saramPy import Saram
    >>> s = Saram(token='token value', user='username')

    :param token: Token for the Entry/URL. Provided in Slack
    :type token: str
    :param local: Uses localhost as the host
    :type local: bool
    :param base_url: Set the base url
    :type base_url: str
    :return: Saram object
    :rtype: object
    '''

    def __init__(self, token: str, base_url: str=None,
                 local: bool=False) -> object:
        self.output: str = None
        self.command_run: str = None
        self.command_error: str = None
        self.comment = ['saramPy']
        self.file_path: str = None
        self.response: object = None
        self.type: str = None
        self.token: str = token
        self.local: bool = local
        self.self_file: str = sys.argv[0]
        self.base_url = base_url if base_url else self._check_dev()
        self.url: str = f'{self.base_url}api/{token}'
        self._conf_file = f'{Path(Path().home())}/.saram.conf'
        
        # function alias
        self.send = self.send_to_server

        logging.basicConfig()

    def _get_file_name(self, path):
        """Returns the basename from the path"""
        return Path(path).parts[-1]

    def _check_dev(self) -> str:
        """Returns localhost or default Saram server url"""
        if self.local:
            return 'http://localhost:5001/'
        else:
            return 'https://saram.securisecctf.com/'

    def _token_generator(self, title: str) -> str:
        u = str(uuid1())[0:8]
        t = '-'.join(re.sub(r'[^a-zA-Z0-9 ]', '', title).split())[0:25]
        logging.debug(f'Token generated: {u}-{t}')
        return f'{u}-{t}'

    def script_read_self(self, comment: str=None, script_name: str=None) -> Saram:
        '''
        Read the contents of the file that this function is 
        called in and return the whole content. Optional parameters are 
        ```comment``` and ```script``` name.

        :param comment: Optional make a comment
        :type comment: str
        :param script_name: Optional name of the script being read
        :type script_name: str
        :return: Returns Saram object. Access with ```output``` attribute
        :rtype: str
        
        >>> s.script_read_self(script_name="solver.py", comment="Solve pwn challenge")
        >>> s.send() # send the content to the server
        '''

        path = sys.argv[0]
        with open(path, 'r') as f:
            data = f.read()
            self.file_path = self._get_file_name(path)
            self.output = data
            self.type = 'script'
            if comment is not None:
                self.comment.append(comment)
            self.command_run = 'Script' if script_name is None else script_name
            return self

    def script_dump(self, script_name: str=None, comment=None) -> Saram:
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
                    if comment is not None:
                        self.comment.append(comment)
                    self.command_run = 'Script dump' if script_name is None else script_name
                    self.output = ''.join(lines)
                    return self

    def file_content(self, file_path: str, comment: str=None, file_name: str=None) -> Saram:
        '''
        Reads the content of the provided files path. Optional 
        parameters are comment and file_name. 

        :param file_path: File path
        :type file_path: str
        :param comment: Optional make a comment
        :type comment: str
        :param file_name: File path
        :type file_name: str
        :return: Saram object
        :rtype: object

        >>> s.file_content('/path/to/file.extension').send() # send the content to the server
        '''

        with open(file_path, 'r') as f:
            data = f.read()
            self.file_path = self._get_file_name(file_path)
            self.output = data
            self.type = 'file'
            if comment is not None:
                self.comment.append(comment)
            self.command_run = 'File' if file_name is None else file_name
            return self

    def variable_output(self, var: any, comment: str=None, script_name: str=None) -> Saram:
        '''
        Send any data like the output of a python script 
        to the server. This is useful when only the output of a particular 
        variable needs to the sent to the sever, and not the whole 
        script itself. Optional parameters are comment and script_name.

        :param var: Variable
        :type var: any
        :param comment: Optional make a comment
        :type comment: str
        :param script_name: Variable
        :type script_name: any
        :return: Saram object
        :rtype: object

        >>> # set data to a variable
        >>> response = request.get('https://google.com').text
        >>> # Send data to the server
        >>> s.variable_output(response).send()
        '''

        self.type = 'script'
        self.command_run = 'Script' if script_name is None else script_name
        self.output = var
        if comment is not None:
            self.comment.append(comment)
        return self

    def send_to_server(self) -> requests.Response:
        '''
        Sends a dict object to the server to save. Will print 
        OK or 200 status code on success.

        >>> s.run_command(command).send_to_server()

        :return: response from request. access with ```response``` attribute
        :rtype: requests.Response
        '''

        with open(self._conf_file, 'r') as f:
            conf = json.loads(f.read())
            self.user = conf['username'] 
            self.apiKey = conf['apiKey']

        json_payload = {
            'id': str(uuid1()),
            'type': self.type,
            'output': self.output,
            'command': self.command_run,
            'user': self.user,
            'comment': self.comment,
            'options': {
                'marked': 2
            },
            'time': str(datetime.utcnow())
        }
        headers = {
            'x-saram-apikey': self.apiKey,
            'x-saram-username': self.user,
        }
        r = requests.patch(self.url, json=json_payload, headers=headers)
        self.response = r
        if r.status_code != 200:
            logging.error(f'{r.status_code} {r.text}')
            raise ServerError('Could not add')
        print(r.text)
        return self

    def run_command(self, command: str, comment: str=None) -> Saram:
        '''
        Runs the command and gets the output of stdout. Does not 
        support bash one liners or too many piped outputs. In those 
        cases, write the command to a file, and send the content of the 
        file instead with ```file_content```. Optional params are ```comment```.

        :param command: Command to run. Could be string or an array
        :type command: str
        :param comment: Optional make a comment
        :type comment: str
        :return: Saram object. Access with ```command_output``` attribute
        :rtype: self

        >>> s.run_command('ls -l /tmp/', comment='Output of ls')
        >>> s.send()
        '''

        command = command if isinstance(command, str) else ' '.join(command)
        output = delegator.run(command)
        self.type = 'stdout'
        if comment is not None:
            self.comment.append(comment)
        self.output = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', output.out)
        self.command_error = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', output.err)
        self.command_run = command if isinstance(
            command, str) else ' '.join(command)
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
        super().__init__(None, local=local, base_url=base_url)

    def create(self, title: str, category: str, slack_link: str) -> Saram:
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

        valid_cat = [
            'android',
            'cryptograpy',
            'firmware',
            'forensics',
            'hardware',
            'ios',
            'misc',
            'network',
            'none',
            'other',
            'pcap',
            'pwn',
            'reversing',
            'scripting',
            'stego',
            'web'
        ]

        if category not in valid_cat:
            valid = '\n'.join(valid_cat)
            raise TypeError(f'Valid categories are \n{valid}')

        entry = {
            'title': title,
            'category': category,
            'slackLink': slack_link,
            'timeCreate': str(datetime.utcnow()),
            'data': []
        }
        headers = {
            'x-saram-apikey': self.apiKey,
            'x-saram-username': self.user,
        }
        token = self._token_generator(title)
        url = f'{self.base_url}api/create/{token}'
        entry_url = f'{self.base_url}{token}'
        print(entry_url)
        r = requests.post(url, json=entry, headers=headers)
        logging.info(r.status_code)
        logging.info(entry_url)
        self.response = r
        self.url = url
        self.token = token
        logging.info(f'Url for entry: {entry_url}')
        return self

    def delete_entry(self, token: str, del_id: str) -> Saram:
        """
        Delete an entry

        :param token: Token for the entry
        :type token: str
        :param del_id: Id of the object to be deleted
        :type del_id: str
        :return: Saram object
        :rtype: object
        """

        url = f'{self.base_url}api/{token}/{del_id}'
        headers = {
            'x-saram-apikey': self.apiKey,
            'x-saram-username': self.user,
        }
        r = requests.delete(url, headers=headers)
        if r.status_code != 200:
            logging.error(f'{r.status_code} {r.text}')
            return self
        self.response = r
        self.url = url
        print(r.text)
        return self

class SaramInit(Saram):
    """
    The class will create the saram.conf file and read 
    values from it from the main Saram class. ```api_key``` 
    is required at init.

    :param api_key: API key. Provided in Saram after authentication
    :type token: str
    :param local: Uses localhost as the host
    :type local: bool
    :param base_url: Set the base url
    :type base_url: str
    """

    def __init__(self, api_key: str, local: bool=False, base_url: str=None) -> None:
        super().__init__(None, base_url, local)
        self.api_key = api_key
        self._home_path = Path().home()
        self._conf_file = Path(f'{self._home_path}/.saram.conf')

    def _verify_api_key(self):
        r = requests.post(
            f'{self.base_url}misc/valid/key',
            json={'key': self.api_key}
        )
        if r.status_code == 200:
            return r.json()
        else:
            raise TypeError('API key is not valid')
        
    def init(self) -> None:
        creds = self._verify_api_key()
        with open(self._conf_file, 'w') as f:
            f.write(json.dumps(creds))
        print(f'Saved the conf file to ${self._conf_file}')
