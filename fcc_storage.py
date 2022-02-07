from base_storage import BaseStorage
from config import config

class FccStorage(BaseStorage):
    def __init__(self, context):
        self._context = context

    def list_files(self):
        return []
