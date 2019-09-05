import logging
import os
import sys
import splunk.admin as admin
import splunk_accounts_schema
import urllib
import base_eai_handler
import log_helper

if sys.platform == 'win32':
    import msvcrt

    # Binary mode is required for persistent mode on Windows.
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)

# Setup the handler
logger = log_helper.setup(logging.INFO, 'SplunkAccountsEAIHandler', 'splunk_accounts_handler.log')

class SplunkAccountsEAIHandler(base_eai_handler.BaseEAIHandler):
    def setup(self):
        # Add our supported args
        for arg in splunk_accounts_schema.ALL_FIELDS:
            self.supportedArgs.addOptArg(arg)

    def handleList(self, confInfo):
        """
        Called when user invokes the "list" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Splunk accounts list requested.')

        # Fetch from splunk accounts conf handler
        conf_handler_path = self.get_conf_handler_path_name('splunk_accounts', 'nobody')
        splunk_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'list', 'GET')

        self.set_conf_info_from_eai_payload(confInfo, splunk_accounts_eai_response_payload)

    def handleCreate(self, confInfo):
        """
        Called when user invokes the "create" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Splunk account creation requested.')

        # Validate and extract correct POST params
        params = self.validate_splunk_accounts_schema_params()

        post_args = {
            'name': params['name'],
            'label': params['label'],
            'splunk_hec_endpoint': params['splunk_hec_endpoint'],
            'splunk_hec_ack_token': params['splunk_hec_ack_token'],
            'splunk_hec_no_ack_token': params['splunk_hec_no_ack_token'],
        }

        splunk_accounts_eai_response_payload = self.simple_request_eai(self.get_conf_handler_path_name('splunk_accounts'),
            'create', 'POST', post_args)

        splunk_accounts_rest_path = '/servicesNS/%s/%s/splunk_accounts/%s' % ('nobody', self.appName, urllib.quote_plus(params['name']))

        splunk_accounts_eai_response_payload = self.simple_request_eai(splunk_accounts_rest_path, 'read', 'GET')

        self.set_conf_info_from_eai_payload(confInfo, splunk_accounts_eai_response_payload)


    def handleEdit(self, confInfo):
        """
        Called when user invokes the 'edit' action. Index modification is not supported through this endpoint. Both the
        scripted input and the grand_central_aws_accounts.conf stanza will be overwritten on ANY call to this endpoint.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Splunk account edit requested.')

        name = self.callerArgs.id
        conf_stanza = urllib.quote_plus(name)
        params = self.validate_splunk_accounts_schema_params()
        conf_handler_path = '%s/%s' % (
        self.get_conf_handler_path_name('splunk_accounts', 'nobody'), conf_stanza)

        # Create post args - remove name to ensure edit instead of create
        splunk_accounts_conf_postargs = {
            'label': params['label'],
            'splunk_hec_endpoint': params['splunk_hec_endpoint'],
            'splunk_hec_ack_token': params['splunk_hec_ack_token'],
            'splunk_hec_no_ack_token': params['splunk_hec_no_ack_token'],
        }

        # Edit splunk_accounts.conf
        splunk_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'edit', 'POST',
                                                                                splunk_accounts_conf_postargs)

        # Always populate entry content from request to list handler.
        splunk_accounts_rest_path = '/servicesNS/%s/%s/splunk_accounts/%s' % (
        'nobody', self.appName, conf_stanza)
        splunk_accounts_eai_response_payload = self.simple_request_eai(splunk_accounts_rest_path,
                                                                                'read', 'GET')
        self.set_conf_info_from_eai_payload(confInfo, splunk_accounts_eai_response_payload)


    def handleRemove(self, confInfo):
        """
        Called when user invokes the 'remove' action. Removes the requested stanza from inputs.conf (scripted input),
        removes the requested stanza from grand_central_aws_accounts.conf, and removes all related credentials

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Splunk account removal requested.')

        name = self.callerArgs.id
        conf_stanza = urllib.quote_plus(name)

        splunk_accounts_rest_path = '/servicesNS/%s/%s/splunk_accounts/%s' % (
            'nobody', self.appName, urllib.quote_plus(name))
        splunk_accounts_eai_response_payload = self.simple_request_eai(splunk_accounts_rest_path,
                                                                                'read', 'GET')

        # Delete splunk_accounts.conf stanza
        conf_handler_path = '%s/%s' % (self.get_conf_handler_path_name('splunk_accounts'), conf_stanza)
        splunk_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'remove', 'DELETE')
        self.set_conf_info_from_eai_payload(confInfo, splunk_accounts_eai_response_payload)


    def validate_splunk_accounts_schema_params(self):
        """
        Validates raw request params against the server schema
        """
        params = self.get_params(schema=splunk_accounts_schema, filter=splunk_accounts_schema.SPLUNK_ACCOUNTS_FIELDS)
        return self.validate_params(splunk_accounts_schema.splunk_accounts_schema, params)


admin.init(SplunkAccountsEAIHandler, admin.CONTEXT_NONE)
