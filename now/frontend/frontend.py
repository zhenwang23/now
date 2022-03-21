import base64
import os
import sys
from urllib.request import urlopen

import streamlit as st
from docarray import DocumentArray
from jina import Client, Document


def deploy_streamlit():
    """
    We want to provide the end-to-end experience to the user.
    Please deploy a streamlit frontend on k8s/local to access the api.
    You can get the starting point for the streamlit application from alex.
    """
    print('Run Streamlit with:', sys.argv)
    print(sys.argv)
    _, host, port, data = sys.argv
    da_img = None
    da_txt = None

    # General
    TOP_K = 9
    DEBUG = os.getenv("DEBUG", False)
    DATA_DIR = "../data/images/"

    if data in ds_set:
        da_img, da_txt = load_data(root_data_dir + data + '.img10.bin'), load_data(
            root_data_dir + data + '.txt10.bin'
        )

    class UI:
        about_block = """
        ### About
        This is a meme search engine using [Jina's neural search framework](https://github.com/jina-ai/jina/).
        - [Live demo](https://examples.jina.ai/memes)
        - [Play with it in a notebook](https://colab.research.google.com/github/jina-ai/workshops/blob/main/memes/meme_search.ipynb) (t-only)
        - [Repo](https://github.com/alexcg1/jina-meme-search)
        - [Dataset](https://www.kaggle.com/abhishtagatya/imgflipscraped-memes-caption-dataset)
        """

        css = """
        <style>
            .reportview-container .main .block-container{{
                max-width: 1200px;
                padding-top: 2rem;
                padding-right: 2rem;
                padding-left: 2rem;
                padding-bottom: 2rem;
            }}
            .reportview-container .main {{
                color: "#111";
                background-color: "#eee";
            }}
        </style>
        """

    def search_by_t(input, server, port, limit=TOP_K):
        print('initialize client at', server, port)
        client = Client(host=server, protocol="grpc", port=port)
        print('search text', server, port)
        response = client.search(
            Document(text=input),
            parameters={"limit": limit, 'filter': {}},
            return_results=True,
            show_progress=True,
        )

        return response[0].matches

    def search_by_file(document, server, port, limit=TOP_K, convert_needed=True):
        """
        Wrap file in Jina Document for searching, and do all necessary conversion to make similar to indexed Docs
        """
        print('connect client to ', server, port)
        client = Client(host=server, protocol="grpc", port=port)
        query_doc = document
        if query_doc.blob != b'':
            query_doc.convert_blob_to_image_tensor()
        query_doc.set_image_tensor_shape((224, 224))
        response = client.search(
            query_doc,
            parameters={"limit": limit, 'filter': {}},
            return_results=True,
            show_progress=True,
        )

        return response[0].matches

    def convert_file_to_document(query):
        data = query.read()

        doc = Document(blob=data)
        print(doc)

        return doc

    matches = []

    # Layout
    st.set_page_config(page_title="NOW", page_icon='https://jina.ai/favicon.ico')

    st.markdown(
        body=UI.css,
        unsafe_allow_html=True,
    )
    col1, mid, col2 = st.columns([1, 1, 20])
    with col1:
        st.image('https://jina.ai/favicon.ico', width=60)
    with col2:
        st.header("NOW ")

    # design and create toggle button
    st.write(
        '<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>',
        unsafe_allow_html=True,
    )
    st.write(
        '<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-right:50px;}</style>',
        unsafe_allow_html=True,
    )
    media_type = st.radio('', ["text", "Image"])

    if media_type == "Image":
        upload_c, preview_c = st.columns([12, 1])
        query = upload_c.file_uploader("")
        if query:
            doc = convert_file_to_document(query)
            matches = search_by_file(document=doc, server=host, port=port)
        if da_img is not None:
            st.subheader("samples:")
            img_cs = st.columns(5)
            txt_cs = st.columns(5)
            for doc, c, txt in zip(da_img, img_cs, txt_cs):
                with c:
                    print('type', type(doc.blob), doc.blob)
                    st.image(doc.blob if doc.blob else doc.tensor, width=100)
                with txt:
                    if st.button('Search', key=doc.id):
                        matches = search_by_file(
                            document=doc, server=host, port=port, convert_needed=False
                        )

    elif media_type == "text":
        query = st.text_input("", key="text_search_box")
        if query:
            matches = search_by_t(input=query, server=host, port=port)
        if st.button("Search", key="text_search"):
            matches = search_by_t(input=query, server=host, port=port)
        if da_txt is not None:
            st.subheader("samples:")
            c1, c2, c3 = st.columns(3)
            c4, c5, c6 = st.columns(3)
            for doc, col in zip(da_txt, [c1, c2, c3, c4, c5, c6]):
                with col:
                    if st.button(doc.content):
                        matches = search_by_t(input=doc.content, server=host, port=port)

    if matches:
        st.header('Search results')
        # Results area
        c1, c2, c3 = st.columns(3)
        c4, c5, c6 = st.columns(3)
        c7, c8, c9 = st.columns(3)
        all_cs = [c1, c2, c3, c4, c5, c6, c7, c8, c9]
        # # TODO dirty hack to filter out text. Instead output modality should be passed as parameter
        # matches = [m for m in matches if m.tensor is None]
        for c, match in zip(all_cs, matches):
            match.mime_type = 'img'
            print('match.blob', len(match.blob))
            if match.blob != b'':
                match.convert_blob_to_datauri()
            print('match.tensor', match.tensor)
            if match.tensor is not None:
                match.convert_image_tensor_to_uri()
            c.image(match.convert_blob_to_datauri().uri)


def load_data(data_path: str) -> DocumentArray:
    print('⬇ load data')
    if data_path.startswith('http'):
        if not os.path.exists('data/tmp'):
            os.makedirs('data/tmp')
        url = data_path
        print('url', url)
        data_path = (
            f"data/tmp/{base64.b64encode(bytes(url, 'utf-8')).decode('utf-8')}.bin"
        )
        if not os.path.exists(data_path):
            with urlopen(url) as f:
                content = f.read()
            with open(data_path, 'wb') as f:
                f.write(content)

    try:
        da = DocumentArray.load_binary(data_path)
    except Exception:
        da = DocumentArray.load_binary(data_path, compress='gzip')
    return da


TEXT_SAMPLES = ['red shoe', 'blue tops']
root_data_dir = (
    'https://storage.googleapis.com/jina-fashion-data/data/one-line/datasets/jpeg/'
)

ds_set = {
    'nft-monkey',
    'deepfashion',
    'nih-chest-xrays',
    'stanford-cars',
    'bird-species',
    'best-artworks',
    'geolocation-geoguessr',
}


if __name__ == '__main__':
    deploy_streamlit()
