from base_storage import BaseStorage

class CxStorage(BaseStorage):
    def __init__(self, context):
        self._context = context

    def file_details(self, file_id):
        raise NotImplementedError()

    def list_files(self):
        raise NotImplementedError()

    def list_files_tabular(self):
        raise NotImplementedError()

    def delete_file(self, file_id):
        raise NotImplementedError()
