
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer

from pandas import Series, DataFrame, Panel
import numpy as np
import requests
import requests.auth
import pandas as pd
def generate_lda_for(df, nameofplot, num_topics):
    numberoftopics = 30
    def docs_preprocessor(docs):
        tokenizer = RegexpTokenizer(r'\w+')
        for idx in range(len(docs)):
            docs[idx] = docs[idx].lower()  # Convert to lowercase.
            docs[idx] = tokenizer.tokenize(docs[idx])  # Split into words.

        # Remove numbers, but not words that contain numbers.
        docs = [[token for token in doc if not token.isdigit()] for doc in docs]

        # Remove words that are only one character.
        docs = [[token for token in doc if len(token) > 3] for doc in docs]

        # Lemmatize all words in documents.
        lemmatizer = WordNetLemmatizer()
        docs = [[lemmatizer.lemmatize(token) for token in doc] for doc in docs]

        return docs
    docs = docs_preprocessor(list(df.body))
    print(docs)
    from gensim.models import Phrases
    # Add bigrams and trigrams to docs (only ones that appear 10 times or more).
    bigram = Phrases(docs, min_count=10)
    trigram = Phrases(bigram[docs])

    for idx in range(len(docs)):
        for token in bigram[docs[idx]]:
            if '_' in token:
                # Token is a bigram, add to document.
                docs[idx].append(token)
        for token in trigram[docs[idx]]:
            if '_' in token:
                # Token is a bigram, add to document.
                docs[idx].append(token)

    from gensim.corpora import Dictionary

    # Create a dictionary representation of the documents.
    dictionary = Dictionary(docs)
    print('Number of unique words in initital documents:', len(dictionary))

    # Filter out words that occur less than 10 documents, or more than 20% of the documents.
    dictionary.filter_extremes(no_below=10, no_above=0.2)
    print('Number of unique words after removing rare and common words:', len(dictionary))
    corpus = [dictionary.doc2bow(doc) for doc in docs]
    print('Number of unique tokens: %d' % len(dictionary))
    print('Number of documents: %d' % len(corpus))

    from gensim.models import LdaModel

    # def check_number_topics(num_topics):
    #     print('Current number of topics:'+str(num_topics))
    # num_topics = 30
    chunksize = 500 # size of the doc looked at every pass
    passes = 20 # number of passes through documents
    iterations = 400
    eval_every = 1  # Don't evaluate model perplexity, takes too much time.

    # Make a index to word dictionary.
    # temp = dictionary[0]  # This is only to "load" the dictionary.
    id2word = dictionary.id2token

    model = LdaModel(corpus=corpus, id2word=id2word, chunksize=chunksize, \
                           alpha='auto', eta='auto', \
                           iterations=iterations, num_topics=num_topics, \
                           passes=passes, eval_every=eval_every)

    from array import array


    from sklearn.metrics.pairwise import cosine_similarity

    from collections import OrderedDict
    import numpy as np

    def get_doc_topic_dist(model, corpus, kwords=False):

        '''
        LDA transformation, for each doc only returns topics with non-zero weight
        This function makes a matrix transformation of docs in the topic space.
        '''
        top_dist =[]
        keys = []

        for d in corpus:
            tmp = {i:0 for i in range(num_topics)}
            tmp.update(dict(model[d]))
            vals = list(OrderedDict(tmp).values())
            top_dist += [np.asarray(vals)]
            if kwords:
                keys += [np.asarray(vals).argmax()]

        return np.asarray(top_dist), keys

    # def test_num_topics():
    df['tokenz'] = docs

    docs1 = df['tokenz'].apply(lambda l: l[:int(len(l)/2)])
    docs2 = df['tokenz'].apply(lambda l: l[int(len(l)/2):])

    corpus1 = [dictionary.doc2bow(doc) for doc in docs1]
    corpus2 = [dictionary.doc2bow(doc) for doc in docs2]

    # Using the corpus LDA model tranformation
    lda_corpus1 = model[corpus1]
    lda_corpus2 = model[corpus2]
    top_dist1, _ = get_doc_topic_dist(model, lda_corpus1)
    top_dist2, _ = get_doc_topic_dist(model, lda_corpus2)

    print("Intra similarity: cosine similarity for corresponding parts of a doc(higher is better):")
    a = np.mean([cosine_similarity(c1.reshape(1, -1), c2.reshape(1, -1))[0][0] for c1,c2 in zip(top_dist1, top_dist2)])
    print(a)

    random_pairs = np.random.randint(0, len(df['body']), size=(400, 2))

    print("Inter similarity: cosine similarity between random parts (lower is better):")
    b = np.mean([cosine_similarity(top_dist1[i[0]].reshape(1, -1), top_dist2[i[1]].reshape(1, -1)) for i in random_pairs])
    
    print(b)
    import pyLDAvis
    import pyLDAvis.gensim
    pyLDAvis.enable_notebook()

    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning) 
    p = pyLDAvis.gensim.prepare(model, corpus, dictionary)
    pyLDAvis.save_html(p, str(nameofplot)+'.html')
    return(str(nameofplot)+'.html')