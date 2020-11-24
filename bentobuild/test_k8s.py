import unittest
from k8s import KubernetesApiClient


class TestKubernetesApiClient(unittest.TestCase):

    def test_create_builder_job(self):
        job_name = "test-foo"
        job_ns = "fake"
        job_img = "img-123"

        c = KubernetesApiClient("http://yatai-service.local", test=True)
        job = c.create_builder_job(job_name, job_img, job_ns, "something:1234")

        self.assertEqual(job.metadata.name, job_name)
        self.assertEqual(job.metadata.namespace, job_ns)
        self.assertEqual(
            job.spec.template.spec.init_containers[0].image,
            "bentoml/yatai-service")


if __name__ == '__main__':
    unittest.main()
