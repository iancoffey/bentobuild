import os
import sys
import base64

from build import KubernetesApiClient
from kubernetes import client
from kubernetes.client.rest import ApiException

default_name = "bentobuild-job-01"


class BentoPodBuilder():
    def __init__(self, yatai_service=None):
        if yatai_service:
            self.yatai_service = yatai_service
            return
        env_yatai_service = os.environ.get('BENTOML__YATAI_SERVICE__URL')
        if env_yatai_service:
            self.yatai_service = env_yatai_service
            return
        print("No Yatai Service defined nby arguments or Env! \
              Please set 'BENTOML__YATAI_SERVICE__URL'")

        self.api = KubernetesApiClient()

        configuration = client.Configuration()

        self.corev1 = client.CoreV1Api(client.ApiClient(configuration))

        self.batchv1 = client.BatchV1Api(client.ApiClient(configuration))

    # Safe builds are done in a temporary namespace
    def safe_build(self,
                   service,
                   image,
                   ns,
                   cleanup=True,
                   name=default_name):

        self.ns = "build-%s-%s" % name, base64.urlsafe_b64encode(os.urandom(6))

        # self.check_ns(service, image, ns, name)

        self.create_ns(service, image, ns, name)

        self.create_builder_job(service, image, ns, name)

# spawn background process to cleanup after completion
#        if cleanup:
#            self.delete_ns()

    def create_ns(self, ns):
        body = client.V1Namespace(name=ns)
        try:
            api_response = self.corev1.create_namespace(body)
            print(api_response)
        except ApiException as e:
            print("at=error fn=create_namespace err=%q\n" % e)

    def create_builder_job(self, service,
                           image,
                           ns,
                           name=default_name):

        job = self.api.create_builder_pod(
            name,
            image,
            ns,
            service
            )

        try:
            api_response = self.batchv1.create_namespaced_job(
                namespace=ns,
                body=job)
            print(str(api_response.status))
        except ApiException as e:
            print(e)
            sys.Exit(1)
