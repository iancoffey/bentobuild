import sys

from bentobuild.builder import GenericBuilder
from bentobuild.k8s import KubernetesApiClient
from kubernetes import client
from kubernetes.client.rest import ApiException

default_name = "model-build"


class BentoJobBuilder(GenericBuilder):
    def __init__(self, yatai_service=None):
        super().__init__(yatai_service)

        print("yataiservice->%s" % self.yatai_service)

        self.api = KubernetesApiClient(self.yatai_service)

        configuration = client.Configuration()

        apiclient = client.ApiClient(configuration)

        self.corev1 = client.CoreV1Api(apiclient)

        self.batchv1 = client.BatchV1Api(apiclient)

    def safe_build(self,
                   service,
                   image,
                   ns,
                   cleanup=True,
                   name=default_name):

        print("fn=safe_build at=build-namespace ns=%s" % ns)

        if not self.check_ns_exists(ns):
            print("at=missing-build-ns ns=%s", ns)
            sys.exit(2)

        return self.create_builder_job(service, image, ns, name)

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
        except ApiException as e:
            print(e)
            sys.Exit(1)

        return created

    def status(self, job):
        try:
            update = self.batchv1.read_namespaced_job(
                job.metadata.name,
                job.metadata.namespace)
        except ApiException as e:
            print("at=status error=%s" % e)
            return

        status = self.parse_status(update.status)

        print("fn=status name=%s ns=%s status=%s" % (
            job.metadata.name,
            job.metadata.namespace,
            status))
        return status

    def parse_status(self, status):
        if not status.start_time:
            return "unstarted"
        if not status.completion_time:
            return "running"
        if status.succeeded:
            return "succeeded"
        return "failed"
