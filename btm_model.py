import pandas as pd
import bitermplus as btm
import matplotlib.pyplot as plt

# Load data
data = pd.read_csv("/Users/jamiesanders/Desktop/CBQ_dissertation/data/sample_36_lemmatised.csv")

# prepare BTM files
X, vocabulary, vocab_dict = btm.get_words_freqs(data["prepared_texts"])
docs_vec = btm.get_vectorized_docs(data["prepared_texts"], vocabulary)
biterms = btm.get_biterms(docs_vec)

