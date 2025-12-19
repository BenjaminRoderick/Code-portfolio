import gpt_api
import os
import json
import datetime
import random
import numpy as np
from random import randrange

class User:
    def __init__(self, path, client):
        self.generate_tweets = False

        self.client = client

        with open(path, 'r') as f:
            params_dict = json.load(f)
        
        self.post_freq = params_dict['post_freq']
        self.start_time_exp = None
        self.end_feed_time = None
        self.scroll_time_exp = params_dict['scroll_time_exp']
        self.wait_time_exp = params_dict['wait_time_exp']
        self.interests_list = params_dict['interests_list']
        self.personality_traits = params_dict['personality_traits']
        self.location = params_dict['location']
        self.username = params_dict['username']
        self.name = params_dict['name']

        self.author_id = None
        self.current_posts = 0
        self.last_post_time = None
    
    def __len__(self):
        return self.current_posts

    def create_user_profile(self):
        bio = gpt_api.generate_user_bio(self.client, self.personality_traits)
        profile_dict = {
            "username": self.username,
            "name": self.name,
            "description": bio,
            "location": self.location
        }
        return profile_dict

    def scroll_feed(self, post_list):
        # Simulate scrolling through a feed for a certain duration
        start_time = (datetime.timedelta(hours=self.start_time_exp.hour,
                                        minutes=self.start_time_exp.minute)
                                        + datetime.timedelta(minutes=generate_waiting_time(15)))
        scroll_duration = max(np.random.normal(self.scroll_time_exp, self.scroll_time_exp / 4), 15)  # at least 15 minutes

        end_time = datetime.timedelta(minutes=scroll_duration) + start_time
        new_posts = []

        for post in post_list:
            post_time = datetime.datetime.strptime(post['created_at'], "%Y-%m-%dT%H:%M:%S.000Z")
            if ((post_time - start_time).date() != post_time.date()
                or (post_time - end_time).date() == post_time.date()):# check if the post is within the scroll time
                continue

            if self.current_posts < self.post_freq:
                if self.detect_post_interest(post):
                    to_append = self.write_post(post, True)
                    if to_append == None:
                        break
                    new_posts.append(to_append)
                elif random.random() < 0.1:  # 10% chance to post spontaneously
                    to_append = self.write_post(post, False)
                    if to_append == None:
                        break
                    new_posts.append(to_append)

        return new_posts


    def write_post(self, context_post, is_response):
        try:
            text_to_post = self.generate_post_text(context_post, is_response)
        except:
            text_to_post = f'I love {random.choice(self.interests_list)}!'

        context_post_time = datetime.datetime.strptime(context_post['created_at'], "%Y-%m-%dT%H:%M:%S.000Z")
        if context_post_time >= self.end_feed_time:
            return None
        
        if self.last_post_time != None:
            context_post_time = max(context_post_time, self.last_post_time)# can't write a post too close to the last one
        
        self.last_post_time = context_post_time

        post_time = (context_post_time
                     + datetime.timedelta(minutes=writing_time(text_to_post))
                     + datetime.timedelta(minutes=generate_waiting_time(self.wait_time_exp))
                     )

        self.current_posts += 1

        return {'text': text_to_post,
                'created_at': datetime.datetime.strftime(post_time, "%Y-%m-%dT%H:%M:%S.000Z"),
                'author_id': self.author_id,
                }
    
    def set_start(self, start_time, end_time):
        start = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.000Z")
        end = datetime.datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.000Z")
        delta = end - start
        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        random_second = randrange(max(30, int_delta - 120 * self.scroll_time_exp))
        self.start_time_exp = start + datetime.timedelta(seconds=random_second)
        self.end_feed_time = end

    def generate_post_text(self, context_post, is_response):
        if is_response:
            return gpt_api.generate_response_post(self.client,
                                                    self.personality_traits,
                                                    context_post['text']
                                                    )
        else:
            return context_post['text']
    
    def detect_post_interest(self, post):
        # Simple keyword matching to detect interest
        for interest in self.interests_list:
            if interest in post['text'].lower():
                return True
        return False


class Bot:
    def __init__(self):
        self.client = gpt_api.setup_api()

        self.users = [User(f'bot_users/{filename}', self.client) for filename in os.listdir('bot_users')]

    global_session_info = None
    def create_user(self, session_info):
        global global_session_info
        global_session_info = session_info
        new_users = [user.create_user_profile() for user in self.users]

        return new_users
    
    def generate_content(self, datasets_json, users_list):
        global global_session_info
        start_time = global_session_info["sub_sessions_info"][datasets_json["sub_session_id"]-1]["start_time"]
        end_time = global_session_info["sub_sessions_info"][datasets_json["sub_session_id"]-1]["end_time"]

        posts = []
        for user in self.users:
            user.set_start(start_time, end_time)
            for u in users_list:
                if (u['username'] == user.username) and (u['name'] == user.name) and (u['location'] == user.location):
                    user.author_id = u['id']
                    break

            if user.author_id != None:
                posts += user.scroll_feed(datasets_json['posts'])

        return posts

def generate_waiting_time(expected):
    # minutes of wait time according to exponential distribution
    # expected: expected wait time in minutes
    return max(np.random.exponential(expected), 1)  # at least 1 minute

def writing_time(text):
    # minutes of writing time according to number of characters
    wpm = np.random.beta(2, 5) * 200  # words per minute (scaled to 200 as max)
    return len(text) / (wpm * 5)  # assuming average word length of 5 characters
