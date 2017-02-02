import numpy as np

def calculate_cluster_probabilities(clustering):
    total_data_objects = clustering.shape[0]
    total_clusters = np.unique(clustering[:, 1]).size
    cluster_probabilities = np.empty(total_clusters)
    for i, cluster in enumerate(range(total_clusters)):
        cluster_mask = clustering[:, 1] == cluster
        data_objects_in_cluster = clustering[cluster_mask]
        cluster_probabilities[i] = data_objects_in_cluster.shape[0] / total_data_objects
    return cluster_probabilities

def calculate_entropy(clustering):
    cluster_probabilities = calculate_cluster_probabilities(clustering)
    return -1 * np.sum(np.multiply(cluster_probabilities, np.log10(cluster_probabilities)))

def calculate_mutual_info(ground_truth_clustering, clustering):
    total_data_objects = clustering.shape[0]
    total_clusters = np.unique(clustering[:, 1]).size
    ground_truth_total_clusters = np.unique(ground_truth_clustering[:, 1]).size
    result = 0
    for i in range(total_clusters):
        probabilities_in_both = np.empty(total_clusters)
        for j in range(total_clusters):
            cluster_mask = np.all([clustering[:, 1] == i, ground_truth_clustering[:, 1] == j], axis=0)
            data_objects_in_both = clustering[cluster_mask]
            probabilities_in_both[j] = (data_objects_in_both.shape[0] / total_data_objects)
        ground_truth_cluster_probabilities = calculate_cluster_probabilities(ground_truth_clustering)
        cluster_probabilities = calculate_cluster_probabilities(clustering)
        if cluster_probabilities.shape[0] > ground_truth_cluster_probabilities.shape[0]:
            cluster_probabilities = cluster_probabilities[:ground_truth_cluster_probabilities.shape[0]]
        elif ground_truth_cluster_probabilities.shape[0] > cluster_probabilities.shape[0]:
            ground_truth_cluster_probabilities = ground_truth_cluster_probabilities[:cluster_probabilities.shape[0]]
        probabilities_in_both = probabilities_in_both[:cluster_probabilities.shape[0]]
        total = 0
        for j in range(probabilities_in_both.size):
            if probabilities_in_both[j] > 0:
                total = total + (probabilities_in_both[j] * np.log10(probabilities_in_both[j] / (cluster_probabilities[j] * ground_truth_cluster_probabilities[j])))
        result = result + total
    return result

def calculate_normalised_mutual_info(ground_truth_clustering, clustering):
    ground_truth_clustering_entropy = calculate_entropy(ground_truth_clustering)
    clustering_entropy = calculate_entropy(clustering)
    mutual_info = calculate_mutual_info(ground_truth_clustering, clustering)
    return np.divide(mutual_info, np.sqrt(np.multiply(clustering_entropy, ground_truth_clustering_entropy)))

def get_cluster_labels(clustering, label_column):
    return np.unique(clustering[:, label_column])

def calculate_total_data_objects(clustering):
    return clustering.shape[0]

def calculate_total_true_positives(ground_truth_clustering, clustering):
    total = 0
    for i, data_object_1_label in enumerate(clustering):
        for j, data_object_2_label in enumerate(clustering):
            if i != j:
                if data_object_1_label == data_object_2_label and ground_truth_clustering[i] == ground_truth_clustering[j]:
                    total += 1
    return total

def calculate_total_true_negatives(ground_truth_clustering, clustering):
    total = 0
    for i, data_object_1_label in enumerate(clustering):
        for j, data_object_2_label in enumerate(clustering):
            if i != j:
                if data_object_1_label != data_object_2_label and ground_truth_clustering[i] != ground_truth_clustering[j]:
                    total += 1
    return total

def calculate_total_false_positives(ground_truth_clustering, clustering):
    total = 0
    for i, data_object_1_label in enumerate(clustering):
        for j, data_object_2_label in enumerate(clustering):
            if i != j:
                if data_object_1_label == data_object_2_label and ground_truth_clustering[i] != ground_truth_clustering[j]:
                    total += 1
    return total

def calculate_total_false_negatives(ground_truth_clustering, clustering):
    total = 0
    for i, data_object_1_label in enumerate(clustering):
        for j, data_object_2_label in enumerate(clustering):
            if i != j:
                if data_object_1_label != data_object_2_label and ground_truth_clustering[i] == ground_truth_clustering[j]:
                    total += 1
    return total

def calculate_jaccard_coefficient(ground_truth_clustering, clustering):
    total_true_positives = calculate_total_true_positives(ground_truth_clustering, clustering)
    total_false_positives = calculate_total_false_positives(ground_truth_clustering, clustering)
    total_false_negatives = calculate_total_false_negatives(ground_truth_clustering, clustering)
    return total_true_positives / (total_true_positives + total_false_positives + total_false_negatives)
