from time import sleep

import requests
from src.deployment.deployment import apply_replace
from src.deployment.flow import cmd, wait_for_lb
from yaspin import yaspin


def run(
    data,
    gateway_host,
    gateway_port,
    gateway_host_internal,
    gateway_port_internal,
    docker_frontend_tag,
):
    # deployment
    with yaspin(text="Deploy frontend", color="green") as spinner:
        apply_replace(
            'src/deployment/k8s_frontend-deployment.yml',
            {
                'data': data,
                'gateway_host': gateway_host_internal,
                'gateway_port': gateway_port_internal,
                'docker_frontend_tag': docker_frontend_tag,
            },
        )

        if gateway_host == 'localhost':
            cmd('kubectl apply -f src/deployment/k8s_frontend-svc-node.yml')
            while True:
                try:
                    url = 'http://localhost:30080'
                    requests.get(url)
                    break
                except Exception:
                    sleep(1)
            frontend_host = 'http://localhost'
            frontend_port = '30080'
        else:
            cmd('kubectl apply -f src/deployment/k8s_frontend-svc-lb.yml')
            frontend_host = f'http://{wait_for_lb("frontend-lb", "nowapi")}'
            frontend_port = '80'

        spinner.ok('🚀')
        return frontend_host, frontend_port


if __name__ == '__main__':
    run(
        'best-artworks',
        'remote',
        None,
        'gateway.nowapi.svc.cluster.local',
        '8080',
        docker_frontend_tag='0.0.1',
    )
    # 31080
