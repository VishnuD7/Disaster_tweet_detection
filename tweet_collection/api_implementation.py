
import tweepy
import csv
import ssl
import time
import datetime
from requests.exceptions import Timeout, ConnectionError
from requests.packages.urllib3.exceptions import ReadTimeoutError

# Add your Twitter API credentials
consumer_key = "consumer_key"
consumer_secret = "consumer_secret_key"
access_key = "Access_key"
access_secret = "Secret_key"

# Handling authentication with Twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)

# Create a wrapper for the API provided by Twitter
api = tweepy.API(auth)

# Setting up the keywords, hashtag or mentions we want to listen
keywords = ["disaster", "wildfire", "earthquake", "shootout", "flood", "#forestfire", "Cyclone", "wildfire", "tsunami", "typhoon",
            "strom", "volcanic eruptions", "landslide", "aftershock", "accident","ablaze", "airplane accident","ambulance", "annihilated",
            "armageddon", "arson", "arsonist", "attack", "attacked", "battle", "bioterror", "blood", "blown up", "body bagging", "bomb",
            "bombed", "bombing", "bridge collapse", "buildings burning", "burned", "bush fires", "casualties", "catastrophe", "chemical emergency",
            "collapse", "collision", "crash", "damage", "danger", "dead", "deaths", "debris", "demolish", "demolition", "derail", "destroy", "destruction",
            "detonate", "detonation", "devastated", "drought", "dust storm", "emergency", "emergency plan", "engulfed", "evacuate", "evacuation",
            "explode", "exploded", "explosion", "famine", "fatal", "fatalities", "fear", "fire", "fire truck", "flames", "flooding", "hail",
            "hailstorm", "hazard", "hazardous", "heat wave", "hellfire", "hijack", "hijacker", "hostage", "hurricane", "injured", "lava",
            "lightning", "loud bang", "mass murder", "massacre", "mayhem", "meltdown", "military", "mudslide", "natural disaster", 
            "nuclear disaster", "obiliterate", "oil spill", "outbreak", "panic", "police", "radiation emergency", "rainstorm", "razed",
            "refugees", "rescue", "rescued", "riot", "sandstorm", "screaming", "seismic", "sinkhole", "siren", "smoke", "snowstorm", "stretcher",
            "structural failure", "suicide bomb", "sunk", "survive", "terrorism", "terrorist", "threat", "thunder", "thunderstorm", "tornado",
            "tragedy", "trapped", "upheaval", "violent storm", "volcano", "war zone", "weapon", "whirlwind", "wild fire","windstorm",
            "wounded", "wreck"]

# Set the name for CSV file  where the tweets will be saved
filename = "tweets"

# We need to implement StreamListener to use Tweepy to listen to Twitter
class StreamListener(tweepy.StreamListener):

    def on_status(self, status):

        try:
            # saves the tweet object
            tweet_object = status

            # Checks if its a extended tweet (>140 characters)
            if 'extended_tweet' in tweet_object._json:
                tweet = tweet_object.extended_tweet['full_text']
            else:
                tweet = tweet_object.text

            '''Convert all named and numeric character references
            (e.g. &gt;, &#62;, &#x3e;) in the string s to the
            corresponding Unicode characters'''
            tweet = (tweet.replace('&amp;', '&').replace('&lt;', '<')
                     .replace('&gt;', '>').replace('&quot;', '"')
                     .replace('&#39;', "'").replace(';', " ")
                     .replace(r'\u', " "))

            # Save the keyword that matches the stream
            keyword_matches = []
            for word in keywords:
                if word.lower() in tweet.lower():
                    keyword_matches.extend([word])

            keywords_strings = ", ".join(str(x) for x in keyword_matches)

            # Save other information from the tweet
            user = status.author.screen_name
            location = status.user.location 
            timeTweet = status.created_at
            tweetId = status.id
            tweetUrl = "https://twitter.com/statuses/" + str(tweetId)

            # Exclude retweets, too many mentions and too many hashtags
            if not any((('RT @' in tweet, 'RT' in tweet,
                       tweet.count('@') >= 2, tweet.count('#') >= 4))):

                # Saves the tweet information in a new row of the CSV file
                writer.writerow([user, location, tweet, keywords_strings, timeTweet,
                                  tweetUrl])

        except Exception as e:
            print('Encountered Exception:', e)
            pass

def work():

    # Opening a CSV file to save the gathered tweets
    with open(filename+".csv", 'w') as file:
        global writer
        writer = csv.writer(file)

        # Add a header row to the CSV
        writer.writerow(["User","Location", "Tweet", "Matched Keywords", "Date", 
                         "Tweet URL"])

        # Initializing the twitter streap Stream
        try:
            streamingAPI = tweepy.streaming.Stream(auth, StreamListener())
            streamingAPI.filter(track=keywords)

        # Stop temporarily when hitting Twitter rate Limit
        except tweepy.RateLimitError:
            print("RateLimitError...waiting ~15 minutes to continue")
            time.sleep(1001)
            streamingAPI = tweepy.streaming.Stream(auth, StreamListener())
            streamingAPI.filter(track=[keywords])

        # Stop temporarily when getting a timeout or connection error
        except (Timeout, ssl.SSLError, ReadTimeoutError,
                ConnectionError) as exc:
            print("Timeout/connection error...waiting ~15 minutes to continue")
            time.sleep(1001)
            streamingAPI = tweepy.streaming.Stream(auth, StreamListener())
            streamingAPI.filter(track=[keywords])

        # Stop temporarily when getting other errors
        except tweepy.TweepError as e:
            if 'Failed to send request:' in e.reason:
                print("Time out error caught.")
                time.sleep(1001)
                streamingAPI = tweepy.streaming.Stream(auth, StreamListener())
                streamingAPI.filter(track=[keywords])
            else:
                print("Other error with this user...passing")
                pass

if __name__ == '__main__':

    work()

import pandas as pd

ds_today=pd.read_csv(filename + datetime.datetime.now().strftime("%Y-%m-%d-%H")+".csv")
print(ds_today["Tweet"])

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


ds_today["Tweet"] = clean_data(ds_today["Tweet"])
print(ds_today["Tweet"])

import nltk
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

stop_words = set(stopwords.words("english"))

ds_today["Tweet"] = ds_today["Tweet"].apply(lambda x:" ".join(term for term in x.split() if term not in stop_words))
ps = PorterStemmer()

ds_today["Tweet"] = ds_today["Tweet"].apply(lambda x:" ".join([ps.stem(word) for word in x.split()]))


wl = WordNetLemmatizer()

ds_today["Tweet"] = ds_today["Tweet"].apply(lambda x:" ".join([wl.lemmatize(word) for word in x.split()]))
print(ds_today["Tweet"])

