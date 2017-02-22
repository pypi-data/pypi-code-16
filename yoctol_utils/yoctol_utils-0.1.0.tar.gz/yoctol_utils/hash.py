from sklearn.utils import murmurhash3_32


def consistent_hash(hash_str):
	return murmurhash3_32(hash_str, seed=0)
