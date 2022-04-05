from docarray import DocumentArray
from jina import Executor, requests


class MostSimpleIndexer(Executor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = DocumentArray()

    @requests
    def index(self, docs: DocumentArray, **kwargs):
        self.index.extend(docs)

    @requests(on='/search')
    def search(self, docs: DocumentArray, **kwargs):
        docs.match(self.index)
        return docs
