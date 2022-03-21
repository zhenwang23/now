import multiprocessing as mp

from docarray import Document, DocumentArray

# $ pip uninstall jina
# $ pip uninstall docarray
# $ pip install jina==2.6.4
# $ mv .venv/lib/python3.8/site-packages/docaarray .venv/lib/python3.8/site-packages/old
# $ pip install docarray
from old import Document as OldDocument
from old import DocumentArray as OldDocumentArray
from tqdm import tqdm


def _convert_doc(old: OldDocument) -> Document:
    new = Document(id=old.id, mime_type=old.mime_type)
    if old.tags['content_type'] == 'image':
        new.uri = old.uri
        new.tensor = old.blob
    else:
        new.text = old.text
    for k, v in old.tags.items():
        new.tags[k] = v
    new.embedding = old.embedding
    return new


def convert_dataset(dataset: str, num_workers: int = 8):
    path = f'{dataset}.bin'

    print(f'===> {dataset}')
    print(f'  Loading {dataset} dataset from {path} ...')
    old_docs = OldDocumentArray.load_binary(path)
    print(f'  Old dataset size: {len(old_docs)}')

    print('  Converting docs ...')
    with mp.Pool(processes=num_workers) as pool:
        new_docs = list(tqdm(pool.imap(_convert_doc, old_docs)))

    new_docs = DocumentArray(new_docs)

    print(f'  New dataset size: {len(new_docs)}')

    print('  Saving new docs ...')
    out = f'new.{dataset}.bin'
    new_docs.save_binary(out, compress='gzip')
    print(f'  Saved new docs to {out} ...')


def main():
    """
    Main method.
    """
    datasets = [
        'deepfashion',
        'deepfashion.img10',
        'deepfashion.txt10',
        'deepfashion.ViT-B32',
        'deepfashion.ViT-B16',
        'deepfashion.ViT-L14',
        'nih-chest-xrays',
        'nih-chest-xrays.img10',
        'nih-chest-xrays.txt10',
        'nih-chest-xrays.ViT-B32',
        'nih-chest-xrays.ViT-B16',
        'nih-chest-xrays.ViT-L14',
        'geolocation-geoguessr',
        'geolocation-geoguessr.img10',
        'geolocation-geoguessr.txt10',
        'geolocation-geoguessr.ViT-B32',
        'geolocation-geoguessr.ViT-B16',
        'geolocation-geoguessr.ViT-L14',
        'stanford-cars',
        'stanford-cars.img10',
        'stanford-cars.txt10',
        'stanford-cars.ViT-B32',
        'stanford-cars.ViT-B16',
        'stanford-cars.ViT-L14',
        'bird-species',
        'bird-species.img10',
        'bird-species.txt10',
        'bird-species.ViT-B32',
        'bird-species.ViT-B16',
        'bird-species.ViT-L14',
        'best-artworks',
        'best-artworks.img10',
        'best-artworks.txt10',
        'best-artworks.ViT-B32',
        'best-artworks.ViT-B16',
        'best-artworks.ViT-L14',
    ]
    num_workers = 8

    for dataset in datasets:
        convert_dataset(dataset, num_workers)


if __name__ == '__main__':
    main()
