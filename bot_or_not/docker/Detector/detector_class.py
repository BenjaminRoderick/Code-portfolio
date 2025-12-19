import os
import re
import torch
from datetime import datetime, timedelta
import emoji

import qwen_embeddings
import conv_neural
from recurrent_neural_integrated import recurrent_neural_network

VOCAB_SIZE = 151936
EMB_DIM = 1536
MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"

class Detector:
    def __init__(self):
        if torch.cuda.is_available():
            self.device = torch.device('cuda')
        else:
            self.device = torch.device('cpu')

        check = 0
        for filename in os.listdir('models'):
            if filename.startswith('embeddings_') and filename.endswith('.pth'):
                self.embedding, self.tokenizer = qwen_embeddings.load_embedding_model(
                    vocab_size=VOCAB_SIZE,
                    emb_dim=EMB_DIM,
                    embeddings_filename=f'models/{filename}',
                    tokenizer_name=MODEL_NAME
                )
                self.embedding.to(self.device)
                check += 1
                continue

            if filename.startswith('integrated_rnn') and filename.endswith('.pt'):
                self.model_rnn = recurrent_neural_network(
                    cnn_dim=3*EMB_DIM,
                    hidden_dim=2*EMB_DIM,
                    cnn=conv_neural.conv_neural_network(
                        embedding_dim=EMB_DIM,
                        num_filters_list=[EMB_DIM]*3
                        )
                ).to(self.device)
                self.model_rnn.load_state_dict(torch.load(f'models/{filename}', weights_only=True, map_location=self.device))
                check += 1
                continue

        if check != 2:
            raise ValueError('Incorrect files in models directory, ensure that there is a file for skipgram, cnn and rnn models')
        self.model_rnn.eval()


    def detect_bot(self, session_data, thresh=0.81):
        embedding = self.embedding

        marked_account = []
        user_posts = {}
        data = []

        for post in session_data['posts']:
            user = post['author_id']
            if user not in user_posts:
                user_posts[user] = []
            user_posts[user].append([post['text'], post['created_at']])#each user has a list of posts, each post is a list of [text, created_at]

        for user in session_data['users']:
            user_id = user['id']

            data.append([user_id, user['description'], user['location'], user_posts[user_id], user['z_score']])
            #the goal is to have a nested list with columns: user_id, description, location, post_history_embedding
            #currently user_posts[user_id] is a list

        processed_inputs, user_ids = preprocess_data(data, self.tokenizer)

        for index in range(len(processed_inputs)):
            bios, posts, since_lasts, z_scores = processed_inputs[index]
            bios_tensor = torch.tensor(bios).to(self.device)
            posts_tensor = torch.tensor(posts).to(self.device)
            since_tensor = torch.tensor(since_lasts).to(self.device)
            z_tensor = torch.tensor(z_scores).to(self.device)

            with torch.no_grad():
                bios_emb, posts_emb = embedding(bios_tensor), embedding(posts_tensor)

                pred = self.model_rnn(posts_emb, bios_emb, since_tensor.reshape(-1,1), z_tensor.reshape(-1,1)).item()
                marked_account.append(
                    {
                        "user_id": user_ids[index],
                        "confidence": int(round(pred * 100)),
                        "bot": (pred >= thresh)
                    }
                )

        return marked_account


def preprocess_data(data, tokenizer):
    '''
    data has shape:
    [
        [user_id, bio, location, [post_list], z_score]
    ]
    post_list:
    [
        [text, created_at]
    ]
    
    outputs:
    final_user_list: shape(num_users, 4, num_posts)
    [
        [bios, posts, since_lasts, z_scores]
    ]
    final_label_list: shape(num_users, 1)
    list[int]
    '''
    final_user_list = []
    final_id_list = []

    for user_info in data:
        bio = replace_unicode(user_info[1])
        z_score = user_info[4]
        posts_sub = [replace_unicode(post[0]) for post in user_info[3]]
        tokenized_posts_and_bio = tokenizer([bio] + posts_sub, add_special_tokens=False, padding=True)

        posts = []
        since_last = []
        for i in range(len(user_info[3])):
            post_time = datetime.strptime(user_info[3][i][1],"%Y-%m-%dT%H:%M:%S.000Z")
            if len(posts) == 0:
                since_last_post = 0
            else:
                since_last_post = (post_time - last_post_time) / timedelta(minutes=1)#convert the difference to minutes

            last_post_time = post_time
            posts.append(tokenized_posts_and_bio['input_ids'][i+1])
            since_last.append(since_last_post)
            #[tokenized_posts_and_bio[0], tokenized_posts_and_bio[i+1], since_last_post, z_score]
        final_user_list.append([tokenized_posts_and_bio['input_ids'][0], posts, since_last, z_score])
        final_id_list.append(user_info[0])

    return final_user_list, final_id_list

def replace_unicode(text):
    regex1 = re.sub('\u2019', "'", text)
    demojified_text = emoji.demojize(regex1)
    regex2 = re.sub(':', '', demojified_text)
    regex3 = re.sub('https://t.co/twitter_link', 'link', regex2)
    return regex3
