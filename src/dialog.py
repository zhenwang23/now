from __future__ import print_function, unicode_literals

import os
from dataclasses import dataclass
from typing import Optional

import cowsay
from pyfiglet import Figlet
from PyInquirer import Separator
from PyInquirer.prompt import prompt
from src.deployment.deployment import cmd
from src.system_information import get_system_state

NEW_CLUSTER = '🐣 create new'
AVAILABLE_SOON = 'will be available in upcoming versions'
QUALITY_MAP = {
    'medium': ('ViT-B32', 'openai/clip-vit-base-patch32'),
    'good': ('ViT-B16', 'openai/clip-vit-base-patch16'),
    'excellent': ('ViT-L14', 'openai/clip-vit-large-patch14'),
}


@dataclass
class UserInput:
    # data related
    dataset: Optional[str] = 'deepfashion'
    is_custom_dataset: Optional[bool] = False
    custom_dataset_type: Optional[str] = None
    dataset_secret: Optional[str] = None
    dataset_url: Optional[str] = None
    dataset_path: Optional[str] = None
    # model related
    model_quality: str = 'medium'
    model_variant: str = 'ViT-B32'
    # cluster related
    cluster: Optional[str] = None
    create_new_cluster: bool = False
    new_cluster_type: str = 'local'


def headline():
    f = Figlet(font='slant')
    print('Welcome to:')
    print(f.renderText('Jina NOW'))
    print('Get your search case up and running - end to end.')
    print(
        'We take your images and texts, train a model, push it to the jina hub, '
        'deploy a flow and a frontend in the cloud or locally.'
    )
    print(
        'If you want learn more about our framework please visit: https://docs.jina.ai/'
    )
    print(
        '💡 Make sure you assign give enough memory to your Docker daemon. '
        '5GB - 8GB should be okay.'
    )
    print()


def get_user_input(contexts, active_context, os_type, arch, **kwargs) -> UserInput:
    headline()
    user_input = UserInput()
    ask_data(user_input, **kwargs)
    ask_quality(user_input, **kwargs)
    ask_deployment(user_input, contexts, active_context, os_type, arch)
    return user_input


def prompt_plus(questions, attribute):
    answer = prompt(questions)
    if attribute in answer:
        return answer[attribute]
    else:
        os.system('clear')
        cowsay.cow('see you soon 👋')
        exit(0)


def ask_data(user_input: UserInput, **kwargs):
    questions = [
        {
            'type': 'list',
            'name': 'dataset',
            'message': 'What dataset do you want to use?',
            'choices': [
                {'name': '🖼 artworks (≈8K docs)', 'value': 'best-artworks'},
                {
                    'name': '💰 nft - bored apes (10K docs)',
                    'value': 'nft-monkey',
                },
                {'name': '🦆 birds (≈12K docs)', 'value': 'bird-species'},
                {'name': '🚗 cars (≈16K docs)', 'value': 'stanford-cars'},
                {
                    'name': '🏞 geolocation (≈50K docs)',
                    'value': 'geolocation-geoguessr',
                },
                {'name': '👕 fashion (≈53K docs)', 'value': 'deepfashion'},
                {
                    'name': '☢️ chest x-ray (≈100K docs)',
                    'value': 'nih-chest-xrays',
                },
                Separator(),
                {
                    'name': '✨ custom',
                    'value': 'custom',
                },
            ],
        },
    ]
    if kwargs['dataset_type']:
        user_input.dataset = 'custom'
    elif kwargs['dataset']:
        user_input.dataset = kwargs['dataset']
    else:
        user_input.dataset = prompt_plus(questions, 'dataset')

    if user_input.dataset == 'custom':
        user_input.is_custom_dataset = True
        ask_data_custom(user_input, **kwargs)
    else:
        user_input.is_custom_dataset = False


def ask_data_custom(user_input: UserInput, **kwargs):
    questions = [
        {
            'type': 'list',
            'name': 'custom_dataset_type',
            'message': (
                'How do you want to provide input? (format: https://docarray.jina.ai/)'
            ),
            'choices': [
                {
                    'name': 'docarray.pull(...) (recommended)',
                    'value': 'docarray',
                },
                {
                    'name': 'docarray URL',
                    'value': 'url',
                },
                {
                    'name': 'local mounted path',
                    'value': 'path',
                    'disabled': AVAILABLE_SOON,
                },
            ],
        },
    ]
    if kwargs['dataset_type']:
        custom_dataset_type = prompt_plus(questions, 'custom_dataset_type')
        user_input.custom_dataset_type = custom_dataset_type
    else:
        custom_dataset_type = kwargs['dataset_type']

    if custom_dataset_type == 'docarray' and not kwargs['secret']:
        questions = [
            {
                'type': 'password',
                'name': 'secret',
                'message': 'Please enter your docarray secret',
            },
        ]
        user_input.dataset_secret = prompt_plus(questions, 'secret')
    elif custom_dataset_type == 'url' and not kwargs['url']:
        questions = [
            {
                'type': 'input',
                'name': 'url',
                'message': 'Please paste in your URL for the docarray:',
            },
        ]
        user_input.dataset_url = prompt_plus(questions, 'url')
    else:
        pass


def ask_quality(user_input: UserInput, **kwargs):
    questions = [
        {
            'type': 'list',
            'name': 'quality',
            'message': 'What quality do you expect?',
            'choices': [
                {'name': '🦊 medium (≈3GB mem, 15q/s)', 'value': 'medium'},
                {'name': '🐻 good (≈3GB mem, 2.5q/s)', 'value': 'good'},
                {
                    'name': '🦄 excellent (≈4GB mem, 0.5q/s)',
                    'value': 'excellent',
                },
            ],
            'filter': lambda val: val.lower(),
        }
    ]
    if kwargs['quality']:
        quality = kwargs['quality']
    else:
        quality = prompt_plus(questions, 'quality')
        if quality == 'medium':
            print('  🚀 you trade-off a bit of quality for having the best speed')
        elif quality == 'good':
            print('  ⚖️ you have the best out of speed and quality')
        elif quality == 'excellent':
            print('  ✨ you trade-off speed to having the best quality')

    user_input.model_quality, user_input.model_variant = QUALITY_MAP[quality]


def ask_deployment(user_input: UserInput, contexts, active_context, os_type, arch):
    choices = ([c['name'] for c in contexts] if contexts is not None else []) + [
        NEW_CLUSTER
    ]
    if active_context is not None:
        choices.remove(active_context['name'])
        choices = [active_context['name']] + choices

    choices = [c for c in choices if 'minikube' not in c]

    questions = [
        {
            'type': 'list',
            'name': 'cluster',
            'message': 'Where do you want to deploy your search engine?',
            'choices': choices,
            'filter': lambda val: val.lower(),
        }
    ]
    cluster = prompt_plus(questions, 'cluster')
    user_input.cluster = cluster

    if cluster == NEW_CLUSTER:
        user_input.cluster = None
        user_input.create_new_cluster = True
        questions = [
            {
                'type': 'list',
                'name': 'cluster_new',
                'message': 'Where do you want to create a new cluster?',
                'choices': [
                    {
                        'name': '📍 local (Kubernetes in Docker)',
                        'value': 'local',
                    },
                    {'name': '⛅️ Google Kubernetes Engine', 'value': 'gke'},
                    {
                        'name': '⛅️ Amazon Elastic Kubernetes Service',
                        'disabled': AVAILABLE_SOON,
                    },
                    {
                        'name': '⛅️ Azure Kubernetes Service',
                        'disabled': AVAILABLE_SOON,
                    },
                    {
                        'name': '⛅️ DigitalOcean Kubernetes',
                        'disabled': AVAILABLE_SOON,
                    },
                ],
                'filter': lambda val: val.lower(),
            }
        ]
        user_input.new_cluster_type = prompt_plus(questions, 'cluster_new')
        if user_input.new_cluster_type == 'gke':
            output, _ = cmd('which gcloud')
            if output is not None:
                cmd(
                    f'/bin/bash ./src/scripts/install_gcloud.sh {os_type} {arch}',
                    output=False,
                    error=False,
                )


if __name__ == '__main__':
    print(get_user_input(*get_system_state()))
