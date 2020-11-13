import os
import sys
import shortuuid

from bentobuild.build import KubernetesApiClient
from kubernetes import client
from kubernetes.client.rest import ApiException

default_name = "myjob"


class BentoPodBuilder():
    def __init__(self, yatai_service=None):
        self.yatai_service = None
        if yatai_service:
            self.yatai_service = yatai_service

        env_yatai_service = os.environ.get('BENTOML__YATAI_SERVICE__URL')
        if env_yatai_service and not self.yatai_service:
            self.yatai_service = env_yatai_service

        if not self.yatai_service:
            print("Yatai Service undefined in arguments and Env! \
                   Set 'BENTOML__YATAI_SERVICE__URL'")

        self.api = KubernetesApiClient(self.yatai_service)

        configuration = client.Configuration()

        self.corev1 = client.CoreV1Api(client.ApiClient(configuration))

        self.batchv1 = client.BatchV1Api(client.ApiClient(configuration))

    # Safe builds are done in a temporary namespace that is auto-cleaned up
    def safe_build(self,
                   service,
                   image,
                   cleanup=True,
                   name=default_name):

        self.ns = "%s%s" % (name,
                            shortuuid.ShortUUID().random(length=4).lower())

        print("at=unique-namespace ns=%s" % self.ns)

        # self.check_ns(service, image, ns, name)

        self.create_ns(self.ns)

        self.create_builder_job(service, image, self.ns, name)

# spawn background process to cleanup after completion
#        if cleanup:
#            self.delete_ns()

    def create_ns(self, ns):
        body = client.V1Namespace(metadata=dict(name=ns))
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
