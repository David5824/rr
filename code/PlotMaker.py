import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.formula.api import *
from DataPreprocessor import *

TAXI_COLOURS = ("green", "yellow")
YEARS = (2017, 2018)
MONTHS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
LOCATION_IDS = range(0, 265 + 1)
PASSENGER_COUNTS = range(1, 9 + 1)


def get_file_location(taxi_color, month, year, explore_folder="../raw_data"):
    """ Finds the file directory for the given taxi_colour, month and year. """

    taxi_color_string = str(taxi_color)
    year_string = str(year)
    month_string = ""
    if month < 10:
        month_string += "0"
    month_string += str(month)

    return (explore_folder + "/" + taxi_color_string + "/" + taxi_color_string + "_tripdata_" + year_string + "-" +
            month_string + ".csv")


def taxi_data_bar_plot(xaxis, yaxis, taxi_colours, xvalues=None, months=MONTHS, years=YEARS,
                       explore_folder=SELECTED_DATA_FOLDER):
    if xvalues is None:
        for taxi_colour in taxi_colours:
            xvalues = []
            for year in years:
                for month in months:
                    file_location = get_file_location(taxi_color=taxi_colour, month=month, year=year,
                                                      explore_folder=explore_folder)
                    df = pd.read_csv(file_location)
                    xvalues += list(set(df[xaxis]))
                    xvalues = list(set(xvalues))
                    print(file_location, "Parse Completed!")

    for taxi_colour in taxi_colours:
        n_dict = {i: [] for i in xvalues}
        for year in years:
            for month in months:
                file_location = get_file_location(taxi_color=taxi_colour, month=month, year=year,
                                                  explore_folder=explore_folder)
                df = pd.read_csv(file_location)
                for i in xvalues:
                    df2 = df.loc[(df[xaxis] == i), [yaxis]]
                    n_dict[i] += list(df2[yaxis])
                print(file_location, "Parse Completed!")

        mean_dict = {i: np.mean(np.array(n_dict[i])) for i in xvalues}
        median_dict = {i: np.median(np.array(n_dict[i])) for i in xvalues}

        plt.bar([str(i) for i in xvalues], list(mean_dict.values()), width=0.8, color=taxi_colour)
        plt.savefig("../plots/" + str(taxi_colour) + "_" + str(xaxis) + "_vs_" + str(yaxis) + "_bar_plot.png")
        plt.xlabel(xaxis)
        plt.ylabel(yaxis)
        plt.title(xaxis + " vs " + yaxis)
        plt.show()
        plt.clf()
        plt.bar([str(i) for i in xvalues], list(median_dict.values()), width=0.8, color=taxi_colour)
        plt.savefig("../plots/" + str(taxi_colour) + "_" + str(xaxis) + "_vs_" + str(yaxis) + "_bar_plot.png")
        plt.title(xaxis + " vs " + yaxis)
        plt.xlabel(xaxis)
        plt.ylabel(yaxis)
        plt.show()
        plt.clf()


def taxi_regression_line_plot(xaxis, yaxis, taxi_colours, months=MONTHS, years=YEARS,
                              explore_folder=SELECTED_DATA_FOLDER, store_folder="../plots", poly_deg=7):

    for taxi_colour in taxi_colours:
        xvalues = []
        yvalues = []
        for year in years:
            for month in months:
                file_location = get_file_location(taxi_color=taxi_colour, month=month, year=year,
                                                  explore_folder=explore_folder)
                df = pd.read_csv(file_location)
                xvalues += list(df[xaxis])
                yvalues += list(df[yaxis])
                print(file_location, "Parse Completed!")
        x = np.array(xvalues)
        y = np.array(yvalues)

        x2 = np.arange(int(min(x)), int(max(x)), 0.1)
        for deg in range(1, poly_deg + 1):
            p = list(np.polyfit(x, y, deg=deg))
            p.reverse()
            y2 = [sum([p[j]*i**j for j in range(1, deg + 1)]) + p[0] for i in x2]
            plt.plot(x2, y2, label=deg)
            print(deg, "complete!")
        plt.legend(loc="lower left")
        plt.title(xaxis + " vs " + yaxis)
        plt.xlabel(xaxis)
        plt.ylabel(yaxis)
        plt.savefig(store_folder + "/" + str(taxi_colour) + "_poly_plot_" + str(xaxis) + "_vs_" + str(yaxis) + ".png")
        plt.clf()


def save_all_line_plots(response_var='total_cost', predictor_vars=('passenger_count', 'month', 'day', 'hour',
                                                                   'tempF', 'precipInches', 'windspeedMiles',
                                                                   'weekday')):
    for predictor_var in predictor_vars:
        taxi_regression_line_plot(predictor_var, response_var, TAXI_COLOURS, poly_deg=7,
                                  store_folder="plots/poly_plots")
    for predictor_var1 in predictor_vars:
        for predictor_var2 in predictor_vars:
            taxi_regression_line_plot(predictor_var1, predictor_var2, TAXI_COLOURS, poly_deg=1,
                                      store_folder="plots/interaction_lines")