library(tidyverse)
library(tm)
library(lubridate)

setwd("/Users/jamiesanders/Desktop/CBQ_dissertation")

##### Data loading #####

# Load data
raw_extract <- read_csv(file = "data/sample30_checked.csv")

# Regex to detect BOE
check_regex <- "bank of england|(\\b|#)boe\\b|(\\b|#)bofe|bankofengland|bank #of england|bank #of #england|bank of #england"

gsub("Replying to \\n.*\\n\\s", "",raw_extract$Embedded_text[5])

# Following cleaning:
# All tweet text to lower case
# All extra spaces removed
# All leading and trailing spaces removed
# Only keep texts longer than 5 words
# Make sure Bank of England is mentioned in accordance to check_regex
# Exclude BOE tweets
cleaned_data <- raw_extract %>%
  mutate(
    tweet_ID = 1:nrow(raw_extract),
    gsub("^Replying to \\n.*\\n\\s", "", Embedded_text),
    Embedded_text = tolower(Embedded_text),
    Embedded_text = str_replace_all(Embedded_text, "\\s+", " "),
    Embedded_text = trimws(Embedded_text),
    Embedded_text = removePunctuation(Embedded_text),
    Embedded_text = gsub("[a-z0-9]*…|’", "", Embedded_text)) %>%
  select(tweet_ID, UserName, Timestamp, date, Embedded_text) %>%
  filter(str_count(Embedded_text, "\\w+") >= 5,
         str_detect(Embedded_text, check_regex),
         UserName != "@bankofengland")

###### detecting #########

# Load words 
dict <- read_csv("data/dictionary.csv")
dict$regex <- paste0("\\b", dict$phrase, "\\b")

+# main search
hit_detecter <- function(text, dictionary = dict) {
  
  hits <- str_detect(text, dictionary$regex)
  n_hits <- sum(hits)
  cats <- paste(unique(dict$category[hits]), collapse = ", ", sep = ", ")

  return(list(n_hits, cats))
  
}

hits_data <- cleaned_data
hits_data$n_hits <- NA
hits_data$hit_cats <- NA

for (i in 1:nrow(hits_data)) {
  
  hits <- hit_detecter(hits_data$Embedded_text[i]) 
  hits_data$n_hits[i] <- hits[[1]]
  if (length(hits[[2]]) != 0) {
      hits_data$hit_cats[i] <- hits[[2]]
  }
}

sum(hits_data$n_hits)

plot_data <- hits_data %>%
  group_by(year = lubridate::floor_date(date, "year")) %>%
  summarise(hits = sum(n_hits > 0), n = n())

ggplot(plot_data, aes(x = year, y = hits*100/n)) + geom_line() +
  theme_bw() +
  labs(x = 'Year',
       y = "Hit rate (%)",
       title = 'Percentage of Tweets containing conspiratorial terms')

