import logging
import os
import sys
import uuid
import splunk.admin as admin
import grand_central_gcp_accounts_schema
import urllib
import hashlib
import base_eai_handler
import log_helper
import json
import time
from datetime import datetime

libpath = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(libpath, '3rdparty')]
import boto3

if sys.platform == 'win32':
    import msvcrt

    # Binary mode is required for persistent mode on Windows.
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)

# Setup the handler
logger = log_helper.setup(logging.INFO, 'GrandCentralGCPAccountsEAIHandler', 'grand_central_gcp_accounts_handler.log')

class GrandCentralGCPAccountsEAIHandler(base_eai_handler.BaseEAIHandler):
    def setup(self):
        # Add our supported args
        for arg in grand_central_gcp_accounts_schema.ALL_FIELDS:
            self.supportedArgs.addOptArg(arg)

    def handleList(self, confInfo):
        """
        Called when user invokes the "list" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Grand Central GCP accounts list requested.')

        # Fetch from grand_central_gcp_accounts conf handler
        conf_handler_path = self.get_conf_handler_path_name('grand_central_gcp_accounts', 'nobody')
        grand_central_gcp_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'list', 'GET')

        # Add link alternate (without mgmt, scheme, host, port) to list response
        for grand_central_gcp_account in grand_central_gcp_accounts_eai_response_payload['entry']:
            grand_central_gcp_account_link_alternate = grand_central_gcp_account['links']['alternate'].replace('/configs/conf-grand_central_gcp_accounts/', '/grand_central_gcp_accounts/')

            grand_central_gcp_account['content']['grand_central_gcp_accounts_link_alternate'] = grand_central_gcp_account_link_alternate


        self.set_conf_info_from_eai_payload(confInfo, grand_central_gcp_accounts_eai_response_payload)

    def handleCreate(self, confInfo):
        """
        Called when user invokes the "create" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Grand Central GCP account creation requested.')

        # Validate and extract correct POST params
        server_params = self.validate_server_schema_params()
        auth_params = self.validate_auth_schema_params()
        params = auth_params.copy()
        params.update(server_params)

        # Password creation
        gcp_json_key_link_alternate = self.password_create(params['gcp_json_key'], params['gcp_json_key'])

        # grand_central_gcp_accounts.conf creation and response
        post_args = {
            'name': params['name'],
            'display_name': params['display_name'],
            'gcp_project_id': params['gcp_project_id'],
            'gcp_json_key_link_alternate': gcp_json_key_link_alternate,
            'data_collection_deployed': '0',
            'data_collection_deployment_success': '0',
            'tags': params['tags'],
            'splunk_account_link_alternate': self.get_param('splunk_account_link_alternate', default=''),
        }

        grand_central_gcp_accounts_eai_response_payload = self.simple_request_eai(self.get_conf_handler_path_name('grand_central_gcp_accounts'),
                                                                    'create', 'POST', post_args)

        # Always populate entry content from request to list handler.
        grand_central_gcp_accounts_rest_path = '/servicesNS/%s/%s/grand_central_gcp_accounts/%s' % (
            'nobody', self.appName, urllib.quote_plus(params['name']))
        grand_central_gcp_accounts_eai_response_payload = self.simple_request_eai(grand_central_gcp_accounts_rest_path, 'read', 'GET')

        self.set_conf_info_from_eai_payload(confInfo, grand_central_gcp_accounts_eai_response_payload)

    def handleEdit(self, confInfo):
        """
        Called when user invokes the 'edit' action. Index modification is not supported through this endpoint. Both the
        scripted input and the grand_central_gcp_accounts.conf stanza will be overwritten on ANY call to this endpoint.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Grand Central GCP Account edit requested.')

        name = self.callerArgs.id
        conf_stanza = urllib.quote_plus(name)
        params = self.validate_server_schema_params()
        conf_handler_path = '%s/%s' % (self.get_conf_handler_path_name('grand_central_gcp_accounts', 'nobody'), conf_stanza)

        grand_central_gcp_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'list', 'GET')
        old_gcp_json_key_name = grand_central_gcp_accounts_eai_response_payload['entry'][0]['content'][
            'gcp_json_key_name']
        old_gcp_json_key_link_alternate = grand_central_gcp_accounts_eai_response_payload['entry'][0]['content']['gcp_json_key_link_alternate']

        # Create post args - remove name to ensure edit instead of create

        grand_central_gcp_accounts_conf_postargs = {
            'display_name': params['display_name'],
        }

        # Handle optional post args
        if 'tags' in params and params['tags'] != '':
            grand_central_gcp_accounts_conf_postargs['tags'] = params['tags']
        if 'splunk_account_link_alternate' in params and params['splunk_account_link_alternate'] != '':
            grand_central_gcp_accounts_conf_postargs['splunk_account_link_alternate'] = params['splunk_account_link_alternate']

        # Change password if provided in params
        if old_gcp_json_key_name != params['gcp_json_key_name']:
            if self.get_param('gcp_json_key'):
                # New username and password provided
                auth_params = self.validate_auth_schema_params()
                params.update(auth_params)
                # Edit passwords.conf stanza
                grand_central_gcp_accounts_conf_postargs['gcp_json_key_link_alternate'] = self.password_edit(old_gcp_json_key_link_alternate, params['gcp_json_key_name'], params['gcp_json_key'])
            else:
                # Can't change username without providing password
                raise admin.InternalException('GCP JSON Key name must be provided on GCP JSON Key change.')
        if (old_gcp_json_key_name == params['gcp_json_key_name'] and self.get_param('gcp_json_key')):
            # Password update to existing username
            auth_params = self.validate_auth_schema_params()
            params.update(auth_params)
            # Edit passwords.conf stanza
            grand_central_gcp_accounts_conf_postargs['gcp_json_key_link_alternate'] = self.password_edit(old_gcp_json_key_link_alternate, params['gcp_json_key_name'], params['gcp_json_key'])

        # Edit grand_central_gcp_accounts.conf
        grand_central_gcp_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'edit', 'POST',
                                                                                  grand_central_gcp_accounts_conf_postargs)

        # Always populate entry content from request to list handler.
        grand_central_gcp_accounts_rest_path = '/servicesNS/%s/%s/grand_central_gcp_accounts/%s' % ('nobody', self.appName, conf_stanza)
        grand_central_gcp_accounts_eai_response_payload = self.simple_request_eai(grand_central_gcp_accounts_rest_path, 'read', 'GET')
        self.set_conf_info_from_eai_payload(confInfo, grand_central_gcp_accounts_eai_response_payload)

    def handleRemove(self, confInfo):
        """
        Called when user invokes the 'remove' action. Removes the requested stanza from inputs.conf (scripted input),
        removes the requested stanza from grand_central_gcp_accounts.conf, and removes all related credentials

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Grand Central GCP Account removal requested.')

        name = self.callerArgs.id
        conf_stanza = urllib.quote_plus(name)

        # Grab the link alternate and username from the grand_central_gcp_accounts GET response payload before it gets deleted
        grand_central_gcp_accounts_rest_path = '/servicesNS/%s/%s/grand_central_gcp_accounts/%s' % ('nobody', self.appName, conf_stanza)
        grand_central_gcp_accounts_eai_response_payload = self.simple_request_eai(grand_central_gcp_accounts_rest_path, 'read', 'GET')
        gcp_json_key_link_alternate = grand_central_gcp_accounts_eai_response_payload['entry'][0]['content']['gcp_json_key_link_alternate']

        # Delete passwords.conf stanza
        self.password_delete(gcp_json_key_link_alternate)

        # Delete grand_central_gcp_accounts.conf stanza
        conf_handler_path = '%s/%s' % (self.get_conf_handler_path_name('grand_central_gcp_accounts'), conf_stanza)
        grand_central_gcp_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'remove', 'DELETE')
        self.set_conf_info_from_eai_payload(confInfo, grand_central_gcp_accounts_eai_response_payload)

    def password_edit(self, password_link_alternate, new_username, password):
        """
        Edits a password entry using the storage/passwords endpoint. This endpoint will first delete the existing
        entry, then creates a new one.

        Arguments
        password_link_alternate -- The link alternate of the password entry
        password -- The actual password which will be encrypted and stored in passwords.conf
        """
        self.password_delete(password_link_alternate)
        return self.password_create(new_username, password)

    def password_delete(self, password_link_alternate):
        """
        Deletes a password entry using the storage/passwords endpoint.

        Arguments
        password_link_alternate -- The link alternate of the password entry
        """
        passwords_conf_payload = self.simple_request_eai(password_link_alternate, 'remove', 'DELETE')

    def hash_len_confirm(self, password, password_after, password_orig_hash, password_after_hash):
        """
        Confirms length of plaintext password matches retrieved decrypted password. Also compares the hashes of
        the initial and retrieved passwords.

        Arguments
        password -- The actual password which was encrypted and stored in passwords.conf
        password_after -- The decrypted password retrieved from passwords.conf
        password_orig_hash -- The hash of the actual password which was encrypted and stored in passwords.conf
        password_after_hash -- The hash of the decrypted password retrieved from passwords.conf
         """
        assert len(password_after) == len(password)
        assert password_orig_hash == password_after_hash

    def password_create(self, username, password):
        """
        Creates a password entry using the storage/passwords endpoint. This endpoint will validate successful creationof the password by comparing length and hashes of the provided password and the retrieved cleartext password. Password realm will include a unique GUID.

        Arguments
        username -- The username associated with the provided password
        password -- The actual password which will be encrypted and stored in passwords.conf
        """
        m = hashlib.md5()
        m.update(password)
        password_orig_hash = m.hexdigest()

        realm = str(uuid.uuid4().hex)

        passwords_conf_postargs = {
            'realm': realm,
            'name': username,
            'password': password
        }

        passwords_rest_path = '/servicesNS/%s/%s/storage/passwords/' % ('nobody', self.appName)

        # Create password
        passwords_conf_payload = self.simple_request_eai(passwords_rest_path, 'create', 'POST', passwords_conf_postargs)
        password_link_alternate = passwords_conf_payload['entry'][0]['links']['alternate']

        # Load password to check hash and length
        passwords_conf_payload = self.simple_request_eai(password_link_alternate, 'list', 'GET')
        password_after = passwords_conf_payload['entry'][0]['content']['clear_password']

        m = hashlib.md5()
        m.update(password_after)
        password_after_hash = m.hexdigest()

        try:
            self.hash_len_confirm(password, password_after, password_orig_hash, password_after_hash)
        except Exception, e:
            logger.error(e)
            raise admin.InternalException('Password stored incorrectly %s' % e)

        return password_link_alternate

    def convert_date_to_age(self, datetime_string):

        if datetime_string == '0' or datetime_string == '':
            return datetime_string

        epoch = datetime(1970, 1, 1)
        joined_date = int((datetime.strptime(datetime_string, '%m/%d/%Y') - epoch).total_seconds())

        today = int(time.time())
        return str((today - joined_date)/(60*60*24))

    def validate_server_schema_params(self):
        """
        Validates raw request params against the server schema
        """
        params = self.get_params(schema=grand_central_gcp_accounts_schema, filter=grand_central_gcp_accounts_schema.SERVER_FIELDS)
        return self.validate_params(grand_central_gcp_accounts_schema.server_schema, params)

    def validate_auth_schema_params(self):
        """
        Validates raw request params against the auth schema
        """
        params = self.get_params(schema=grand_central_gcp_accounts_schema, filter=grand_central_gcp_accounts_schema.AUTH_FIELDS)
        return self.validate_params(grand_central_gcp_accounts_schema.auth_schema, params)

admin.init(GrandCentralGCPAccountsEAIHandler, admin.CONTEXT_NONE)
