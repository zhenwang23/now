from argparse import Namespace

import pytest
from docarray import Document
from jina import Client

from now.cli import cli
from now.dialog import NEW_CLUSTER


@pytest.mark.parametrize(
    'dataset', ['best-artworks', 'deepfashion']
)  # art -> no finetuning, fashion -> finetuning
@pytest.mark.parametrize('quality', ['medium'])
@pytest.mark.parametrize('cluster', [NEW_CLUSTER])
@pytest.mark.parametrize('cluster_new', ['local'])
def test_backend(
    dataset: str,
    quality: str,
    cluster: str,
    cluster_new: str,
):
    args = {
        'data': None,
        'dataset': dataset,
        'quality': quality,
        'cluster': cluster,
        'cluster_new': cluster_new,
        'proceed': True,
    }
    args = Namespace(**args)
    cli(args=args)

    if dataset == 'best-artworks':
        search_text = 'impressionism'
    elif dataset == 'nft-monkey':
        search_text = 'laser eyes'
    else:
        search_text = 'test'

    client = Client(
        host='localhost',
        protocol="grpc",
        port=31080,  # 30080 for frontend, 31080 for backend
    )
    response = client.search(
        Document(text=search_text),
        parameters={"limit": 9, "filter": {}},
    )

    assert response[0].matches
