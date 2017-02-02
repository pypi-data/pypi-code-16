import itertools

def support(itemsets, transactions):
    """Returns the percentage of transactions that contain the itemsets.

    Parameters
    ----------
    itemsets : list of frozenset
    transactions : list of list

    Returns
    -------
    dict
    Key of each item is the itemset and the value is the itemset's support
    """
    counts = {}
    for itemset in itemsets:
        counts[itemset] = 0
    for transaction in transactions:
        for itemset in itemsets:
            if itemset.issubset(transaction):
                counts[itemset] += 1
    supports = {}
    total_transactions = len(transactions)
    for itemset, count in counts.items():
        supports[itemset] = count / total_transactions
    return supports

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
    itemset_a_support = support([itemset_a], transactions)[itemset_a]
    if itemset_a_support == 0:
        return 0
    itemset_a_union_b = itemset_a.union(itemset_b)
    return support([itemset_a_union_b], transactions)[itemset_a_union_b] \
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
    if frequent_sub_itemsets:
        for sub_itemset in frequent_sub_itemsets:
            all_items = all_items.union(sub_itemset)
    else:
        for transaction in transactions:
            all_items = all_items.union(transaction)
    all_length_k_itemsets = itertools.product(all_items, repeat=k)
    all_length_k_itemsets = frozenset(frozenset(itemset) for itemset in all_length_k_itemsets)
    all_length_k_itemsets = frozenset(filter(lambda itemset: len(itemset) == k, all_length_k_itemsets))
    # Remove itemsets that don't have a frequent sub-itemset to take advantage
    # of the Apriori property
    pruned_length_k_itemsets = all_length_k_itemsets
    if frequent_sub_itemsets:
        pruned_length_k_itemsets = set()
        for itemset in all_length_k_itemsets:
            has_frequent_sub_itemset = False
            for sub_itemset in frequent_sub_itemsets:
                if sub_itemset.issubset(itemset):
                    has_frequent_sub_itemset = True
            if has_frequent_sub_itemset:
                pruned_length_k_itemsets.add(itemset)
    frequent_itemsets = []
    frequent_supports = []
    supports = support(pruned_length_k_itemsets, transactions)
    for itemset, itemset_support in supports.items():
        if itemset_support >= min_support:
            frequent_itemsets.append(itemset)
            frequent_supports.append(itemset_support)
    return frequent_itemsets, frequent_supports

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
