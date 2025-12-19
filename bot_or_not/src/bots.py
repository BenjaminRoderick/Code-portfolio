import os
import json
import datetime
import random
import string
import numpy as np
import gpt_api

def main():
    random.seed(42)
    np.random.seed(42)
    path = os.path.dirname(os.path.abspath(__file__))[:-3]
    datapath = path + 'data/'
    outpath = path + 'out/'
    keypath = path + 'keys/'

    client = gpt_api.setup_api(keypath)

    with open(datapath + 'detector_dataset_1.json', 'r') as f:
        data = json.load(f)

    test_bot = Bot(
        post_freq=100000,  # effectively unlimited for testing
        start_hour=18,
        scroll_time_exp=70,
        wait_time_exp=10,
        interests_list=['movie', 'show', 'series', 'film', 'cinema', 'actor', 'actress', 'director'],
        personality_traits='Hello, World!'
    )

    seen_posts, new_posts = test_bot.scroll_feed(data['posts'])

    print(f'{seen_posts} posts seen during scroll.\nThis bot created {len(new_posts)} new posts')

    final_dict = test_bot.create_output_dict(data, new_posts)

    with open(outpath + 'bot_output.json', 'w') as f:
        json.dump(final_dict, f, default=str, indent=4)


class Bot:
    def __init__(self,
                 post_freq,
                 start_hour,
                 scroll_time_exp,
                 wait_time_exp,
                 interests_list,
                 personality_traits,
                 location='Internet',
                 username='bot',
                 name='bot',
                 client=None
                 ):
        self.author_id = generate_id()  # unique identifier for the bot
        self.client = client  # OpenAI client for generating text

        self.post_freq = post_freq  # total posts allowed
        self.current_posts = 0  # current number of posts made
        self.last_post_time = None  # time of the last post made

        self.start_time_exp = datetime.time(start_hour, 15)  # expected start time of activity
        self.scroll_time_exp = scroll_time_exp  # expected scroll time in minutes
        self.wait_time_exp = wait_time_exp  # expected wait time in minutes

        self.username = username
        self.name = name
        self.interests_list = interests_list  # list of interests to interact with
        self.personality_traits = personality_traits  # description of personality for text generation
        self.location = location
        print(f'Creating bot with author_id: {self.author_id}\n')

    def generate_user(self, average_posts=0, std_dev_posts=1):
        if self.client:
            bio = gpt_api.generate_user_bio(self.client, self.personality_traits)
        else:
            bio = f'About me: {self.personality_traits}'

        return {
            'id': self.author_id,
            'tweet_count': self.current_posts,
            'z_score': (average_posts - self.current_posts) / std_dev_posts,
            'username': self.username,
            'name': self.name,
            'description': bio,
            'location': self.location
            }

    def scroll_feed(self, post_list):
        # Simulate scrolling through a feed for a certain duration
        start_time = (datetime.timedelta(hours=self.start_time_exp.hour,
                                        minutes=self.start_time_exp.minute)
                                        + datetime.timedelta(minutes=generate_waiting_time(15)))
        scroll_duration = max(np.random.normal(self.scroll_time_exp, self.scroll_time_exp / 4), 15)  # at least 15 minutes

        end_time = datetime.timedelta(minutes=scroll_duration) + start_time
        print(f'User: {self.username}, id: {self.author_id}\nStarting scroll at {start_time}, ending at {end_time}\nTotal time: {scroll_duration} minutes\n')
        seen_posts = 0
        new_posts = []

        for post in post_list:
            post_time = datetime.datetime.strptime(post['created_at'], "%Y-%m-%dT%H:%M:%S.000Z")
            if ((post_time - start_time).date() != post_time.date()
                or (post_time - end_time).date() == post_time.date()):# check if the post is within the scroll time
                continue

            try:
                if self.current_posts < self.post_freq:
                    if self.detect_post_interest(post):
                        new_posts.append(self.write_post(post, True))
                    elif random.random() < 0.1:  # 10% chance to post spontaneously
                        new_posts.append(self.write_post(post, False))
            except:
                print('Unable to generate new posts, aborting and saving.')
                break

            seen_posts += 1
        
        return seen_posts, new_posts

    def write_post(self, context_post, is_response):
        text_to_post = self.generate_post_text(context_post, is_response)
        context_post_time = datetime.datetime.strptime(context_post['created_at'], "%Y-%m-%dT%H:%M:%S.000Z")
        if self.last_post_time != None:
            context_post_time = max(context_post_time, self.last_post_time)# can't write a post too close to the last one
        
        self.last_post_time = context_post_time

        post_time = (context_post_time
                     + datetime.timedelta(minutes=writing_time(text_to_post))
                     + datetime.timedelta(minutes=generate_waiting_time(self.wait_time_exp))
                     )

        post_id = generate_id()
        self.current_posts += 1

        print(f'Generated post for user: {self.username}\nat {post_time}\nid: {post_id}\n')
        return {'text': text_to_post,
                'created_at': datetime.datetime.strftime(post_time, "%Y-%m-%dT%H:%M:%S.000Z"),
                'id': post_id,
                'author_id': self.author_id,
                'lang': 'en'
                }

    def generate_post_text(self, context_post, is_response):
        # Placeholder for LLM integration to generate post text
        if self.client:
            if is_response:
                return gpt_api.generate_response_post(self.client,
                                                      self.personality_traits,
                                                      context_post['text']
                                                      )
            else:
                return gpt_api.generate_spontaneous_post(self.client,
                                                         self.personality_traits,
                                                         random.choice(self.interests_list)
                                                         )
        else:
            return f'I love {random.choice(self.interests_list)}!'
    
    def detect_post_interest(self, post):
        # Simple keyword matching to detect interest
        for interest in self.interests_list:
            if interest in post['text'].lower():
                return True
        return False

    def create_output_dict(self, data, new_posts):
        original_data = dict(data)
        num_posts = original_data['metadata']['total_amount_posts']
        num_users = original_data['metadata']['total_amount_users']

        standard_deviation = (original_data['metadata']['users_average_amount_posts']
                              - original_data['users'][0]['tweet_count']) / original_data['users'][0]['z_score']
        average_posts = (num_posts + len(new_posts)) / (num_users + 1)

        original_data['metadata']['users_average_amount_posts'] = average_posts
        original_data['metadata']['total_amount_users'] += 1
        original_data['metadata']['total_amount_posts'] += len(new_posts)

        post_list_final = original_data['posts'] + new_posts
        new_user = self.generate_user(average_posts, standard_deviation)
        user_list_final = original_data['users'] + [new_user]
        random.shuffle(user_list_final)

        original_data['metadata']['users_average_z_score'] = ((original_data['metadata']['users_average_z_score']
                                                               * (num_users) + new_user['z_score'])
                                                               / (num_users + 1)
                                                               )

        original_data['posts'] = sorted(post_list_final, key=lambda x: x['created_at'])
        original_data['users'] = user_list_final
        # sorting and shuffling to hide bot activity in the data
        return original_data

def generate_waiting_time(expected):
    # minutes of wait time according to exponential distribution
    # expected: expected wait time in minutes
    return max(np.random.exponential(expected), 1)  # at least 1 minute

def writing_time(text):
    # minutes of writing time according to number of characters
    wpm = np.random.beta(2, 5) * 200  # words per minute (scaled to 200 as max)
    return len(text) / (wpm * 5)  # assuming average word length of 5 characters

def generate_id():
    id = ''
    for section in [8, 4, 4, 4, 12]:
        part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=section))
        id += part + '-'
    return id[:-1]  # remove trailing '-'

if __name__ == "__main__":
    main()