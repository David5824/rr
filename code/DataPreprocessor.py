import pandas as pd
import json
import numpy as np

from HolidayChecker import *
from WeatherDataProcessor import *
import time

TAXI_COLOURS = ("green", "yellow")
YEARS = (2017, 2018, 2019)
MONTHS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
LOCATION_IDS = range(0, 265 + 1)

RAW_DATA_FOLDER = "../raw_data"
FILTERED_DATA_FOLDER = "../preprocessed_data/1 filtered"
SELECTED_DATA_FOLDER = "../preprocessed_data/2 selected"
TRANSFORMED_DATA_FOLDER = "../preprocessed_data/3 transformed"
MERGED_DATA_FOLDER = "../preprocessed_data/4 merged"

ADDITIONAL_DATA_FOLDER = "../additional data"


def get_file_location(taxi_color, month, year, explore_folder):
    """ Finds the file directory for the given taxi_colour, month and year. """

    taxi_color_string = str(taxi_color)
    year_string = str(year)
    month_string = ""
    if month < 10:
        month_string += "0"
    month_string += str(month)

    return (explore_folder + "/" + taxi_color_string + "/" + taxi_color_string + "_tripdata_" + year_string + "-" +
            month_string + ".csv")


def get_instance_count(taxi_colours, months, years, explore_folder=RAW_DATA_FOLDER):
    """ Determines the number of avalible instances of data at a specified explore_location for a specified
    taxi_colours, months, and years."""

    count = 0
    for taxi_colour in taxi_colours:
        for year in years:
            for month in months:
                file_location = get_file_location(taxi_colour, month, year, explore_folder)
                df = pd.read_csv(file_location)
                count += len(df)
    return count


MIN_FARE = 2.50  # USD
MIN_FARE_RATE = 0.5  # USD Per 1/5 mile
MAX_PASSENGER_COUNT = 41
SPEED_LIMIT = 65  # mph


def preprocess_filter(taxi_colours, years, months, store_folder=FILTERED_DATA_FOLDER, explore_folder=RAW_DATA_FOLDER):
    """ Filters out erroneous instances from the csv files in the explore_folder that correspond to the inputted
        taxi_colours, years and months. These filtered files are then saved to the store_folder in similar format. """

    for taxi_colour in taxi_colours:
        size_contrasts = []
        pickup_name = ''
        dropoff_name = ''
        if taxi_colour == 'green':
            pickup_name += 'lpep_pickup_datetime'
            dropoff_name += 'lpep_dropoff_datetime'
        elif taxi_colour == 'yellow':
            pickup_name += 'tpep_pickup_datetime'
            dropoff_name += 'tpep_dropoff_datetime'

        for year in years:
            for month in months:
                t0 = time.time()
                file_location = get_file_location(taxi_colour, month, year, explore_folder)
                df = pd.read_csv(file_location)
                df['pickup_datetime'] = pd.to_datetime(df[pickup_name])
                df['dropoff_datetime'] = pd.to_datetime(df[dropoff_name])
                df['trip_time'] = (df['dropoff_datetime'] - df['pickup_datetime']).dt.seconds
                df['trip_speed'] = abs(60 * 60 * df['trip_distance'] / df['trip_time'])

                df_col = ['pickup_datetime', 'PULocationID', 'DOLocationID', 'passenger_count', 'tip_amount',
                          'total_amount']
                pre_filter_length = len(df)
                df = df.loc[(df['passenger_count'] > 0) &
                            (df['passenger_count'] < 41) &
                            (df['fare_amount'] >= MIN_FARE + ((5 * df['trip_distance']) // 1) * MIN_FARE_RATE) &
                            (df['tip_amount'] >= 0) &
                            (df['tip_amount'] <= df['total_amount']) &
                            (df['total_amount'] >= 0) &
                            (df['improvement_surcharge'] >= 0) &
                            (df['mta_tax'] >= 0) &
                            (df['extra'] >= 0) &
                            ((df['dropoff_datetime'].dt.year == 2017) |
                             (df['dropoff_datetime'].dt.year == 2018)) &
                            ((df['pickup_datetime'].dt.year == 2017) |
                             (df['pickup_datetime'].dt.year == 2018)) &
                            ((df['payment_type'] == 1) |
                             ((df['payment_type'] == 2) & (df['tip_amount'] == 0))) &
                            (df['trip_time'] > 0) &
                            (df['trip_distance'] > 0) &
                            (df['trip_speed'] <= SPEED_LIMIT), df_col]
                post_filter_length = len(df)
                size_contrasts.append((pre_filter_length, post_filter_length))

                path = get_file_location(taxi_color=taxi_colour, month=month, year=year, explore_folder=store_folder)
                df.to_csv(path)
                print(path, "Filter Save Completed!", time.time() - t0)
        pre_full = sum([pre for pre, post in size_contrasts])
        post_full = sum([post for pre, post in size_contrasts])
        print("Data Filtered:", 1 - post_full / pre_full)


def create_location_json(explore_folder=FILTERED_DATA_FOLDER, store_folder=ADDITIONAL_DATA_FOLDER):
    tip_amount_name = 'tip_amount'
    total_amount_name = 'total_amount'
    pu_location_id = 'PULocationID'
    do_location_id = 'DOLocationID'

    for taxi_colour in TAXI_COLOURS:
        res_dict = {i: {j: [] for j in LOCATION_IDS} for i in LOCATION_IDS}
        for year in YEARS:
            for month in MONTHS:
                file_location = get_file_location(taxi_color=taxi_colour, month=month, year=year,
                                                  explore_folder=explore_folder)
                df = pd.read_csv(file_location)
                for i in range(len(df)):
                    total_amount = df[total_amount_name][i]
                    do_loc = df[do_location_id][i]
                    pu_loc = df[pu_location_id][i]
                    tip_amount = df[tip_amount_name][i]
                    res_dict[pu_loc][do_loc].append(total_amount - tip_amount)
                print(file_location, "Parse Completed!")
        print(taxi_colour, "complete")
        json.dump(res_dict, open(store_folder + "/" + taxi_colour + "_loc_dict.json", 'w'))


def create_location_stats_json(taxi_colour, explore_folder=ADDITIONAL_DATA_FOLDER, store_folder=ADDITIONAL_DATA_FOLDER):
    new_dict = {i: {j: {} for j in LOCATION_IDS} for i in LOCATION_IDS}
    with open(explore_folder + "/" + taxi_colour + "_loc_dict.json", 'r') as f:
        big_dict = json.load(f)
    if big_dict:
        c = 0
        total_size = len(LOCATION_IDS)*len(LOCATION_IDS)
        for i1 in big_dict.keys():
            for i2 in big_dict[i1].keys():
                new_dict[int(i1)][int(i2)] = dict(pd.Series(big_dict[i1][i2], dtype=float).describe())
                print(c, "/", total_size)
                c += 1
    json.dump(new_dict, open(store_folder + "/" + taxi_colour + "_loc_stats_dict.json", 'w'))


def generate_location_tables(taxi_colour, explore_folder=ADDITIONAL_DATA_FOLDER):

    print("Begin Task: Generating Location Tables")
    location_table_mean = np.empty((len(LOCATION_IDS), len(LOCATION_IDS)), dtype=object)
    location_table_median = np.empty((len(LOCATION_IDS), len(LOCATION_IDS)), dtype=object)
    with open(explore_folder + "/" + taxi_colour + "_loc_stats_dict.json", "r") as f:
        location_stats_dict = json.load(f)

    trip_means = []
    trip_medians = []

    for i in LOCATION_IDS:
        for j in LOCATION_IDS:
            n = location_stats_dict[str(i)][str(j)]["count"]
            if n > 0:
                mean = location_stats_dict[str(i)][str(j)]["mean"]
                median = location_stats_dict[str(i)][str(j)]["50%"]
                location_table_mean[i][j] = mean
                location_table_median[i][j] = median
                trip_means.append(mean)
                trip_medians.append(median)

    overall_trip_mean = np.mean(np.array(trip_means))
    overall_trip_median = np.median(np.array(trip_medians))

    for i in LOCATION_IDS:
        for j in LOCATION_IDS:
            if location_table_mean[i][j] is None:
                location_table_mean[i][j] = overall_trip_mean
            if location_table_median[i][j] is None:
                location_table_median[i][j] = overall_trip_median
    print("End Task: Generating Location Tables")

    return location_table_mean, location_table_median


def preprocess_select_relevant(taxi_colours, years, months, store_folder=SELECTED_DATA_FOLDER,
                               explore_folder=FILTERED_DATA_FOLDER, pu_datetime_name='pickup_datetime'):
    weather_dict = get_weather_dict()
    for taxi_colour in taxi_colours:
        mean_tables, median_tables = generate_location_tables(taxi_colour)
        for year in years:
            for month in months:
                t0 = time.time()
                file_location = get_file_location(taxi_colour, month, year, explore_folder)
                df = pd.read_csv(file_location)

                df[pu_datetime_name] = pd.to_datetime(df[pu_datetime_name])
                df['year'] = df[pu_datetime_name].dt.year
                df['month'] = df[pu_datetime_name].dt.month  # Could add days as a fraction.
                df['day'] = df[pu_datetime_name].dt.day
                df['hour'] = (df[pu_datetime_name].dt.hour + df[pu_datetime_name].dt.minute / 60 +
                              df[pu_datetime_name].dt.minute / (60 * 60))
                df['total_cost'] = df['total_amount'] - df['tip_amount']
                df['is_holiday'] = pd.Series([is_holiday(s.year, s.month, s.day) for s in df[pu_datetime_name]])
                df['tempF'] = pd.Series([weather_dict[(s.year, s.month, s.day, s.hour)]['tempF']
                                         for s in df[pu_datetime_name]])
                df['precipInches'] = pd.Series([weather_dict[(s.year, s.month, s.day, s.hour)]['precipInches']
                                                for s in df[pu_datetime_name]])
                df['windspeedMiles'] = pd.Series([weather_dict[(s.year, s.month, s.day, s.hour)]['windspeedMiles']
                                                  for s in df[pu_datetime_name]])
                df['weekday'] = pd.Series([s.weekday() for s in df[pu_datetime_name]])
                df['mean_trip'] = pd.Series([mean_tables[taxi_colour][df['PULocationID'][i]]
                                             [df['DOLocationID'][i]] for i in range(len(df))])
                df['median_trip'] = pd.Series([median_tables[taxi_colour][df['PULocationID'][i]]
                                               [df['DOLocationID'][i]] for i in range(len(df))])
                df2 = df[['total_cost', 'passenger_count', 'year', 'month', 'day', 'hour', 'is_holiday', 'tempF',
                          'precipInches', 'windspeedMiles', 'weekday', 'mean_trip', 'median_trip']]
                path = get_file_location(taxi_color=taxi_colour, month=month, year=year, explore_folder=store_folder)
                df2.to_csv(path)
                print(path, "Selection Save Completed!", time.time() - t0)


def preprocess_transform(taxi_colours, years, months, store_folder=TRANSFORMED_DATA_FOLDER,
                         explore_folder=SELECTED_DATA_FOLDER, deg=5):
    transformation_features = ('passenger_count', 'month', 'day', 'hour', 'tempF', 'precipInches', 'windspeedMiles',
                               'weekday')
    for taxi_colour in taxi_colours:
        for year in years:
            for month in months:
                t0 = time.time()
                file_location = get_file_location(taxi_colour, month, year, explore_folder)
                df = pd.read_csv(file_location)
                for transformation_feature in transformation_features:
                    for i in range(2, deg + 1):
                        df[transformation_feature + str(i)] = df[transformation_feature]**i
                path = get_file_location(taxi_color=taxi_colour, month=month, year=year, explore_folder=store_folder)
                df.to_csv(path)
                print(path, "Selection Save Completed!", time.time() - t0)


def join_dataframes(taxi_colours, years=YEARS, months=MONTHS, store_folder=MERGED_DATA_FOLDER,
                    explore_folder=TRANSFORMED_DATA_FOLDER):
    for taxi_colour in taxi_colours:
        first_year = years[0]
        first_month = months[0]
        file_location = get_file_location(taxi_colour, first_month, first_year, explore_folder)
        df_total = pd.read_csv(file_location)
        for year in years:
            for month in months:
                t0 = time.time()
                if month != first_month or year != first_year:
                    file_location = get_file_location(taxi_colour, month, year, explore_folder)
                    df = pd.read_csv(file_location)
                    df_total = pd.concat([df_total, df], ignore_index=True)
                    print(len(df))
                print(year, month, "Merge Completed!", time.time() - t0)
        try:
            del df_total['Unnamed: 0']
        except KeyError:
            pass
        try:
            del df_total['Unnamed: 0.1']
        except KeyError:
            pass
        df_total.to_csv(store_folder + "/trans_" + taxi_colour + ".csv", index=False)


# This function failed, prevent me from testing
def preprocess_filter2019(taxi_colours, years, months, store_folder=FILTERED_DATA_FOLDER, explore_folder=RAW_DATA_FOLDER):
    """ Filters out erroneous instances from the csv files in the explore_folder that correspond to the inputted
        taxi_colours, years and months. These filtered files are then saved to the store_folder in similar format. """

    for taxi_colour in taxi_colours:
        size_contrasts = []
        pickup_name = ''
        dropoff_name = ''
        if taxi_colour == 'green':
            pickup_name += 'lpep_pickup_datetime'
            dropoff_name += 'lpep_dropoff_datetime'
        elif taxi_colour == 'yellow':
            pickup_name += 'tpep_pickup_datetime'
            dropoff_name += 'tpep_dropoff_datetime'

        for year in years:
            for month in months:
                t0 = time.time()
                file_location = get_file_location(taxi_colour, month, year, explore_folder)
                df = pd.read_csv(file_location)
                df['pickup_datetime'] = pd.to_datetime(df[pickup_name])
                df['dropoff_datetime'] = pd.to_datetime(df[dropoff_name])
                df['trip_time'] = (df['dropoff_datetime'] - df['pickup_datetime']).dt.seconds
                df['trip_speed'] = abs(60 * 60 * df['trip_distance'] / df['trip_time'])
                df['PULocationID'] = pd.Series([int(i) for i in df['PULocationID']])
                df['DOLocationID'] = pd.Series([int(i) for i in df['DOLocationID']])
                df_col = ['pickup_datetime', 'PULocationID', 'DOLocationID', 'passenger_count', 'tip_amount',
                          'total_amount']
                pre_filter_length = len(df)
                df = df.loc[(df['passenger_count'] > 0) &
                            (df['passenger_count'] < 41) &
                            (df['fare_amount'] >= MIN_FARE + ((5 * df['trip_distance']) // 1) * MIN_FARE_RATE) &
                            (df['tip_amount'] >= 0) &
                            (df['tip_amount'] <= df['total_amount']) &
                            (df['total_amount'] >= 0) &
                            (df['improvement_surcharge'] >= 0) &
                            (0 <= df['PULocationID']) &
                            (df['PULocationID'] <= 265) &
                            (0 <= df['DOLocationID']) &
                            (df['DOLocationID'] <= 265) &
                            (df['mta_tax'] >= 0) &
                            (df['extra'] >= 0) &
                            (df['dropoff_datetime'].dt.year == 2019) &
                            ((df['payment_type'] == 1) |
                             ((df['payment_type'] == 2) & (df['tip_amount'] == 0))) &
                            (df['trip_time'] > 0) &
                            (df['trip_distance'] > 0) &
                            (df['trip_speed'] <= SPEED_LIMIT), df_col]
                post_filter_length = len(df)
                size_contrasts.append((pre_filter_length, post_filter_length))

                path = get_file_location(taxi_color=taxi_colour, month=month, year=year, explore_folder=store_folder)
                df.to_csv(path)
                print(path, "Filter Save Completed!", time.time() - t0)
        pre_full = sum([pre for pre, post in size_contrasts])
        post_full = sum([post for pre, post in size_contrasts])
        print("Data Filtered:", 1 - post_full / pre_full)


