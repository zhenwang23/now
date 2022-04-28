"""
This suite tests that the demo datasets are available
with the correct names in the GC bucket

To run the test locally you need to set the `GOOGLE_APPLICATION_CREDENTIALS`
environment variable to point to your service account json file or
place the file `service_account.json` in the root of the project.
"""
import os
from typing import Tuple

import pytest
from google.cloud import storage

from now.constants import AVAILABLE_DATASET, Modality, Quality
from now.data_loading.data_loading import get_dataset_url

project = 'jina-simpsons-florian'
bucket_name = 'jina-fashion-data'
base_url = 'https://storage.googleapis.com/jina-fashion-data/'


@pytest.fixture(scope='session')
def gc_storage(service_account_file_path: str) -> Tuple[storage.Client, storage.Bucket]:
    if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_file_path
    client = storage.Client(project=project)
    return client, client.get_bucket(bucket_name)


def file_exists(client: storage.Client, bucket: storage.Bucket, name: str) -> bool:
    return storage.Blob(bucket=bucket, name=name.replace(base_url, '')).exists(client)


@pytest.mark.parametrize(
    'modality, ds_name', [(m, d) for m in Modality for d in AVAILABLE_DATASET[m]]
)
@pytest.mark.parametrize('quality', [q for q in Quality])
def test_dataset_is_available(
    gc_storage: Tuple[storage.Client, storage.Bucket],
    ds_name: str,
    modality: Modality,
    quality: Quality,
):
    client, bucket = gc_storage
    if modality == Modality.MUSIC:  # music has no quality config
        quality = None
    url = get_dataset_url(ds_name, quality, modality)

    assert file_exists(client, bucket, url)
