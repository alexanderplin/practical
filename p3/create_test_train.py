import csv
import numpy as np
test_train_reader = csv.reader(open('train.csv'))
next(test_train_reader,None)
seen_users = {}

train_train = []
train_test = []
test_count = 0

for idx,(user_id,artist_id,plays) in enumerate(test_train_reader):
    if idx % 1000 == 0:
        print idx
    if seen_users.get(user_id,None)==None:
        seen_users[user_id] = 1
        train_test += [[test_count,user_id,artist_id,plays]]
        test_count += 1
    else:
        train_train += [[user_id,artist_id,plays]]

np.savetxt('train_test.csv', train_test, fmt=['%s','%s','%s','%s'], delimiter=',', header='Id,user,artist,plays', comments='')
np.savetxt('train_train.csv', train_train, fmt=['%s','%s','%s'], delimiter=',', header='user,artist,plays', comments='')
np.savetxt('train_test_no_y.csv', np.array(train_test)[:,:-1], fmt=['%s','%s', '%s'], delimiter=',', header='Id,user,artist', comments='')
