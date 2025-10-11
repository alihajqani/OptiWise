# ===== IMPORTS & DEPENDENCIES =====
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn_extra.cluster import KMedoids
from sklearn.metrics import silhouette_score, davies_bouldin_score

# --- Private helper function for pre-processing ---
def _preprocess_data(features_df: pd.DataFrame):
    """Internal function to scale and apply PCA to features."""
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features_df)
    n_samples, n_features = features_df.shape
    n_components = min(5, n_features, n_samples)
    pca = PCA(n_components=n_components)
    pca_features = pca.fit_transform(scaled_features)
    return pca_features

# --- Main function to get all comparison results ---
def get_all_clustering_results(df: pd.DataFrame, selected_features: list):
    """
    Runs all clustering algorithms for all k values and returns a list of all results.
    """
    # 1. Select and Validate Data
    features_df = df[selected_features]
    if not all(features_df.dtypes.apply(pd.api.types.is_numeric_dtype)):
        raise ValueError("تمام ستون‌های انتخاب شده باید عددی باشند.")

    # 2. Pre-process Data
    pca_features = _preprocess_data(features_df)
    
    # 3. Setup and Run Competition
    n_samples = len(features_df)
    max_k = min(10, n_samples - 1)
    if max_k < 2: raise ValueError("تعداد نمونه‌ها برای خوشه‌بندی کافی نیست (حداقل ۲).")
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
            if len(set(labels)) < 2: continue

            all_results.append({
                'algorithm': alg_name,
                'k': k,
                'silhouette': silhouette_score(pca_features, labels),
                'davies_bouldin': davies_bouldin_score(pca_features, labels)
            })
    
    return all_results

# --- Function to run a single selected model ---
def run_single_clustering_model(df: pd.DataFrame, selected_features: list, algorithm_name: str, k: int):
    """
    Runs a single, specific clustering model and returns the labels for each DMU.
    """
    # 1. Select and Pre-process Data
    features_df = df[selected_features]
    pca_features = _preprocess_data(features_df)

    # 2. Initialize the selected algorithm
    if algorithm_name == 'K-Means':
        model = KMeans(n_clusters=k, random_state=42, n_init='auto')
    elif algorithm_name == 'K-Medoids':
        model = KMedoids(n_clusters=k, random_state=42)
    elif algorithm_name == 'Ward':
        model = AgglomerativeClustering(n_clusters=k)
    else:
        raise ValueError(f"الگوریتم '{algorithm_name}' پشتیبانی نمی‌شود.")

    # 3. Fit and return labels
    labels = model.fit_predict(pca_features)
    return labels.tolist()