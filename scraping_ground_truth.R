library(dplyr)
library(rvest)
library(xml2)

## Scraping newspunch.com

URL_prefix <- "https://newspunch.com/page/"
URL_suffix <- "/?s=%22Bank+of+England%22"
pages <- 1:9

search_URLs <- paste0(URL_prefix, pages, URL_suffix)

findArticles <- function(search_URL) {
  
  article_URLs <- search_URLs[9] %>%
    read_html() %>%
    html_nodes(".entry-title.mh-posts-list-title") %>%
    html_nodes("a") %>%
    html_attr("href")
  
  return(article_URLs)
  
}

article_URLs <- sapply(search_URLs, findArticles) %>%
  as.vector()


article_URLs[1] %>%
  read_html() %>%
  html_nodes('.entry-content.clearfix') %>%
  html_nodes('blockquote') %>%
  html_text(trim = TRUE)

 lines <- article_URLs[60] %>%
  read_html() %>%
  html_nodes(".entry-content.clearfix") %>%
  html_nodes(xpath = '//p[not(@id or @class)]') %>%
  html_text(trim = TRUE)

  html_text(trim = TRUE)
    
