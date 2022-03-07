import math
import subprocess
from time import sleep

from jina import Flow
from jina.clients import Client
from jina.clients.helper import pprint_routes
from tqdm import tqdm
from kubernetes import config, client as k8s_client
from yaspin import yaspin
from yaspin.spinners import Spinners


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def cmd(command, output=True, error=True, wait=True):
    if output:
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    else:
        with open("NUL", "w") as fh:
            if output:
                stdout = subprocess.PIPE
            else:
                stdout = fh
            if error:
                stderr = subprocess.PIPE
            else:
                stderr = fh
            process = subprocess.Popen(command.split(), stdout=stdout, stderr=stderr)
    if wait:
        output, error = process.communicate()
        return output, error


def wait_for_lb(lb_name):
    config.load_kube_config()
    v1 = k8s_client.CoreV1Api()
    while True:
        try:
            services = v1.list_namespaced_service(namespace='visionapi')
            ip = [s.status.load_balancer.ingress[0].ip for s in services.items if s.metadata.name == lb_name][0]
            if ip:
                break
        except:
            pass
        sleep(1)
    return ip


def deploy_flow(executor_name, index, infrastructure, vision_model, cluster_type, final_layer_output_dim, embedding_size):
    flow_kwargs = {}
    docker_prefix = '+docker'
    runtime_backend = 'process'

    if infrastructure == 'local':
        flow_kwargs['volumes'] = [f'data/tmp/cache:/root/.cache']

    f = Flow(
        name='visionapi',
        # protocol='http',
        port_expose=8080,
        runtime_backend=runtime_backend,
        install_requirements=True,
        cors=True,
    ).add(
        name='encoder_clip',
        uses=f'jinahub{docker_prefix}://CLIPEncoder/v0.2.0',
        uses_with={
            'pretrained_model_name_or_path': vision_model
        },
        **flow_kwargs
    ).add(
        name='linear_head',
        uses=f'jinahub{docker_prefix}://{executor_name}',
        uses_with={
            'final_layer_output_dim': final_layer_output_dim,
            'embedding_size': embedding_size
        },
    ).add(
        name='indexer',
        uses=f'jinahub{docker_prefix}://PQLiteIndexer/v0.2.3-rc',
        uses_with={
            'dim': embedding_size,
            'metric': 'cosine'
        },
        uses_metas={'workspace': 'pq_workspace'},
    )
    f.plot('/root/data/deployed_flow.png', vertical_layout=True)

    index = [x for x in index if x.text is '']
    if infrastructure == 'local':
        with f:
            print('start indexing', len(index))
            for x in batch(index, 64):
                f.index(x, on_done=pprint_routes)
            print('block flow')
            f.block()
        return 'localhost'
    else:
        with yaspin(text="convert flow to kubernetes yaml", color="green") as spinner:
            f.to_k8s_yaml('jina-now-k8s')
            spinner.ok('🔄')

        # create namespace
        cmd('kubectl create namespace visionapi', output=False, error=False)

        # deploy flow
        with yaspin(Spinners.earth, text="deploy jina flow (might take some time depending on the internet connection and selected quality)") as spinner:
            cmd('kubectl apply -R -f jina-now-k8s')
            gateway_host_internal = 'gateway.visionapi.svc.cluster.local'
            gateway_port_internal = 8080
            if cluster_type == 'local':
                cmd(f'kubectl apply -f src/deployment/k8s_backend-svc-node.yml')
                gateway_host = 'localhost'
                gateway_port = 31080
            else:
                cmd(f'kubectl apply -f src/deployment/k8s_backend-svc-lb.yml')
                gateway_host = wait_for_lb('gateway-lb')
                gateway_port = 8080

            # wait for flow to come up
            cmd('/bin/bash ./src/scripts/wait_for_flow.sh')
            spinner.ok("🚀")

        print(f'▶ start indexing {len(index)} documents soon:')
        while True:
            # print('try to send data via port forward...')
            try:
                client = Client(host=gateway_host, port=gateway_port)
                client.show_progress = True
                for x in tqdm(batch(index, 50), total=math.ceil(len(index)/50)):
                    response = client.post('/index', request_size=50, inputs=x)
                print('⭐  success - your data is indexed')
                break
            except Exception as e:
                sleep(2)
        return gateway_host, gateway_port, gateway_host_internal, gateway_port_internal


if __name__ == '__main__':
    import pickle

    with open('../../filename.pickle', 'rb') as handle:
        (executor_name, index, infrastructure, vision_model, final_layer_output_dim, embedding_size) = pickle.load(
            handle)
    deploy_flow(executor_name, index, 'local', vision_model, final_layer_output_dim, embedding_size)