import itertools

def support(itemset, transactions):
    """Returns the percentage of transactions that contain the itemset.

    Parameters
    ----------
    itemset : frozenset
    transactions : list of list

    Returns
    -------
    float
        Percentage of transactions that contain the itemset
    """
    contains_itemset = 0
    for transaction in transactions:
        if itemset.issubset(transaction):
            contains_itemset += 1
    return contains_itemset / len(transactions)


def confidence(itemset_a, itemset_b, transactions):
    """Returns the percentage of transactions that contain both itemset_a and
    itemset_b.

    Parameters
    ----------
    itemset_a : frozenset
    itemset_b : frozenset
    transactions : list of list

    Returns
    -------
    float
        Percentage of transactions that contain both itemset_a and itemset_b
    """
    itemset_a_support = support(itemset_a, transactions)
    if itemset_a_support == 0:
        return 0
    return support(itemset_a.union(itemset_b), transactions) \
        / itemset_a_support

def get_frequent_length_k_itemsets(transactions, min_support=0.2, k=1, frequent_sub_itemsets=None):
    """Returns all the length-k itemsets, from the transactions, that satisfy
    min_support.

    Parameters
    ----------
    transactions : list of list
    min_support : float, optional
        From 0.0 to 1.0. Percentage of transactions that should contain an
        itemset for it to be considered frequent.
    k : int, optional
        Length that the frequent itemsets should be
    frequent_sub_itemsets : frozenset of frozenset, optional
        Facilitates candidate pruning by the Apriori property. Length-k itemset
        candidates that aren't supersets of at least 1 frequent sub-itemset are
        pruned.

    Returns
    -------
    list of frozenset
    list of float
    """
    if min_support <= 0 or min_support > 1:
        raise ValueError('min_support must be greater than 0 and less than or equal to 1.0')
    if k <= 0:
        raise ValueError('k must be greater than 0')
    all_items = set()
    for transaction in transactions:
        all_items = all_items.union(transaction)
    length_k_itemsets = itertools.product(all_items, repeat=k)
    length_k_itemsets = frozenset(frozenset(itemset) for itemset in length_k_itemsets)
    length_k_itemsets = frozenset(filter(lambda itemset: len(itemset) == k, length_k_itemsets))
    # Remove itemsets that don't have a frequent sub-itemset to take advantage
    # of the Apriori property
    if frequent_sub_itemsets:
        to_remove = set()
        for itemset in length_k_itemsets:
            has_frequent_sub_itemset = False
            for sub_itemset in frequent_sub_itemsets:
                if itemset.issuperset(sub_itemset):
                    has_frequent_sub_itemset = True
            if not has_frequent_sub_itemset:
                to_remove.add(itemset)
        length_k_itemsets = length_k_itemsets.difference(to_remove)
    frequent_itemsets = []
    supports = []
    for itemset in length_k_itemsets:
        itemset_support = support(itemset, transactions)
        if itemset_support >= min_support:
            frequent_itemsets.append(itemset)
            supports.append(itemset_support)
    return frequent_itemsets, supports

def get_frequent_itemsets(transactions, min_support=0.2):
    """Returns all the itemsets, from the transactions, that satisfy
    min_support.

    Uses the Apriori algorithm.

    Parameters
    ----------
    transactions : list of list
    min_support : float, optional
        From 0.0 to 1.0. Percentage of transactions that should contain an
        itemset for it to be considered frequent.

    Returns
    -------
    list of frozenset
    list of float
    """
    k = 1
    length_k_frequent_itemsets, length_k_supports = get_frequent_length_k_itemsets(
        transactions,
        min_support=min_support,
        k=k
    )
    frequent_itemsets = length_k_frequent_itemsets
    supports = length_k_supports
    while len(length_k_frequent_itemsets) > 0:
        k += 1
        length_k_frequent_itemsets, length_k_supports = get_frequent_length_k_itemsets(
            transactions,
            min_support=min_support,
            k=k,
            frequent_sub_itemsets=length_k_frequent_itemsets
        )
        frequent_itemsets += length_k_frequent_itemsets
        supports += length_k_supports
    return frequent_itemsets, supports
