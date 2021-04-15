"""
Calculate Theil's uncertainty between two columns of a pandas dataframe

This work comes from [The Search For Categorical Correlation]
(https://towardsdatascience.com/the-search-for-categorical-correlation-a1cf7f1888c9)
and [The Dython Library](https://github.com/shakedzy/dython)
but I have abstracted and simplified it here for my use
"""

import math
from collections import Counter

from scipy.stats import entropy


def handle_na(x):
    """
    Remove NaN in the data.
    :param x: a pandas column
    :return: the column without NaNs
    """
    # return x.dropna()
    return x.fillna("")


def conditional_entropy(x, y, log_base: float = math.e):
    """
    Calculates the conditional entropy of x given y: S(x|y)

    Wikipedia: https://en.wikipedia.org/wiki/Conditional_entropy

    Please see [The Dython Library](https://github.com/shakedzy/dython)
    for attribution and source

    Parameters:
    -----------
    x : list / NumPy ndarray / Pandas Series
        A sequence of measurements
    y : list / NumPy ndarray / Pandas Series
        A sequence of measurements
    log_base: float, default = e
        specifying base for calculating entropy. Default is base e.

    Returns:
    --------
    float
    """

    # remove NaN
    x = handle_na(x)
    y = handle_na(y)

    y_counter = Counter(y)
    xy_counter = Counter(list(zip(x, y)))
    total_occurrences = sum(y_counter.values())
    entrop = 0.0
    for xy in xy_counter.keys():
        p_xy = xy_counter[xy] / total_occurrences
        p_y = y_counter[xy[1]] / total_occurrences
        entrop += p_xy * math.log(p_y / p_xy, log_base)
    return entrop


def theils_u(x, y):
    """
    Calculates Theil's U statistic (Uncertainty coefficient) for categorical-
    categorical association. This is the uncertainty of x given y: value is
    on the range of [0,1] - where 0 means y provides no information about
    x, and 1 means y provides full information about x.

    This is an asymmetric coefficient: U(x,y) != U(y,x)

    Please see [The Dython Library](https://github.com/shakedzy/dython)
    for attribution and source

    Wikipedia: https://en.wikipedia.org/wiki/Uncertainty_coefficient

    Parameters:
    -----------
    x : list / NumPy ndarray / Pandas Series
        A sequence of categorical measurements
    y : list / NumPy ndarray / Pandas Series
        A sequence of categorical measurements

    Returns:
    --------
    float in the range of [0,1]
    """

    # remove NaN
    x = handle_na(x)
    y = handle_na(y)

    s_xy = conditional_entropy(x, y)
    x_counter = Counter(x)
    total_occurrences = sum(x_counter.values())
    p_x = list(map(lambda n: n / total_occurrences, x_counter.values()))
    s_x = entropy(p_x)
    if s_x == 0:
        return 1
    else:
        return (s_x - s_xy) / s_x
