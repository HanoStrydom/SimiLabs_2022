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