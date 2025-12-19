import json
import os

import bot_class

def main():
    bot = bot_class.Bot()

    datapath = os.path.dirname(__file__)[:-10] + 'data/'
    for filename in os.listdir(datapath):
        if filename.startswith('detector_') and filename.endswith('.json'):
            with open(datapath + filename, 'r') as f:
                input_dataset = json.load(f)

    input_dataset['sub_session_id'] = 1
    global_session_info = {'sub_sessions_info':
                {0:
                    {
                        'start_time': '2024-03-16T00:00:08.000Z',
                        'end_time': '2024-03-17T23:59:59.000Z'
                    }
                }
            }
    
    users_list = bot.create_user(global_session_info)
    created_posts = bot.generate_content(input_dataset, users_list)

    print(users_list)
    print(created_posts)

if __name__ == '__main__':
    main()