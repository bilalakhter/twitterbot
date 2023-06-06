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
import pytz 


load_dotenv()

API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("Api_Key_Secret")
BEARER_TOKEN = os.getenv("Bearer_Token")
ACCESS_TOKEN = os.getenv("Access_Id")
ACCESS_TOKEN_SECRET = os.getenv("Access_secret")
client = tweepy.Client(BEARER_TOKEN , API_KEY , API_KEY_SECRET , ACCESS_TOKEN , ACCESS_TOKEN_SECRET)



# extras

def log_tweets():
    print("logging tweets do not cancel the process")
    with open("tweet_id.csv", "r", encoding="utf-8") as tweets_file:
        tweets_reader = csv.reader(tweets_file)
        if not any(tweets_reader): 
            return  
        
        next(tweets_reader)  

        with open("log.csv", "a", newline="", encoding="utf-8") as log_file:
            log_writer = csv.writer(log_file, quoting=csv.QUOTE_NONNUMERIC)
            for row in tweets_reader:
                tweet_id = row[0].strip()  
                tweet_url = f"https://twitter.com/web/status/{tweet_id}"
                log_writer.writerow([tweet_url])



def extract_tweet_ids(csv_file, output_file):
    print("extracting tweet ids")
    try:
        df = pd.read_csv(csv_file)
    except pd.errors.EmptyDataError:
        print("CSV file is empty")
        df = pd.DataFrame()  
    
    if "id" not in df.columns:
        print("CSV file does not contain tweet IDs")
        return False
    
    tweet_ids = df["id"].astype(str)
    tweet_ids.to_csv(output_file, index=False)
    
    return True


def clear_tweets():
    print("clearing tweets")
    with open("tweets.csv", "w", encoding="utf-8") as tweets_file:
        tweets_file.write("")



def read_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        print("No tweet found change keywords", file_path)
        return True


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


# task 1

list_search_keywords = os.getenv("list_search_keywords")
list_id1 = os.getenv("list_id")
list_id2 = list_id1.split(",")
list_id = random.choice(list_id2)
reply_phrase_task1 = os.getenv("reply_phrase_task1")
reply_phrase_list_task1 = reply_phrase_task1.split(",")
interval_task1 = int(os.getenv("interval_task1"))
starting_time_task1 = os.getenv("starting_time_task1")
ending_time_task1 = os.getenv("ending_time_task1")
running_task1 = os.getenv("running_task1")
list_tweet_old = os.getenv("list_tweet_old")
time_duration_list = os.getenv("time_duration_list")


def get_list_tweets(list_id):
    print("Getting tweets for your required list")
    
    now = datetime.utcnow()
    if time_duration_list == "hours":
        since_time = now - timedelta(hours=int(list_tweet_old))
    elif time_duration_list == "minutes":
        since_time = now - timedelta(minutes=int(list_tweet_old))
    
    since_time = since_time.replace(tzinfo=pytz.UTC)
    
    max_results = 20
    tweets = client.get_list_tweets(id=list_id, max_results=max_results, expansions="author_id", tweet_fields="created_at,text,in_reply_to_user_id")
    tweet_data = tweets.data
    result = []

    if not tweet_data is None and len(tweet_data) > 0:
        for tweet in tweet_data:
            tweet_time = tweet['created_at']  
            if tweet_time >= since_time and not tweet['text'].startswith('RT') and tweet.get('in_reply_to_user_id') is None:
                obj = {}
                obj['id'] = tweet['id']
                obj['text'] = tweet['text']
                result.append(obj)
    else:
        print("No tweets found")
        return []
    
    return result




def tweet_searched_list(list_id, list_search_keywords):
    print("Searching tweets for your required list")
    tweets = get_list_tweets(list_id)

    filtered_tweets = []
    for tweet in tweets:
        text = tweet['text'].lower()
        keywords = list_search_keywords.split(',')
        regex = r"\b(" + "|".join(keywords) + r")\b"
        if re.search(regex, text):
            filtered_tweets.append(tweet)

    if len(filtered_tweets) > 0:
        df = pd.DataFrame(filtered_tweets, columns=["id", "text"])
        df.to_csv("tweets.csv", index=False, sep=",", encoding="utf-8", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)



def reply_to_tweets_task1(csv_file, reply_phrase_list_task1):
    print("Replying to tweets")
    df = read_csv(csv_file)

    
    if df is True:
        print("No tweet found change keywords")
        return True

    last_1000_rows = df.tail(1000)
    tweet_ids = last_1000_rows["id"].astype(str)

    log_file = "log_id_tweet.csv"
    existing_tweet_ids = set()

    with open(log_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        existing_tweet_ids = set(row[0] for row in reader)

    with open(log_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for tweet_id in tweet_ids:
            if tweet_id in existing_tweet_ids:
                print(f"Skipping tweet ID {tweet_id}: Already replied to this tweet")
                continue

            try:
                random_reply = random.choice(reply_phrase_list_task1)

                client.create_tweet(in_reply_to_tweet_id=tweet_id, text=f"{random_reply}")
                print(f"Replied to tweet ID: {tweet_id}")

                writer.writerow([tweet_id])

                time.sleep(interval_task1)
            except tweepy.TweepError as e:
                if isinstance(e, tweepy.TweepError) and e.api_code == 403:
                    print(f"Skipping tweet ID {tweet_id}: Forbidden - cannot reply to this tweet")
                    continue
                else:
                    print(f"Error occurred while replying to tweet ID {tweet_id}: {e}")
                    continue              

# task 2

you_follow_search_keywords = os.getenv("you_follow_search_keywords")
reply_phrase_task2 = os.getenv("reply_phrase_task2")
reply_phrase_list_task2 = reply_phrase_task2.split(",")
interval_task2 = int(os.getenv("interval_task2"))
starting_time_task2 = os.getenv("starting_time_task2")
ending_time_task2 = os.getenv("ending_time_task2")
running_task2 = os.getenv("running_task2")
you_follow_tweet_old = os.getenv("you_follow_tweet_old")
time_duration_you_follow = os.getenv("time_duration_you_follow")




def search_tweets_you_follow():
    print("Searching tweets for the users you follow")
    now = datetime.utcnow()
    if time_duration_you_follow == "hours":
     since_time = now - timedelta(hours =int(you_follow_tweet_old))
    if time_duration_you_follow == "minutes":
        since_time = now - timedelta(minutes =int(you_follow_tweet_old)) 
    since_time = since_time.replace(tzinfo=pytz.UTC)
    max_results = 20
    tweets = client.get_home_timeline(max_results=max_results,exclude="replies", expansions="author_id", tweet_fields="created_at,text")
    tweet_data = tweets.data
    result = []

    if not tweet_data is None and len(tweet_data) > 0:
        for tweet in tweet_data:
            tweet_time = tweet['created_at']
            if tweet_time >= since_time and not tweet['text'].startswith('RT'):
                obj = {}
                obj['id'] = tweet['id']
                obj['text'] = tweet['text']
                result.append(obj)
    else:
        print("No tweets found")
        return []

    return result

   


def tweet_searched_you_follow(you_follow_search_keywords):
    print("Searching tweets for people you follow")
    tweets = search_tweets_you_follow()

    filtered_tweets = []
    for tweet in tweets:
        text = tweet['text'].lower()
        keywords = you_follow_search_keywords.split(',')
        regex = r"\b(" + "|".join(keywords) + r")\b"
        if re.search(regex, text):
            filtered_tweets.append(tweet)

    if len(filtered_tweets) > 0:
        df = pd.DataFrame(filtered_tweets, columns=["id", "text"])
        df.to_csv("tweets.csv", index=False, sep=",", encoding="utf-8", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)



def reply_to_tweets_task2(csv_file, reply_phrase_list_task2):
    print("Replying to tweets")
    df = read_csv(csv_file)

    if df is True:
        print("No tweet found change keywords")
        return True 

    last_1000_rows = df.tail(1000)
    tweet_ids = last_1000_rows["id"].astype(str)

    log_file = "log_id_tweet.csv"
    existing_tweet_ids = set()

    with open(log_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        existing_tweet_ids = set(row[0] for row in reader)

    with open(log_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for tweet_id in tweet_ids:
            if tweet_id in existing_tweet_ids:
                print(f"Skipping tweet ID {tweet_id}: Already replied to this tweet")
                continue

            try:
                random_reply = random.choice(reply_phrase_list_task2)

                client.create_tweet(in_reply_to_tweet_id=tweet_id, text=f"{random_reply}")
                print(f"Replied to tweet ID: {tweet_id}")

                writer.writerow([tweet_id])

                time.sleep(interval_task2)
            except tweepy.TweepError as e:
                if isinstance(e, tweepy.TweepError) and e.api_code == 403:
                    print(f"Skipping tweet ID {tweet_id}: Forbidden - cannot reply to this tweet")
                    continue
                else:
                    print(f"Error occurred while replying to tweet ID {tweet_id}: {e}")
                    continue   


# task 3

search_keyword = os.getenv("search_keyword")
reply_phrase_task3 = os.getenv("reply_phrase_task3")
reply_phrase_list_task3 = reply_phrase_task3.split(",")
interval_task3 = int(os.getenv("interval_task3"))
starting_time_task3 = os.getenv("starting_time_task3")
ending_time_task3 = os.getenv("ending_time_task3")
running_task3 = os.getenv("running_task3")
all_tweets_old = os.getenv("all_tweet_old")
time_duration_all_tweets = os.getenv("time_duration_all_tweets")

def search_tweets(query):
    print("searching tweets in all for your required keyword")
    now = datetime.utcnow()
    if time_duration_all_tweets == "hours":
     since_time = now - timedelta(hours=int(all_tweets_old))
    if time_duration_all_tweets == "minutes":
        since_time = now - timedelta(minutes=int(all_tweets_old)) 
    since_time = since_time.replace(tzinfo=pytz.UTC)
    max_results = 20
    tweets = client.search_recent_tweets(query=query,max_results=max_results, expansions="author_id", tweet_fields="created_at,text")
    tweet_data = tweets.data
    result = []

    if not tweet_data is None and len(tweet_data) > 0:
        for tweet in tweet_data:
            tweet_time = tweet['created_at']
            if tweet_time >= since_time:
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
    print("Replying to tweets")
    df = read_csv(csv_file)


    if df is True:
        print("No tweet found change keywords")
        return True

    last_1000_rows = df.tail(1000)
    tweet_ids = last_1000_rows["id"].astype(str)

    log_file = "log_id_tweet.csv"
    existing_tweet_ids = set()

    with open(log_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        existing_tweet_ids = set(row[0] for row in reader)

    with open(log_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for tweet_id in tweet_ids:
            if tweet_id in existing_tweet_ids:
                print(f"Skipping tweet ID {tweet_id}: Already replied to this tweet")
                continue

            try:
                random_reply = random.choice(reply_phrase_list_task3)

                client.create_tweet(in_reply_to_tweet_id=tweet_id, text=f"{random_reply}")
                print(f"Replied to tweet ID: {tweet_id}")

                writer.writerow([tweet_id])

                time.sleep(interval_task3)
            except tweepy.TweepError as e:
                if isinstance(e, tweepy.TweepError) and e.api_code == 403:
                    print(f"Skipping tweet ID {tweet_id}: Forbidden - cannot reply to this tweet")
                    continue
                else:
                    print(f"Error occurred while replying to tweet ID {tweet_id}: {e}")
                    continue   


# task 4

search_owner_tweets_task4 = os.getenv("search_owner_tweets_task4")
starting_time_task4 = os.getenv("starting_time_task4")
ending_time_task4 = os.getenv("ending_time_task4")
running_task4 = os.getenv("running_task4")
time_duration_owner_tweet = os.getenv("time_duration_owner_tweet")
owner_tweet_old = os.getenv("owner_tweet_old")
interval_break_task4_seconds = int(os.getenv("interval_break_task4_seconds"))

def search_tweets_owner(search_owner_tweets_task4):
    print("Checkig for your posted tweets to retweet")
    now = datetime.utcnow()
    if time_duration_owner_tweet == "hours":
        since_time = now - timedelta(hours =int(owner_tweet_old))
    if time_duration_owner_tweet == "minutes":
        since_time = now - timedelta(minutes =int(owner_tweet_old)) 
    since_time = since_time.replace(tzinfo=pytz.UTC)       
    tweets = client.search_recent_tweets(query=search_owner_tweets_task4, max_results=25, expansions="author_id", tweet_fields="created_at,text")
    tweet_data = tweets.data
    result = []

    if  not tweet_data is None and len(tweet_data) > 0:
        for tweet in tweet_data:
            tweet_time = tweet['created_at']
            if tweet_time >= since_time:
              obj = {}
              obj['id'] = tweet['id']
              obj['text'] = tweet['text']
              result.append(obj)
    else:
        return []
    
    return result








def tweet_searched_owner(search_owner_tweets_task4):
    tweets = search_tweets_owner(search_owner_tweets_task4)
    if len(tweets) > 0:
        df = pd.DataFrame(tweets, columns=["id", "text"])
        df.to_csv("tweets_owner.csv", index=False, sep=",", encoding="utf-8", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)



def retweet_owner_tweets(csv_file):
    print("retweeting your tweets")
    df = read_csv(csv_file)
    tweet_ids = df["id"].astype(str)

    for tweet_id in tweet_ids:
        time.sleep(20)
        try:
            client.retweet(tweet_id)
            print(f"Retweeted tweet ID: {tweet_id}")

            time.sleep(20)
        except tweepy.TweepError as e:
            print(f"Error occurred while replying to tweet ID {tweet_id}: {e}")
            continue



#tasks


def task1():
    clear_tweets()
    clear_tweet_id()
    tweet_searched_list(list_id,list_search_keywords)
    extract_tweet_ids('tweets.csv', 'tweet_id.csv')
    reply_to_tweets_task1('tweet_id.csv', reply_phrase_list_task1)
    log_tweets()
    time.sleep(5)






def task2():
    clear_tweets()
    clear_tweet_id()
    tweet_searched_you_follow(you_follow_search_keywords)
    extract_tweet_ids('tweets.csv', 'tweet_id.csv')
    reply_to_tweets_task2('tweet_id.csv', reply_phrase_list_task2)
    log_tweets()
    time.sleep(5)





def task3():
    clear_tweets()
    clear_tweet_id()
    tweet_searched(search_keyword)
    extract_tweet_ids('tweets.csv', 'tweet_id.csv')
    reply_to_tweets_task3('tweet_id.csv', reply_phrase_list_task3)
    log_tweets()
    time.sleep(5)



def task4():
    clear_tweets_owner()
    clear_tweet_id_owner()
    tweet_searched_owner(search_owner_tweets_task4)
    time.sleep(5)
    extract_tweet_ids('tweets_owner.csv', 'tweets_owner_id.csv')
    time.sleep(5)
    retweet_owner_tweets('tweets_owner_id.csv')
    time.sleep(10)



#automation

def operation1():
 if running_task1 == "y":
    while True:
        current_time = time.strftime("%H:%M:%S")
        if starting_time_task1 <= current_time <= ending_time_task1:
            print("Task 1 is running \n")
            task1()
            print("Task 1 is completed will run again until its ending time \n")
        else:
            time.sleep(30)

def operation2():
   if running_task2 == "y": 
    while True:
        current_time = time.strftime("%H:%M:%S")
        if starting_time_task2 <= current_time <= ending_time_task2:
            print("Task 2 is running \n")
            task2()
            print("Task 2 is completed will run again until its ending time\n")
        else:
            time.sleep(30)

def operation3():
   if running_task3 == "y": 
    while True:
        current_time = time.strftime("%H:%M:%S")
        if starting_time_task3 <= current_time <= ending_time_task3:
            print("Task 3 is running \n ")
            task3()
            print("Task 3 is completed will run again until its ending time\n")
        else:
            time.sleep(30)

def operation4():
   if running_task4 == "y": 
    while True:
        current_time = time.strftime("%H:%M:%S")
        if not (starting_time_task1 <= current_time <= ending_time_task1) or (starting_time_task2 <= current_time <= ending_time_task2) or (starting_time_task3 <= current_time <= ending_time_task3):
          print("Task 4 is running\n ")
          task4()
          print("Task 4 is completed\n")
          time.sleep(int(interval_break_task4_seconds)) 
          print("Task 4 is running again\n")   



thread1 = threading.Thread(target=operation1)
thread2 = threading.Thread(target=operation2)
thread3 = threading.Thread(target=operation3)
thread4 = threading.Thread(target=operation4)



thread1.start()
thread2.start()
thread3.start()
thread4.start()



