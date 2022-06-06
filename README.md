# CBQ_dissertation

## Pipeline
1. scraper_36sample.py

Runs scweet tweet scraper to create dataset. Runs some initial checks on dataset and cleaning. Saves final dataset for use in later files.

2. btm_python.py

Model selection for BTM. Uses output from scraper_36sample.py and runs a wide then narrow K-search using coherence. Semantic coherence plot saved. Final model selected, run and inference conducted.

3. dataset_desc.R

Provides some descriptive statistics on the tweet dataset.

4. dictionary_approach.R

