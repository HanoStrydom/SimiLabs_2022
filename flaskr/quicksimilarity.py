import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Cosine Similarity is a method of calculating the similarity of two vectors by 
# taking the dot product and dividing it by the magnitudes of each vector
# It is a method where text is transformed into numbers and stored in a vector
# https://en.wikipedia.org/wiki/Cosine_similarity

count_vect = CountVectorizer()
vectorizer = TfidfVectorizer()

def calc_cosine_similarity(x,y):
  color = ""
  corpus = [x,y]
  X_train_counts = count_vect.fit_transform(corpus)
  # creates a vector containing the two documents' word-to-numeric conversions
  pd.DataFrame(X_train_counts.toarray(),columns=count_vect.get_feature_names(),index=['Document 1','Document 2'])

  # Term Frequency Inverse Document Frequency (TFIDF). 
  # Technique to measure how unique a certain word is relative to every other word in a document. 
  # This is calculated on a scale from 0–1 with the most common words approaching 0 and the most unique words approaching 1. 
  trsfm=vectorizer.fit_transform(corpus)
  pd.DataFrame(trsfm.toarray(),columns=vectorizer.get_feature_names(),index=['Document 1','Document 2'])
  # this returns a matrix in the form of [[trsfm[0:1], trsfm]]. Calculates the cosine_similarity (trsfm)
  val = cosine_similarity(trsfm[0:1], trsfm)
  # print(f"Value: {val}")
  if val[0][1] > 0.00 and val[0][1] <= 0.25:
    color = "green"
  elif val[0][1] > 0.25 and val[0][1] <= 0.5:
    color = "yellow"
  elif val[0][1] > 0.50 and val[0][1] <= 0.75:
    color = "orange"
  elif val[0][1] > 0.75 and val[0][1] <= 1.0:
    color = "red"
  else:
    color = "black"

  # returns a tuple of the similarity score and the color
  return val[0][1],color

def jaccard_similarity(x,y):
  # returns the jaccard similarity between two lists
  color = ""
  intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
  union_cardinality = len(set.union(*[set(x), set(y)]))
  val = intersection_cardinality/float(union_cardinality)
  # determine color of text on frontend based on the sililarity score
  if val > 0.00 and val <= 0.25:
    color = "green"
  elif val > 0.25 and val <= 0.5:
    color = "yellow"
  elif val > 0.50 and val <= 0.75:
    color = "orange"
  elif val > 0.75 and val <= 1.0:
    color = "red"
  else:
    color = "black"

  # returns a tuple of the similarity score and the color
  return val,color
  
  
  
  
  
  
  
  
