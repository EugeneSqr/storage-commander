from cx_storage import CxStorage
from fcc_storage import FccStorage

def get_storage(context):
    if context.storage == 'fcc':
        return FccStorage(context)
    if context.storage == 'cx':
        return CxStorage(context)
    return None
