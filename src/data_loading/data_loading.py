import base64
import os
import random
import uuid
from copy import deepcopy
from typing import Optional

from docarray import DocumentArray
from yaspin import yaspin

from src.utils import download


def _fetch_da_from_url(url: str) -> DocumentArray:
    if not os.path.exists('data/tmp'):
        os.makedirs('data/tmp')
    data_path = (
        f"data/tmp/{base64.b64encode(bytes(url, 'utf-8')).decode('utf-8')}.bin"
    )
    if not os.path.exists(data_path):
        download(url, data_path)

    with yaspin(text="extracting dataset", color="green") as spinner:
        da = DocumentArray.load_binary(data_path)
        spinner.ok("📂")
    return da


def remove_duplicates(da: DocumentArray):
    """Some da"""
    # known_set = set()
    # unique_dataset = DocumentArray()
    # for i, d in enumerate(da):
    #     d.id = str(uuid.uuid4())
    #     l = d.tags['finetuner_label']
    #     if d.text and l in known_set:
    #         continue
    #     unique_dataset.append(d)
    #     known_set.add(l)
    # return unique_dataset
    # da_text = DocumentArray(d for d in da if d.text)
    # da_img = DocumentArray(d for d in da if not d.text)
    # da_text.embeddings = da_text.embeddings - da_text.embeddings.mean(0)
    # da_img.embeddings = da_img.embeddings - da_img.embeddings.mean(0)

    new_da = DocumentArray()
    for i, d in enumerate(da):
        new_doc = deepcopy(d)
        new_doc.id = str(uuid.uuid4())
        new_da.append(new_doc)
    return new_da


def load_data(
    dataset: str,
    model_quality: str,
    is_custom: bool,
    custom_type: str,
    secret: Optional[str],
    url: Optional[str],
    path: Optional[str],
) -> DocumentArray:

    print('⬇  download data')

    if not is_custom:
        url = (
            'https://storage.googleapis.com/jina-fashion-data/data/one-line/datasets/'
            f'jpeg/{dataset}.{model_quality}.bin'
        )
        da = _fetch_da_from_url(url)

    else:
        if custom_type == 'docarray':
            try:
                da = DocumentArray.pull(token=secret, show_progress=True)
            except:
                print('💔 oh no, the secret of your docarray is wrong, or it was deleted after 14 days')
                exit(1)
        elif custom_type == 'url':
            da = _fetch_da_from_url(url)
        else:
            da = DocumentArray.from_files(path + '/**')
            da.apply(lambda d: d.load_uri_to_image_tensor())
            for d in da:
                d.tags['finetuner_label'] = os.path.dirname(d.uri).split('/')[-1]

    da = da.shuffle(seed=42)
    da = remove_duplicates(da)
    return da


# def load_all_data(dataset):
#     for k, v in dataset.items():
#         if v is not None:
#             dataset[k] = load_data(v)


def fill_missing(ds, train_val_split_ratio, num_default_val_queries, is_debug):
    # ds['index'] = deepcopy(DocumentArray(d for d in ds['index'] if d.tensor is not None))
    if ds['train'] is None:
        ds['train'] = ds['index']
    if ds['val'] is None:
        # TODO makes split based on classes rather than instances
        split_index = max(int(len(ds['train']) * train_val_split_ratio), len(ds['train']) - 5000)
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
        # for d in ds['val_query_image']:
        #     ds['val_index_image'].remove(d)
