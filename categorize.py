import pandas as pd
import numpy as np
import re
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import linear_kernel
import pickle


def categorize_csv(scraped_csv, categorized_csv):
    save_to_file = open(categorized_csv, 'w')
    save_to_file.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s \n' % ('UPC_code', 'title', 'brand', 'description+dimensions',"height", "width", "length", "weight", "color", "size","family","class"))
    df = pd.read_csv('GS1-processed.csv')
    vectorizer = pickle.load(open('vectorizer.sav', 'rb'))
    df['Doc_vec'] = df.apply(lambda row: vectorizer.transform([row['Doc']]), axis = 1)
    ps = PorterStemmer()
    with open(scraped_csv, 'r',encoding='utf-8',errors='ignore') as csv:
        lines = csv.readlines()
        for i, line in enumerate(lines):
            if i == 0:
                continue # pass header
            try:
                lis = line.split(',')
                string = lis[1]
                string = string.lower()
                string = re.sub(r'[^A-Za-z0-9]+',' ',string)
                string = nltk.word_tokenize(string)
                string = [ps.stem(w) for w in string]
                string = ' '.join(string)
                string_vec = vectorizer.transform([string])
                df['sim'] = df.apply(lambda row: linear_kernel(string_vec, row['Doc_vec'])[0][0], axis = 1)
                ind = df['sim'].idxmax()
                class_des = df.iloc[ind]['Class Description'].strip(',')[0]
                save_to_file.write('%s,%s,%s \n' % (line.strip('\n'), df.iloc[ind]['Family Description'], class_des))

            except:
                pass
            if i>100:
                break
            if i%10 ==0:
                print(i, 'UPC codes categorized.')
    save_to_file.close()
    return categorized_csv

if __name__ == '__main__':
    scraped_csv = 'UPC-scraped.csv'
    categorized_csv = scraped_csv[:-11] + 'categorized.csv'
    categorize_csv(scraped_csv, categorized_csv)


