import base64
import enum
import os
import random
import uuid
from copy import deepcopy
from os.path import join as osp
from typing import Optional, Tuple

from docarray import DocumentArray
from yaspin import yaspin

from now.constants import BASE_STORAGE_URL, IMAGE_MODEL_QUALITY_MAP, Modality, Quality
from now.data_loading.convert_datasets_to_jpeg import to_thumbnail_jpg
from now.utils import download, sigmap


class DatasetType(str, enum.Enum):
    DEMO = 'demo'
    PATH = 'path'
    URL = 'url'
    DOCARRAY = 'docarray'


def _fetch_da_from_url(
    url: str, downloaded_path: str = '~/.cache/jina-now'
) -> DocumentArray:
    data_dir = os.path.expanduser(downloaded_path)
    if not os.path.exists(osp(data_dir, 'data/tmp')):
        os.makedirs(osp(data_dir, 'data/tmp'))
    data_path = (
        data_dir
        + f"/data/tmp/{base64.b64encode(bytes(url, 'utf-8')).decode('utf-8')}.bin"
    )
    if not os.path.exists(data_path):
        download(url, data_path)

    with yaspin(sigmap=sigmap, text="Extracting dataset", color="green") as spinner:
        da = DocumentArray.load_binary(data_path)
        spinner.ok("📂")
    return da


def _deep_copy_da(da: DocumentArray) -> DocumentArray:
    new_da = DocumentArray()
    for i, d in enumerate(da):
        new_doc = deepcopy(d)
        new_doc.id = str(uuid.uuid4())
        new_da.append(new_doc)
    return new_da


def load_data(
    output_modality: Modality,
    dataset: str,
    model_quality: Quality,
    is_custom: bool,
    custom_type: str,
    secret: Optional[str],
    url: Optional[str],
    path: Optional[str],
) -> Tuple[DocumentArray, DatasetType]:

    if not is_custom:
        print('⬇  Download data')
        url = _get_dataset_url(dataset, model_quality, output_modality)
        da = _fetch_da_from_url(url)
        ds_type = 'demo'

    else:
        if custom_type == 'docarray':
            print('⬇  pull docarray')
            try:
                da = DocumentArray.pull(token=secret, show_progress=True)
                ds_type = 'docarray_pull'
            except Exception:
                print(
                    '💔 oh no, the secret of your docarray is wrong, or it was deleted after 14 days'
                )
                exit(1)
        elif custom_type == 'url':
            print('⬇  Download data')
            da = _fetch_da_from_url(url)
            ds_type = 'url'
        else:
            if os.path.isfile(path):
                try:
                    da = DocumentArray.load_binary(path)
                    ds_type = 'local_da'
                except Exception as e:
                    print('Failed to load the binary file provided')
                    exit(1)
            else:
                da = DocumentArray.from_files(path + '/**')

                def convert_fn(d):
                    try:
                        d.load_uri_to_image_tensor()
                        return to_thumbnail_jpg(d)
                    except:
                        return d

                with yaspin(
                    sigmap=sigmap, text="Pre-processing data", color="green"
                ) as spinner:
                    da.apply(convert_fn)
                    da = DocumentArray(d for d in da if d.blob != b'')
                    spinner.ok('🏭')
                ds_type = 'local_folder'

                # for d in da:
                #     d.tags['finetuner_label'] = os.path.dirname(d.uri).split('/')[-1]

    da = da.shuffle(seed=42)
    da = _deep_copy_da(da)
    return da, ds_type


def _get_dataset_url(
    dataset: str, model_quality: Optional[str], output_modality: Modality
) -> str:
    data_folder = None
    if output_modality == Modality.IMAGE:
        data_folder = 'jpeg'
    elif output_modality == Modality.TEXT:
        data_folder = 'text'
    elif output_modality == Modality.AUDIO:
        data_folder = 'audio'

    if model_quality is not None:
        return f'{BASE_STORAGE_URL}/{data_folder}/{dataset}.{IMAGE_MODEL_QUALITY_MAP[model_quality][0]}.bin'
    else:
        return f'{BASE_STORAGE_URL}/{data_folder}/{dataset}.bin'


def fill_missing(ds, train_val_split_ratio, num_default_val_queries, is_debug):
    # ds['index'] = deepcopy(DocumentArray(d for d in ds['index'] if d.tensor is not None))
    if ds['train'] is None:
        ds['train'] = ds['index']
    if ds['val'] is None:
        # TODO makes split based on classes rather than instances
        split_index = max(
            int(len(ds['train']) * train_val_split_ratio),
            len(ds['train']) - 5000,
        )
        train = ds['train']
        ds['train'], ds['val'] = train[:split_index], train[split_index:]

    if ds['val_index'] is None:
        ds['val_index'] = deepcopy(ds['val'])
    if ds['val_query'] is None:
        if is_debug:
            num_queries = 10
        else:
            num_queries = 100

        ds['val_query'] = DocumentArray(
            [deepcopy(doc) for doc in random.sample(ds['val_index'], num_queries)]
        )
        # for d in ds['val_query']:
        #     ds['val_index'].remove(d)

    if ds['val_index_image'] is None:
        ds['val_index_image'] = deepcopy(
            # DocumentArray(d for d in ds['val'] if d.blob is not None)
            DocumentArray(d for d in ds['val'] if d.blob != b'')
        )
    if ds['val_query_image'] is None:
        ds['val_query_image'] = DocumentArray(
            [
                deepcopy(doc)
                for doc in random.sample(ds['val_index_image'], num_default_val_queries)
            ]
        )
