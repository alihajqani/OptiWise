# ===== IMPORTS & DEPENDENCIES =====
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn_extra.cluster import KMedoids
from pyclustering.cluster.kmedians import kmedians
from sklearn.metrics import silhouette_score, davies_bouldin_score
import warnings

# Suppress ConvergenceWarning from sklearn KMeans if it appears
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


# ===== CORE BUSINESS LOGIC =====
def _preprocess_data(features_df: pd.DataFrame):
    """
    Implements the definitive "Scenario B" preprocessing methodology.
    This method was chosen as it produced the cluster structure most similar
    to the reference document's visual output (highest ARI score).
    
    The process is as follows:
    1. Scale the data using StandardScaler.
    2. Apply standard PCA (no rotation) to reduce dimensionality to 5 components.
    """
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features_df)
    
    n_components = 5
    n_samples, n_features = features_df.shape
    if n_components >= n_features:
        n_components = n_features - 1 if n_features > 1 else 1

    pca = PCA(n_components=n_components, random_state=42)
    pca_features = pca.fit_transform(scaled_features)
    
    return pca_features


def get_all_clustering_results(df: pd.DataFrame, selected_features: list):
    """
    Run all clustering algorithms (K-Means, K-Medoids, Ward, and K-Median) across a range of k values
    using the definitive "Scenario B" preprocessing method.
    """
    features_df = df[selected_features]
    if not all(features_df.dtypes.apply(pd.api.types.is_numeric_dtype)):
        raise ValueError("تمام ستون‌های انتخاب شده باید عددی باشند.")

    processed_features = _preprocess_data(features_df)

    n_samples = len(features_df)
    max_k = min(10, n_samples - 1)
    if max_k < 2:
        raise ValueError("تعداد نمونه‌ها برای خوشه‌بندی کافی نیست (حداقل ۲).")
    k_range = range(2, max_k + 1)

    # --- K-Median is NOT added to this dictionary due to its different API ---
    algorithms_to_test = {
        'K-Means': KMeans(random_state=42, n_init='auto'),
        'K-Medoids': KMedoids(random_state=42),
        'Ward': AgglomerativeClustering()
    }

    all_results = []

    for k in k_range:
        # --- Run scikit-learn compatible algorithms ---
        for alg_name, algorithm in algorithms_to_test.items():
            if isinstance(algorithm, AgglomerativeClustering):
                algorithm.n_clusters = k
            else:
                algorithm.n_clusters = k
            try:
                labels = algorithm.fit_predict(processed_features)
                if len(set(labels)) < 2: continue
                all_results.append({
                    'algorithm': alg_name, 'k': k,
                    'silhouette': silhouette_score(processed_features, labels),
                    'davies_bouldin': davies_bouldin_score(processed_features, labels)
                })
            except Exception: continue
        
        # --- Run K-Median separately ---
        try:
            # For reproducibility, we seed the initial medians
            np.random.seed(42)
            initial_medians_indices = np.random.choice(n_samples, k, replace=False)
            initial_medians = processed_features[initial_medians_indices]
            
            kmedians_instance = kmedians(processed_features, initial_medians)
            kmedians_instance.process()
            clusters = kmedians_instance.get_clusters()
            
            # Convert pyclustering output to a standard label array
            labels = np.zeros(n_samples, dtype=int)
            for i, cluster in enumerate(clusters):
                labels[cluster] = i
            
            if len(set(labels)) > 1:
                all_results.append({
                    'algorithm': "K-Median", 'k': k,
                    'silhouette': silhouette_score(processed_features, labels),
                    'davies_bouldin': davies_bouldin_score(processed_features, labels)
                })
        except Exception: continue

    return all_results


def run_single_clustering_model(df: pd.DataFrame, selected_features: list, algorithm_name: str, k: int):
    """
    Run a specific clustering model for a given k, using the definitive "Scenario B" preprocessing.
    Now includes support for K-Median.
    """
    features_df = df[selected_features]
    processed_features = _preprocess_data(features_df)
    n_samples = len(features_df)

    if algorithm_name == 'K-Means':
        model = KMeans(n_clusters=k, random_state=42, n_init='auto')
        labels = model.fit_predict(processed_features)
    elif algorithm_name == 'K-Medoids':
        model = KMedoids(n_clusters=k, random_state=42)
        labels = model.fit_predict(processed_features)
    elif algorithm_name == 'Ward':
        model = AgglomerativeClustering(n_clusters=k)
        labels = model.fit_predict(processed_features)
    elif algorithm_name == 'K-Median':
        # For reproducibility, we seed the initial medians
        np.random.seed(42)
        initial_medians_indices = np.random.choice(n_samples, k, replace=False)
        initial_medians = processed_features[initial_medians_indices]
        
        kmedians_instance = kmedians(processed_features, initial_medians)
        kmedians_instance.process()
        clusters = kmedians_instance.get_clusters()
        
        # Convert pyclustering output to a standard label array
        labels = np.zeros(n_samples, dtype=int)
        for i, cluster in enumerate(clusters):
            labels[cluster] = i
    else:
        raise ValueError(f"الگوریتم '{algorithm_name}' پشتیبانی نمی‌شود.")

    return labels.tolist()