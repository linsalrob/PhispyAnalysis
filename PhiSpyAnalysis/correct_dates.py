"""
A class to convert dates to a standard format.

We use years as our unit, but could also use seconds.

Convert the collection date to a number. We take todays date, and then convert relative to that
it allows dates pre-unix-epoch.

We set our epoch to 01/01/0001 and then add one year (we don't have anything in 0 BC)
so that the dates end up calendar dates.

We also could set the epoch to 24/02/1977 when [phiX174 sequence was
published](https://pubmed.ncbi.nlm.nih.gov/870828/))
"""

import re
import sys
# for parsing collection dates
import numpy as np
from dateutil.parser import parse, ParserError
import pytz
import pandas as pd


class CantConvertDate(Exception):
    """Can't Parse This Date"""

    def __init__(self, message):
        self.message = message


class DateConverter:
    def __init__(self, epoch="1/1/0001"):
        self.epoch = epoch
        self.yr = re.compile("^[~]*(\\d{4})['s]*$")  # eg ~1970's
        self.yrrange = re.compile("^(\\d{4})\\s*.\\s*(\\d{4})$")  # eg 2001-2002
        self.myd = re.compile('^\\d{1,4}/\\d{1,2}/\\d{1,4}$')  # eg 2/3/21
        self.moyr = re.compile('^\\w{3}-\\d{2}$')  # eg Dec-09 should be 01-Dec-09 else parsed as 9th Dec this year
        self.damoyrrange = re.compile('^(\\d+\\s+\\w+\\s+\\d{4})\\s*.{1,3}?\\s*(\\d+\\s+\\w+\\s+\\d{4})$')
        self.modacyrrange = re.compile('^(\\w+\\s+\\d+,*\\s+\\d{4})\\s*.{1,3}?\\s*(\\w+\\s+\\d+,*\\s+\\d{4})$')
        self.moyrrange = re.compile('^(\\w+\\s+\\d{4})\\s*.{1,3}?\\s*(\\w+\\s+\\d{4})$')
        self.year42 = re.compile('^(\\d{4})-\\d{2}$')
        self.lem = re.compile("^late\\s*|^early\\s*|^mid\\s*|^prior to\\s*|^before\\s*|^pre-", re.IGNORECASE)

        try:
            # adate = parse()
            self.adate = parse(self.epoch)
        except ParserError as e:
            raise CantConvertDate(f"There was an error parsing the epoch {self.epoch}: {e}\n")

        self.adate = self.adate.replace(tzinfo=pytz.UTC)

    def try_parsing(self, x):
        """
        Attempt to parse a date, and catch an error.

        If we fail, we return None, otherwise we return the years since now()
        """
        try:
            dt = parse(x)
        except:
            return None

        dt = dt.replace(tzinfo=pytz.UTC)

        if dt < self.adate:
            tdelt = self.adate - dt
            seconds = -1 * ((tdelt.days * 86400) + tdelt.seconds)
        else:
            tdelt = dt - self.adate
            seconds = (tdelt.days * 86400) + tdelt.seconds
        # convert seconds to years
        # then we add one because our epoch is now Jan 1, 0001
        return (seconds / 31557600) + 1

    def convert_date(self, x, verbose=False):
        """
        Convert the date to years and fractions.

        We try several times, and clean it up as we go along.

        :param x: the date string to convert
        :param verbose: more output information
        """
        if pd.isna(x):
            return np.nan

        # we need to fix this before trying to parse
        m = self.moyr.match(x)
        if m:
            x = '01-' + x

        # can we parse this date? If so, lets do it and return the value
        attempt = self.try_parsing(x)
        if attempt:
            if verbose:
                sys.stderr.write("Parsed at step 1\n")
            return attempt
        orix = x

        if x.lower() in ['restricted access', 'none', 'not collected', 'not applicable',
                         'not available: not collected', 'unspecified']:
            return np.nan

        # a few one off cases that are just easier to fix
        if 'May 2015-Nov 2015' == x:
            x = 'May 2015'

        if '1954-65' == x:
            x = '01 January 1954'

        if 'Jul-00' == x:
            x = 'Jul-2000'

        if '2015_9' == x:
            x = 'Sep-2015'

        if '31-Mac-2013' == x:
            x = '31-May-2013'

        if '2010-0916' == x:
            x = '16 Sep 2010'

        x = self.lem.sub('', x)

        if '_' in x:
            x = x.replace('_', '-')

        x = x.replace(' or earlier', '')
        x = x.replace('collected in the ', '')

        # some regular expressions of variants of day month year - day month year ranges. We choose 1
        m = self.yrrange.match(x)
        if m:
            x = '01 January ' + m.groups()[1]

        m = self.yr.match(x)
        if m:
            x = '01 January ' + m.groups()[0]

        m = self.year42.match(x)
        if m:
            x = '01 January ' + m.groups()[0]

        m = self.modacyrrange.match(x)
        if m:
            x = m.groups()[1]

        m = self.damoyrrange.match(x)
        if m:
            x = m.groups()[1]

        m = self.moyrrange.match(x)
        if m:
            x = '01 ' + m.groups()[1]

        # can we parse this date? If so, lets do it and return the value
        attempt = self.try_parsing(x)
        if attempt:
            if verbose:
                sys.stderr.write(f"Parsed at step 2. Now {orix} is {x}\n")
            return attempt

        if '/' in x:
            p = x.split('/')
            x = p[1]

        # can we parse this date? If so, lets do it and return the value
        attempt = self.try_parsing(x)
        if attempt:
            if verbose:
                sys.stderr.write(f"Parsed at step 3. Now {orix} is {x}\n")
            return attempt

        if x.endswith('-00'):
            x = x.replace('-00', '-2000')

        # can we parse this date? If so, lets do it and return the value
        attempt = self.try_parsing(x)
        if attempt:
            if verbose:
                sys.stderr.write(f"Parsed at step 4. Now {orix} is {x}\n")
            return attempt

        if verbose:
            sys.stderr.write(f"can't parse |{x}| from |{orix}|\n")

        return np.nan
