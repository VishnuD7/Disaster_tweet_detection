
import nltk
nltk.download('stopwords')
import pandas as pd
import numpy as np
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import re
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report


ds_train = pd.read_csv("/train.csv")
ds_test = pd.read_csv("/test.csv")
print("Train and Test data sets are imported successfully")
def drop_col(trainORtest, col_name):
    trainORtest.drop(col_name, axis=1, inplace=True)
drop_col(ds_train, "keyword")
drop_col(ds_train, "location")

drop_col(ds_test, "keyword")
drop_col(ds_test, "location")


def clean_data(name):
    # Replace email addresses with 'email'
    processed = name.str.replace(r'^.+@[^\.].*\.[a-z]{2,}$',
                                 'emailaddress')

    # Replace URLs with 'webaddress'
    processed = processed.str.replace(r'^http\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?$',
                                      'webaddress')

    # Replace money symbols with 'moneysymb' (£ can by typed with ALT key + 156)
    processed = processed.str.replace(r'£|\$', 'moneysymb')

    # Replace 10 digit phone numbers (formats include paranthesis, spaces, no spaces, dashes) with 'phonenumber'
    processed = processed.str.replace(r'^\(?[\d]{3}\)?[\s-]?[\d]{3}[\s-]?[\d]{4}$',
                                      'phonenumbr')

    # Replace numbers with 'numbr'
    processed = processed.str.replace(r'\d+(\.\d+)?', 'numbr')

    # Remove punctuation
    processed = processed.str.replace(r'[^\w\d\s]', ' ')

    # Replace whitespace between terms with a single space
    processed = processed.str.replace(r'\s+', ' ')

    # Remove leading and trailing whitespace
    processed = processed.str.replace(r'^\s+|\s+?$', '')

    # change words to lower case - Hello, HELLO, hello are all the same word
    processed = processed.str.lower()

    return processed

clean_train = clean_data(ds_train["text"])
clean_test = clean_data(ds_test["text"])


stop_words = set(stopwords.words("english"))

clean_train = clean_train.apply(lambda x:" ".join(term for term in x.split() if term not in stop_words))

clean_test = clean_test.apply(lambda x:" ".join(term for term in x.split() if term not in stop_words))



ps = PorterStemmer()

clean_train = clean_train.apply(lambda x:" ".join([ps.stem(word) for word in x.split()]))

clean_test = clean_test.apply(lambda x:" ".join([ps.stem(word) for word in x.split()]))


from nltk.stem import WordNetLemmatizer

wl = WordNetLemmatizer()
nltk.download('wordnet')
clean_train = clean_train.apply(lambda x:" ".join([wl.lemmatize(word) for word in x.split()]))

clean_test = clean_test.apply(lambda x:" ".join([wl.lemmatize(word) for word in x.split()]))


ds_train["text"] = clean_train
ds_test["text"] = clean_test

from sklearn.model_selection import train_test_split

seed = 42

X = ds_train.text
y = ds_train.target
print(X)
print(y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=seed)

vectorizer=TfidfVectorizer()
checker_pipeline = Pipeline([
            ('vectorizer', vectorizer),
            ('classifier', LogisticRegression())
        ])
vectorizer.set_params(stop_words=None, max_features=100000, ngram_range=(1,4))

sentiment_fit = checker_pipeline.fit(X_train, y_train)

y_pred = sentiment_fit.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print("accuracy score: {0:.2f}%".format(accuracy*100))
print(classification_report(y_test, y_pred, target_names=[str(i) for i in np.unique(y_test)]))

filename = "finalized_model"
joblib.dump(sentiment_fit,filename)

"""# New Section"""

filename = "finalized_model"

modelReload = joblib.load(filename)
modelReload.predict(ds_test['text'])
