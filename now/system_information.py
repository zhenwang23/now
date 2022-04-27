import os

from now.deployment.deployment import cmd


def get_system_state(kubectl_path='kubectl', **kwargs):
    # There is an issue with the python-client mentioned below. If the current
    # context is not set then the `list_kube_config_contexts() throws error
    # https://github.com/kubernetes-client/python/issues/1193
    # https://github.com/kubernetes-client/python/issues/518
    # try:
    #     contexts, active_context = config.list_kube_config_contexts()
    # except Exception as e:
    #     contexts = None
    #     active_context = None

    # TODO: Replace the below code with python-client when the above issue is resolved

    contexts, _ = cmd(f'{kubectl_path} config get-contexts --output=name')
    contexts = contexts.decode('utf-8').strip().split('\n')
    active_context, err = cmd(f'{kubectl_path} config current-context')
    if err:
        active_context = None
    else:
        active_context = active_context.decode('utf-8').strip()

    is_debug = (
        os.environ['IS_DEBUG'].lower() == 'true' if 'IS_DEBUG' in os.environ else False
    )
    return contexts, active_context, is_debug
