# ===== IMPORTS & DEPENDENCIES =====
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn_extra.cluster import KMedoids
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
    # Step 1: Scale the data to have a mean of 0 and a variance of 1.
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features_df)
    
    # Step 2: Apply PCA to reduce dimensions to 5.
    # 'random_state' is set for reproducibility.
    n_components = 5
    
    # Ensure n_components is valid for the given data
    n_samples, n_features = features_df.shape
    if n_components >= n_features:
        # Fallback for datasets with fewer features than 5
        n_components = n_features - 1 if n_features > 1 else 1

    pca = PCA(n_components=n_components, random_state=42)
    pca_features = pca.fit_transform(scaled_features)
    
    return pca_features


def get_all_clustering_results(df: pd.DataFrame, selected_features: list):
    """
    Run all clustering algorithms (K-Means, K-Medoids, Ward) across a range of k values
    using the definitive "Scenario B" preprocessing method.
    """
    features_df = df[selected_features]
    if not all(features_df.dtypes.apply(pd.api.types.is_numeric_dtype)):
        raise ValueError("تمام ستون‌های انتخاب شده باید عددی باشند.")

    # Apply the final, Scenario B preprocessing
    processed_features = _preprocess_data(features_df)

    n_samples = len(features_df)
    # Ensure k is not too large for the number of samples
    max_k = min(10, n_samples - 1)
    if max_k < 2:
        raise ValueError("تعداد نمونه‌ها برای خوشه‌بندی کافی نیست (حداقل ۲).")
    k_range = range(2, max_k + 1)

    algorithms_to_test = {
        'K-Means': KMeans(random_state=42, n_init='auto'),
        'K-Medoids': KMedoids(random_state=42),
        'Ward': AgglomerativeClustering()
    }

    all_results = []

    for alg_name, algorithm in algorithms_to_test.items():
        for k in k_range:
            # Set the number of clusters for the current iteration
            if isinstance(algorithm, AgglomerativeClustering):
                algorithm.n_clusters = k
            else:
                algorithm.n_clusters = k

            try:
                labels = algorithm.fit_predict(processed_features)
                
                # Scores can only be calculated if more than one cluster is found
                if len(set(labels)) < 2:
                    continue

                all_results.append({
                    'algorithm': alg_name,
                    'k': k,
                    'silhouette': silhouette_score(processed_features, labels),
                    'davies_bouldin': davies_bouldin_score(processed_features, labels)
                })
            except Exception:
                # In case a specific combination fails, just skip it.
                continue

    return all_results


def run_single_clustering_model(df: pd.DataFrame, selected_features: list, algorithm_name: str, k: int):
    """
    Run a specific clustering model (K-Means, K-Medoids, or Ward) for a given k,
    using the definitive "Scenario B" preprocessing method.
    """
    features_df = df[selected_features]
    processed_features = _preprocess_data(features_df)

    if algorithm_name == 'K-Means':
        model = KMeans(n_clusters=k, random_state=42, n_init='auto')
    elif algorithm_name == 'K-Medoids':
        model = KMedoids(n_clusters=k, random_state=42)
    elif algorithm_name == 'Ward':
        model = AgglomerativeClustering(n_clusters=k)
    else:
        raise ValueError(f"الگوریتم '{algorithm_name}' پشتیبانی نمی‌شود.")

    labels = model.fit_predict(processed_features)
    return labels.tolist()