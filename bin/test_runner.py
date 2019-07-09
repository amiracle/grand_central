import argparse
import unittest
import urllib
import splunk.rest as rest

def cli_arguments():
    parser = argparse.ArgumentParser(description='Run /services/** REST handler tests.')
    parser.add_argument('-u', '--username', default='admin', help='Splunk username.')
    parser.add_argument('-p', '--password', default='changeme', help='Splunk password.')
    parser.add_argument('-mgmt', '--mgmt_scheme_host_port', default='https://localhost:8089', help='Splunk mangement scheme host port.')
    args = parser.parse_args()
    return args

def run_test(TestCase):
    runner = unittest.TextTestRunner()
    itersuite = unittest.TestLoader().loadTestsFromTestCase(TestCase)
    runner.run(itersuite)

class TestRESTHandler(unittest.TestCase):
    def create_helper(self, endpoint, postargs, user='nobody'):
        return rest.simpleRequest('/servicesNS/%s/ensemble/%s' % (user, endpoint), getargs=dict(output_mode='json'), postargs=postargs, method='POST', sessionKey=self.session_key)

    def delete_helper(self, endpoint, name, user='nobody'):
        return rest.simpleRequest(
            '/servicesNS/%s/ensemble/%s/%s' % (user, endpoint, urllib.quote_plus(name)),
            getargs=dict(output_mode='json'), method='DELETE',
            sessionKey=self.session_key)

    def edit_helper(self, endpoint, name, postargs, user='nobody'):
        return rest.simpleRequest('/servicesNS/%s/ensemble/%s/%s' % (user, endpoint, urllib.quote_plus(name)), getargs=dict(output_mode='json'),
            postargs=postargs, method='POST', sessionKey=self.session_key)

    def list_helper(self, endpoint, get_args=None, user='nobody'):
        rest_get_args = {
            'output_mode': 'json'
        }
        if get_args is not None:
            rest_get_args.update(get_args, user='nobody')
        return rest.simpleRequest('/servicesNS/%s/ensemble/%s' % (user, endpoint),
            getargs=dict(output_mode='json'), method='GET', sessionKey=self.session_key)

    def read_helper(self, endpoint, name, user='nobody'):
        return rest.simpleRequest('/servicesNS/%s/ensemble/%s/%s' % (user, endpoint, urllib.quote_plus(name)), getargs=dict(output_mode='json'), method='GET',
            sessionKey=self.session_key)

    def template_create_helper(self, search_templates_path, postargs):
        return rest.simpleRequest(search_templates_path, getargs=dict(output_mode='json'), postargs=postargs,method='POST', sessionKey=self.session_key)

    def template_delete_helper(self, search_template_path):
        return rest.simpleRequest(
            search_template_path,
            getargs=dict(output_mode='json'), method='DELETE',
            sessionKey=self.session_key)
