from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option
import logging
import os
import sys
import log_helper
from datetime import datetime
import uuid
import json
import splunk.rest as rest
import boto3

debug_logger = log_helper.setup(logging.INFO, 'GetAWSPriceListDebug', 'get_aws_price_list_debug.log')

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

@Configuration()
class GetAWSPriceListCommand(GeneratingCommand):

    aws_master_account_id = Option(require=True)
    service_code = Option(require=True)

    def generate(self):
        session_key = self._metadata.searchinfo.session_key
        grand_central_aws_accounts_rest_path = '/servicesNS/%s/%s/grand_central_aws_accounts/%s' % ('nobody', 'grand_central', self.aws_master_account_id)

        grand_central_aws_accounts_eai_response_payload = simple_request_eai(grand_central_aws_accounts_rest_path, 'read', 'GET', session_key)

        grand_central_aws_account = grand_central_aws_accounts_eai_response_payload['entry'][0]

        aws_secret_key_link_alternate = grand_central_aws_account['content']['aws_secret_key_link_alternate']
        aws_access_key = grand_central_aws_account['content']['aws_access_key']

        passwords_conf_payload = simple_request_eai(aws_secret_key_link_alternate, 'list', 'GET', session_key)
        SECRET_KEY = passwords_conf_payload['entry'][0]['content']['clear_password']


        client = boto3.client('pricing', aws_access_key_id=aws_access_key, aws_secret_access_key=SECRET_KEY, region_name='us-east-1')
        response = client.get_products(ServiceCode=self.service_code)

        for price in response['PriceList']:
            yield {"_raw": price}

        while 'NextToken' in response:
            response = client.get_products(ServiceCode=self.service_code, NextToken=response['NextToken'])
            for price in response['PriceList']:
                yield {"_raw": price}

dispatch(GetAWSPriceListCommand, sys.argv, sys.stdin, sys.stdout, __name__)
