import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn_extra.cluster import KMedoids
from sklearn.metrics import silhouette_score, davies_bouldin_score


def _preprocess_data(features_df: pd.DataFrame):
    """Scale features and apply PCA for dimensionality reduction."""
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features_df)
    n_samples, n_features = features_df.shape
    n_components = min(5, n_features, n_samples)
    pca = PCA(n_components=n_components)
    pca_features = pca.fit_transform(scaled_features)
    return pca_features


def get_all_clustering_results(df: pd.DataFrame, selected_features: list):
    """
    Run clustering algorithms across k values and return comparison metrics.
    """
    features_df = df[selected_features]
    if not all(features_df.dtypes.apply(pd.api.types.is_numeric_dtype)):
        raise ValueError("تمام ستون‌های انتخاب شده باید عددی باشند.")

    pca_features = _preprocess_data(features_df)

    n_samples = len(features_df)
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
            if isinstance(algorithm, AgglomerativeClustering):
                algorithm.n_clusters = k
            else:
                algorithm.n_clusters = k

            labels = algorithm.fit_predict(pca_features)
            if len(set(labels)) < 2:
                continue

            all_results.append({
                'algorithm': alg_name,
                'k': k,
                'silhouette': silhouette_score(pca_features, labels),
                'davies_bouldin': davies_bouldin_score(pca_features, labels)
            })

    return all_results


def run_single_clustering_model(df: pd.DataFrame, selected_features: list, algorithm_name: str, k: int):
    """
    Run a specific clustering model and return labels for each DMU.
    """
    features_df = df[selected_features]
    pca_features = _preprocess_data(features_df)

    if algorithm_name == 'K-Means':
        model = KMeans(n_clusters=k, random_state=42, n_init='auto')
    elif algorithm_name == 'K-Medoids':
        model = KMedoids(n_clusters=k, random_state=42)
    elif algorithm_name == 'Ward':
        model = AgglomerativeClustering(n_clusters=k)
    else:
        raise ValueError(f"الگوریتم '{algorithm_name}' پشتیبانی نمی‌شود.")

    labels = model.fit_predict(pca_features)
    return labels.tolist()