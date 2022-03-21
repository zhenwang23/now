import tempfile

import cowsay

from now import run_backend, run_frontend
from now.cloud_manager import setup_cluster
from now.dialog import get_user_input
from now.system_information import get_system_state


def run_k8s(os_type='linux', arch='x86_64', **kwargs):
    with tempfile.TemporaryDirectory() as tmpdir:
        docker_frontend_tag = '0.0.1'
        contexts, active_context, is_debug = get_system_state()
        user_input = get_user_input(contexts, active_context, os_type, arch, **kwargs)
        setup_cluster(user_input.cluster, user_input.new_cluster_type)
        (
            gateway_host,
            gateway_port,
            gateway_host_internal,
            gateway_port_internal,
        ) = run_backend.run(user_input, is_debug, tmpdir)
        frontend_host, frontend_port = run_frontend.run(
            user_input.dataset,
            gateway_host,
            gateway_port,
            gateway_host_internal,
            gateway_port_internal,
            docker_frontend_tag,
        )
        url = f'{frontend_host}' + (
            '' if str(frontend_port) == '80' else f':{frontend_port}'
        )
        print()

        # print(f'✅ Your search case running.\nhost: {node_ip}:30080')
        # print(f'host: {node_ip}:30080')
        cowsay.cow(f'You made it:\n{url}')


if __name__ == '__main__':
    run_k8s()
