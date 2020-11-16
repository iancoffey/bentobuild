# bentobuild

A helper which provides a simple api to launching pods to create docker images from BentoML Services in a Kubernetes clister, by making use of BentoMLs [YataiService](https://docs.bentoml.org/en/latest/concepts.html#customizing-model-repository).

This does not use the `bentoml containerize` command because it requires Docker daemon and our build containers wont be running a docker daemon. Instead, this package creates a custom Kubernetes Job, which uses` bentoml retrieve` alongside [`Kaniko executor`](https://github.com/GoogleContainerTools/kaniko) to build the BentoML context and artifacts into a docker image and push it to your desired docker image and tag.

The resulting image can be served via KFServing inferenceservice or via the bundled serving experiment.

The builder can either schedule a standard Kubernetes Job (the default), or try the experimental support for Tekton Tasks.

## YataiService Required

This project really only makes sense when using BentoML with a [`YataiService`](https://docs.bentoml.org/en/latest/concepts.html#customizing-model-repository), as multiple pods will need to access the model storage backend.

I would suggest running the `YataiService` so it is only open to local cluster traffic, and refer to it via its `cluster.local` domain name.

## Example

In the example below, the builder will create a new temporary build namespace, populate it with the correct build resources and the clean up the ns and everything in it. If you set `cleanup=False`, the namespace will be preserved for inspection.

```
import bentobuild

builder = bentobuild.Builder()

builder.safe_build('FastaiDemo:20201105133154_04F821', 'iancoffey/mydemo:latest', 'test1')

# resources begin running

builder.status() # prints some output from the Job status

```

## Docker Credentials

It is important to establish Docker credentials for the builder to use to push to your desired repo.

To do this, the project supports mounting a configmap containting a Docker `config.json` into the build environment.

See the [Kaniko documentation](https://github.com/GoogleContainerTools/kaniko/blob/master/README.md#pushing-to-different-registries) for more info on how to format and create this secret.

# move to README -> The Tekton catalog bentoml and kaniko tasks must be installed prior to using
# the Tekton task builder
# kubectl apply -f https://github.com/tektoncd/catalog/blob/master/task/bentoml/0.1/bentoml.yaml
# kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/master/task/kaniko/0.1/kaniko.yaml

