import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import json
from collections import Counter
from collections import defaultdict
import scipy.sparse as sp
from scipy.stats import percentileofscore, scoreatpercentile
from sklearn.cluster import MiniBatchKMeans, KMeans
from sklearn.metrics import silhouette_score
from scipy import stats
import numpy as np

artist_index_to_id_reader = csv.reader(open('col_labels_index.csv'))
next(artist_index_to_id_reader, None)
# maps artist_index to id
artist_index_to_id = {}
# maps artist_id to artist_index
artist_id_to_index = {}
for row in artist_index_to_id_reader:
   k, v = row
   artist_index_to_id[int(v)] = k
   artist_id_to_index[k] = int(v)

user_artists_reader = csv.reader(open('train_train.csv'))
next(user_artists_reader, None)
# maps user_id to list of artist_ids
user_artists = defaultdict(list)
# maps artist_id to list of plays
artist_plays = defaultdict(list)
user_id_to_plays_temp = defaultdict(list)

for count,(user_id, artist_id, plays) in enumerate(user_artists_reader):
    plays = int(plays)
    if user_artists.get(user_id, None) == None:
        user_artists[user_id]= {artist_id : plays}
    else:
        user_artists[user_id][artist_id] = plays
    user_id_to_plays_temp[user_id].append(plays)
    artist_plays[artist_id].append(plays)

user_percentiles = defaultdict(list)
for user_id,plays in user_id_to_plays_temp.iteritems():
    user_percentiles[user_id] = np.percentile(plays,range(1,101))

artist_percentiles = defaultdict(list)
total_plays = []
artist_modes = defaultdict(int)
for artist_id, plays in artist_plays.iteritems():
    artist_percentiles[artist_id] = np.percentile(plays,range(1,101))
    artist_modes[artist_id] = stats.mode(plays)
    total_plays+=plays
global_median = np.median(total_plays)

artist_id_to_genre = json.load(open("artist_id_to_genre_spot"))
artist_id_to_popularity = json.load(open("artist_id_to_popularity_spot"))

# artist_id_to_genre = json.load(open("artist_id_to_genre"))

# key: genre, value = artist_index_list
genre_matrix = defaultdict(list)
# keeps track of genre_ids
genre_id_to_genre = defaultdict(str)
genre_genre_to_id = defaultdict(int)
genre_count = 0
genre_name_to_count = defaultdict(int)
artist_id_to_name = defaultdict(str)
# artist_id_lookup = csv.reader(open('artists/artists.csv'))
# next(artist_id_lookup, None)
# for artist_index, row in enumerate(artist_id_lookup):
#     artist_id = row[0]
#     artist_id_to_name[artist_id] = row[1]
#     d = Counter(artist_id_to_genre.get(artist_id,{}))
#     # get the top three genres
#     for genre,_ in d.most_common(3):
#         genre_name_to_count[genre] += 1
#         # keeps track of genres
#         if genre not in genre_genre_to_id:
#             genre_id_to_genre[genre_count] = genre
#             genre_genre_to_id[genre] = genre_count
#             genre_count+=1
#         genre_matrix[genre_genre_to_id[genre]].append(artist_index)


artist_id_lookup_reader = csv.reader(open('artists/artists.csv'))
next(artist_id_lookup_reader, None)
for artist_index, row in enumerate(artist_id_lookup_reader):
    artist_id = row[0]
    artist_id_to_name[artist_id] = row[1]
    # get the top three genres
    for genre in artist_id_to_genre[artist_id]:
        genre_name_to_count[genre] += 1
        # keeps track of genres
        if genre not in genre_genre_to_id:
            genre_id_to_genre[genre_count] = genre
            genre_genre_to_id[genre] = genre_count
            genre_count+=1
        genre_matrix[genre_genre_to_id[genre]].append(artist_index)

# create sparse matrix for clustering
len_artists = 2000
mat = sp.dok_matrix((genre_count,len_artists), dtype=np.int8)
for genre_id, artist_ids in genre_matrix.items():
    mat[genre_id,artist_ids] = 1
data = mat.transpose().tocsr()
# best number of clusters to consider
# sill_scores = []
# for num_clusters in range(25,40):
#     # clustering
#     K = KMeans(n_clusters=num_clusters)
#     K.fit(data)
#     sill_scores += [silhouette_score(data, K.labels_)]
# num_clusters = np.argmax(sill_scores)+25
# print "Best # Cluster: ",num_clusters
K = KMeans(n_clusters = 5)
K.fit(data)

# iterate through test and make predictions
test_reader = csv.reader(open('train_test_no_y.csv'))
next(test_reader, None)
final_result = []
for index_id, user_id, artist_id in test_reader:
    if int(index_id) % 1000 == 0:
        print index_id
    # look for which cluster artist is in
    artist_index = artist_id_to_index[artist_id]
    cluster_of_artist = K.labels_[artist_index]

    # get all other artist indicies in that cluster
    artists_in_current_cluster = [i for i,x in enumerate(K.labels_) if x == cluster_of_artist]

    # all the artists this user has listened to
    user_artist_history = [artist_id_to_index[x] for x in user_artists[user_id].keys()]
    # intersection of artist in current cluster and user history
    artists_in_cluster_and_user =  list(set(user_artist_history).intersection(set(artists_in_current_cluster)))

    percentiles = []
    popularity = []
    for cluster_artist_index in artists_in_cluster_and_user:
        # plays of current artist
        current_user_plays = user_artists[user_id][artist_index_to_id[cluster_artist_index]]

        # calculate percentile of play compared to all other users
        # calc = percentileofscore(np.array(artist_plays[artist_index_to_id[cluster_artist_index]]), current_user_plays, kind='weak')

        artist_percentile_cache = artist_percentiles[artist_index_to_id[cluster_artist_index]]

        # right_bin_index is effectively percentile +- 1
        right_bin_index = np.digitize(current_user_plays, artist_percentile_cache).astype(int).item(0)
        # keep percentile inbound
        if right_bin_index == 100:
            right_bin_index = 99
        percentiles += [right_bin_index]
        # get popularity of each artist
        popularity += [artist_id_to_popularity[artist_index_to_id[cluster_artist_index]]]
    popularity = np.array(popularity)
    # if no percentiles (no artists of user history in the artist we are trying to predict on's cluster, use median)
    flag = False
    if percentiles == []:
        flag = True #(we can also use cluster median)
    # average percentile of plays of artists in current cluster
    else:
        percentile_mean = int(np.round(np.average(percentiles,weights = popularity)))
    if percentile_mean > 50:
        percentile_mean = ((percentile_mean-50) * (10/40)) + 50
    elif percentile_mean < 50:
        percentile_mean = 50-((50-percentile_mean) * (10/40))
    # get the value of the percentile based on user play percentile average
    unknown_artist_plays_prediction = global_median if flag else user_percentiles[user_id][percentile_mean]

    final_result += [[int(index_id), unknown_artist_plays_prediction]]
np.savetxt('results_valid_cluster.csv', final_result, fmt=['%d','%f'], delimiter=',', header='Id,plays', comments='')
