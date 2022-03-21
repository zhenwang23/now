from typing import Optional

import cowsay
from kubernetes import client, config
from yaspin import yaspin

from now.deployment.flow import cmd
from now.dialog import prompt_plus
from now.gke_deploy import create_gke_cluster


def create_local_cluster():
    out, error = cmd('kind get clusters')
    if error != b'' and 'failed to list clusters' in error:
        print(error.decode('utf-8'))
        exit(0)
    if out == b'jina-now\n':
        questions = [
            {
                'type': 'list',
                'name': 'proceed',
                'message': 'The local cluster is running already. '
                'Should it be recreated?',
                'choices': [
                    {'name': '⛔ no - stop', 'value': False},
                    {'name': '✅ yes - recreate', 'value': True},
                ],
            },
        ]
        recreate = prompt_plus(questions, 'proceed')
        if recreate:
            with yaspin(text="Remove local cluster", color="green") as spinner:
                cmd('/usr/local/bin/kind delete clusters jina-now', output=False)
                spinner.ok('💀')
        else:
            cowsay.cow('see you soon 👋')
            exit(0)
    with yaspin(text="Setup local cluster", color="green") as spinner:
        cmd(
            '/usr/local/bin/kind create cluster --name jina-now --config src/kind.yml',
            output=False,
        )
        spinner.ok("📦")


def setup_cluster(cluster_name: Optional[str], provider: str):
    if cluster_name is not None:
        cmd(f'kubectl config use-context {cluster_name}')
        ask_existing()
    else:
        if provider == 'local':
            create_local_cluster()
        elif provider == 'gke':
            create_gke_cluster()


def ask_existing():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    if 'nowapi' in [item.metadata.name for item in v1.list_namespace().items]:
        questions = [
            {
                'type': 'list',
                'name': 'proceed',
                'message': (
                    'jina-now is deployed already. Do you want to remove the '
                    'current data?'
                ),
                'choices': [
                    {'name': '⛔ no - stop', 'value': False},
                    {'name': '✅ yes - remove', 'value': True},
                ],
            },
        ]
        remove = prompt_plus(questions, 'proceed')
        if remove:
            with yaspin(text="Remove old deployment", color="green") as spinner:
                cmd('kubectl delete ns nowapi', output=False, error=False)
                spinner.ok('💀')
        else:
            cowsay.cow('see you soon 👋')
            exit(0)
