from collections.abc import Collection


def squash_collection(collection: Collection) -> Collection | object:
    if len(collection) == 1:
        return collection

    return collection
