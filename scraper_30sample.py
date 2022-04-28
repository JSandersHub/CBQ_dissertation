import random
import pandas as pd
import regex as re
from Scweet.scweet import scrape
from Scweet.user import get_user_information, get_users_following, get_users_followers
from datetime import datetime, timedelta
from tqdm import tqdm

"""
Parameters
"""
days_per_year = 30 # number of days to sample per year
year_range = [2011, 2021] # first and last year to sample
random.seed(42) # seed for sampling


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
        words = ['Bank of England'],
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
full_sample.to_csv('/Users/jamiesanders/Desktop/CBQ_dissertation/data/sample30.csv')

"""
Data integrity check and supplement
"""

full_sample = pd.read_csv('/Users/jamiesanders/Desktop/CBQ_dissertation/data/sample30.csv')

full_sample['date'] = full_sample['Timestamp'].apply(lambda x: re.split('T', x)[0])
print(full_sample['date'].nunique())
# One too many...

full_sample['date'][~full_sample['date'].isin(sample_days)]
# It picked up the scrape day too

freq_table = full_sample['date'].value_counts()
# 2018-10-20 seems low

# I'll repeat it here
rerun181020 = scrape(
    since = '2018-10-20',
    until = '2018-10-21', 
    words = ['Bank of England'],
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

# It's correct - interesting.

# It looks like the mysterious 2022 data was next to:
# 2020-03-26
# and 
# 2020-07-27
# I will check both of these are correct

rerun200326 = scrape(
    since = '2020-03-26',
    until = '2020-03-27', 
    words = ['Bank of England'],
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

print(freq_table['2020-03-26'])

# Missing loads!

rerun2007287 = scrape(
    since = '2020-07-27',
    until = '2020-07-28', 
    words = ['Bank of England'],
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

print(freq_table['2020-07-27'])
# Missing 1... small change

# Let's fix
full_sample = full_sample[~full_sample['date'].isin(['2022-04-27', '2020-03-26'])]
full_sample = full_sample.drop('Unnamed: 0', axis = 1)
print(full_sample['date'].nunique())

rerun200326['date'] = rerun200326['Timestamp'].apply(lambda x: re.split('T', x)[0])
full_sample = full_sample.append(rerun200326)
print(full_sample['date'].nunique()) # correct
full_sample['date'][~full_sample['date'].isin(sample_days)] # none

pd.DataFrame(columns = ['date'],data = sample_days).to_csv('/Users/jamiesanders/Desktop/CBQ_dissertation/data/sample30_days.csv')
full_sample.to_csv('/Users/jamiesanders/Desktop/CBQ_dissertation/data/sample30_checked.csv')

