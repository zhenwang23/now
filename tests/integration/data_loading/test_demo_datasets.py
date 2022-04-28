"""
This suite tests that the demo datasets are available
with the correct names in the GC bucket

To run the test locally you need to set the `GOOGLE_APPLICATION_CREDENTIALS`
environment variable to point to your service account json file or
place the file `service_account.json` in the root of the project.
"""

import pytest
import requests

from now.constants import AVAILABLE_DATASET, Modality, Quality
from now.data_loading.data_loading import get_dataset_url


@pytest.mark.parametrize(
    'modality, ds_name', [(m, d) for m in Modality for d in AVAILABLE_DATASET[m]]
)
@pytest.mark.parametrize('quality', [q for q in Quality])
def test_dataset_is_available(
    ds_name: str,
    modality: Modality,
    quality: Quality,
):
    if modality == Modality.MUSIC:  # music has no quality config
        quality = None
    url = get_dataset_url(ds_name, quality, modality)

    assert requests.head(url).status_code == 200
