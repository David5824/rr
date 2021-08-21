import pandas as pd

print("Begin Task: Processing Holiday Data")
HOLIDAYS = set()

# Manually add 2017 holidays.
HOLIDAYS.add((2017, 1, 2))
HOLIDAYS.add((2017, 1, 16))
HOLIDAYS.add((2017, 2, 13))
HOLIDAYS.add((2017, 2, 20))
HOLIDAYS.add((2017, 5, 29))
HOLIDAYS.add((2017, 7, 4))
HOLIDAYS.add((2017, 9, 4))
HOLIDAYS.add((2017, 10, 9))
HOLIDAYS.add((2017, 11, 7))
HOLIDAYS.add((2017, 11, 10))
HOLIDAYS.add((2017, 11, 23))
HOLIDAYS.add((2017, 12, 25))

# Manually add 2018 holidays.
HOLIDAYS.add((2018, 1, 1))
HOLIDAYS.add((2018, 1, 15))
HOLIDAYS.add((2018, 2, 12))
HOLIDAYS.add((2018, 2, 19))
HOLIDAYS.add((2018, 5, 28))
HOLIDAYS.add((2018, 7, 4))
HOLIDAYS.add((2018, 9, 3))
HOLIDAYS.add((2018, 10, 8))
HOLIDAYS.add((2018, 11, 6))
HOLIDAYS.add((2018, 11, 12))
HOLIDAYS.add((2018, 11, 22))
HOLIDAYS.add((2018, 12, 25))

# Manually add 2019 holidays.
HOLIDAYS.add((2019, 1, 1))
HOLIDAYS.add((2019, 1, 21))
HOLIDAYS.add((2019, 2, 12))
HOLIDAYS.add((2019, 2, 18))
HOLIDAYS.add((2019, 5, 27))
HOLIDAYS.add((2019, 7, 4))
HOLIDAYS.add((2019, 9, 2))
HOLIDAYS.add((2019, 10, 14))
HOLIDAYS.add((2019, 11, 5))
HOLIDAYS.add((2019, 11, 11))
HOLIDAYS.add((2019, 11, 28))
HOLIDAYS.add((2019, 12, 25))


def is_holiday(year, month, day):
    """ Takes a datetime between 2017 and 2019 (inclusive) and returns a True or False corresponding to whether that
        datetime is a public holiday in New York City. """
    return int((year, month, day) in HOLIDAYS)


def is_series_holiday(series):
    return pd.Series([is_holiday(s.dt.year, s.dt.month, s.dt.day) for s in series])


print("End Task: Processing Holiday Data")

