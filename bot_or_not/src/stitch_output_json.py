import os
import json
import math
import random

def main():
    '''
    input//output json files have structure:
    {
    id: 20/22,
    lang: "en",
    metadata:
        {
        "total_amount_users":
        "total_amount_posts":
        "topics": []
        "users_average_amount_posts": 32.068627450980394,
        "users_average_z_score": -6.530723674265627e-17
        },
    "posts": [],
    "users": []
    }
    '''
    path = os.path.dirname(os.path.abspath(__file__))[:-3]
    outpath = path + 'out/'

    bot_users = {}
    with open(outpath + 'the_film_poet.json', 'r') as f:
        data = json.load(f)
    with open(path + 'data/results_dataset_1.json', 'r') as f:
        bot_data = json.load(f)
    
    for user in bot_data['users']:
        if user['is_bot']:
            bot_users[user['user_id']] = user

    post_list_final = data['posts']
    for filename in os.listdir(outpath):
        if filename.endswith('_1.json'):
            with open(outpath + filename, 'r') as f:
                temp_dict = json.load(f)

            user_to_add = temp_dict['users']
            user_to_add['tweet_count'] = len(temp_dict['posts'])
            data['users'].append(user_to_add)

            bot_users[user_to_add['id']] = {
                'is_bot': True,
                'bot_team_id': 21,
                'bot_team_name': 'benbots',
                'user_id': user_to_add['id'],
                'tweet_count': user_to_add['tweet_count'],
                'z_score': 0,
                'username': user_to_add['username'],
                'name': user_to_add['name'],
                'description': user_to_add['description'],
                'location': user_to_add['location'],
                'detectors': []
                }#results dataset uses 'user_id' all others use 'id'
            
            post_list_final += temp_dict['posts']

    random.shuffle(data['users'])
    data['posts'] = sorted(post_list_final, key=lambda x: x['created_at'])#produce the final lists of users and posts
    
    total_posts = len(data['posts'])
    total_users = len(data['users'])
    average_num_posts = total_posts / total_users

    std_dev = 0
    for user in data['users']:
        std_dev += (user['tweet_count'] - average_num_posts) ** 2
    
    std_dev = math.sqrt(std_dev / total_users)

    total_z_score = 0
    final_results_users = []
    for user in data['users']:
        if user['id'] in bot_users.keys():
            results_user = bot_users[user['id']]
        else:
            results_user = {
                "is_bot": False,
                "bot_team_id": -1,
                "bot_team_name": "Not A Bot",
                'user_id': user['id'],
                'tweet_count': user['tweet_count'],
                'z_score': 0,
                'username': user['username'],
                'name': user['name'],
                'description': user['description'],
                'location': user['location'],
                'detectors': []
            }

        z_score = (user['tweet_count'] - average_num_posts) / std_dev
        user['z_score'] = z_score
        results_user['z_score'] = z_score
        total_z_score += z_score
        final_results_users.append(results_user)

    average_z_score = total_z_score / total_users

    data['metadata']['total_amount_users'] = total_users
    data['metadata']['total_amount_posts'] = total_posts
    data['metadata']['users_average_amount_posts'] = average_num_posts
    data['metadata']['users_average_z_score'] = average_z_score#update the metadata

    results_dict = {}
    results_dict['id'] = data['id']
    results_dict['posts'] = data['posts']
    results_dict['users'] = final_results_users

    with open(outpath + 'detector_dataset_1_bots.json', 'w') as f:
        json.dump(data, f, default=str, indent=4)
    
    with open(outpath + 'results_dataset_1_bots.json', 'w') as f:
        json.dump(results_dict, f, default=str, indent=4)


if __name__ == '__main__':
    main()