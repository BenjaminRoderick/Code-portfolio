from openai import OpenAI
import os
import time
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
OUTPATH = os.path.dirname(os.path.abspath(__file__))[:-3] + 'out/api_outputs/'
os.makedirs(OUTPATH, exist_ok=True)# ensure output directory exists

def setup_api(keypath):
    with open(keypath + 'openai.md', 'r') as f:
        api_key = f.read().strip()
    
    client = OpenAI(
        api_key=api_key
        )
    return client

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def get_response(client, prompt, request_type):
    response = client.responses.create(
        model="gpt-5-nano",
        input=prompt
    )
    time.sleep(15)

    if len(response.output_text) != 0:
        with open(OUTPATH + f'{request_type}_response_{response.id}.txt', 'w') as f:
            f.write(f'Prompt:\n{prompt}\n\n{response.output_text}')
    else:
        print('No response, retrying...\n')

    return response.output_text

def generate_response_post(client, personality_traits, context_post_text):
    prompt = (f'Generate a twitter post responding to the following post: {context_post_text}.'
              + f' The user should respond in a manner consistent with the following description of their personality: {personality_traits}.'
              + ' Return only one answer with no additional text.'
              )
    
    return get_response(client, prompt, 'post_resp')

def generate_spontaneous_post(client, personality_traits, topic):
    prompt = (f'Generate a twitter post that a user with the following personality traits would make: {personality_traits}.'
              + f' The post should relate to the following topic: {topic}.'
              + ' Return only one answer with no additional text.'
              )
    
    return get_response(client, prompt, 'post_spon')
    

def generate_user_bio(client, personality_traits):
    prompt = (f'Generate a short twitter bio for a user with the following personality traits: {personality_traits}.'
              + ' The bio should be concise and be related the user\'s interests and character without explicitly stating their personality traits.'
              + ' Return only one answer with no additional text.'
              )
    
    return get_response(client, prompt, 'bio')