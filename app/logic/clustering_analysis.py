import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def run_clustering_pipeline(df: pd.DataFrame, dmu_column: str, selected_features: list):
    """
    Runs the clustering pipeline on the provided dataframe using only the selected features.
    
    Args:
        df (pd.DataFrame): The full dataframe loaded from the Excel file.
        dmu_column (str): The name of the column containing DMU identifiers.
        selected_features (list): A list of column names to be used for clustering.

    Returns:
        dict: A dictionary containing the clustering results.
    """
    # 1. Select the relevant data
    dmu_names = df[dmu_column]
    features_df = df[selected_features]

    # Check for non-numeric data in selected features
    if not all(features_df.dtypes.apply(pd.api.types.is_numeric_dtype)):
        raise ValueError("تمام ستون‌های انتخاب شده باید عددی باشند.")

    # 2. Pre-processing: Normalization (scaling)
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features_df)

    # 3. Pre-processing: PCA (dimensionality reduction)
    n_samples, n_features = features_df.shape
    n_components = min(5, n_features, n_samples)
    pca = PCA(n_components=n_components)
    pca_features = pca.fit_transform(scaled_features)

    # 4. Find the optimal number of clusters (k) using Silhouette Score
    best_score = -1
    best_k = -1
    best_labels = None
    
    max_k = min(10, n_samples - 1)
    if max_k < 2:
        raise ValueError("تعداد واحدهای تصمیم‌گیرنده برای خوشه‌بندی کافی نیست (حداقل ۲ واحد نیاز است).")

    for k in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        labels = kmeans.fit_predict(pca_features)
        score = silhouette_score(pca_features, labels)
        
        if score > best_score:
            best_score = score
            best_k = k
            best_labels = labels
            
    # 5. Prepare and return results
    results = {
        'dmu_names': dmu_names.tolist(),
        'labels': best_labels.tolist(),
        'best_k': best_k,
        'best_score': best_score,
        'algorithm': 'K-Means'
    }
    return results