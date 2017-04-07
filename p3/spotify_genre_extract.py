import spotipy
import pprint
import csv
import json
from collections import defaultdict

sp = spotipy.Spotify()
artist_id_to_genre_reader = csv.reader(open('artists/artists.csv'))
next(artist_id_to_genre_reader, None)
# maps artist_index to id
artist_id_to_genre = defaultdict(list)
artist_id_to_popularity = defaultdict(int)
for idx, (artist_id,artist_name) in enumerate(artist_id_to_genre_reader):
    if idx % 100 == 0:
        print idx
    if artist_name == '':
        artist_id_to_genre[artist_id] = []
        continue
    try:
        result = sp.search(artist_name,type='artist')
    except Exception as e:
        print ('exception on ID: ',artist_id)
        continue
    if result['artists']['items'] == []:
        artist_id_to_genre[artist_id] = []
        continue
    # artist_id_to_genre[artist_id] = result['artists']['items'][0]['genres']
    artist_id_to_popularity[artist_id] = result['artists']['items'][0]['popularity']

# fill missing keys
for key in artist_id_to_genre.keys():
    if artist_id_to_popularity.get(key,None) == None:
        print "missing id: ",key
        artist_id_to_popularity[key] = 50

# result = sp.search(artist_id_to_name['e664d1cd-23ab-48d5-b8fa-e98485daa5be'],type='artist')
# artist_id_to_popularity['e664d1cd-23ab-48d5-b8fa-e98485daa5be'] = result['artists']['items'][0]['popularity']

json.dump(artist_id_to_popularity,open("artist_id_to_popularity_spot",'w'))
