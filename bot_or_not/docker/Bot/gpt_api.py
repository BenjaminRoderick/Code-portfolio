from openai import OpenAI
import os
import time

def setup_api():
    api_key = os.getenv('ENV_API_TOKEN')
    
    client = OpenAI(
        api_key=api_key
        )
    return client

def get_response(client, prompt):
    response = client.responses.create(
        model="gpt-5-nano",
        input=prompt
    )
    time.sleep(15)

    return response.output_text

def generate_response_post(client, personality_traits, context_post_text):
    prompt = (f'Generate a twitter post responding to the following post: {context_post_text}.'
              + f' The user should respond in a manner consistent with the following description of their personality: {personality_traits}.'
              + ' Return only one answer with no additional text.'
              + '\nInclude the statement: https://t.co/twitter_link at the end of the post.'
              + '\nExample output:\n'
              + 'In today\'s video, I break down a gritty comeback by the #Sens against the #Isles, look at some absurd goalie stats from this year, discuss Joonas Korpisalo\'s up-and-down game, rave about a huge performance by Brady Tkachuk and Tim Stzle, plus MORE!\n\n: https://t.co/twitter_link https://t.co/twitter_link'
              )
    
    return get_response(client, prompt )

def generate_spontaneous_post(client, personality_traits, topic):
    prompt = (f'Generate a twitter post that a user with the following personality traits would make: {personality_traits}.'
              + f' The post should relate to the following topic: {topic}.'
              + ' Return only one answer with no additional text.'
              )
    
    return get_response(client, prompt)
    

def generate_user_bio(client, personality_traits):
    prompt = (f'Generate a short twitter bio for a user with the following  description of their personality traits:\n{personality_traits}.\n'
              + 'The bio should be concise and be related the user\'s interests and character without explicitly stating  any of the provided information about their personality traits.'
              + ' Return only one answer with no additional text.\n'
              + 'Example output:\nI have been watching the NBA since 1968,  My PAGE ISNT 4 EVERYONE.  DEFENSE REBOUNDING WINS CHIPS.'
              )
    
    return get_response(client, prompt)

def generate_user_bio_multi(client, users_list, example_users):
    prompt = (f'For each of the {len(users_list)} descriptions of personality traits below, create a short twitter bio.'
              + ' Each bio should be concise and be related the user\'s interests and character without explicitly stating their description.'
              + f' Return only all {len(users_list)} answers in inline json format with no additional text.'
              + '\nExample output:\n{"username": "twitter_bio", '
              + ', '.join([f'"{example_users[i]['username']}": "{example_users[i]['description']}"'
                              for i in range(len(example_users))])
              + '}\nList of users:\n'
              + '\n\n'.join([f'"username": "{users_list[i].username}",\n"description": "{users_list[i].personality_traits}"'
                             for i in range(len(users_list))])
              )
    
    resp = get_response(client, prompt)
    return resp