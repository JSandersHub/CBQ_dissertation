library(tidyverse)
library(xtable)
library(quanteda)
library(quanteda.textstats)
library(quanteda.textplots)

setwd("/Users/jamiesanders/Desktop/CBQ_dissertation")

##### Data loading #####

# Load data
raw_extract <- read_csv(file = "data/sample36_checked.csv")

##### Frequency statistics #####

# Frequency by day
dailyFreq <- raw_extract %>%
  group_by(date) %>%
  summarise(ttl = n()) 

# Frequency stats by Year
yearlyFreq <- dailyFreq %>%
  mutate(Year = as.character(date),
         Year = str_extract(Year, "^[0-9]{4}")) %>%
  group_by(Year) %>%
  summarise(Total = sum(ttl),
            Min = min(ttl),
            Max = max(ttl),
            Average = mean(ttl))

# Add a total column
totalFreq <- dailyFreq %>%
  summarise(Total = sum(ttl),
            Min = min(ttl),
            Max = max(ttl),
            Average = mean(ttl)) %>%
  mutate(Year = "Total")

freqTable <- yearlyFreq %>%
  bind_rows(totalFreq)

# Save as LaTeX table
print(xtable(freqTable, type = "latex"), include.rownames = FALSE, file = "sample_totals.tex")

##### Observations histogram #####

# Investigate top days
dailyFreq %>%
  arrange(desc(ttl))

# 2013-02-07: MPC rate decision day before and Mark Carney appointment hearing with TSC
# 2016-06-16: MPC rate decision day (maintained 0.5%)
# 2018-02-08: MPC rate decision day (maintained 0.5%)

# Plot histogram
ggplot(dailyFreq, aes(x = ttl)) +
  geom_histogram() +
  theme_bw() +
  labs(x = "Total Tweets",
       y = "Count") +
  geom_vline(aes(xintercept = mean(ttl)),
             linetype = 'dashed') +
  geom_text(aes(x = 400, y = 100, label = paste0("Mean: ", mean(ttl)), angle = 90)) +
  geom_text(aes(x = 3345, y = 5, label = "(1)")) +
  geom_text(aes(x = 3110, y = 5, label = "(2)")) +
  geom_text(aes(x = 2880, y = 5, label = "(3)"))

##### Other descriptive stats #####

# Word count
wc <- str_count(raw_extract$Embedded_text, "\\w+")
sum(wc)
mean(wc)
max(wc)
min(wc)

# Top words
tkns <- quanteda::tokens(raw_extract$Embedded_text,
                         what = "word",
                         remove_punct = TRUE,
                         remove_symbols = TRUE,
                         remove_numbers = TRUE,
                         remove_url = TRUE)
dfmat_tweets <- dfm(tkns)
dfmat_tweets <- dfm_remove(dfmat_tweets, c(stopwords(), "bank", "england", "england's", "boe", "bankofengland"))
tstat_freq <- textstat_frequency(dfmat_tweets)
