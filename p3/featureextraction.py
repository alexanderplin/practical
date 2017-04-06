import musicbrainzngs
import csv
import json
from musicbrainzngs.musicbrainz import WebServiceError

musicbrainzngs.set_useragent("python-musicbrainzngs-example","0.1","https://github.com/alastair/python-musicbrainzngs/",)
reader_artist = csv.reader(open('artists/artists.csv'))
next(reader_artist, None)
artists = {}
for idx,row in enumerate(reader_artist):
    print idx
    if row[1] == "":
        continue
    while(True):
        try:
            result = musicbrainzngs.get_artist_by_id(row[0],includes=["tags", "ratings"])
        except Exception as exc:
            print "Error with artist ID: ",row[0], " Message: ", exc
            break
        else:
            # handle get_location
            location = result["artist"].get("area", None)
            if location == None:
                location_name = None
            else:
                location_name = location.get("name", None)
            # handle get_tags
            tags = result['artist'].get('tag-list', None)
            if tags == None:
                tag_list = []
            else:
                tag_list = result["artist"]["tag-list"]

            artists[row[0]] = {'location':location_name, "tag-list":tag_list}
            break
print("exporting")
with open('artistdata2', 'w') as outfile:
    json.dump(artists, outfile)

# reader_train = csv.reader(open('train/train.csv'))
# train = {}
# for row in reader_train:
#     train.setdefault(row[1],1)
#
# print len(train)
#
# reader_test = csv.reader(open('test/test.csv'))
# test = {}
# for row in reader_test:
#     test.setdefault(row[2],1)
#
# print len(test)
#
# reader_profile = csv.reader(open('artists/artists.csv'))
# len_profile = sum([1 for row in reader_profile])
# print len_profile
# print sum([train.get(row[0], 0) for row in reader_profile])
