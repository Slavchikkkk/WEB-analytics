import praw
import pandas as pd
import csv
from datetime import datetime, timezone


def enter_auth_params():
    client_id = input("Enter client id: ") 
    client_secret = input("Enter client secret: ") 
    user_agent = input("Enter user agent: ") # Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36
    return client_id, client_secret, user_agent

def initiate_auth(client_id, client_secret, user_agent):
    try:
        reddit_client=praw.Reddit(client_id=client_id,client_secret=client_secret,user_agent=user_agent)
        print("Authentication successful!")

    except Exception as e:
        print("Authentication failed:", e)
        exit()
    return reddit_client



def account_scan(reddit_client):
    target_username = input("Enter target account id for scanning: ") # netflix
    posts_info = []

    for submission in reddit_client.redditor(target_username).submissions.new(limit=2000):
        if submission.is_self and submission.selftext:
            post_text = submission.selftext
        else:
            post_text = None
            posts_info.append({
                'author': submission.author,
                'title': submission.title,
                'number_of_comments': submission.num_comments,
                'created_time': datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
                'post_text': post_text,
                'url': submission.url
        })
    return posts_info

def show_results(posts_info):
    posts_df = pd.DataFrame(posts_info)
    print(posts_df)

def save_to_csv(posts_info):
    file_name = input("Enter dataset name: ")
    keys = posts_info[0].keys() if posts_info else []
    with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(posts_info)



if __name__ == "__main__":
    client_id, client_secret, user_agent = enter_auth_params()
    reddit_client = initiate_auth(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
    posts = account_scan(reddit_client=reddit_client)
    show_results(posts)
    save_to_csv(posts)