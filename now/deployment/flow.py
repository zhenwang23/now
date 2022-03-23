import math
import os.path
import pathlib
from time import sleep

from jina import Flow
from jina.clients import Client
from jina.clients.helper import pprint_routes
from kubernetes import client
from kubernetes import client as k8s_client
from kubernetes import config
from tqdm import tqdm
from yaspin import yaspin
from yaspin.spinners import Spinners

from now.deployment.deployment import apply_replace, cmd

cur_dir = pathlib.Path(__file__).parent.resolve()


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx : min(ndx + n, l)]


def wait_for_lb(lb_name, ns):
    config.load_kube_config()
    v1 = k8s_client.CoreV1Api()
    while True:
        try:
            services = v1.list_namespaced_service(namespace=ns)
            ip = [
                s.status.load_balancer.ingress[0].ip
                for s in services.items
                if s.metadata.name == lb_name
            ][0]
            if ip:
                break
        except Exception:
            pass
        sleep(1)
    return ip


def wait_for_all_pods_in_ns(ns, num_pods, max_wait=1800):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    for i in range(max_wait):
        pods = v1.list_namespaced_pod(ns).items
        not_ready = [
            'x'
            for pod in pods
            if not pod.status
            or not pod.status.container_statuses
            or not len(pod.status.container_statuses) == 1
            or not pod.status.container_statuses[0].ready
        ]
        if len(not_ready) == 0 and num_pods == len(pods):
            return
        sleep(1)


def deploy_k8s(
    f, ns, infrastructure, cluster_type, num_pods, tmpdir, kubectl_path, **kwargs
):
    if infrastructure == 'local':
        with f:
            print('start indexing', len(index))
            for x in batch(index, 64):
                f.index(x, on_done=pprint_routes)
            print('block flow')
            f.block()
        return 'localhost'
    else:
        k8_path = os.path.join(tmpdir, f'k8s/{ns}')
        with yaspin(text="Convert Flow to Kubernetes YAML", color="green") as spinner:
            f.to_k8s_yaml(k8_path)
            spinner.ok('🔄')

        # create namespace
        cmd(f'{kubectl_path} create namespace {ns}', output=False)

        # deploy flow
        with yaspin(
            Spinners.earth,
            text="Deploy Jina Flow (might take some time depending on internet connection and selected quality)",
        ) as spinner:
            cmd(f'{kubectl_path} apply -R -f {k8_path}')
            gateway_host_internal = f'gateway.{ns}.svc.cluster.local'
            gateway_port_internal = 8080
            if cluster_type == 'local':
                apply_replace(
                    f'{cur_dir}/k8s_backend-svc-node.yml', {'ns': ns}, kubectl_path
                )
                gateway_host = 'localhost'
                gateway_port = 31080
            else:
                apply_replace(
                    f'{cur_dir}/k8s_backend-svc-lb.yml', {'ns': ns}, kubectl_path
                )
                gateway_host = wait_for_lb('gateway-lb', ns)
                gateway_port = 8080

            # wait for flow to come up
            wait_for_all_pods_in_ns(ns, num_pods)
            spinner.ok("🚀")
        return gateway_host, gateway_port, gateway_host_internal, gateway_port_internal


def deploy_flow(
    executor_name,
    index,
    infrastructure,
    vision_model,
    cluster_type,
    final_layer_output_dim,
    embedding_size,
    tmpdir,
    **kwargs,
):
    flow_kwargs = {}
    docker_prefix = '+docker'
    runtime_backend = 'process'

    if infrastructure == 'local':
        flow_kwargs['volumes'] = ['data/tmp/cache:/root/.cache']
    ns = 'nowapi'
    f = (
        Flow(
            name=ns,
            port_expose=8080,
            cors=True,
        )
        .add(
            name='encoder_clip',
            uses=f'jinahub{docker_prefix}://CLIPEncoder/v0.2.1',
            uses_with={'pretrained_model_name_or_path': vision_model},
            env={'JINA_LOG_LEVEL': 'DEBUG'},
            **flow_kwargs,
        )
        .add(
            name='linear_head',
            uses=f'jinahub{docker_prefix}://{executor_name}',
            uses_with={
                'final_layer_output_dim': final_layer_output_dim,
                'embedding_size': embedding_size,
            },
            env={'JINA_LOG_LEVEL': 'DEBUG'},
        )
        .add(
            name='indexer',
            uses=f'jinahub{docker_prefix}://PQLiteIndexer/v0.2.3-rc',
            uses_with={'dim': embedding_size, 'metric': 'cosine'},
            uses_metas={'workspace': 'pq_workspace'},
            env={'JINA_LOG_LEVEL': 'DEBUG'},
        )
    )
    # f.plot('./flow.png', vertical_layout=True)

    index = [x for x in index if x.text == '']

    (
        gateway_host,
        gateway_port,
        gateway_host_internal,
        gateway_port_internal,
    ) = deploy_k8s(f, ns, infrastructure, cluster_type, 7, tmpdir, **kwargs)
    print(f'▶ indexing {len(index)} documents')

    client = Client(host=gateway_host, port=gateway_port)
    for x in tqdm(batch(index, 50), total=math.ceil(len(index) / 50)):
        # first request takes soooo long
        client.post('/index', request_size=50, inputs=x)

    print('⭐ Success - your data is indexed')
    return gateway_host, gateway_port, gateway_host_internal, gateway_port_internal


if __name__ == '__main__':
    import pickle

    with open('../../filename.pickle', 'rb') as handle:
        (
            executor_name,
            index,
            infrastructure,
            vision_model,
            final_layer_output_dim,
            embedding_size,
        ) = pickle.load(handle)
    deploy_flow(
        executor_name,
        index,
        'local',
        vision_model,
        final_layer_output_dim,
        embedding_size,
    )
