"""
Configuration of output report
"""

# How many top n contributors show in the tables summarizing contributors activity
# and productivity
TOP_N_CONTRIBUTORS: int = 10

# Minimal number of insertions and deletions for insertions / deletions ratio stats - for contributors with
# low activity number are exceptionally high (for example 5 insertions and 0 deletions the ratio
# is infinite)
MIN_INSERTIONS = 50
MIN_DELETIONS = 10

# How many top words show in the words frequency tables
TOP_N_WORDS = 15

# How many top n days shows in the table summarizing relation
# between number of commits and time to nearest merge
TOP_N_DAYS_TIME_TO_MERGE = 20

# Insertions deletions outliers border as number of standard
# deviations added to the mean value
SD_OUTLIERS_BORDER = 3

# Number of bins for histograms showing number of insertions and
# deletions. Set 'auto' if you would like seaborn to set it
# in an automated way
HISTOGRAM_BINS_NUM = 50
