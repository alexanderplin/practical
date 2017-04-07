import json
from urllib2 import Request, urlopen, URLError
import pprint

artist_ids_train = {'0103c1cc-4a09-4a5d-a344-56ad99a77193': 47,
  '01d3c51b-9b98-418a-8d8e-37f6fab59d8c': 136,
  '0383dadf-2a4e-4d10-a46a-e9e041da8eb3': 240,
  '3e55d51d-687f-4a9d-af96-2fabccf802e5': 72,
  '3eb72791-6322-466b-87d3-24d74901eb2d': 83,
  '3f2a12e9-6398-42fd-b257-2f6abd4aa5fc': 54,
  '67f66c07-6e61-4026-ade5-7e782fad3a5d': 84,
  '7113aab7-628f-4050-ae49-dbecac110ca8': 70,
  '85af0709-95db-4fbc-801a-120e9f4766d0': 66,
  '8bfac288-ccc5-448d-9573-c33ea2aa5c30': 50,
  '980ee2d8-2ee9-407b-b48e-48360fbc7437': 60,
  'a0327dc2-dc76-44d5-aec6-47cd2dff1469': 23,
  'b10bbbfc-cf9e-42e0-be17-e2c3e1d2600d': 51,
  'b616019a-810c-4b05-a558-ad8406f225ff': 15,
  'ba853904-ae25-4ebb-89d6-c44cfbd71bd2': 33,
  'cba77ba2-862d-4cee-a8f6-d3f9daf7211c': 13,
  'cd8c5019-5d75-4d5c-bc28-e1e26a7dd5c8': 32,
  'd735497b-25f9-4503-8fb5-f50150730c18': 40,
  'e11051f9-0098-41aa-9edb-8dacd8f1c6b5': 41,
  'ebfc1398-8d96-47e3-82c3-f782abcdb13d': 32}

artist_ids_test = ['144ef525-85e9-40c3-8335-02c32d0861f3',
  '1723c867-d5c5-4a61-a40b-8c04fa7acf1b',
  '28503ab7-8bf2-4666-a7bd-2644bfc7cb1d',
  '319b1175-ced9-438f-986b-9239c3edd92d',
  '49018fd2-95ef-4f7e-92bb-813159909314',
  '6e17c8d1-2493-46cc-88d4-64b848a32593',
  '82eb8936-7bf6-4577-8320-a2639465206d',
  'a3cb23fc-acd3-4ce0-8f36-1e5aa6a18432',
  'cc197bad-dc9c-440d-a5b5-d52ba2e14234',
  'cc7d4686-ea02-45fd-956e-94c1a322558c',
  'd43d12a1-2dc9-4257-a2fd-0a3bb1081b86',
  'ea4dfa26-f633-4da6-a52a-f49ea4897b58',
  'fbb375f9-48bb-4635-824e-4120273b3ba7',
  'ffb2d3e3-a4cc-48cf-8fb0-f2f846e9d7b9']

for artist_id in artist_ids_test:
	root_url = 'http://musicbrainz.org/ws/2/artist/'
	request = Request(root_url + artist_id + '?inc=tags+ratings&fmt=json')
	while True:
		try:
			response = urlopen(request)
			test = response.read()
			pprint.pprint(json.loads(test)['name'])
			pprint.pprint(json.loads(test)['tags'])
			break
		except URLError, e:
		    print 'None. Got an error code:', e