from statsmodels.formula.api import *
import pandas as pd
import time
from statsmodels.iolib.smpickle import load_pickle
import statsmodels.api as sm


def do_regression(path="../preprocessed_data/4 merged/trans_" + "yellow" + ".csv", taxi_colour="green",
                  features_for_removal=tuple(['Unnamed: 0'])):
    t0 = time.time()
    file_location = path
    df = pd.read_csv(file_location)

    def get_equation(dataframe, features_for_removal):
        dependent_variable = "total_cost"
        independent_variables = list(dataframe.columns)
        for feature_for_removal in features_for_removal:
            if feature_for_removal in independent_variables:
                independent_variables.remove(feature_for_removal)
        if dependent_variable in independent_variables:
            independent_variables.remove(dependent_variable)

        equation_string = dependent_variable + " ~ "
        i = 0
        for independent_variable in independent_variables:
            if i != 0:
                equation_string += " + "
            equation_string += independent_variable
            i += 1
        return equation_string

    print("Begin Modelling!", time.time() - t0)
    t0 = time.time()
    fit = ols(formula=get_equation(df, ['Unnamed: 0']), data=df).fit()
    fit.summary()
    fit.save("Regression_model_untransed_" + taxi_colour)

    print(fit.summary())
    print(time.time() - t0)

