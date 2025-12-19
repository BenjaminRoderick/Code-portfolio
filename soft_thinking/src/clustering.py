import sklearn
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import numpy as np
import torch
import matplotlib.pyplot as plt
import pandas as pd
from load_embeddings import load_embedding_model

random_state = 42
n_clusters = 10

model, tokenizer = load_embedding_model(151936, 1536, "embeddings_qwen.pth", "unembeddings_qwen.pth", "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")

all_tokens = list(tokenizer.get_vocab().keys())
emb_weight = torch.load("embeddings_qwen.pth")["weight"]
all_embeddings = emb_weight.detach().cpu().numpy()
print(f"Embeddings shape: {all_embeddings.shape}")

#hdbscan, dbscan?

# #Kmeans
# kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init="auto").fit(all_embeddings)
# token_clusters = dict(zip(all_tokens, kmeans.labels_))
# print(kmeans.labels_)

# for token, label in list(token_clusters.items())[:10]:
#     print(f"Token: {token}, Cluster: {label}")

#PCA

# #Calculate the covariance matrix
# cov_matrix = np.cov(all_embeddings, rowvar=False)

# #Calculate the eigenvalues and eigenvectors
# eig_vals, eig_vecs = np.linalg.eig(cov_matrix)

# #Verification
# #Calculate the total variance
# total_var = np.var(all_embeddings, axis=0).sum()
# print(f"Total variance: {total_var:.2f}")

# #Calculate the sum of the eigenvalues
# eig_vals_sum = eig_vals.sum()
# print(f"Sum of eigenvalues: {eig_vals_sum:.2f}")

# #Calculate the proportion of variance explained by each principal component
# var_exp = eig_vals / total_var
# print(f"Proportion of variance explained by each principal component:\n{var_exp}")

# #Plot the proportion of explained variance by each particular principal component
# fig, ax = plt.subplots(1, 2, figsize=(20, 12))

# ax[0].plot(var_exp, marker="o")
# ax[0].set_xlabel("Principal component")
# ax[0].set_ylabel("Proportion of explained variance")
# ax[0].set_title("Scree plot")

# ax[1].plot(np.cumsum(var_exp), marker="o")
# ax[1].set_xlabel("Principal component")
# ax[1].set_ylabel("Cumulative sum of explained variance")
# ax[1].set_title("Cumulative scree plot")
# plt.savefig("scree_plot_pca", dpi=600, bbox_inches='tight')
# plt.show()

# pca = PCA(n_components=3)
# pca_embeddings = pca.fit_transform(all_embeddings)

# fig = plt.figure(figsize=(10, 8))
# ax = fig.add_subplot(111, projection='3d')

# ax.scatter(
#     pca_embeddings[:, 0],
#     pca_embeddings[:, 1],
#     pca_embeddings[:, 2],
#     s=5, alpha=0.5
# )

# ax.set_xlabel('PC1')
# ax.set_ylabel('PC2')
# ax.set_zlabel('PC3')
# plt.title("PCA of Token Embeddings with 3 components")
# plt.savefig("pca_3.png", dpi=600, bbox_inches='tight')
# plt.show()

# plt.figure(figsize=(10, 8))
# plt.scatter(pca_embeddings[:, 0], pca_embeddings[:, 1], s=5, alpha=0.5)
# plt.title("PCA of Token Embeddings with 2 components")
# plt.xlabel("PCA 1")
# plt.ylabel("PCA 2")
# plt.savefig("pca_2.png", dpi=600, bbox_inches='tight')
# plt.show()
