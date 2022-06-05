library(tidyverse)
library(BTM)
library(tm)
library(textplot)
library(ggraph)
library(concaveman)

setwd("/Users/jamiesanders/Desktop/CBQ_dissertation")

##### Data loading #####

# Regex to detect BOE
check_regex <- "bank of england|(\\b|#)boe\\b|(\\b|#)bofe|bankofengland|bank #of england|bank #of #england|bank of #england"

# Load data
raw_extract <- read_csv(file = "data/sample30_checked.csv") 
raw_extract <- raw_extract %>%
  mutate(Embedded_text = tolower(Embedded_text)) %>%
  filter(str_detect(Embedded_text, check_regex),
         UserName != "@bankofengland")

##### Descriptive statistics #####

# Frequency table by date
frequency_table <- raw_extract %>%
  group_by(date) %>%
  summarise(volume = n())

# Min observations
paste0("The lowest volume of tweets was ",
       min(frequency_table$volume),
       " which occured on ",
       frequency_table$date[frequency_table$volume == min(frequency_table$volume)])

# Max observations
paste0("The highest volume of tweets was ",
       max(frequency_table$volume),
       " which occured on ",
       frequency_table$date[frequency_table$volume == max(frequency_table$volume)])

# Observations hitorgram
ggplot(frequency_table, aes(x = volume)) +
  geom_histogram() +
  theme_bw() +
  labs(x = "Total Tweets",
       y = "Count") +
  ggtitle("Histogram of number of tweets per day (dotted line shows mean average)") +
  geom_vline(aes(xintercept = mean(volume)),
             linetype = 'dashed')


##### Topic Modelling (BTM) #####

# All tweet text to lower case
# All extra spaces removed
# All leading and trailing spaces removed
# Only keep texts longer than 5 words
# Make sure Bank of England is mentioned in accordance to check_regex
# Exclude BOE tweets
cleaned_data <- raw_extract %>%
  mutate(tweet_ID = 1:nrow(raw_extract),
         Embedded_text = str_replace_all(Embedded_text, "\\s+", " "),
         Embedded_text = str_replace_all(Embedded_text, check_regex, ""),
         Embedded_text = str_replace(Embedded_text, "replying to [@.*\\s]+", ""),
         Embedded_text = str_replace(Embedded_text, "rt @.* : ", ""),
         Embedded_text = str_replace_all(Embedded_text, "http[^\\s]*", ""),
         Embedded_text = str_replace_all(Embedded_text, "[a-z0-9]+\\.\\.\\.\\s*$", ""),
         Embedded_text = tm::removeWords(Embedded_text, stopwords()),
         Embedded_text = tm::stemDocument(Embedded_text),
         Embedded_text = str_replace_all(Embedded_text, "[^[:alnum:] ]", ""),
         Embedded_text = str_replace_all(Embedded_text, "\\bs\\b", ""),
         Embedded_text = trimws(Embedded_text)
         ) %>%
  select(tweet_ID, UserName, Timestamp, date, Embedded_text) %>%
  filter(str_count(Embedded_text, "\\w+") >= 5)

# Doc ID column
cleaned_data$doc_no <- 1:nrow(cleaned_data)

# Split into lemmas
lemma_split <- cleaned_data %>% 
  mutate(
    lemma = str_split(as.character(Embedded_text), "\\s")) %>% 
  unnest(lemma) %>%
  select(doc_no, lemma) %>%
  filter(str_detect(lemma, "[0-9]|[a-z]"))

# K-search conducted in python
# to try 15-17

# run btms
btm15 <- BTM::BTM(lemma_split, k = 15, trace = 5, iter = 500)
terms(btm15, top_n = 15)

btm16 <- BTM::BTM(lemma_split, k = 16, trace = 5, iter = 500)
terms(btm16, top_n = 15)

btm17 <- BTM::BTM(lemma_split, k = 17, trace = 5, iter = 500)
terms(btm17, top_n = 15)

