from kubernetes import client, config
import uuid
build_id = uuid.uuid1()

config_mount_dir = "/kaniko/.docker/"
bento_mount_dir = "/tmp/%s" % build_id
target_dir = "%s/build" % bento_mount_dir
yatai_image = "bentoml/yatai-service"


class KubernetesApiClient():
    def __init__(self, yatai_service):
        try:
            config.load_incluster_config()
        except Exception as ex:
            print(ex)
            config.load_kube_config()

        # self.service_account=
        self.configuration = client.Configuration()
        self.yatai_service = yatai_service

    def create_builder_pod(self, job_name, container_image,
                           ns, bentoservice):

        print("at=starting-job-creation job=%s" % job_name)
        bento_env = client.V1EnvVar(
            name='BENTOML__YATAI_SERVICE__URL',
            value=self.yatai_service)

        volume = client.V1Volume(
            name=f"bento-storage",
            empty_dir=client.V1EmptyDirVolumeSource())

        volume_mount = client.V1VolumeMount(
            name=f"bento-storage",
            mount_path=bento_mount_dir)

        docker_config = client.V1Volume(
            name="docker-config",
            config_map=client.V1ConfigMapVolumeSource(name="docker-config"))

        docker_config_mount = client.V1VolumeMount(
            name=f"docker-config",
            mount_path=config_mount_dir)

        # use bentoml retrieve to obtain the correct build context
        bento_args = [
            "bentoml",
            "retrieve",
            bentoservice,
            "--target_dir=%s" % target_dir,
            "--debug"]

        # tl;dr build context into image and push without docker daemon
        # (for headless use in CI pipelines, etc)
        bento_container = client.V1Container(
            name="%s-bento" % job_name,
            image=yatai_image,
            args=bento_args,
            env=[bento_env],
            image_pull_policy="Always",
            volume_mounts=[volume_mount],
        )

        bento_ls_container = client.V1Container(
            name="%s-ls-dir" % job_name,
            image="busybox:latest",
            args=["ls", "-la", target_dir],
            image_pull_policy="Always",
            volume_mounts=[volume_mount]
        )

        kaniko_args = [
            "--dockerfile=%s/Dockerfile" % target_dir,
            "--context=dir://%s" % target_dir,
            "--destination=%s" % container_image,
            "--verbosity=debug",
            "--digest-file=%s/digest.txt" % target_dir,
            "--single-snapshot"
        ]

        ls_container = client.V1Container(
            name="%s-dockerconfigls" % job_name,
            image="busybox:latest",
            args=["cat", "%s/config.json" % config_mount_dir],
            image_pull_policy="Always",
            volume_mounts=[volume_mount, docker_config_mount],
        )

        kaniko_container = client.V1Container(
            name="%s-kaniko" % job_name,
            image="gcr.io/kaniko-project/executor:latest",
            args=kaniko_args,
            image_pull_policy="Always",
            volume_mounts=[volume_mount, docker_config_mount],
            env=[
                client.V1EnvVar(
                    name="DOCKER_CONFIG",
                    value="/kaniko/.docker/")]
        )

        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": "bentobuild"}),
            spec=client.V1PodSpec(restart_policy="Never",
                                  init_containers=[
                                      bento_container,
                                  ],
                                  containers=[
                                      bento_ls_container,
                                      ls_container,
                                      kaniko_container,
                                  ],
                                  volumes=[volume, docker_config]),
        )

        spec = client.V1JobSpec(
            template=template,
            backoff_limit=3,
            ttl_seconds_after_finished=60)

        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(name=job_name, namespace=ns),
            spec=spec)

        print("at=initialized-job job=%s ns=%s" %
              (job.metadata.name, job.metadata.namespace))

        return job
