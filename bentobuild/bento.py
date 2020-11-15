import os
import sys
import shortuuid

from bentobuild.build import KubernetesApiClient
from kubernetes import client
from kubernetes.client.rest import ApiException

default_name = "model-build"


class BentoJobBuilder():
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
                   ns,
                   cleanup=True,
                   name=default_name):

        print("fn=safe_build at=build-namespace ns=%s" % ns)

        self.check_ns_exists(ns)

        return self.create_builder_job(service, image, ns, name)

    def check_ns_exists(self, ns):
        try:
            api_response = self.corev1.read_namespace(ns)
            print("at=verify-namespace-success ns=%s" % ns)
        except ApiException as e:
                print("at=error-ns-doesnt-exist fn=check_ns_exists ns=%q" % ns)

    def create_builder_job(self, service, image, ns,
                           name=default_name):

        job = self.api.create_builder_pod(
            name,
            image,
            ns,
            service
            )

        try:
            created = self.batchv1.create_namespaced_job(
                namespace=ns,
                body=job)
            #print(str(created))
        except ApiException as e:
            print(e)
            sys.Exit(1)

        return created

    def status(self, job):
        print("fn=status name=%s ns=%s" % (
            job.metadata.name,
            job.metadata.namespace))
        try:
            update = self.batchv1.read_namespaced_job(
                job.metadata.name,
                job.metadata.namespace)
            print(str(update.status))
        except ApiException as e:
            print("at=status error=%s" % e)

#class BentoTaskBuilder():
#    def __init__(self):
#        print("wip")
