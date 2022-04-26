import enum


class Modality(str, enum.Enum):
    IMAGE = 'image'
    AUDIO = 'audio'
    TEXT = 'text'


class Quality(str, enum.Enum):
    MEDIUM = 'medium'
    GOOD = 'good'
    EXCELLENT = 'excellent'


BASE_STORAGE_URL = (
    'https://storage.googleapis.com/jina-fashion-data/data/one-line/datasets'
)

IMAGE_MODEL_QUALITY_MAP = {
    Quality.MEDIUM: ('ViT-B32', 'openai/clip-vit-base-patch32'),
    Quality.GOOD: ('ViT-B16', 'openai/clip-vit-base-patch16'),
    Quality.EXCELLENT: ('ViT-L14', 'openai/clip-vit-large-patch14'),
}


AVAILABLE_DATASET = {
    Modality.IMAGE: [
        'best-artworks',
        'nft-monkey',
        'tll',
        'bird-species',
        'stanford-cars',
        'deepfashion',
        'nih-chest-xrays',
        'geolocation-geoguessr',
    ],
    Modality.AUDIO: [
        'music-genres-small',
        'music-genres-large',
    ],
    Modality.TEXT: [
        'rock-lyrics',
        'pop-lyrics',
        'rap-lyrics',
        'indie-lyrics',
        'metal-lyrics',
    ],
}
