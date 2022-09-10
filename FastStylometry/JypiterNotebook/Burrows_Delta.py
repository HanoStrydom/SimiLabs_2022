from faststylometry import Corpus
from faststylometry import load_corpus_from_folder
from faststylometry import tokenise_remove_pronouns_en
from faststylometry import calculate_burrows_delta
from faststylometry import predict_proba, calibrate, get_calibration_curve

train_corpus = load_corpus_from_folder("faststylometry/data/train")
train_corpus.tokenise(tokenise_remove_pronouns_en)

# Load Sense and Sensibility, written by Jane Austen (marked as "janedoe")
# and Villette, written by Charlotte Bronte (marked as "currerbell", Bronte's real pseudonym)
test_corpus = load_corpus_from_folder("faststylometry/data/test", pattern=None)

# You can set pattern to a string value to just load a subset of the corpus.
test_corpus.tokenise(tokenise_remove_pronouns_en)

calculate_burrows_delta(train_corpus, test_corpus, vocab_size = 50)