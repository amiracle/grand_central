import os
import sys
from wa_constants import *

libpath = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(libpath, '3rdparty')]
import botocore.session

class WellArchitected:
    def __init__(self, kwargs):
        self.session = botocore.session.get_session()
        self.client = self.session.create_client(**kwargs)

    def create_workload(self, kwargs):
        try:
            workload = self.client.create_workload(**kwargs)
            return workload
        except Exception as e:
            raise e

    def create_milestone(self, kwargs):
        try:
            milestone = self.client.create_milestone(**kwargs)
            return milestone
        except Exception as e:
            raise e

    def list_workloads(self, kwargs):
        try:
            workloads = self._get_workloads(kwargs)
            return workloads
        except Exception as e:
            raise e

    def list_milestones(self, kwargs):
        try:
            milestones = self._get_milestones(kwargs)
            return milestones
        except Exception as e:
            raise e

    def list_lens_review_improvements(self, kwargs):
        try:
            response = self.client.list_lens_review_improvements(**kwargs)
            return response
        except Exception as e:
            raise e

    def update_workload(self, kwargs):
        try:
            response = self.client.update_workload(**kwargs)
            return response
        except Exception as e:
            raise e

    def update_answer(self, kwargs):
        try:
            response = self.client.update_answer(**kwargs)
            return response
        except Exception as e:
            raise e

    def delete_workload(self, kwargs):
        try:
            response = self.client.delete_workload(**kwargs)
            return response
        except Exception as e:
            print(e)

    def _get_workloads(self, kwargs):
        try:
            response = self.client.list_workloads(**kwargs)
            return response['WorkloadSummaries']
        except Exception as e:
            raise e

    def _get_milestones(self, kwargs):
        try:
            response = self.client.list_milestones(**kwargs)
            return response['MilestoneSummaries']
        except Exception as e:
            raise e