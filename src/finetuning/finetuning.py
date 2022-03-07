from copy import deepcopy

import finetuner
from docarray import DocumentArray
from docarray.math.evaluation import ndcg_at_k
from finetuner.tuner.callback import EvaluationCallback, BestModelCheckpoint, EarlyStopping
from finetuner.tuner.pytorch.losses import TripletLoss
from finetuner.tuner.pytorch.miner import TripletEasyHardMiner
from jina import Flow

from src.deployment.flow import batch
from src.hub.head_encoder.head_encoder import LinearHead
from src.utils import get_device

epochs = 50  # use early stopping


def finetune_layer(ds, batch_size, final_layer_output_dim, embedding_size):
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
    train_embedding, validation_embedding, query_embedding, index_embedding = embedding_datasets
    # print(
    #     f'data size: (train, {len(train_embedding)}), (val, {len(validation_embedding)}), (query, {len(query_embedding)}), (index, {len(index_embedding)})')
    save_dir = 'src/hub/head_encoder'
    callbacks = [
        EvaluationCallback(
            # TODO parameterize limit based on dataset
            query_embedding, index_embedding, limit=20, num_workers=8, metrics={
                'ndcg': (ndcg_at_k, {})}
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

    head = LinearHead(final_layer_output_dim, embedding_size)
    # noinspection PyTypeChecker
    finetuner.fit(
        head,
        train_data=train_embedding,
        eval_data=validation_embedding,
        epochs=epochs,
        learning_rate=1e-4,
        batch_size=batch_size,
        loss=TripletLoss(
            # Todo maybe cosine
            distance='euclidean',
            margin=0.5,
            miner=TripletEasyHardMiner(pos_strategy='hard', neg_strategy='hard'),
        ),
        device=get_device(),
        # configure_optimizer=configure_optimizer,
        num_items_per_class=4,
        callbacks=callbacks,
        tag_key=finetuner.__default_tag_key__
    )
    print('  🧠 perfect! Early stopping triggered since the accuracy is great already')
    return f'{save_dir}/best_model_ndcg'


def add_clip_embeddings(dataset, vision_model, infrastructure):
    need_to_add_embeddings = False
    for k, da in dataset.items():
        if da is None:
            continue
        for d in da:
            if d.embedding is None:
                need_to_add_embeddings = True
                break
    if not need_to_add_embeddings:
        print('👍 dataset already contains embeddings')
        return
    print('embed datasets:')

    if infrastructure == 'local':
        flow_kwargs = {'volumes': [f'data/tmp/cache:/root/.cache']}
    else:
        flow_kwargs = {}
    with Flow().add(
            name='clip',
            uses='jinahub{docker_prefix}://CLIPEncoder/v0.2.0',
            uses_with={
                'pretrained_model_name_or_path': vision_model
            },
            **flow_kwargs
    ) as f:
        print('embedding flow started')
        for k, da in dataset.items():
            if da is not None:
                # this is just to save computation in case we have the embeddings already
                results_image = DocumentArray()
                results_text = DocumentArray()
                embedding_dataset = DocumentArray()
                no_embedding_dataset_image = DocumentArray()
                no_embedding_dataset_text = DocumentArray()
                for d in da:
                    if d.embedding is None:
                        if d.text:
                            no_embedding_dataset_text.append(d)
                        else:
                            no_embedding_dataset_image.append(d)

                    else:
                        embedding_dataset.append(d)

                def append_result_image(resp):
                    results_image.extend(DocumentArray(resp.data.docs))

                def append_result_text(resp):
                    results_text.extend(DocumentArray(resp.data.docs))

                print('start embedding image', k)
                for x in batch(no_embedding_dataset_image, 16):
                    f.index(x, on_done=append_result_image)
                print('start embedding text', k)
                for x in batch(no_embedding_dataset_text, 16):
                    f.index(x, on_done=append_result_text)
                dataset[k] = (embedding_dataset + results_image + results_text).shuffle(42)
