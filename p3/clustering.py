import scipy.sparse as sparse
from sklearn.cluster import k_means as KMeans
import time

if __name__ == '__main__':
    sparse_matrix = sparse.load_npz("sparse-users.npz")
    print "Finishing loading sparse matrix"
    start = time.time()
    K = KMeans(sparse_matrix, n_clusters=50, n_jobs=4, verbose = True)
    print time.time()-start
