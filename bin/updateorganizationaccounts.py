from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option
import logging
import os
import sys
import log_helper
from datetime import datetime
import uuid
import json
import splunk.rest as rest

debug_logger = log_helper.setup(logging.INFO, 'UpdateOrganizationAccountsDebug', 'update_organization_accounts_debug.log')

pid = os.getpid()
tstart = datetime.now()
guid = str(uuid.uuid4().hex)


def simple_request_messages_to_str(messages):
    """
    Returns a readable string from a simple request response message

    Arguments
    messages -- The simple request response message to parse
    """
    entries = []
    for message in messages:
        entries.append(message.get('text'))
    return ','.join(entries)


def simple_request_eai(url, action, method, session_key, params=None):
    """
    Returns the payload response from a simpleRequest call

    Arguments
    url -- The REST handler endpoint to use in the simpleRequest
    action -- The readable requested action used in logs
    method -- The REST method to make the request with
    session_key -- The valid session key which will be used in the request
    params -- The parameters sent in the POST body of the simpleRequest
    """
    if not params:
        params = {}
    debug_logger.info(
        'action=http_internal_request state=start method=%s url=%s pid=%s guid=%s' % (method, url, pid, guid))
    try:
        response, content = rest.simpleRequest(
            url,
            getargs=dict(output_mode='json'),
            postargs=params,
            method=method,
            sessionKey=session_key
        )
    except Exception, e:
        debug_logger.error('action=http_internal_request state=error error="%s" pid=%s guid=%s' % (e, pid, guid))
        raise Exception('Unable to %s %s entry. %s' % (action, url, e))
    debug_logger.info('action=http_internal_request state=end pid=%s guid=%s' % (pid, guid))

    try:
        payload = json.loads(content)
    except Exception, e:
        debug_logger.error('action=http_internal_request state=error error="%s"' % e)
        raise Exception('Unable to parse %s response payload.' % url)

    if response.status not in [200, 201]:
        message = simple_request_messages_to_str(response.messages)
        debug_logger.error('action=http_internal_request state=error error="%s"' % message)
        raise Exception(
            'Unable to %s %s entry. %s' % (action, url, message))
    return payload

@Configuration(type='reporting')
class UpdateOrganizationAccountsCommand(GeneratingCommand):

    aws_master_account_id = Option(require=True)

    def generate(self):
        session_key = self._metadata.searchinfo.session_key
        organizations_handler_path = '/servicesNS/nobody/grand-central/organizations'

        debug_logger.info('action=organizations_accounts_update state=start pid=%s guid=%s' % (pid, guid))
        try:
            post_args = {
                'name': self.aws_master_account_id,
                'aws_account_id': self.aws_master_account_id,
            }
            organizations_accounts_update_eai_response_payload = simple_request_eai(
                organizations_handler_path,
                'create',
                'POST',
                session_key,
                params=post_args,
            )
        except Exception, e:
            debug_logger.error('action=organizations_accounts_update state=error error="%s" pid=%s guid=%s' % (e, pid, guid))
            raise e
        debug_logger.info('action=organizations_accounts_update state=end pid=%s guid=%s' % (pid, guid))

        yield {'Update Status': 'Successful'}

dispatch(UpdateOrganizationAccountsCommand, sys.argv, sys.stdin, sys.stdout, __name__)
