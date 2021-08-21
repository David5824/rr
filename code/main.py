import numpy as np
import pandas as pd
import time
import datetime
import json

from HolidayChecker import *
from DataPreprocessor import *
from RegressionModel import *
from PlotMaker import *

TAXI_COLOURS = ["green", "yellow"]
TRAIN_YEARS = [2017, 2018]
TEST_YEARS = [2019]
MONTHS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
LOCATION_IDS = range(0, 265 + 1)
DAYS_IN_WEEK = 7
MAX_PASSENGER_COUNT = 9
HOURS_IN_DAY = 24

# NOTE, ALL THESE FUNCTIONS WERE RAN OVER THE COURSE OF SEVERAL DAYS. THIS WILL LIKELY TAKE A LONG TIME TO RUN.
# (Checking code and understanding logic would be much faster).
# Apologies for not using jupyter, I now realise how much better it is for replication usage.

# I did not call all these functions together and developed everything over a slow course of time. This is an
# approximation of everything I did.
print("raw_data link:", "https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page")
print("2017-2019", "yellow and green taxi data")
get_instance_count(taxi_colours=TAXI_COLOURS, months=MONTHS, years=TRAIN_YEARS, explore_folder=RAW_DATA_FOLDER)
get_instance_count(taxi_colours=TAXI_COLOURS, months=MONTHS, years=TEST_YEARS, explore_folder=RAW_DATA_FOLDER)
preprocess_filter(taxi_colours=TAXI_COLOURS, months=MONTHS, years=TRAIN_YEARS,
                  store_folder=FILTERED_DATA_FOLDER, explore_folder=RAW_DATA_FOLDER)
create_location_json(explore_folder=FILTERED_DATA_FOLDER, store_folder=ADDITIONAL_DATA_FOLDER)
for taxi_colour in TAXI_COLOURS:
    create_location_stats_json(taxi_colour, explore_folder=ADDITIONAL_DATA_FOLDER, store_folder=ADDITIONAL_DATA_FOLDER)
for taxi_colour in TAXI_COLOURS:
    generate_location_tables(taxi_colour, explore_folder=ADDITIONAL_DATA_FOLDER)
preprocess_select_relevant(TAXI_COLOURS, YEARS, MONTHS, store_folder=SELECTED_DATA_FOLDER,
                           explore_folder=FILTERED_DATA_FOLDER)
preprocess_transform(TAXI_COLOURS, YEARS, MONTHS, store_folder=TRANSFORMED_DATA_FOLDER,
                     explore_folder=SELECTED_DATA_FOLDER, deg=4)
save_all_line_plots()
join_dataframes(TAXI_COLOURS, years=[2018], months=[6, 7, 8, 9, 10, 11, 12], store_folder=MERGED_DATA_FOLDER,
                explore_folder=TRANSFORMED_DATA_FOLDER + "/trans")
join_dataframes(TAXI_COLOURS, years=YEARS, months=MONTHS, store_folder=MERGED_DATA_FOLDER,
                explore_folder=TRANSFORMED_DATA_FOLDER + "/untrans")
do_regression(path="../preprocessed_data/4 merged/trans/" + "yellow" + ".csv", taxi_colour="yellow",
              features_for_removal=('Unnamed: 0', 'month', 'year'))
do_regression(path="../preprocessed_data/4 merged/trans/" + "green" + ".csv", taxi_colour="green",
              features_for_removal=('Unnamed: 0', 'month', 'year'))
do_regression(path="../preprocessed_data/4 merged/untrans/" + "green" + ".csv", taxi_colour="green",
              features_for_removal=('Unnamed: 0', 'year'))
do_regression(path="../preprocessed_data/4 merged/untrans/" + "yellow" + ".csv", taxi_colour="yellow",
              features_for_removal=('Unnamed: 0', 'year'))
