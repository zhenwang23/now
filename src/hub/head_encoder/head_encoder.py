import os
import time
from pathlib import Path
from typing import Optional

import numpy as np
import torch
from jina import DocumentArray, Executor, requests


import torch.nn.functional as F
from torch.nn import Linear, Module


class LinearHead(Module):
    def __init__(self, final_layer_output_dim, embedding_size):
        super(LinearHead, self).__init__()
        self.linear1 = Linear(final_layer_output_dim, embedding_size, bias=False)

    def forward(self, x):
        x = x.float()
        x = self.linear1(x)
        normalized_embedding = F.normalize(x, p=2, dim=1)  # L2 normalize
        return normalized_embedding


class FineTunedLinearHeadEncoder(Executor):
    def __init__(self, final_layer_output_dim, embedding_size, model_path='best_model_ndcg', *args, **kwargs):
        super().__init__(**kwargs)
        model_path = Path(__file__).parent / 'best_model_ndcg'
        self.model = LinearHead(final_layer_output_dim, embedding_size)
        self.model.load_state_dict(
            torch.load(model_path, map_location='cpu'))

    @requests
    def encode(self, docs: Optional[DocumentArray], **kwargs):
        blobs = []
        texts = []
        for d in docs:
            blobs.append(d.blob)
            texts.append(d.text)
            d.tensor = d.embedding
        docs.embed(self.model)
        for d, blob, text in zip(docs, blobs, texts):
            if type(d.embedding) != np.ndarray:
                d.embedding = d.embedding.numpy()
            if blob is not None:
                d.blob = blob
            elif text:
                d.text = text
            else:
                raise Exception('neither text nor image present')

        # for efficiency, it is in the same executor
        # for d in docs:
        #     if d.blob is not None:
        #         d.convert_image_tensor_to_uri()
        return docs
