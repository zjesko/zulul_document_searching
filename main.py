# import xapian
import os
import sys
import re
import nltk
import string
import pandas as pd
import csv
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.corpus import words

# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')

stop_words = stopwords.words('english')

fdf = pd.read_csv("fulltext.csv")
adf = pd.read_csv("summaries.csv",header=None)
no_full = fdf.shape[0]
no_abs = adf.shape[0]

def remove_brackets(st):
    ret = ''
    skip1c = 0
    skip2c = 0
    for i in st:
        if i == '[': skip1c +=1
        elif i == '{': skip2c +=1
        if i == ']' and skip1c > 0: skip1c -=1
        if i == '}' and skip2c > 0: skip2c -=1
        elif skip1c == 0 and skip2c == 0: ret += i
    return ret

def clean(t):
    text = remove_brackets(t)
    text = text.replace('>', ' greater than ')
    text = text.replace('<', ' less than ')
    text = text.replace('=', ' equal to ')
    text = text.replace('\n', ' ')
    text = text.replace('- ', '')
    tokens = word_tokenize(text)
    lowert = []
    for token in tokens:
        lowert.append(token.lower())
    for token in lowert:
        if token in stop_words:
            lowert.remove(token)
    lowert = list(filter(lambda a: a not in string.punctuation, lowert))
    #Synonym Code (maybe insert into lowert list)
    return " ".join(lowert)

#List of abstract strings and full strings
abstracts = []
fulls = []

# print(adf)
def exists(w):
    return w.lower() in word.words()
for index , row in adf.iterrows():
    text = remove_brackets(str(row[0]))
    cleaned_text = clean(text)
    
    #Synonym Code (maybe insert into cleaned text)
    abstracts.append(cleaned_text)

for i in range(no_full):
    text = remove_brackets(fdf.loc[i, "paper_text"])
    cleaned_text = clean(text)
    fulls.append(cleaned_text)

#Answer Matrix
# matrix = []

#Xapian code start

#indexing

dbpath = sys.argv[1]

def index(i, dbpath):

    db = xapian.WritableDatabase(dbpath, xapian.DB_CREATE_OR_OPEN)

    content = fulls[i]
    print(content);
    termgen = xapian.TermGenerator()
    termgen.set_stopper_strategy(xapian.TermGenerator.STOP_ALL)
    termgen.set_stemmer(xapian.Stem('en'))

    doc = xapian.Document()
    termgen.set_document(doc)

    termgen.index_text(content)
    db.add_document(doc)
    f.close();

for i in range(no_full):
    index(i, dbpath)

#querying for relevance

def search(dbpath, querystring, offset=0, pagesize=10):

    db = xapian.Database(dbpath)

    queryparser = xapian.QueryParser()
    queryparser.set_stemmer(xapian.Stem("en"));
    queryparser.set_stemming_strategy(queryparser.STEM_ALL)

    query_terms = querystring.split(' ')
    query_terms[0] = query_terms[0].lower()
    query = xapian.Query(query_terms[0])
    query = xapian.Query(100, query)
    for i in range(1, len(query_terms)):
        query_terms[i] = query_terms[i].lower()
        query2 = xapian.Query(query_terms[i])
        # if query_terms[i] is "5g":
        #     print("does come here")
        #     query2 = xapian.Query(100, query2)
        query = xapian.Query(xapian.Query.OP_OR, query,
                query2)

    print(query)

    enquire = xapian.Enquire(db)
    enquire.set_query(query)

    matches = []

    mset = enquire.get_mset(offset, pagesize)

    for match in enquire.get_mset(offset, pagesize):
        matches.append(match.docid)
    
    return matches

for i in range(no_abstracts):
    temp = []
    all_matches = search(dbpath, abstracts[i])
    for j in range(no_fulls):
        cnt = 0
        for match in all_matches:
            if match.docid == j:
                temp.append(match.weight)
                cnt = 1
        if not cnt:
            temp.append(0)

    matrix.append(temp)


#Xapian Code end

with open("./output_matrix.csv", "w+", newline = "") as f:
    writer = csv.writer(f)
    writer.writerows(martix)
