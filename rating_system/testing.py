import sys
import os
import numpy as np
import psycopg2.extras
import psycopg2
import pandas as pd
import config as ecallisto_config

from daily_observations import DailyObservation

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "radiospectra2"))


class Rating:
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.database = self.get_db()

    def get_db(self):
        """Connect to the database"""
        return psycopg2.connect(host=ecallisto_config.DB_HOST,
                                user=ecallisto_config.DB_USER,
                                database=ecallisto_config.DB_DATABASE,
                                port=ecallisto_config.DB_PORT,
                                password=ecallisto_config.DB_PASSWORD)

    def get_all_instruments(self):
        """Get all data from the database"""
        sql_query_instruments = f"""
            SELECT path, snr, std 
            FROM test 
            WHERE start_time BETWEEN '{self.start_time}' AND '{self.end_time}' 
                AND snr IS NOT NULL 
            ORDER BY snr DESC;
        """
        with self.database.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(sql_query_instruments)
            instruments = cursor.fetchall()
        return instruments

    def convert_to_stars(self, score):
        ranking = [1.0, 2.0, 3.0, 4.0, 5.0]
        percent = np.percentile(score, [0, 25, 50, 75, 100])
        rating = np.interp(score, percent, ranking)
        return np.round(rating, 2)

    def rate_stations(self):
        instruments = self.get_all_instruments()
        df = pd.DataFrame(instruments, columns=["path", "snr", "std"])
        df = df[df['snr'].notna()]
        df["station_name"] = df["path"].str.split('[/|_]', expand=True)[4]
        df["snr_rating"] = self.convert_to_stars(df["snr"])
        df["std_rating"] = self.convert_to_stars(df["std"])
        df["counter"] = df["station_name"].tolist()
        values, counts = np.unique(df["counter"], return_counts=True)
        df = df.groupby('station_name').mean().round(decimals=2).sort_values(by='snr_rating', ascending=False)
        df["number_of_files"] = counts
        return df[["snr", "snr_rating", "std", "std_rating", "number_of_files"]]

    def combine_daily_observations(self):
        """
        Integrates DailyObservation with the rating system to provide a comprehensive analysis.
        """
        daily_observation = DailyObservation(self.start_time, self.end_time, "")
        daily_data = daily_observation.data

        ratings = self.rate_stations()

        # Merge daily observations with ratings
        combined_data = pd.merge(daily_data, ratings, left_on='Station', right_index=True, how='inner')
        return combined_data

    def calculate_total_duration(self):
        """
        Calculates the total duration and average SNR and std for each station.

        Returns:
            pandas.DataFrame: Total duration and average SNR and std data by station.
        """
        combined_data = self.combine_daily_observations()

        combined_data['Duration'] = pd.to_timedelta(combined_data['Duration'])
        total_duration = combined_data.groupby('Station')['Duration'].sum().reset_index()
        total_duration['Duration'] = total_duration['Duration'].apply(
            lambda duration: f"{duration.days} days, {str(duration)[-8:]}" if duration.days > 0 else str(duration)
        )

        average_stats = combined_data.groupby('Station').agg({'Avg-SNR': 'mean', 'Avg-STD': 'mean'}).reset_index()
        total_duration = total_duration.merge(average_stats, on='Station')
        return total_duration


if __name__ == '__main__':
    rating = Rating('2021-09-08 08:00:00', '2021-09-08 18:45:00')
    df_ratings = rating.rate_stations()
    print(df_ratings)

    combined_data = rating.combine_daily_observations()
    print(combined_data)

    total_duration_data = rating.calculate_total_duration()
    print(total_duration_data)
