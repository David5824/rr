import pandas as pd


def get_weather_dict(weather_data_path="../weather_data/weather_data_1hr.csv"):
    print("Begin Task: Processing Weather Data")
    weather_df = pd.read_csv(weather_data_path)
    weather_df['date'] = pd.to_datetime(weather_df['date'])

    weather_dict = {}
    for index, row in weather_df.iterrows():
        year = row['date'].year
        if 2000 <= year <= 2019:
            month = row['date'].month
            day = row['date'].day
            hour = row['time'] // 100
            weather_dict[(year, month, day, hour)] = {'tempF': row['tempF'],
                                                      'precipInches': row['precipInches'],
                                                      'windspeedMiles': row['windspeedMiles']}
    print("End Task: Processing Weather Data")
    return weather_dict
