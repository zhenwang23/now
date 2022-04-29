from argparse import Namespace

import pytest
from fastapi.testclient import TestClient

from now.cli import cli
from now.dialog import NEW_CLUSTER


@pytest.mark.parametrize(
    'output_modality, dataset',
    [('image', 'best-artworks'), ('image', 'deepfashion'), ('text', 'rock-lyrics')],
)  # art, rock-lyrics -> no finetuning, fashion -> finetuning
@pytest.mark.parametrize('quality', ['medium'])
@pytest.mark.parametrize('cluster', [NEW_CLUSTER['value']])
@pytest.mark.parametrize('new_cluster_type', ['local'])
def test_backend(
    output_modality: str,
    dataset: str,
    quality: str,
    cluster: str,
    new_cluster_type: str,
    test_client: TestClient,
):
    sandbox = dataset == 'best-artworks'
    kwargs = {
        'output_modality': output_modality,
        'data': dataset,
        'quality': quality,
        'sandbox': sandbox,
        'cluster': cluster,
        'new_cluster_type': new_cluster_type,
        'proceed': True,
    }
    kwargs = Namespace(**kwargs)
    cli(args=kwargs)

    if dataset == 'best-artworks':
        search_text = 'impressionism'
    elif dataset == 'nft-monkey':
        search_text = 'laser eyes'
    else:
        search_text = 'test'

    # Perform end-to-end check via bff
    if output_modality == 'image':
        response = test_client.post(
            f'/api/v1/image/search{search_text}',
            params={'limit': 9},  # limit has no effect as of now
        )
    elif output_modality == 'text':
        response = test_client.post(
            f'/api/v1/text/search{search_text}',
            params={'limit': 9},  # limit has no effect as of now
        )
    else:
        # add more here when the new modality is added
        response = None
    assert response.status_code == 200
    # Limit param is not respected and hence 20 matches are returned
    # Therefore, once the limit is implemented in the CustomIndexer,
    # we should change the below value to 9
    assert len(response[0].matches) == 20
