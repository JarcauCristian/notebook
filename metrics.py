import numpy as np

def mean_index_adequacy(points: np.ndarray, labels: np.ndarray) -> float:
    K = len(np.unique(labels))  # number of clusters
    sum_squared_distances = 0
    
    for k in np.unique(labels):
        cluster_points = points[labels == k]
        cluster_centroid = np.mean(cluster_points, axis=0)
        sum_squared_distances += np.sum((cluster_points - cluster_centroid) ** 2)
    
    MIA = np.sqrt(sum_squared_distances / K)
    return round(MIA, 2)

def clustering_dispersion_indicator(points: np.ndarray, labels: np.ndarray) -> float:
    # Calculate the overall centroid
    overall_centroid = np.mean(points, axis=0)
    
    # Calculate d_bar(C), the average distance of all points to the overall centroid
    d_bar_C = np.mean(np.sqrt(np.sum((points - overall_centroid) ** 2, axis=1)))
    
    # Calculate d(L(k)) for each cluster k and their squared differences from d_bar(C)
    squared_diffs = []
    for k in np.unique(labels):
        cluster_points = points[labels == k]
        cluster_centroid = np.mean(cluster_points, axis=0)
        d_L_k = np.mean(np.sqrt(np.sum((cluster_points - cluster_centroid) ** 2, axis=1)))
        squared_diffs.append((d_bar_C - d_L_k) ** 2)
    
    # Compute the CDI
    CDI = 1 / d_bar_C * np.sqrt(np.sum(squared_diffs) / len(squared_diffs))
    return round(CDI, 2)

def variance_ratio_criterion(points: np.ndarray, labels: np.ndarray) -> float:
    M = len(points)  # total number of points
    overall_centroid = np.mean(points, axis=0)
    d_bar_squared_L = np.mean(np.sum((points - overall_centroid) ** 2, axis=1))

    W = 0
    for k in np.unique(labels):
        cluster_points = points[labels == k]
        n_k = len(cluster_points)  # number of elements in cluster k
        cluster_centroid = np.mean(cluster_points, axis=0)
        d_bar_squared_L_k = np.mean(np.sum((cluster_points - cluster_centroid) ** 2, axis=1))
        W += (n_k - 1) * (1 - (n_k / M) * (d_bar_squared_L_k / d_bar_squared_L))
    
    K = len(np.unique(labels))  # number of clusters
    VRC = (1 / M) * (1 + (W / (K - 1))) * (1 - (W / (M - K)))**(-1)

    return round(VRC, 2)