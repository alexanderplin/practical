import scipy.sparse as sparse
from sklearn.cluster import MiniBatchKMeans
import time
import csv
import numpy as np
from sklearn.model_selection import KFold

sparse_matrix = sparse.load_npz("sparse-users.npz")

label_reader = csv.reader(open('col_labels_index.csv'))
next(label_reader, None)
artist = {}
for row in label_reader:
   k, v = row
   artist[k] = v

user_reader = csv.reader(open('user-ids.csv'))
user = {}
for id_key, row in enumerate(user_reader):
    k = row[0]
    user[k] = id_key

test = csv.reader((open('test.csv')))
next(test, None)
test_user_artist = {}
test_count = 0
for i, row in enumerate(test):
    test_count += 1
    if test_user_artist.get(row[1]) == None:
    	test_user_artist[row[1]] = {row[0]: row[2]}
    else:
    	test_user_artist[row[1]][row[0]] = row[2]

num_clusters = 1000
K = MiniBatchKMeans(n_clusters=num_clusters)
K.fit(sparse_matrix)
results = np.zeros(test_count)

clusters = {}
for i,users in enumerate(K.labels_):
    if clusters.get(users, None) == None:
        clusters[users] = [i]
    else:
        clusters[users].append(i)

cluster_medians = np.zeros((num_clusters, len(artist)))
for i, (cluster_id, indexes) in enumerate(clusters.iteritems()):
    hallo = sparse_matrix[indexes].todense()
    hallo = hallo.astype('float')
    hallo[hallo == 0] = 'nan'
    median = np.nanmedian(hallo, axis=0).reshape(-1,)
    cluster_medians[i] = median[242:]

for test_user_id, dict_artist in test_user_artist.iteritems():
    # lookup user in cluster
    # lookup index of user
    test_user_index = user[test_user_id]
    # lookup cluster
    test_user_cluster = K.labels_[test_user_index]
    for num_id, artist_id in dict_artist.iteritems():
        num_id = int(num_id)-1
        artist_index = int(artist[artist_id])
        res = cluster_medians[test_user_cluster][artist_index]
        results[num_id] = res

results = np.nan_to_num(results).reshape(-1, 1)
indices = np.array(range(1, test_count + 1)).reshape(-1, 1)
print np.sum(np.isnan(results))
print indices.shape
final_results = np.concatenate((indices, results), axis=1)
print final_results.shape
np.savetxt('results1.txt', final_results, fmt=['%u','%f'], delimiter=',', header='Id,plays', comments='')
#
# print results[949380-1]
# KFold(n_splits=5, random_state=None, shuffle=False)
# for train_index, test_index in kf.split(sparse_matrix):
#     X_train, X_test = sparse_matrix[train_index], sparse_matrix[test_index]
#     K = MiniBatchKMeans(n_clusters=50)
#     K.fit(X_train)
#
#
#
# print K.labels_
# print K.cluster_centers_
# len(K.cluster_centers_[0])
