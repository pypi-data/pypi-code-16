"""
Batching support.

"""


def batched(resources, batch_size, **kwargs):
    """
    Chunk resources into batches.

    """
    batch = []
    for resource in resources:
        batch.append(resource)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
