import re

import pandas as pd
import bitermplus as btm
from statistics import mean
import matplotlib.pyplot as plt

from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

ps = PorterStemmer()
stops = stopwords.words('english')

# Load data
data = pd.read_csv("/Users/jamiesanders/Desktop/CBQ_dissertation/data/sample36_checked.csv")

# remove links
data['Embedded_text'] = data['Embedded_text'].apply(
    lambda x: re.sub(r'\b(http|www).*\b', '', x))

# Keep just characters
data['Embedded_text'] = data['Embedded_text'].apply(
    lambda x: re.sub('[^a-zA-Z\s]+', '', x))

# Keep just characters
data['Embedded_text'] = data['Embedded_text'].apply(lambda x: x.lower())

# Remove BOE
data['Embedded_text'] = data['Embedded_text'].apply(
    lambda x: re.sub(r"bank of england|\bboe\b|bankofengland", "", x))

# Make list
texts = data['Embedded_text'].to_list()

# Tokenise
prepared_texts = []
for text in texts:
    
    words = word_tokenize(text)
    
    # Stem and stopwords
    filtered_words = [ps.stem(word) for word in words if word not in stops and len(word) >= 2]
    
    # paste back together
    clean_text = " ".join(filtered_words)

    prepared_texts.append(clean_text)

data["prepared_texts"] = prepared_texts

# Keep only >=2 words (Yan, Xiaohui, et al. keeps all >1)
data = data.loc[[len(s.split()) >= 2 for s in data["prepared_texts"]] , ]

# prepare BTM files
X, vocabulary, vocab_dict = btm.get_words_freqs(data["prepared_texts"], stop_words=stops)
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
for k in range(7, 26, 1):

    model = btm.BTM(
        X, vocabulary, seed=42, T=k, M=20, alpha=50/k, beta=0.01)
    model.fit(biterms, iterations=150)
    
    sem_co_near.append(mean(model.coherence_))

# plot
plt.plot(range(7, 26, 1), sem_co_near, color='black')
plt.ylabel("Average semantic coherence")
plt.xlabel("Topics")
plt.locator_params(axis="both", integer=True, tight=True)
# plt.savefig('write_up/narrow_k_search.pdf',  bbox_inches='tight')
plt.show()

fig, axs = plt.subplots(2, sharey=True)
axs[0].plot(range(5, 105, 5), sem_co, color='black')
axs[1].plot(range(7, 26, 1), sem_co_near, color='black')
axs[0].locator_params(axis="both", integer=True, tight=True)
axs[1].locator_params(axis="both", integer=True, tight=True)
axs[0].set_yticks(range(-730, -650, 15))
fig.text(0, 0.5, 'Model average semantic coherence', va='center', rotation='vertical')
axs[1].set_xlabel('Topics')
plt.savefig('write_up/k_search.pdf',  bbox_inches='tight')
plt.show()

# Save data
data.to_csv("/Users/jamiesanders/Desktop/CBQ_dissertation/data/sample_36_lemmatised.csv")
