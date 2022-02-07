from base_storage import BaseStorage

class CxStorage(BaseStorage):
    def __init__(self, context):
        self._context = context

    def list_files(self):
        raise Exception('Not implemented')
