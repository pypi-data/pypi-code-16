import numpy as np

def euclidean_distance(a, b):
    subtracted_elements_squared = np.power(np.subtract(a, b), 2)
    elements_total = np.sum(subtracted_elements_squared)
    return np.sqrt(elements_total)

def calculate_centroids(data_objects, assignments):
    clusters = np.unique(assignments)
    centroids = np.zeros((clusters.size, data_objects.shape[1]))
    for i, cluster in enumerate(clusters):
        cluster_data_objects = data_objects[assignments == cluster]
        centroids[i] = np.divide(np.sum(cluster_data_objects, axis=0), cluster_data_objects.shape[0])
    return centroids

def assign_to_centroids(data_objects, centroids):
    assignments = np.empty((data_objects.shape[0]), dtype=int)
    for i, data_object in enumerate(data_objects):
        closest_centroid = 0
        distance_from_closest = euclidean_distance(data_object, centroids[0])
        for j, centroid in enumerate(centroids):
            distance = euclidean_distance(data_object, centroid)
            if distance < distance_from_closest:
                closest_centroid = j
                distance_from_closest = distance
        assignments[i] = closest_centroid
    return assignments

def kmeans(data_objects, k, iterations):
    centroids = np.zeros((0, np.size(data_objects, 1)))
    # Pick the original centroids from the data objects
    for i in range(k):
        centroids = np.append(centroids, [data_objects[np.random.randint(0, np.size(data_objects, 0))]], axis=0)
    # Make initial assignments
    assignments = assign_to_centroids(data_objects, centroids)
    for i in range(iterations):
        updated_centroids = calculate_centroids(data_objects, assignments)
        assignments = assign_to_centroids(data_objects, updated_centroids)
    return assignments
