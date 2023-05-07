from collections.abc import Collection
from typing import Union


def squash_collection(collection: Collection) -> Union[Collection, object]:
    if len(collection) == 1:
        return collection

    return collection
