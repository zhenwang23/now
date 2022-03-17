import os

from kubernetes import config


def get_system_state():
    try:
        contexts, active_context = config.list_kube_config_contexts()
    except Exception:
        contexts = None
        active_context = None

    is_debug = (
        os.environ['IS_DEBUG'].lower() == 'true' if 'IS_DEBUG' in os.environ else False
    )
    return contexts, active_context, is_debug
