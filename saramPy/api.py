from saramPy import Saram
import json
import requests


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
        self._valid_types = ['file', 'stdout',
                             'script', 'dump', 'tool', 'image']
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
            'x-saram-username': self.username,
            'x-saram-avatar': self.avatar
        }

    def get_all_entries(self) -> list:
        """
        Gets an array of all the valid entries

        :raises StatusNotOk: Exception on fail
        :return: Array containing objects of all the entries
        :rtype: list

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.get_all_entries()
        >>> print(s)
        """

        r = requests.get(f'{self.api_url}all/entries', headers=self._headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

    def get_entry(self, token: str) -> dict:
        """
        Gets all the data associated with a single entry

        :param token: Valid token for entry
        :type token: str
        :raises StatusNotOk: Exception if not found
        :return: object with all entry data
        :rtype: dict

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.get_entry(token='080d33e0-demo-title')
        >>> print(s)
        """

        r = requests.get(f'{self.api_url}{token}', headers=self._headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

    def delete_entry(self, token: str) -> dict:
        """
        Delete an entry entirely

        :param token: Valid token for entry
        :type token: str
        :raises StatusNotOk: Exception on fail
        :return: OK object
        :rtype: dict

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.delete_entry('080d33e0-demo-title')
        >>> print(s)
        """

        r = requests.delete(f'{self.api_url}{token}', headers=self._headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

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

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.update_entry(
        >>>     token='080d33e0-demo-title',
        >>>     description='Some description',
        >>>     priority='high'
        >>> )
        >>> print(s)
        """

        payload = {
            'priority': priority,
            'description': description
        }
        r = requests.post(f'{self.api_url}{token}',
                          headers=self._headers, json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

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

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.create_new_section(
        >>>     token='080d33e0-demo-title',
        >>>     type='stdout',
        >>>     output='echo output',
        >>>     command='echo',
        >>>     comment='Demo comment'
        >>> )
        >>> print(s)
        """

        payload = {
            'type': type,
            'output': output,
            'command': command,
            'user': self.username,
            'comment': {
                'text': comment,
                'username': self.username,
                'avatar': self.avatar
            }
        }
        if type not in self._valid_types:
            raise TypeError(f'Valid types are {self._valid_types}')
        r = requests.patch(f'{self.api_url}{token}', headers=self._headers,
                           json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

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

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.add_comment(
        >>>     token='080d33e0-demo-title',
        >>>     dataid='bfe02810-656d-11e9-be3a-05d3364ece32',
        >>>     comment='Additional comment'
        >>> )
        >>> print(s)
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
            raise StatusNotOk(r.status_code, r.text)

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

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.delete_section(
        >>>     token='080d33e0-demo-title',
        >>>     dataid='12f45080-656e-11e9-be3a-05d3364ece32'
        >>> )
        >>> print(s)
        """

        r = requests.delete(
            f'{self.api_url}{token}/{dataid}', headers=self._headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

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

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.create_new_entry(
        >>>     title='Some demo title',
        >>>     category='ios'
        >>> )
        >>> print(s)
        """

        if category not in self._valid_categories:
            raise NotValidCategory(
                f'Valid categories are {self._valid_categories}')
        token = self._token_generator(title)
        payload = {
            'title': title,
            'category': category
        }
        r = requests.post(f'{self.api_url}create/{token}', headers=self._headers,
                          json=payload)
        if r.status_code == 200:
            print('Created new entry')
        else:
            raise StatusNotOk(r.status_code, r.text)

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

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.reset_api_key(
        >>>     old_apikey='oldSecretApiKey',
        >>>     username='demoUser'
        >>> )
        >>> print(s)
        """

        payload = {
            'apiKey': old_apikey,
            'username': username
        }
        r = requests.post(f'{self.api_url}reset/key',
                          headers=self._headers, json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

    def reset_password(self, password: str) -> dict:
        """
        Reset password

        :param password: A valid password
        :type password: str
        :raises StatusNotOk: Exception on fail
        :return: object containing new API key
        :rtype: dict

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.reset_password(
        >>>     password='newGoodPassword'
        >>> )
        >>> print(s)
        """

        payload = {
            'apiKey': self.apiKey,
            'username': self.username,
            'password': password
        }
        r = requests.post(f'{self.api_url}reset/password',
                          headers=self._headers, json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

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

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.change_username(
        >>>     api_key='secretApiKey',
        >>>     old_username='oldUserName',
        >>>     new_username='newUserName'
        >>> )
        >>> print(s)
        """

        payload = {
            'apiKey': api_key,
            'username': old_username,
            'newUsername': new_username
        }
        r = requests.post(f'{self.api_url}reset/username',
                          headers=self._headers, json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

    def change_avatar(self, avatar: str) -> dict:
        """
        Change the username to a new username

        :param avatar: Valid avatar url. Only built in avatars are allowed. A valid 
        url is ``/static/avatar/[1-9].png``
        :type avatar: str
        :raises StatusNotOk: Exception on fail
        :return: object with both old and new usernames
        :rtype: dict

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.change_avatar(
        >>>     avatar='/static/avatar/2.png'
        >>> )
        >>> print(s)
        """

        payload = {
            'avatar': avatar
        }
        r = requests.post(f'{self.api_url}reset/avatar',
                          headers=self._headers, json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

    def get_all_chat(self, token: str) -> dict:
        """
        Get all chat messages associated with an entry

        :param token: A valid token
        :type token: str
        :raises StatusNotOk: Exception on fail
        :return: Array of all chat objects
        :rtype: dict

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.get_all_chat(
        >>>     token='ef3ace10-test'
        >>> )
        >>> print(s)
        """

        r = requests.get(f'{self.api_url}{token}/chat',
                         headers=self._headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

    def post_chat_message(self, token: str, message: str) -> dict:
        """
        Post a chat message to an entry

        :param token: A valid entry token
        :type token: str
        :param message: A valid message
        :type message: str
        :raises StatusNotOk: Exception on fail
        :return: Response object
        :rtype: dict

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.post_chat_message(
        >>>     token='ef3ace10-test',
        >>>     message='Message from Py'
        >>> )
        >>> print(s)
        """
        payload = {
            'username': self.username,
            'message': message
        }
        r = requests.post(f'{self.api_url}{token}/chat',
                          headers=self._headers, json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

    def delete_chat_message(self, token: str, chat_id: str) -> dict:
        """
        Delete a chat message from an entry

        :param token: A valid entry token
        :type token: str
        :param chat_id: A valid chat Id
        :type chat_id: str
        :raises StatusNotOk: Exception on fail
        :return: Response object
        :rtype: dict

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.delete_chat_message(
        >>>     token='ef3ace10-test',
        >>>     chat_id='5cc0e3baecfc8a16279b4756'
        >>> )
        >>> print(s)
        """
        payload = {
            'chatId': chat_id,
        }
        r = requests.delete(f'{self.api_url}{token}/chat',
                            headers=self._headers, json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

    def update_chat_message(self, token: str, chat_id: str, message: str) -> dict:
        """
        Update a chat message from an entry

        :param token: A valid entry token
        :type token: str
        :param chat_id: A valid chat Id
        :type chat_id: str
        :param message: A valid message
        :type message: str
        :raises StatusNotOk: Exception on fail
        :return: Response object
        :rtype: dict

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.update_chat_message(
        >>>     token='ef3ace10-test',
        >>>     chat_id='5cc0e3baecfc8a16279b4756'
        >>>     message='Some message to update with'
        >>> )
        >>> print(s)
        """
        payload = {
            'chatId': chat_id,
            'message': message,
        }
        r = requests.patch(f'{self.api_url}{token}/chat',
                           headers=self._headers, json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

    def delete_comment(self, token: str, dataid: str, commentId: str) -> dict:
        """
        Delete a comment from a section

        :param token: A valid entry token
        :type token: str
        :param dataid: A valid section data id
        :type dataid: str
        :param commentId: A valid comment id
        :type commentId: str
        :raises StatusNotOk: Exception on fail
        :return: object with response
        :rtype: dict

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.delete_comment(
        >>>     token='ef3ace10-test',
        >>>     dataid='f12489f0-6619-11e9-a6dd-df81fb7d1eca',
        >>>     commentId='5cbfafd1038ef8ee06c18a3c'
        >>> )
        >>> print(s)
        """

        payload = {
            'commentId': commentId
        }
        r = requests.delete(f'{self.api_url}{token}/{dataid}/comment',
                            headers=self._headers, json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

    def get_report(self, token: str, render: bool=False) -> str:
        """
        Generate a markdown report for an entry. Can be 
        optionally send to render the markdown

        :param token: A valid token
        :type token: str
        :param render: Render?, defaults to False
        :type render: bool, optional
        :raises StatusNotOk: Exception on fail
        :return: Markdown scaffold
        :rtype: str

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.get_report(
        >>>     token='someDemotoken'
        >>> )
        >>> print(s)
        """
        if render:
            render = 'true'
        else:
            render = 'false'
        r = request.get(f'{self.api_url}{token}/report/render={render}',
                        headers=self._headers)
        if r.status_code == 200:
            return r.text
        else:
            raise StatusNotOk(r.status_code, r.text)

    def validate_api_key(self, api_key: str) -> dict:
        """
        Validate and API key and if valid, return the API and assciated username

        :param api_key: Valid API key
        :type api_key: str
        :raises StatusNotOk: Exception
        :return: dict containing the valid API key and associated username
        :rtype: dict

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.validate_api_key('secretApiKey')
        >>> print(s)
        """

        payload = {
            'key': api_key
        }
        r = requests.post(f'{self.base_url}misc/valid/key', json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

    def get_valid_token(self, title: str) -> dict:
        """
        Supply a title, and get a valid token back. This is useful when 
        testing token creation, or when working with other API endpoints.

        :param title: Title to generate the token with
        :type title: str
        :raises StatusNotOk: Exception
        :return: reponse dictionary object
        :rtype: dict

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.get_valid_token(
        >>>     title='Some demo title'
        >>> )
        >>> print(s)
        """

        payload = {
            'title': title
        }
        r = requests.post(f'{self.base_url}misc/valid/token', json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

    def admin_all_users(self) -> list:
        """
        Get an array of all user objects

        :raises StatusNotOk: Exception
        :return: Array of user objects
        :rtype: list

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.admin_all_users()
        >>> print(s)
        """

        r = requests.get(f'{self.api_url}admin/allusers',
                         headers=self._headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

    def admin_find_user(self, user_id: str) -> dict:
        """
        Find a user by user id

        :param user_id: A valid user id
        :type user_id: str
        :raises StatusNotOk: Exception
        :return: A complete user object
        :rtype: dict

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.admin_find_user('1')
        >>> print(s)
        """

        r = requests.get(
            f'{self.api_url}admin/user?id={user_id}', headers=self._headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

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

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.admin_create_user(
        >>>     username='someUserName',
        >>>     password='someSecretPassword',
        >>>     isAdmin=False,
        >>>     avatar='http://pstu.ac.bd/images/defaults/default.png'
        >>> )
        >>> print(s)
        """

        payload = {
            'username': username,
            'password': password,
            'isAdmin': isAdmin,
            'avatar': avatar
        }
        r = requests.post(f'{self.api_url}admin/user',
                          headers=self._headers, json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

    def admin_delete_user(self, user_id: str) -> dict:
        """
        Delete a user by user id

        :param user_id: A valid user id
        :type user_id: str
        :raises StatusNotOk: Exception
        :return: True if deleted
        :rtype: dict

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.admin_delete_user(
        >>>     user_id='5cbf14d11beae8c5e3bdc695'
        >>> )
        >>> print(s)
        """

        payload = {
            'user_id': user_id
        }
        r = requests.delete(f'{self.api_url}admin/user',
                            headers=self._headers, json=payload)
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
        :param isAdmin: Toggle 'true' or 'false'
        :param isAdmin: bool, optional
        :param isDisabled: Toggle 'true' or 'false'
        :param isDisabled: bool, optional
        :param avatar: A link to the profile image for the user, defaults to '/static/logo.png'
        :param avatar: str, optional
        :raises StatusNotOk: Exception
        :return: A complete user object
        :rtype: dict

        >>> # This example shows how to change the admin status of a user
        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.admin_update_user(
        >>>     user_id='2',
        >>>     isAdmin='false',
        >>>     isDisabled='false'
        >>> )
        >>> print(s)
        """
        payload = kwargs
        r = requests.patch(
            f'{self.api_url}admin/user?id={user_id}', headers=self._headers, json=payload)
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

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.admin_get_logs()
        >>> print(s)
        """

        r = requests.get(f'{self.api_url}admin/logs', headers=self._headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)

    def admin_get_status(self) -> list:
        """
        Gets the server status as an array of objects

        :raises StatusNotOk: Exception
        :return: Array of log objects
        :rtype: list

        >>> from saramPy.api import SaramAPI
        >>> saram = SaramAPI()
        >>> s = saram.admin_get_status()
        >>> print(s)
        """

        r = requests.get(f'{self.api_url}admin/status', headers=self._headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise StatusNotOk(r.status_code, r.text)
