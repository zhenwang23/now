import pytest

from now.dialog import NEW_CLUSTER
from now.run_all_k8s import run_k8s


@pytest.fixture
def os_type() -> str:
    pass


@pytest.fixture
def arch() -> str:
    pass


@pytest.mark.parameterize('dataset', ['best-artworks', 'nft-monkey'])
@pytest.mark.parameterize('quality', ['medium', 'good', 'excellent'])
@pytest.mark.parameterize('cluster', [NEW_CLUSTER])
@pytest.mark.parameterize('cluster_new', ['local'])
def test_run8ks(os_type: str, arch: str, dataset: str, quality: str, cluster: str, cluster_new: str, ):
    run_k8s(os_type=os_type, arch=arch, dataset=dataset, quality=quality, cluster=cluster, cluster_new=cluster_new)
    # now test that everything works smoothly
    pass

