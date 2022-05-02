import array
import io
from typing import TYPE_CHECKING, Tuple

import numpy as np
from pydub import AudioSegment
from pydub.utils import get_array_type


def upload_to_gcloud_bucket(project: str, bucket: str, location: str, fname: str):
    """
    Upload local file to Google Cloud bucket.
    """
    if TYPE_CHECKING:
        from google.cloud import storage

    client = storage.Client(project=project)
    bucket = client.get_bucket(bucket)

    with open(fname, 'rb') as f:
        content = io.BytesIO(f.read())

    tensor = bucket.blob(location + '/' + fname)
    tensor.upload_from_file(content, timeout=7200)


def load_mp3(path_to_mp3: str) -> Tuple[np.ndarray, int]:
    # TODO: store mp3 as binary blob on the doc and load in executor accordingly
    sound = AudioSegment.from_mp3(file=path_to_mp3)
    left, right = sound.split_to_mono()

    bit_depth = left.sample_width * 8
    array_type = get_array_type(bit_depth)

    left = np.array(array.array(array_type, left._data))
    right = np.array(array.array(array_type, right._data))

    mean = np.mean([left, right], axis=0)
    normalized = mean / np.max(np.abs(mean))

    return normalized, int(sound.frame_rate)
