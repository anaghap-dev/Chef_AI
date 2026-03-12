import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')


def preprocess_ingredients(text):

    text = str(text).lower()
 #separates each word and commas as tokens and make text as lower
    tokens = word_tokenize(text)

    stop_words = set(stopwords.words('english'))   # remove words like this is are etc
  # remove numbers punctuations etc
    cleaned = [word for word in tokens if word.isalpha() and word not in stop_words]

    return " ".join(cleaned) # returns as text string