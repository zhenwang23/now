from __future__ import annotations, print_function, unicode_literals

import abc
import os
import pathlib
from dataclasses import dataclass
from os.path import expanduser as user
from typing import Dict, Generic, List, Literal, Optional, TypeVar, Union

import cowsay
from kubernetes import client, config
from pyfiglet import Figlet
from yaspin import yaspin

from now.deployment.deployment import cmd
from now.thridparty.PyInquirer import Separator
from now.thridparty.PyInquirer.prompt import prompt
from now.utils import sigmap

cur_dir = pathlib.Path(__file__).parent.resolve()
NEW_CLUSTER = '🐣 create new'
AVAILABLE_SOON = 'will be available in upcoming versions'
QUALITY_MAP = {
    'medium': ('ViT-B32', 'openai/clip-vit-base-patch32'),
    'good': ('ViT-B16', 'openai/clip-vit-base-patch16'),
    'excellent': ('ViT-L14', 'openai/clip-vit-large-patch14'),
}
AVAILABLE_DATASET = [
    'best-artworks',
    'nft-monkey',
    'tll',
    'bird-species',
    'stanford-cars',
    'deep-fashion',
    'nih-chest-xrays',
    'geolocation-geoguessr',
    'music-genres',
]


@dataclass
class UserInput:
    modality: Literal['audio', 'image'] = 'image'

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

    is_complete: bool = False


def print_headline():
    f = Figlet(font='slant')
    print('Welcome to:')
    print(f.renderText('Jina NOW'))
    print('Get your search case up and running - end to end.\n')
    print(
        'You can choose between image and audio search. \nJina now trains a model, pushes it to the jina hub'
        ', deploys a flow and a frontend app in the cloud or locally. \nCheckout one of the demo cases or bring '
        'your own data.\n'
    )
    print(
        'If you want learn more about our framework please visit: https://docs.jina.ai/'
    )
    print(
        '💡 Make sure you give enough memory to your Docker daemon. '
        '5GB - 8GB should be okay.'
    )
    print()


T = TypeVar('T')


class BaseConfigurationStep(Generic[T]):
    def __init__(
        self,
        name: str,
        cli_value: Optional[T] = None,
        choices: Optional[List[Union[Dict, str]]] = None,
        prompt_message: str = None,
        prompt_type: str = 'input',
    ):
        self._name = name
        self._cli_value = cli_value
        self._choices = choices
        self._prompt_message = (
            prompt_message if prompt_message is not None else 'Please provide input.'
        )
        self._prompt_type = prompt_type

    def get_value(self) -> T:
        if self._cli_value is not None:
            return self._cli_value
        else:
            answer = prompt(self._get_questions())
            if self._name in answer:
                return answer[self._name]
            else:
                print("\n" * 10)
                cowsay.cow('see you soon 👋')
                exit(0)

    @abc.abstractmethod
    def configure_user_input(self, user_input: UserInput) -> BaseConfigurationStep:
        raise NotImplementedError('set_user_input')

    def _get_questions(self) -> Dict:
        qs = {
            'name': self._name,
            'type': self._prompt_type,
            'message': self._prompt_message,
        }
        if self._choices is not None:
            qs['choices'] = self._choices
        return qs


class FinalConfigurationStep(BaseConfigurationStep['str']):
    def __init__(self, **kwargs):
        super().__init__(name='final')

    def configure_user_input(self, user_input: UserInput) -> BaseConfigurationStep:
        user_input.is_complete = True
        return self


class ConfigureDataImage(BaseConfigurationStep['str']):
    def __init__(self, **kwargs):
        super().__init__(
            name='dataset_image',
            cli_value=kwargs.get('data'),
            choices=[
                {'name': '🖼  artworks (≈8K docs)', 'value': 'best-artworks'},
                {
                    'name': '💰 nft - bored apes (10K docs)',
                    'value': 'nft-monkey',
                },
                {'name': '👬 totally looks like (≈12K docs)', 'value': 'tll'},
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
            prompt_message='What dataset do you want to use?',
            prompt_type='list',
        )
        self._kwargs = kwargs

    def configure_user_input(self, user_input: UserInput) -> BaseConfigurationStep:
        data = self.get_value()
        if data in AVAILABLE_DATASET:
            user_input.is_custom_dataset = False
            user_input.dataset = data
            return ConfigureQuality(**self._kwargs)
        else:
            user_input.is_custom_dataset = True
            if data == 'custom':
                return ConfigureCustomDatasetType(**self._kwargs)
            else:
                _parse_custom_data_from_cli(data, user_input)
                return ConfigureQuality(**self._kwargs)


class ConfigureDataAudio(BaseConfigurationStep['str']):
    def __init__(self, **kwargs):
        super().__init__(
            name='dataset_audio',
            cli_value=kwargs.get('data'),
            choices=[
                {'name': '🎸 music (≈10K docs)', 'value': 'music-genres'},
                Separator(),
                {
                    'name': '✨ custom',
                    'value': 'custom',
                },
            ],
            prompt_message='What dataset do you want to use?',
            prompt_type='list',
        )
        self._kwargs = kwargs

    def configure_user_input(self, user_input: UserInput) -> BaseConfigurationStep:
        data = self.get_value()
        if data in AVAILABLE_DATASET:
            user_input.is_custom_dataset = False
            user_input.dataset = data
            return ConfigureCluster(**self._kwargs)
        else:
            user_input.is_custom_dataset = True
            if data == 'custom':
                return ConfigureCustomDatasetType(**self._kwargs)
            else:
                _parse_custom_data_from_cli(data, user_input)
                return ConfigureQuality(**self._kwargs)


class ConfigureCustomDatasetType(BaseConfigurationStep['str']):
    class ConfigureDocarrayDataset(BaseConfigurationStep['str']):
        def __init__(self, **kwargs):
            super().__init__(
                name='docarray-dataset',
                prompt_message='Please enter your docarray secret.',
                prompt_type='password',
            )
            self._kwargs = kwargs

        def configure_user_input(self, user_input: UserInput) -> BaseConfigurationStep:
            secret = self.get_value()
            user_input.dataset_secret = secret
            return ConfigureQuality(**self._kwargs)

    class ConfigureUrlDataset(BaseConfigurationStep['str']):
        def __init__(self, **kwargs):
            super().__init__(
                name='url',
                prompt_message='Please paste in your url for the docarray.',
                prompt_type='input',
            )
            self._kwargs = kwargs

        def configure_user_input(self, user_input: UserInput) -> BaseConfigurationStep:
            dataset_url = self.get_value()
            user_input.dataset_url = dataset_url
            return ConfigureQuality(**self._kwargs)

    class ConfigurePathDataset(BaseConfigurationStep['str']):
        def __init__(self, **kwargs):
            super().__init__(
                name='local_path',
                prompt_message='Please enter the path to the local folder.',
                prompt_type='input',
            )
            self._kwargs = kwargs

        def configure_user_input(self, user_input: UserInput) -> BaseConfigurationStep:
            dataset_path = self.get_value()
            user_input.dataset_path = dataset_path
            return ConfigureQuality(**self._kwargs)

    def __init__(self, **kwargs):
        super().__init__(
            name='custom-data',
            choices=[
                {
                    'name': 'docarray.pull id (recommended)',
                    'value': 'docarray',
                },
                {
                    'name': 'docarray URL',
                    'value': 'url',
                },
                {
                    'name': 'local mounted path',
                    'value': 'path',
                },
            ],
            prompt_message='How do you want to provide input? (format: https://docarray.jina.ai/)',
            prompt_type='list',
        )
        self._kwargs = kwargs

    def configure_user_input(self, user_input: UserInput) -> BaseConfigurationStep:
        custom_dataset_type = self.get_value()
        user_input.custom_dataset_type = custom_dataset_type
        if custom_dataset_type == 'docarray':
            return self.ConfigureDocarrayDataset(**self._kwargs).configure_user_input(
                user_input
            )
        if custom_dataset_type == 'url':
            return self.ConfigureUrlDataset(**self._kwargs).configure_user_input(
                user_input
            )
        if custom_dataset_type == 'path':
            return self.ConfigurePathDataset(**self._kwargs).configure_user_input(
                user_input
            )


class ConfigureModality(BaseConfigurationStep['str']):
    def __init__(self, **kwargs):
        super().__init__(
            name='modality',
            cli_value=kwargs.get('modality'),
            choices=[
                {'name': '🏞 Image Search', 'value': 'image'},
                {'name': '🔊 Audio Search', 'value': 'audio'},
            ],
            prompt_message='Which modalities you want to work with?',
            prompt_type='list',
        )
        self._kwargs = kwargs

    def configure_user_input(self, user_input: UserInput) -> BaseConfigurationStep:
        modality = self.get_value()
        user_input.modality = modality
        if modality == 'image':
            return ConfigureDataImage(**self._kwargs)
        else:
            return ConfigureDataAudio(**self._kwargs)


class ConfigureCluster(BaseConfigurationStep['str']):
    class ConfigureNewCluster(BaseConfigurationStep['str']):
        def __init__(self, **kwargs):
            super().__init__(
                name='cluster_new',
                choices=[
                    {
                        'name': '📍 local (Kubernetes in Docker)',
                        'value': 'local',
                    },
                    {'name': '⛅️ Google Kubernetes Engine', 'value': 'gke'},
                    {
                        'name': '⛅️ Jina - Flow as a Service',
                        'disabled': AVAILABLE_SOON,
                    },
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
                prompt_message='Where do you want to create a new cluster?',
                prompt_type='list',
            )
            self._kwargs = kwargs

        def configure_user_input(self, user_input: UserInput) -> BaseConfigurationStep:
            cluster_new = self.get_value()
            user_input.create_new_cluster = True
            user_input.new_cluster_type = cluster_new
            if user_input.new_cluster_type == 'gke':
                _maybe_install_gke(**self._kwargs)
            return FinalConfigurationStep(**self._kwargs)

    def __init__(self, **kwargs):
        self.contexts, self.active_context = kwargs.get('contexts'), kwargs.get(
            'active_context'
        )
        super().__init__(
            name='cluster',
            cli_value=kwargs.get('cluster'),
            choices=(get_context_names(self.contexts, self.active_context))
            + [NEW_CLUSTER],
            prompt_message='Where do you want to deploy your search engine?',
            prompt_type='list',
        )
        self._kwargs = kwargs

    def configure_user_input(self, user_input: UserInput) -> BaseConfigurationStep:
        cluster = self.get_value()

        if cluster == NEW_CLUSTER:
            return self.ConfigureNewCluster(**self._kwargs).configure_user_input(
                user_input
            )
        else:
            user_input.cluster = cluster
            if not cluster_running(cluster):
                print(
                    f'Cluster {cluster} is not running. Please select a different one.'
                )
                return ConfigureCluster(**self._kwargs)
            else:
                return FinalConfigurationStep(**self._kwargs)


class ConfigureQuality(BaseConfigurationStep['str']):
    def __init__(self, **kwargs):
        super().__init__(
            name='quality',
            cli_value=kwargs.get('quality'),
            choices=[
                {'name': '🦊 medium (≈3GB mem, 15q/s)', 'value': 'medium'},
                {'name': '🐻 good (≈3GB mem, 2.5q/s)', 'value': 'good'},
                {
                    'name': '🦄 excellent (≈4GB mem, 0.5q/s)',
                    'value': 'excellent',
                },
            ],
            prompt_message='What quality do you expect?',
            prompt_type='list',
        )
        self._kwargs = kwargs

    def configure_user_input(self, user_input: UserInput) -> BaseConfigurationStep:
        quality = self.get_value()
        if quality == 'medium':
            print('  🚀 you trade-off a bit of quality for having the best speed')
        elif quality == 'good':
            print('  ⚖️ you have the best out of speed and quality')
        elif quality == 'excellent':
            print('  ✨ you trade-off speed to having the best quality')

        user_input.model_quality, user_input.model_variant = QUALITY_MAP[quality]
        return ConfigureCluster(**self._kwargs)


def configure_user_input(**kwargs) -> UserInput:
    print_headline()
    user_input = UserInput()
    config_step = ConfigureModality(**kwargs)
    while not user_input.is_complete:
        config_step = config_step.configure_user_input(user_input)
    return user_input


def prompt_plus(questions, attribute, **kwargs):
    if kwargs and attribute in kwargs.keys() and kwargs[attribute]:
        return kwargs[attribute]
    else:
        answer = prompt(questions)
        if attribute in answer:
            return answer[attribute]
        else:
            print("\n" * 10)
            cowsay.cow('see you soon 👋')
            exit(0)


def get_context_names(contexts, active_context=None):
    names = [c for c in contexts] if contexts is not None else []
    if active_context is not None:
        names.remove(active_context)
        names = [active_context] + names
    return names


def cluster_running(cluster):
    config.load_kube_config(context=cluster)
    v1 = client.CoreV1Api()
    try:
        v1.list_namespace()
    except Exception as e:
        return False
    return True


def _maybe_install_gke(os_type: str, arch: str):
    out, _ = cmd('which gcloud')
    if not out:
        if not os.path.exists(user('~/.cache/jina-now/google-cloud-sdk')):
            with yaspin(
                sigmap=sigmap, text='Setting up gcloud', color='green'
            ) as spinner:
                cmd(
                    f'/bin/bash {cur_dir}/scripts/install_gcloud.sh {os_type} {arch}',
                )
                spinner.ok('🛠️')


def _parse_custom_data_from_cli(data: str, user_input: UserInput):
    try:
        data = os.path.expanduser(data)
    except Exception:
        pass
    if os.path.exists(data):
        user_input.custom_dataset_type = 'path'
        user_input.dataset_path = data
    elif 'http' in data:
        user_input.custom_dataset_type = 'url'
        user_input.dataset_url = data
    else:
        user_input.custom_dataset_type = 'docarray'
        user_input.dataset_secret = data
