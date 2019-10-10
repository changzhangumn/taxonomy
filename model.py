import pandas as pd
import numpy as np
import re
import nltk
import pickle

# set display options
pd.set_option('display.max_columns', 15)
pd.set_option('display.max_colwidth', 500)

# data slicing
df = pd.read_csv('GS1.csv')
df = df.iloc[:,2:12]
df['index'] = range(0, len(df))
df = df.dropna()

# create document and clean
df['Doc'] = df['Family Description']+' '+df['Class Description']+' '+df['Brick Description'] +' '+df['Core Attribute  Type Description']+' '+df['Core Attribute Value Description']
df['Doc'] = df.apply(lambda row: row['Doc'].lower(), axis=1)
df['Doc'] = df.apply(lambda row: re.sub(r'[^A-Za-z0-9]+',' ',row['Doc']), axis=1)

# downsize and remove duplicate rows
df = df.drop(columns=['Core Attribute Type Code', 'Core Attribute  Type Description', 'Core Attribute Value Code', 'Core Attribute Value Description', 'index'])
df = df.drop_duplicates()

# tokenize
from nltk.tokenize import word_tokenize
df['Doc'] = df.apply(lambda row: nltk.word_tokenize(row['Doc']), axis=1)

# stem
from nltk.stem import PorterStemmer
ps = PorterStemmer()
df['Doc'] = df.apply(lambda row: [ps.stem(w) for w in row['Doc']], axis=1)

# create corpus for fitting
corpus = []
for i, row in df.iterrows():
    lis = []
    j = 0

    while j < len(row['Doc']):
        if row['Doc'][j] == 'non':
            j += 2
        else:
            lis.append(row['Doc'][j])
            j += 1

    info = ' '.join(lis)
    df.at[i,'Doc'] = info
    corpus.append(info)

# vectorize
from sklearn.feature_extraction.text import CountVectorizer
vectorizer = CountVectorizer()
vectorizer.fit(corpus)

# save fitted model
filename = 'vectorizer.sav'
pickle.dump(vectorizer, open(filename, 'wb'))

# save dataframe
df.to_csv('GS1-processed.csv')

