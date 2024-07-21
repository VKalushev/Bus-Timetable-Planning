import datetime


# Get timestamp as a string
def get_timestamp():
    return '{date:%Y-%m-%dT%H:%M:%S}'.format(date=datetime.datetime.now())

# Convert timestamp to string
def get_datetime(timestamp):
    return datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")

# Get days since the date
def get_days_since(date):
    difference = datetime.datetime.now() - date
    return difference.days
