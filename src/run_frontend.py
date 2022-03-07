import tempfile
from time import sleep

import requests
from yaspin import yaspin

from src.deployment.flow import cmd, wait_for_lb

def apply_replace(f_in, replace_dict):
    with open(f_in, "r") as fin:
        with tempfile.NamedTemporaryFile(mode='w') as fout:
            for line in fin.readlines():
                for key, val in replace_dict.items():
                    line = line.replace('{' + key + '}', str(val))
                fout.write(line)
            fout.flush()
            cmd(f'kubectl apply -f {fout.name}')

def run(data, gateway_host, gateway_port, gateway_host_internal, gateway_port_internal):
    # deployment
    with yaspin(text="deploy frontend", color="green") as spinner:
        apply_replace(
            'src/deployment/k8s_frontend-deployment.yml',
            {
                'data': data,
                'gateway_host': gateway_host_internal,
                'gateway_port': gateway_port_internal
            }
        )

        if gateway_host == 'localhost':
            cmd(f'kubectl apply -f src/deployment/k8s_frontend-svc-node.yml')
            while True:
                try:
                    url = f'http://localhost:30080'
                    requests.get(url)
                    break
                except Exception as e:
                    sleep(1)
            frontend_host = 'http://localhost'
            frontend_port = '30080'
        else:
            cmd(f'kubectl apply -f src/deployment/k8s_frontend-svc-lb.yml')
            frontend_host = f'http://{wait_for_lb("frontend-lb")}'
            frontend_port = '80'

        spinner.ok('🚀')
        return frontend_host, frontend_port


if __name__ == '__main__':
    run('best-artworks', 'remote', None, 'gateway.visionapi.svc.cluster.local', '8080')
    # 31080
