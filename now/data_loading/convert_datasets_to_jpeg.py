import io
import multiprocessing as mp

from docarray import Document, DocumentArray
from PIL import Image
from tqdm import tqdm


def to_jpg(doc: Document):
    if doc.tensor is not None:
        im = Image.fromarray(doc.tensor)
        doc.tensor = None
        img_byte_arr = io.BytesIO()
        im.save(img_byte_arr, format="JPEG", quality=75)
        doc.blob = img_byte_arr.getvalue()
    return doc


def convert_to_jpeg(dataset: str, num_workers: int = 8):
    path = f'{dataset}.bin'

    print(f'===> {dataset}')
    print(f'  Loading {dataset} dataset from {path} ...')
    docs = DocumentArray.load_binary(path, compress='gzip')
    print(f'  Dataset size: {len(docs)}')

    print(f' convert images to jpeg for smaller datasets')
    # build docs
    with mp.Pool(processes=num_workers) as pool:
        docs = list(tqdm(pool.imap(to_jpg, docs)))
    docs = DocumentArray(docs)

    print(f'  Saving converted docs ...')
    out = f'{dataset}.jpeg.bin'
    docs.save_binary(out)
    print(f'  Saved converted docs to {out} ...')


def main():
    """
    Main method.
    """
    datasets = [
        'deepfashion',
        'deepfashion.img10',
        'deepfashion.ViT-B32',
        'deepfashion.ViT-B16',
        'deepfashion.ViT-L14',
        'nih-chest-xrays',
        'nih-chest-xrays.img10',
        'nih-chest-xrays.ViT-B32',
        'nih-chest-xrays.ViT-B16',
        'nih-chest-xrays.ViT-L14',
        'geolocation-geoguessr',
        'geolocation-geoguessr.img10',
        'geolocation-geoguessr.ViT-B32',
        'geolocation-geoguessr.ViT-B16',
        'geolocation-geoguessr.ViT-L14',
        'stanford-cars',
        'stanford-cars.img10',
        'stanford-cars.ViT-B32',
        'stanford-cars.ViT-B16',
        'stanford-cars.ViT-L14',
        'bird-species',
        'bird-species.img10',
        'bird-species.ViT-B32',
        'bird-species.ViT-B16',
        'bird-species.ViT-L14',
        'best-artworks',
        'best-artworks.img10',
        'best-artworks.ViT-B32',
        'best-artworks.ViT-B16',
        'best-artworks.ViT-L14',
    ]

    for dataset in datasets:
        convert_to_jpeg(dataset)


if __name__ == '__main__':
    main()
