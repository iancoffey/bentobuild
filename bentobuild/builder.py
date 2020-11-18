import os

from kubernetes.client.rest import ApiException

default_name = "model-build"
## BUILDER SETS METADATA ON BEN@TO OBJECT! for the sha of the image associated with it!

class GenericBuilder():
    def __init__(self, yatai_service=None):
        self.yatai_service = None
        if yatai_service:
            self.yatai_service = yatai_service

        env_yatai_service = os.environ.get('BENTOML__YATAI_SERVICE__URL')
        if env_yatai_service and not self.yatai_service:
            self.yatai_service = env_yatai_service

        if not self.yatai_service:
            print("at=yatai-service-undefined")

    def check_ns_exists(self, ns):
        try:
            _ = self.corev1.read_namespace(ns)
            print("at=verify-namespace-success ns=%s" % ns)
            return True
        except ApiException as e:
            print("at=error-ns-doesnt-exist fn=check_ns_exists ns=%q err=%q" %
                  ns, e)
            return False

    def safe_build(self, service, image, ns, name=default_name):
        pass

    # unstarted, running, succeeded, failed
    def status(self, job):
        pass
