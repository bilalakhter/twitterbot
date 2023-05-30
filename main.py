import os 
import re
from dotenv import load_dotenv
import tweepy
import csv
import pandas as pd
import threading
import time
import random
from datetime import datetime, timedelta
import datetime
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("Api_Key_Secret")
BEARER_TOKEN = os.getenv("Bearer_Token")
ACCESS_TOKEN = os.getenv("Access_Id")
ACCESS_TOKEN_SECRET = os.getenv("Access_secret")
client = tweepy.Client(BEARER_TOKEN , API_KEY , API_KEY_SECRET , ACCESS_TOKEN , ACCESS_TOKEN_SECRET)



# extras

def log_tweets():
    print("logging tweets")
    with open("tweets.csv", "r", encoding="utf-8") as tweets_file:
        tweets_reader = csv.reader(tweets_file)
        next(tweets_reader)

        with open("log.csv", "a", newline="", encoding="utf-8") as log_file:
            log_writer = csv.writer(log_file, quoting=csv.QUOTE_NONNUMERIC)
            for row in tweets_reader:
                tweet_id = row[0]  # Assuming the tweet ID is in the first column
                username = row[1]  # Assuming the username is in the second column

                tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"
                log_writer.writerow([tweet_url])

log_tweets()



def extract_tweet_ids(csv_file, output_file):
    print("extracting tweet ids")
    df = pd.read_csv(csv_file)  
    tweet_ids = df["id"].astype(str) 
    tweet_ids.to_csv(output_file, index=False) 

    

def clear_tweets():
    print("clearing tweets")
    with open("tweets.csv", "w", encoding="utf-8") as tweets_file:
        tweets_file.write("")



def read_csv(file_path):
    df = pd.read_csv(file_path)
    return df



def clear_tweet_id():
    print("clearing tweet ids")
    file_path = 'tweet_id.csv'

  
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows([])

    print(f"Cleared content of {file_path} successfully.")





def clear_tweets_owner():
    print("clearing temp cache of your tweets to get update")
    with open("tweets_owner.csv", "w", encoding="utf-8") as tweets_file:
        tweets_file.write("")

def clear_tweet_id_owner():
    file_path = 'tweets_owner_id.csv'

  
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows([])

    print(f"Cleared content of {file_path} successfully.")




# extras end


# tasks

list_search_keywords1 = os.getenv("list_search_keywords")
list_search_keywords2 = list_search_keywords1.split(",")
list_search_keywords = [keyword.strip() for keyword in list_search_keywords2]
list_id1 = os.getenv("list_id")
list_id2 = list_id1.split(",")
list_id = random.choice(list_id2)
reply_phrase_task1 = os.getenv("reply_phrase_task1")
reply_phrase_list_task1 = reply_phrase_task1.split(",")
interval_task1 = int(os.getenv("interval_task1"))
starting_time_task1 = os.getenv("starting_time_task1")
ending_time_task1 = os.getenv("ending_time_task1")
running_task1 = os.getenv("running_task1")

def get_list_tweets(list_id):
    tweets = client.get_list_tweets(id=list_id, max_results=95)
    tweet_data = tweets.data
    result = []

    if  not tweet_data is None and len(tweet_data) > 0:
        for tweet in tweet_data:
            obj = {}
            obj['id'] = tweet['id']
            obj['text'] = tweet['text']
            result.append(obj)
    else:
        print("No tweets found")
        return []
    
    return result

def tweet_searched_list(list_id, list_search_keywords):
    print("searching tweets for your required list")
    tweets = get_list_tweets(list_id)

    filtered_tweets = []
    for tweet in tweets:
        text = tweet['text'].lower()
        if any(re.search(r"\b{}\b".format(re.escape(keyword)), text) for keyword in list_search_keywords):
            filtered_tweets.append(tweet)

    if len(filtered_tweets) > 0:
        df = pd.DataFrame(filtered_tweets, columns=["id", "text"])
        df.to_csv("tweets.csv", index=False, sep=",", encoding="utf-8", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)




def reply_to_tweets_task1(csv_file, reply_phrase_list_task1):
    print("replying to tweets")
    df = read_csv(csv_file)
    tweet_ids = df["id"].astype(str)

    for tweet_id in tweet_ids:
        try:
            random_reply = random.choice(reply_phrase_list_task1)

            client.create_tweet(in_reply_to_tweet_id=tweet_id, text=f"{random_reply}")
            print(f"Replied to tweet ID: {tweet_id}")

            time.sleep(interval_task1)
        except tweepy.TweepError as e:
            if isinstance(e, tweepy.TweepError) and e.api_code == 403:
                print(f"Skipping tweet ID {tweet_id}: Forbidden - cannot reply to this tweet")
                continue
            else:
                print(f"Error occurred while replying to tweet ID {tweet_id}: {e}")
                continue




you_follow_search_keywords = os.getenv("you_follow_search_keywords")
reply_phrase_task2 = os.getenv("reply_phrase_task2")
reply_phrase_list_task2 = reply_phrase_task2.split(",")
interval_task2 = int(os.getenv("interval_task2"))
starting_time_task2 = os.getenv("starting_time_task2")
ending_time_task2 = os.getenv("ending_time_task2")
running_task2 = os.getenv("running_task2")


def search_tweets_you_follow():
    print("searching tweets for the users you follow")
    tweets = client.get_home_timeline(exclude='replies,retweets', max_results=95)
    tweet_data = tweets.data
    result = []

    if  not tweet_data is None and len(tweet_data) > 0:
        for tweet in tweet_data:
            obj = {}
            obj['id'] = tweet['id']
            obj['text'] = tweet['text']
            result.append(obj)
    else:
        print("No tweets found")
        return []
    
    return result

     
 
def tweet_searched_you_follow(you_follow_search_keywords):
    tweets = search_tweets_you_follow()

    filtered_tweets = []
    for tweet in tweets:
        text = tweet['text'].lower()
        if any(re.search(r"\b{}\b".format(re.escape(keyword)), text) for keyword in you_follow_search_keywords):
            filtered_tweets.append(tweet)

    if len(filtered_tweets) > 0:
        df = pd.DataFrame(filtered_tweets, columns=["id", "text"])
        df.to_csv("tweets.csv", index=False, sep=",", encoding="utf-8", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)




def reply_to_tweets_task2(csv_file, reply_phrase_list_task2):
    print("replying to tweets")
    df = read_csv(csv_file)
    tweet_ids = df["id"].astype(str)

    for tweet_id in tweet_ids:
        try:
            random_reply = random.choice(reply_phrase_list_task2)

            client.create_tweet(in_reply_to_tweet_id=tweet_id, text=f"{random_reply}")
            print(f"Replied to tweet ID: {tweet_id}")

            time.sleep(interval_task2)
        except tweepy.TweepError as e:
            if isinstance(e, tweepy.TweepError) and e.api_code == 403:
                print(f"Skipping tweet ID {tweet_id}: Forbidden - cannot reply to this tweet")
                continue
            else:
                print(f"Error occurred while replying to tweet ID {tweet_id}: {e}")
                continue



search_keyword = os.getenv("search_keyword")
reply_phrase_task3 = os.getenv("reply_phrase_task3")
reply_phrase_list_task3 = reply_phrase_task3.split(",")
interval_task3 = int(os.getenv("interval_task3"))
starting_time_task3 = os.getenv("starting_time_task3")
ending_time_task3 = os.getenv("ending_time_task3")
running_task3 = os.getenv("running_task3")



def search_tweets(query):
    print("searching tweets in all for your required keyword")
    tweets = client.search_recent_tweets(query=query, max_results=95)
    tweet_data = tweets.data
    result = []

    if  not tweet_data is None and len(tweet_data) > 0:
        for tweet in tweet_data:
            obj = {}
            obj['id'] = tweet['id']
            obj['text'] = tweet['text']
            result.append(obj)
    else:
        print("No tweets found")
        return []
    
    return result


def tweet_searched(search_keyword):
    tweets = search_tweets(search_keyword)
    if len(tweets) > 0:
        df = pd.DataFrame(tweets, columns=["id", "text"])
        df.to_csv("tweets.csv", index=False, sep=",", encoding="utf-8", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)


def reply_to_tweets_task3(csv_file, reply_phrase_list_task3):
    print("replying to tweets")
    df = read_csv(csv_file)
    tweet_ids = df["id"].astype(str)

    for tweet_id in tweet_ids:
        try:
            random_reply = random.choice(reply_phrase_list_task3)

            client.create_tweet(in_reply_to_tweet_id=tweet_id, text=f"{random_reply}")
            print(f"Replied to tweet ID: {tweet_id}")

            time.sleep(interval_task3)
        except tweepy.TweepError as e:
            if isinstance(e, tweepy.TweepError) and e.api_code == 403:
                print(f"Skipping tweet ID {tweet_id}: Forbidden - cannot reply to this tweet")
                continue
            else:
                print(f"Error occurred while replying to tweet ID {tweet_id}: {e}")
                continue



search_owner_tweets_task4 = os.getenv("search_owner_tweets_task4")
starting_time_task4 = os.getenv("starting_time_task4")
ending_time_task4 = os.getenv("ending_time_task4")
running_task4 = os.getenv("running_task4")


def search_tweets_owner(search_owner_tweets_task4):
    print("Checkig for your posted tweets to retweet")
    tweets = client.search_recent_tweets(query=search_owner_tweets_task4, max_results=95)
    tweet_data = tweets.data
    result = []

    if  not tweet_data is None and len(tweet_data) > 0:
        for tweet in tweet_data:
            obj = {}
            obj['id'] = tweet['id']
            obj['text'] = tweet['text']
            result.append(obj)
    else:
        return []
    
    return result


def tweet_searched_owner(search_tweet_owner):
    tweets = search_tweets_owner(search_owner_tweets_task4)
    if len(tweets) > 0:
        df = pd.DataFrame(tweets, columns=["id", "text"])
        df.to_csv("tweets_owner.csv", index=False, sep=",", encoding="utf-8", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)



def retweet_owner_tweets(csv_file):
    print("retweeting your tweets")
    df = read_csv(csv_file)
    tweet_ids = df["id"].astype(str)

    for tweet_id in tweet_ids:
        time.sleep(10)
        try:
            client.retweet(tweet_id)
            print(f"Retweeted tweet ID: {tweet_id}")

            time.sleep(20)
        except tweepy.TweepError as e:
            print(f"Error occurred while replying to tweet ID {tweet_id}: {e}")
            continue



#task end


def task1():
    clear_tweets()
    clear_tweet_id()
    tweet_searched_list(list_id,list_search_keywords)
    log_tweets()
    extract_tweet_ids('tweets.csv', 'tweet_id.csv')
    reply_to_tweets_task1('tweet_id.csv', reply_phrase_list_task1)
    time.sleep(500)




def task2():
    clear_tweets()
    clear_tweet_id()
    tweet_searched_you_follow(you_follow_search_keywords)
    log_tweets()
    extract_tweet_ids('tweets.csv', 'tweet_id.csv')
    reply_to_tweets_task2('tweet_id.csv', reply_phrase_list_task2)
    time.sleep(500)


def task3():
    clear_tweets()
    clear_tweet_id()
    tweet_searched(search_keyword)
    log_tweets()
    extract_tweet_ids('tweets.csv', 'tweet_id.csv')
    reply_to_tweets_task3('tweet_id.csv', reply_phrase_list_task3)
    time.sleep(500)



def task4():
    clear_tweets_owner()
    clear_tweet_id_owner()
    tweet_searched_owner(search_owner_tweets_task4)
    time.sleep(10)
    extract_tweet_ids('tweets_owner.csv', 'tweets_owner_id.csv')
    time.sleep(10)
    retweet_owner_tweets('tweets_owner_id.csv')
    time.sleep(50)


#automation

def operation1():
 if running_task1 == "y":
    while True:
        current_time = time.strftime("%H:%M:%S")
        if starting_time_task1 <= current_time <= ending_time_task1:
            print("Task 1 is running ")
            task1()
            print("Task 1 is completed")
        else:
            time.sleep(30)

def operation2():
   if running_task2 == "y": 
    while True:
        current_time = time.strftime("%H:%M:%S")
        if starting_time_task2 <= current_time <= ending_time_task2:
            print("Task 2 is running ")
            task2()
            print("Task 2 is completed")
        else:
            time.sleep(30)

def operation3():
   if running_task3 == "y": 
    while True:
        current_time = time.strftime("%H:%M:%S")
        if starting_time_task3 <= current_time <= ending_time_task3:
            print("Task 3 is running ")
            task3()
            print("Task 3 is completed")
        else:
            time.sleep(30)

def operation4():
   if running_task4 == "y": 
    current_time = time.strftime("%H:%M:%S")
    if starting_time_task4 <= current_time <= ending_time_task4:
        print("Task 4 is running ")
        task4()
        print("Task 4 is completed")
    else:
        time.sleep(30)


thread1 = threading.Thread(target=operation1)
thread2 = threading.Thread(target=operation2)
thread3 = threading.Thread(target=operation3)
thread4 = threading.Thread(target=operation4)



thread1.start()
thread2.start()
thread3.start()
thread4.start()





