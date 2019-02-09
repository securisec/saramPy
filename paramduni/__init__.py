import os
import sys
import re
import argparse
import json
import requests
from subprocess import getoutput

__version__ = 0.1
__author__ = 'Hapsida @securisec'


class Paramduni(object):

    def __init__(self, url: str=None):
        self.category = self._category_name(url)
        self.output = None
        self.command_run = None
        self.file_path = None
        self.response = None
        self.token = self._token_from_regex(url)
        self.type = None
        self.url = url

    def _category_name(self, url: str) -> str:
        '''
        Returns the name of the category
        
        :param url: url
        :type url: str
        :return: category name
        :rtype: str
        '''

        return re.search(r'/(\w+)/', url).group(1)

    def _token_from_regex(self, url: str) -> str:
        '''
        Returns the parsed token from the url
        
        :param url: url
        :type url: str
        :raises TypeError: Raises error if token is not valid
        :return: token
        :rtype: str
        '''

        regex = r'[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}'
        search = re.search(regex, url)
        if not search:
            raise TypeError('URL is not valid')
        return search.group()

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

    def send_to_server(self) -> requests.Response:
        '''
        Sends a dict object to the server to save
        
        :return: response from request. access with ```response``` attribute
        :rtype: requests.Response
        '''

        json = {
            'type': self.type,
            'output': self.output,
            'command': self.command_run
        }
        r = requests.post(self.url, json=json)
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
        
        :return: Paramduni object. Access with ```command_output``` attribute
        :rtype: self
        '''

        output = getoutput(command)
        self.type = 'stdout'
        self.output = output
        self.command_run = command
        return self

    @staticmethod
    def parse_args() -> argparse.Namespace:
        '''
        Function that processes and returns the argparse Namespace. 
        This is a static method and doesnt need the ```self```

        :return: namespace
        :rtype: argparse.Namespace
        '''

        parse = argparse.ArgumentParser()
        parse.add_argument('command_to_run', metavar='command_to_run',
                           help='The full command to run. The command should be in quotes')
        parse.add_argument('-u', dest='url',
                           help='URL obtained from the Slack thread')
        a = parse.parse_args()
        return a


# if __name__ == "__main__":
#     app = Paramduni(None)
#     args = app.parse_args()
#     output = app.command_output(args.command_to_run, send_to_server=False)
#     print(f'-----\n{output}\n----')
