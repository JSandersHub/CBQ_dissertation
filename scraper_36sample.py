import random
import pandas as pd
import regex as re
from Scweet.scweet import scrape
from datetime import datetime, timedelta
from tqdm import tqdm

"""
Parameters
"""
days_per_year = 36 # number of days to sample per year
year_range = [2012, 2021] # first and last year to sample
random.seed(25) # seed for sampling


"""
Select days for my sample
"""
sample_days = list()

for year in range(year_range[0], year_range[1]+1):
    population = pd.date_range(start=str(year) + "-01-01",
                               end=str(year) + "-12-31")
    population = list(population)
    sample_days.extend(random.sample(population, days_per_year))
    
sample_days = [a.strftime("%Y-%m-%d") for a in sample_days]


"""
Get tweets
"""

outputs = list()

for day in tqdm(sample_days):
    
    next_day = datetime.strptime(day, "%Y-%m-%d") + timedelta(days = 1)
    next_day = next_day.strftime("%Y-%m-%d")

    sample_day_tweets = scrape(
        since = day,
        until = next_day, 
        words = ['bank of england', 'bankofengland'],
        from_account = None,
        interval = 1,
        headless = False,
        display_type = "Latest",
        save_images = False,
        lang = "en",
        resume = False,
        filter_replies = False,
        proximity = False
        )
    
    outputs.append(sample_day_tweets)
    
full_sample = pd.concat(outputs)
full_sample.to_csv('/Users/jamiesanders/Desktop/CBQ_dissertation/data/sample36.csv')

"""
Data integrity check and supplement
"""

full_sample = pd.read_csv('/Users/jamiesanders/Desktop/CBQ_dissertation/data/sample36.csv')

full_sample['date'] = full_sample['Timestamp'].apply(lambda x: re.split('T', x)[0])
print(full_sample['date'].nunique())
# One too many...

full_sample['date'][~full_sample['date'].isin(sample_days)]

freq_table = full_sample['date'].value_counts()
# Looks reasonable

full_sample = full_sample[full_sample['UserName'] != '@bankofengland']

full_sample.to_csv('/Users/jamiesanders/Desktop/CBQ_dissertation/data/sample36_checked.csv')

