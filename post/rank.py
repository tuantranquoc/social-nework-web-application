from math import sqrt
from datetime import datetime, timedelta
from math import log


def _confidence(ups, downs):
    n = ups + downs
    if n == 0:
        return 0

    z = 1.281551565545
    p = float(ups) / n

    left = p + 1 / (2 * n) * z * z
    right = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    under = 1 + 1 / n * z * z

    return (left - right) / under


def confidence(ups, downs):
    if ups + downs == 0:
        return 0
    else:
        return _confidence(ups, downs)


epoch = datetime(1970, 1, 1)


def epoch_seconds(date):
    naive = date.replace(tzinfo=None)
    td = naive - epoch
    return td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000)


def score(ups, downs):
    return ups - downs

# we currently using this function for hot frontpage
# so how best work
# hot ranking algorithm
def hot(ups, downs, date):
    s = score(ups, downs)
    order = log(max(abs(s), 1), 10)
    sign = 1 if s > 0 else -1 if s < 0 else 0
    seconds = epoch_seconds(date) - 1134028003
    return round(sign * order + seconds / 45000, 7)

