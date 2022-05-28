import re
import string

import pandas as pd
import numpy as np
import bitermplus as btm
from statistics import mean
import matplotlib.pyplot as plt

from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

ps = PorterStemmer()
stops = stopwords.words('english')

# Load data
data = pd.read_csv("/Users/jamiesanders/Desktop/CBQ_dissertation/data/sample30_checked.csv")

# Remove reply stuff
data['Embedded_text'] = data['Embedded_text'].apply(
    lambda x: re.sub(r"^Replying to\s+\n.*\n.*\n\s+", "", x))
data['Embedded_text'] = data['Embedded_text'].apply(
    lambda x: re.sub(r"^Replying to\s+\n@.*\n", "", x))

# Remove RT stuff
data['Embedded_text'] = data['Embedded_text'].apply(
    lambda x: re.sub(r"RT\s*\n.*\n:\s+", "", x))

# Remove punctuation
data['Embedded_text'] = data['Embedded_text'].apply(
    lambda x: x.translate(str.maketrans('', '', string.punctuation))
    .lower())

# Keep only that mention BOE
data = data.loc[data['Embedded_text'].str.contains(r"bank of england|\bboe\b|bankofengland"), ]
data = data.loc[data['UserName'] != "@bankofengland", ]

# Remove BOE
data['Embedded_text'] = data['Embedded_text'].apply(
    lambda x: re.sub(r"bank of england|\bboe\b|bankofengland", "", x))
data['Embedded_text'] = data['Embedded_text'].apply(
    lambda x: re.sub(r"\b[’]*s\b|’", "", x))

# Keep only >=10 words
data = data.loc[[len(s.split()) >= 10 for s in data['Embedded_text']] , ]

# Make list
texts = data['Embedded_text'].to_list()

# Tokenise
prepared_texts = []
for text in texts:
    
    words = word_tokenize(text)
    
    # Stem and stopwords
    filtered_words = [ps.stem(word) for word in words if word not in stops]
    
    # paste back together
    clean_text = " ".join(filtered_words)

    prepared_texts.append(clean_text)

# prepare BTM files
X, vocabulary, vocab_dict = btm.get_words_freqs(prepared_texts, stop_words=stops)
docs_vec = btm.get_vectorized_docs(texts, vocabulary)
biterms = btm.get_biterms(docs_vec)

# Coherance search
sem_co = []
for k in range(5, 105, 5):

    model = btm.BTM(
        X, vocabulary, seed=42, T=k, M=20, alpha=50/k, beta=0.01)
    model.fit(biterms, iterations=100)
    
    sem_co.append(mean(model.coherence_))

# plot
plt.plot(range(5, 105, 5), sem_co, color='black')
plt.ylabel("Average semantic coherence")
plt.xlabel("Topics")
plt.locator_params(axis="both", integer=True, tight=True)
# plt.savefig('write_up/wide_k_search.pdf', bbox_inches='tight')
plt.show()


sem_co_near = []
for k in range(15, 36, 2):

    model = btm.BTM(
        X, vocabulary, seed=42, T=k, M=20, alpha=50/k, beta=0.01)
    model.fit(biterms, iterations=100)
    
    sem_co_near.append(mean(model.coherence_))

# plot
plt.plot(range(15, 36, 2), sem_co_near, color='black')
plt.ylabel("Average semantic coherence")
plt.xlabel("Topics")
plt.locator_params(axis="both", integer=True, tight=True)
# plt.savefig('write_up/narrow_k_search.pdf',  bbox_inches='tight')
plt.show()

fig, axs = plt.subplots(2, sharey=True)
axs[0].plot(range(5, 105, 5), sem_co, color='black')
axs[1].plot(range(15, 36, 2), sem_co_near, color='black')
axs[0].locator_params(axis="both", integer=True, tight=True)
axs[1].locator_params(axis="both", integer=True, tight=True)
axs[0].set_yticks(range(-710, -650, 15))
fig.text(0, 0.5, 'Model average semantic coherence', va='center', rotation='vertical')
axs[1].set_xlabel('Topics')
plt.savefig('write_up/k_search.pdf',  bbox_inches='tight')
plt.show()