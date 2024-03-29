# Based on https://github.com/chris-brown-nz/python-gmail-api
# Created: 2016-12-14
# Author: Chris Brown
# Edited by: Laurence Keijzer
# Based on and using code from examples at: https://developers.google.com/gmail/api/
# Google API test harness: https://developers.google.com/apis-explorer/?hl=en_GB#p/gmail/v1/

from __future__ import print_function
import base64
import email.mime.text
import os
import httplib2
import main
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from googleapiclient.discovery import build

# --------------------------------------------------------------------------------------
# This is the name of the secret file you download from https://console.developers.google.com/iam-admin/projects
# Give it a name that is unique to this project
CLIENT_SECRET_FILE = 'client_secret.json'
# This is the file that will be created in ~/.credentials holding your credentials. It will be created automatically
# the first time you authenticate and will mean you don't have to re-authenticate each time you connect to the API.
# Give it a name that is unique to this project
CREDENTIAL_FILE = 'api_credentials.json'

APPLICATION_NAME = 'AskForMoney'
# Set to True if you want to authenticate manually by visiting a given URL and supplying the returned code
# instead of being redirected to a browser. Useful if you're working on a server with no browser.
# Set to False if you want to authenticate via browser redirect.
MANUAL_AUTH = False
# --------------------------------------------------------------------------------------

try:
    import argparse

    # Include also extra argument options
    flags = argparse.ArgumentParser(parents=[tools.argparser, main.create_argument_parser()]).parse_args()
    if MANUAL_AUTH:
        flags.noauth_local_webserver = True
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials at ~/.credentials/gmail-python-quickstart.json
SCOPES = ['https://mail.google.com/',
          'https://www.googleapis.com/auth/gmail.compose',
          'https://www.googleapis.com/auth/gmail.modify',
          'https://www.googleapis.com/auth/gmail.send']


class PythonGmailAPI:
    def __init__(self):
        pass

    def gmail_send(self, sender_address, to_address, subject, body):
        print('Sending message, please wait...')
        message = self.__create_message(sender_address, to_address, subject, body)
        credentials = self.__get_credentials()
        service = self.__build_service(credentials)
        raw = message['raw']
        raw_decoded = raw.decode("utf-8")
        message = {'raw': raw_decoded}
        message_id = self.__send_message(service, 'me', message)
        print('Message sent. Message ID: ' + message_id)

    def gmail_draft(self, sender_address, to_address, subject, body):
        print('Creating message, please wait...')
        message = self.__create_message(sender_address, to_address, subject, body)
        credentials = self.__get_credentials()
        service = self.__build_service(credentials)
        raw = message['raw']
        raw_decoded = raw.decode("utf-8")
        message = {'raw': raw_decoded}
        message_id = self.__draft_message(service, 'me', message)
        print('Message created. Message ID: ' + message_id)

    @staticmethod
    def __get_credentials():
        """Gets valid user credentials from storage.
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, CREDENTIAL_FILE)
        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            credentials = tools.run_flow(flow, store, flags)
            print('Storing credentials to ' + credential_path)
        return credentials

    @staticmethod
    def __create_message(sender, to, subject, message_text):
        """Create a message for an email.
        Args:
          sender: Email address of the sender.
          to: Email address of the receiver.
          subject: The subject of the email message.
          message_text: The text of the email message.
        Returns:
          An object containing a base64url encoded email object.
        """
        message = email.mime.text.MIMEText(message_text, 'plain', 'utf-8')
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        encoded_message = {'raw': base64.urlsafe_b64encode(message.as_bytes())}
        return encoded_message

    @staticmethod
    def __send_message(service, user_id, message):
        """Send an email message.
        Args:
          service: Authorized Gmail API service instance.
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          message: Message to be sent.
        Returns:
          Sent Message ID.
        """
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        return message['id']

    @staticmethod
    def __draft_message(service, user_id, message):
        """Draft an email message.
        Args:
          service: Authorized Gmail API service instance.
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          message: Message to be sent.
        Returns:
          Sent Message ID.
        """
        draft = (service.users().drafts().create(userId=user_id, body={"message": message}).execute())
        return draft['id']

    @staticmethod
    def __build_service(credentials):
        """Build a Gmail service object.
        Args:
            credentials: OAuth 2.0 credentials.
        Returns:
            Gmail service object.
        """
        http = httplib2.Http()
        http = credentials.authorize(http)
        return build('gmail', 'v1', http=http)
