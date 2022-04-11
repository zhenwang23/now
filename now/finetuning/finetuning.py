import math
import os
from copy import deepcopy
from time import sleep

import finetuner
from docarray import DocumentArray
from docarray.math.evaluation import ndcg_at_k
from finetuner.tuner.callback import (
    BestModelCheckpoint,
    EarlyStopping,
    EvaluationCallback,
)
from finetuner.tuner.pytorch.losses import TripletLoss
from finetuner.tuner.pytorch.miner import TripletEasyHardMiner
from jina import Client, Flow
from tqdm import tqdm
from yaspin import yaspin

from now.deployment.deployment import cmd
from now.deployment.flow import batch, deploy_k8s
from now.hub.head_encoder.head_encoder import LinearHead
from now.utils import get_device, sigmap

epochs = 50  # use early stopping


def finetune_layer(ds, batch_size, final_layer_output_dim, embedding_size, tmpdir):
    embedding_datasets = []
    for da in [ds['train'], ds['val'], ds['val_query'], ds['val_index']]:
        embedding_ds = DocumentArray()
        embedding_datasets.append(embedding_ds)
        for d in da:
            d = deepcopy(d)
            # TODO 3.0
            # d.tensor = d.embedding
            d.tensor = d.embedding
            # d.embedding = None
            embedding_ds.append(d)
    (
        train_embedding,
        validation_embedding,
        query_embedding,
        index_embedding,
    ) = embedding_datasets
    # print(
    #     f'data size: (train, {len(train_embedding)}), (val, {len(validation_embedding)}), (query, {len(query_embedding)}), (index, {len(index_embedding)})')
    save_dir = os.path.join(tmpdir, 'now/hub/head_encoder')
    callbacks = [
        EvaluationCallback(
            # TODO parameterize limit based on dataset
            query_embedding,
            index_embedding,
            limit=20,
            num_workers=8,
            metrics={'ndcg': (ndcg_at_k, {})},
        ),
        BestModelCheckpoint(monitor='ndcg', save_dir=save_dir),
        EarlyStopping(monitor='ndcg', verbose=False, patience=5),
    ]

    # def configure_optimizer(model: torch.nn.Module):
    #     optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)
    #     scheduler = get_linear_schedule_with_warmup(
    #         optimizer,
    #         num_warmup_steps=int(len(ds) / batch_size / 2),
    #         num_training_steps=epochs * math.ceil(len(train_embedding) / batch_size)
    #     )
    #     return optimizer, scheduler

    print('💪 fine-tuning:')
    mean_path = os.path.join(tmpdir, 'now/hub/head_encoder')
    head = LinearHead(final_layer_output_dim, embedding_size, mean_path=mean_path)
    # noinspection PyTypeChecker
    finetuner.fit(
        head,
        train_data=train_embedding,
        eval_data=validation_embedding,
        epochs=epochs,
        learning_rate=5e-4,
        batch_size=batch_size,
        loss=TripletLoss(
            # Todo maybe cosine worked as good as euclidean
            # margin seems to have no effect on the art dataset
            margin=0,
            miner=TripletEasyHardMiner(pos_strategy='hard', neg_strategy='hard'),
        ),
        device=get_device(),
        # configure_optimizer=configure_optimizer,
        num_items_per_class=4,
        callbacks=callbacks,
        tag_key=finetuner.__default_tag_key__,
    )
    print('  🧠 Perfect! Early stopping triggered since accuracy is great already')
    return f'{save_dir}/best_model_ndcg'


def add_clip_embeddings(dataset, vision_model, tmpdir, **kwargs):
    need_to_add_embeddings = False
    with yaspin(
        sigmap=sigmap, text="Check if embeddings already exist", color="green"
    ) as spinner:
        for k, da in dataset.items():
            if da is None:
                continue
            for d in da:
                if d.embedding is None:
                    need_to_add_embeddings = True
                    break
        if not need_to_add_embeddings:
            spinner.ok('👍')
            return
        spinner.fail('👎')

    ns = 'nowtmp'
    f = Flow(name=ns, port_expose=8080, cors=True,).add(
        name='clip',
        uses='jinahub+docker://CLIPEncoder/v0.2.1',
        uses_with={'pretrained_model_name_or_path': vision_model},
    )
    (
        gateway_host,
        gateway_port,
        gateway_host_internal,
        gateway_port_internal,
    ) = deploy_k8s(f, ns, 3, tmpdir, **kwargs)
    for k, da in dataset.items():
        if da is not None:
            # this is just to save computation in case we have the embeddings already
            results = DocumentArray()
            embedding_dataset = DocumentArray()
            no_embedding_dataset = DocumentArray()
            for d in da:
                if d.embedding is None:
                    no_embedding_dataset.append(d)
                else:
                    embedding_dataset.append(d)
            client = Client(host=gateway_host, port=gateway_port)
            print(f'▶ create embeddings for {len(no_embedding_dataset)} documents')
            for x in tqdm(
                batch(no_embedding_dataset, 512),
                total=math.ceil(len(no_embedding_dataset) / 512),
            ):
                while True:
                    try:
                        response = client.post('/index', request_size=16, inputs=x)
                        results.extend(response)
                        break
                    except Exception as e:
                        sleep(1)

            dataset[k] = (embedding_dataset + results).shuffle(42)
    cmd(f'{kwargs["kubectl_path"]} delete ns {ns}')
