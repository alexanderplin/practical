import numpy as np


# predictions_file = "user_median2.csv"
# validation_file = "train_test.csv"

# median: 138.89813147809986
# spotify tags: 215.20608497723825
# musicbrainz tags: ???

predictions_file = "results_valid_cluster.csv"
validation_file = "train_test.csv"

predictions=np.loadtxt(predictions_file, usecols=[1], delimiter=',',skiprows=1)
validation=np.loadtxt(validation_file, usecols=[3], delimiter=',',skiprows=1)
np.sum(np.absolute(predictions-validation))/float(len(validation))
