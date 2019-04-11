from saramPy import Saram
import json
import requests
from uuid import uuid1

class StatusNotOk(Exception):
    """Exception with status code is not 200"""
    pass

class NotValidCategory(Exception):
    """Exception when category is not valid"""
    pass

class SaramAPI(Saram):
    """
    Class that exposes the full API for Saram. Interits from 
    saramPy.Saram. This class reads from the local ``.saram.conf`` file 
    to instialize many of its properties.

    >>> from saramPy.api import SaramAPI
    >>> saram = SaramAPI()
    """

    def __init__(self):
        super().__init__(token=None)
        with open(self._conf_file, 'r') as f:
            conf = json.loads(f.read())
            self.username = conf['username'] 
            self.apiKey = conf['apiKey']
            self.avatar = conf.get('avatar', '/static/saramapi.png')
            self.base_url = conf['base_url']
        self.api_url = f'{self.base_url}api/'
        self._valid_types = ['file', 'stdout', 'script', 'dump', 'tool', 'image']
        self._valid_categories = [
            'android',
            'cryptography',
            'firmware',
            'forensics',
            'hardware',
            'ios',
            'misc',
            'network',
            'pcap',
            'pwn',
            'reversing',
            'stego',
            'web',
            'none',
            'other',
            'scripting',
        ]
        self._headers = {
            'x-saram-apikey': self.apiKey,
            'x-saram-username': self.username
        }

    def get_all_entries(self) -> list:
        """
        Gets an array of all the valid entries
        
        :raises StatusNotOk: Exception on fail
        :return: Array containing objects of all the entries
        :rtype: list
        
        >>> entries = saram.get_all_entries()
        >>> print(entries)
        """

        r = requests.get(f'{self.api_url}all/entries', headers=self._headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk('Could not get all entries')

    def get_entry(self, token: str) -> dict:
        """
        Gets all the data associated with a single entry
        
        :param token: Valid token for entry
        :type token: str
        :raises StatusNotOk: Exception if not found
        :return: object with all entry data
        :rtype: dict

        >>> entry = saram.get_entry(token='sometoken')
        """

        r = requests.get(f'{self.api_url}{token}', headers=self._headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk('Could not create section')

    def delete_entry(self, token: str) -> dict:
        """
        Delete an entry entirely
        
        :param token: Valid token for entry
        :type token: str
        :raises StatusNotOk: Exception on fail
        :return: OK object
        :rtype: dict

        >>> entry = saram.delete_entry(token='sometoken')
        """

        r = requests.delete(f'{self.api_url}{token}', headers=self._headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(f'Could not delete Status code: {r.text}')

    def update_entry(self, token: str, priority: str='none', description: str=None) -> dict:
        """
        Update an entry with varios data points
        
        :param token: Valid token for entry
        :type token: str
        :param priority: The priority/criticality/status of an enty, defaults to none. Valid values are 'info', 'high', 'medium', 'low', 'critical', 'complete', 'none'
        :param priority: str, optional
        :param description: Optional description for the entry, defaults to None
        :param description: str, optional
        :raises StatusNotOk: Exception
        :return: Response oject
        :rtype: dict

        >>> saram.update_entry('sometoken', priority='high')
        """

        payload = {
            'priority': priority,
            'description': description
        }
        r = requests.post(f'{self.api_url}{token}', headers=self._headers, json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(f'Could not update Status code: {r.text}')

    def create_new_section(self, token: str, type: str,
        output: str, command: str, comment: str='saramPy'
    ) -> dict:
        """
        Create a new section. This will add to the existing entry.
        
        :param token: Valid token for the entry
        :type token: str
        :param type: Valid type. Ex. `stdout`
        :type type: str
        :param output: Output of a command/variable etc
        :type output: str
        :param command: Command executed to get the output
        :type command: str
        :param comment: Comment to add, defaults to ['saramPy']
        :param comment: list, optional
        :raises TypeError: Exception if type is not valid
        :raises StatusNotOk: Exception on fail
        :return: OK object
        :rtype: dict
        """

        payload = {
            'id': str(uuid1()),
            'type': type,
            'output': output,
            'command': command,
            'user': self.username,
            'comment': {
                'text': comment,
                'username': self.username,
                'avatar': self.avatar
            },
            'options': {
                'marked': 2
            },
            'time': self._time
        }
        if type not in self._valid_types:
            raise TypeError(f'Valid types are {self._valid_types}')
        r = requests.patch(f'{self.api_url}{token}', headers=self._headers,
        json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk('Could not create section')
    
    def add_comment(self, token: str, dataid: str, comment: str) -> dict:
        """
        Add a comment to a section.
        
        :param token: Valid token for the entry
        :type token: str
        :param dataid: Valid section to add the comment to
        :type dataid: str
        :param comment: Comment to add
        :type comment: str
        :raises StatusNotOk: Exception on fail
        :return: OK object
        :rtype: dict

        >>> entry = saram.add_comment(token='sometoken', dataid='long_data_id', comment='helpful comment')
        """

        payload = {
            'data': {
                'text': comment,
                'username': self.username,
                'avatar': self.avatar
            }
        }
        r = requests.patch(f'{self.api_url}{token}/{dataid}/comment',
        json=payload, headers=self._headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk('Could not add comment')

    def delete_section(self, token: str, dataid: str) -> dict:
        """
        Delete a section. This will delete a single section in an entry
        
        :param token: Valid token for the entry
        :type token: str
        :param dataid: Valid dataid for the section to delete
        :type dataid: str
        :raises StatusNotOk: Exception on fail
        :return: OK object
        :rtype: dict
        """

        r = requests.delete(f'{self.api_url}{token}/{dataid}', headers=self._headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk('Could not delete section')

    def create_new_entry(self, title: str, category: str) -> dict:
        """
        Create a new entry. This is a whole new entry to work with
        
        :param title: Title of section/challenge
        :type title: str
        :param category: Category of section/challenge
        :type category: str
        :raises NotValidCategory: Exception if a vategory is not valid
        :raises StatusNotOk: Exception on fail
        :return: OK response object
        :rtype: dict
        """

        if category not in self._valid_categories:
            raise NotValidCategory(f'Valid categories are {self._valid_categories}')
        token = self._token_generator(title)
        payload = {
            'title': title,
            'category': category,
            'timeCreate': self._time,
            'data': []
        }
        r = requests.post(f'{self.api_url}create/{token}', headers=self._headers,
        json=payload)
        if r.status_code == 200:
            print('Created new entry')
        else:
            raise StatusNotOk(r.text)

    def reset_api_key(self, old_apikey: str, username: str) -> dict:
        """
        Reset the API key
        
        :param old_apikey: Valid API key
        :type old_apikey: str
        :param username: Username associated with valid API key
        :type username: str
        :raises StatusNotOk: Exception on fail
        :return: object containing new API key
        :rtype: dict
        """

        payload = {
            'apiKey': old_apikey,
            'username': username
        }
        r = requests.post(f'{self.api_url}reset/key', headers=self._headers, json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk('Could not create section')
    
    def change_username(self, api_key: str, old_username: str, new_username: str) -> dict:
        """
        Change the username to a new username
        
        :param api_key: Valid API key
        :type api_key: str
        :param old_username: Old username
        :type old_username: str
        :param new_username: New username
        :type new_username: str
        :raises StatusNotOk: Exception on fail
        :return: object with both old and new usernames
        :rtype: dict
        """

        payload = {
            'apiKey': api_key,
            'username': old_username,
            'newUsername': new_username
        }
        r = requests.post(f'{self.api_url}reset/username', headers=self._headers, json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk('Could not create section')

    def validate_api_key(self, api_key: str) -> dict:
        """
        Validate and API key and if valid, return the API and assciated username
        
        :param api_key: Valid API key
        :type api_key: str
        :raises StatusNotOk: Exception
        :return: dict containing the valid API key and associated username
        :rtype: dict

        >>> entry = saram.validate_api_key(api_key='secretapikey')
        """

        payload = {
            'key': api_key
        }
        r = requests.post(f'{self.base_url}misc/valid/key', json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk('Could not validate API key')

    def get_valid_token(self, title: str) -> dict:
        """
        Supply a title, and get a valid token back. This is useful when 
        testing token creation, or when working with other API endpoints.
        
        :param title: Title to generate the token with
        :type title: str
        :raises StatusNotOk: Exception
        :return: reponse dictionary object
        :rtype: dict

        >>> entry = saram.get_valid_token(title='Title of some challenge')
        """

        payload = {
            'title': title
        }
        r = requests.post(f'{self.base_url}misc/valid/token', json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk('Could not create a valid token')

    def admin_all_users(self) -> list:
        """
        Get an array of all user objects
        
        :raises StatusNotOk: Exception
        :return: Array of user objects
        :rtype: list

        >>> print(saram.admin_all_users())
        """

        r = requests.get(f'{self.api_url}admin/allusers', headers=self._headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk('Could not get all users')

    def admin_find_user(self, user_id: str) -> dict:
        """
        Find a user by user id
        
        :param user_id: A valid user id
        :type user_id: str
        :raises StatusNotOk: Exception
        :return: A complete user object
        :rtype: dict

        >>> saram.admin_find_user('somedemoid')
        """

        r = requests.get(f'{self.api_url}admin/user?id={user_id}', headers=self._headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk('Could not find user')

    def admin_create_user(
        self, username: str, password: str, 
        isAdmin: bool=False, avatar: str='/static/logo.png'
    ) -> dict:
        """
        Create a new user
        
        :param username: A valid username. Spaces and special characters are stripped
        :type username: str
        :param password: A password. Password is stored as a hash
        :type password: str
        :param isAdmin: True if the user is an admin, defaults to False
        :param isAdmin: bool, optional
        :param avatar: A link to the profile image for the user, defaults to '/static/logo.png'
        :param avatar: str, optional
        :raises StatusNotOk: Exception
        :return: A complete user object
        :rtype: dict
        """

        payload = {
            'username': username,
            'password': password,
            'isAdmin': isAdmin,
            'avatar': avatar
        }
        r = requests.post(f'{self.api_url}admin/user', headers=self._headers, json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.text)

    def admin_delete_user(self, user_id: str) -> dict:
        """
        Delete a user by user id
        
        :param user_id: A valid user id
        :type user_id: str
        :raises StatusNotOk: Exception
        :return: True if deleted
        :rtype: dict

        >>> saram.admin_delete_user(user_id='somedemoid')
        """

        payload = {
            'user_id': user_id
        }
        r = requests.delete(f'{self.api_url}admin/user', headers=self._headers, json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)
    
    def admin_update_user(self, user_id: str, **kwargs) -> dict:
        """
        Update a users information. Any valid user field can be 
        updated using this method.
        
        :param username: New username to change to
        :type username: str, optional
        :param isAdmin: Toggle True or False
        :param isAdmin: bool, optional
        :param avatar: A link to the profile image for the user, defaults to '/static/logo.png'
        :param avatar: str, optional
        :raises StatusNotOk: Exception
        :return: A complete user object
        :rtype: dict

        >>> # This example shows how to change the admin status of a user
        >>> saram.admin_update_user(user_id='somedemoid', isAdmin=True)
        """
        payload = kwargs
        r = requests.patch(f'{self.api_url}admin/user?id={user_id}'
            , headers=self._headers, json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

    def admin_get_logs(self) -> list:
        """
        Get an arry of all the log objects
        
        :raises StatusNotOk: Exception
        :return: Array of log objects
        :rtype: list
        """

        r = requests.get(f'{self.api_url}admin/logs', headers=self._headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(f'Could not delete Status code: {r.text}')

    def admin_get_status(self) -> list:
        """
        Gets the server status as an array of objects
        
        :raises StatusNotOk: Exception
        :return: Array of log objects
        :rtype: list
        """

        r = requests.get(f'{self.api_url}admin/status', headers=self._headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(f'Could not delete Status code: {r.text}')
