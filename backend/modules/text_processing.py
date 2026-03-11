import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')

def preprocess_ingredients(text):

    tokens = word_tokenize(text.lower())

    stop_words = set(stopwords.words('english'))

    cleaned = [word for word in tokens if word.isalpha() and word not in stop_words]

    return cleaned