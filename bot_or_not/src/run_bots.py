import bots
import gpt_api
import os
import json
import time

def main():
    path = os.path.dirname(os.path.abspath(__file__))[:-3]
    datapath = path + 'data/'
    outpath = path + 'out/'
    keypath = path + 'keys/'

    client = gpt_api.setup_api(keypath)
    ver_num = 1

    with open(datapath + f'detector_dataset_{ver_num}.json', 'r') as f:
        data = json.load(f)
    
    for filename in os.listdir(datapath + 'bot_users/'):
        with open(f'{datapath}bot_users/{filename}', 'r') as f:
            user_info = json.load(f)
            bot_user = bots.Bot(post_freq=user_info['post_freq'],
                                start_hour=user_info['start_hour'],
                                scroll_time_exp=user_info['scroll_time_exp'],
                                wait_time_exp=user_info['wait_time_exp'],
                                interests_list=user_info['interests_list'],
                                personality_traits=user_info['personality_traits'],
                                location=user_info['location'],
                                username=user_info['username'],
                                name=user_info['name'],
                                client=client
                                )
            
            seen_posts, new_posts = bot_user.scroll_feed(data['posts'])

            print(f'User {bot_user.username} saw {seen_posts} posts during scroll.')
            print(f'This bot created {len(new_posts)} new posts')

            #bot_data = bot_user.create_output_dict(data, new_posts)

            outfile = f'{outpath}{bot_user.username}_{ver_num}.json'
            if os.path.exists(outfile):
                with open(outfile, 'r') as g:
                    out_dict = json.load(g)
                
                out_dict['posts'] += new_posts
            else:
                user = bot_user.generate_user()
                out_dict = {'users': user, 'posts': new_posts}

            with open(outfile, 'w') as g:
                #json.dump(bot_data, g, default=str, indent=4)
                json.dump(out_dict, g, default=str, indent=4)
        
if __name__ == '__main__':
    main()