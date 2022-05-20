library(tidyverse)
library(BTM)
library(udpipe)
library(tm)
library(textplot)
library(ggraph)
library(concaveman)

setwd("/Users/jamiesanders/Desktop/CBQ_dissertation")

##### Data loading #####

# Load data
raw_extract <- read_csv(file = "data/sample30_checked.csv")

# Regex to detect BOE
check_regex <- "bank of england|(\\b|#)boe\\b|(\\b|#)bofe|bankofengland|bank #of england|bank #of #england|bank of #england"

# Following cleaning:
# All tweet text to lower case
# All extra spaces removed
# All leading and trailing spaces removed
# Only keep texts longer than 5 words
# Make sure Bank of England is mentioned in accordance to check_regex
# Exclude BOE tweets
cleaned_data <- raw_extract %>%
  mutate(tweet_ID = 1:nrow(raw_extract),
         Embedded_text = tolower(Embedded_text),
         Embedded_text = str_replace_all(Embedded_text, "\\s+", " "),
         Embedded_text = trimws(Embedded_text)) %>%
  select(tweet_ID, UserName, Timestamp, date, Embedded_text) %>%
  filter(str_count(Embedded_text, "\\w+") >= 5,
         str_detect(Embedded_text, check_regex),
         UserName != "@bankofengland")

##### Descriptive statistics #####

# Frequency table by date
frequency_table <- cleaned_data %>%
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
for_btm <- cleaned_data %>%
  select(Embedded_text) %>%
  mutate(
    Embedded_text = gsub(check_regex, "", Embedded_text),
    Embedded_text = gsub("[a-z0-9]*…|’", "", Embedded_text),
    Embedded_text = tm::removeWords(Embedded_text, stopwords()),
    Embedded_text = tm::stemDocument(Embedded_text),
    Embedded_text = gsub("\\shttp.*$", "", Embedded_text),
    Embedded_text = removePunctuation(Embedded_text))

# Doc ID column
for_btm$doc_no <- 1:nrow(for_btm)

# Split into lemmas
lemma_split <- for_btm %>% 
  mutate(
    lemma = str_split(as.character(Embedded_text), "\\s")) %>% 
  unnest(lemma) %>%
  select(-Embedded_text) %>%
  filter(str_detect(lemma, "[0-9]|[a-z]"))

# run btm 10
btm10 <- BTM::BTM(lemma_split, k = 10, trace = 5, iter = 500)
terms(btm10, top_n = 10)
plot(btm10)

# I might re-run this in Python for a K-search
