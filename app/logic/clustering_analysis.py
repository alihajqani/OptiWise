# In app/logic/clustering_analysis.py

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def run_clustering_pipeline(file_path):
    """
    Takes the path to an Excel file and runs the full clustering pipeline.
    Returns a dictionary containing the results.
    """
    # 1. Load data using pandas. Assume the first sheet is the data.
    df = pd.read_excel(file_path)

    if df.shape[1] < 2:
        raise ValueError("فایل اکسل باید حداقل دو ستون داشته باشد (نام واحد و یک شاخص).")
    
    # 2. Separate identifiers (DMUs) from features
    dmu_names = df.iloc[:, 0]
    features = df.iloc[:, 1:].select_dtypes(include=['number']) # Only use numeric columns
    
    if features.shape[1] < 1:
        raise ValueError("هیچ ستون عددی برای تحلیل پیدا نشد.")

    # 3. Pre-processing: Normalization (scaling)
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # 4. Pre-processing: PCA (dimensionality reduction)
    # The document suggests reducing to 5 components if possible.
    n_components = min(5, features.shape[1], features.shape[0])
    pca = PCA(n_components=n_components)
    pca_features = pca.fit_transform(scaled_features)

    # 5. Find the optimal number of clusters (k) using Silhouette Score
    best_score = -1
    best_k = -1
    best_labels = None
    
    # K cannot be greater than the number of samples
    max_k = min(10, len(dmu_names) - 1)
    if max_k < 2:
        raise ValueError("تعداد واحدهای تصمیم‌گیرنده برای خوشه‌بندی کافی نیست (حداقل ۲ واحد نیاز است).")

    for k in range(2, max_k + 1):
        # Using n_init='auto' is the modern default for KMeans
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        labels = kmeans.fit_predict(pca_features)
        score = silhouette_score(pca_features, labels)
        
        if score > best_score:
            best_score = score
            best_k = k
            best_labels = labels
            
    # 6. Prepare and return results
    results = {
        'dmu_names': dmu_names.tolist(),
        'labels': best_labels.tolist(),
        'best_k': best_k,
        'best_score': best_score,
        'algorithm': 'K-Means'
    }

    return results