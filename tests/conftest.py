""" Module holds reusable fixtures """

import os

import pytest


@pytest.fixture()
def resources_folder_path() -> str:
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')


@pytest.fixture()
def image_resource_path(resources_folder_path: str) -> str:
    return os.path.join(resources_folder_path, 'images')
