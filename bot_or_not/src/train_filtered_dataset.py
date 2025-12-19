import re
import emoji
import json
import os
import warnings
import random
import torch
from sklearn.model_selection import train_test_split

from transformers import AutoTokenizer

import conv_neural
import recurrent_neural_integrated
import qwen_embeddings

VOCAB_SIZE = 151936
EMB_DIM = 1536
MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"

def main():
    warnings.filterwarnings("ignore")
    path = os.path.dirname(os.path.abspath(__file__))[:-3]
    datapath = path + "data/"
    outpath = path + 'out/'
    random_seed = 42
    random.seed(random_seed)
    torch.manual_seed(random_seed)

    torch.manual_seed(random_seed)
    if torch.cuda.is_available():
        device = torch.device("cuda")
        torch.cuda.manual_seed(random_seed)
    else:
        device = torch.device("cpu")

    data = fetch_data(datapath)

    train, test = train_test_split(data, test_size=0.2, random_state=random_seed)

    embedding, tokenizer = qwen_embeddings.load_embedding_model(
        vocab_size=VOCAB_SIZE,
        emb_dim=EMB_DIM,
        embeddings_filename=outpath + 'embeddings_qwen.pth',
        tokenizer_name=MODEL_NAME
    )
    embedding.to(device)

    model_found = False
    temp_cnn = conv_neural.conv_neural_network(
        embedding_dim=EMB_DIM,
        num_filters_list=3*[EMB_DIM]
    )
    for filename in os.listdir(outpath):
        if filename.endswith('.pt') and filename.startswith('integrated_rnn_qwen'):
            model_rnn = recurrent_neural_integrated.recurrent_neural_network(
                cnn_dim=3*EMB_DIM,
                hidden_dim=2*EMB_DIM,
                cnn=temp_cnn
                ).to(device)
            model_rnn.load_state_dict(torch.load(outpath + filename, weights_only=True))
            model_found = True
            print(f'Model loaded from file: {filename}\n')
            break

    if not model_found:
        print(f'No model found, training a new model and saving it to:\n{outpath}\n')
        #modified_data = augment_positives(train)
        model_rnn = recurrent_neural_integrated.train_full(
            data=set_positive_ex_ratio(data, 0.3),
            tokenizer=tokenizer,
            embedding=embedding,
            cnn=temp_cnn,
            #cnn=model_disc.cnn,
            cnn_dim=3*EMB_DIM,
            hidden_dim=2*EMB_DIM,
            num_epochs=20,
            batch_size=32,
            device=device,
            outpath=outpath,
            learning_rate=0.01,
            sub_fun=replace_unicode,
            save_file='integrated_rnn_qwen'
        )
    #do this inside the train loop
    #train = set_positive_ex_ratio(train, 0.3)
    stats_dict = recurrent_neural_integrated.test_rnn(test, embedding, model_rnn, device, tokenizer, replace_unicode, thresh=0.81)
    with open(f'{outpath}stats_dict.json', 'w') as f:
        json.dump(stats_dict, f, default=str, indent=4)

    print('done')

def replace_unicode(text):
    regex1 = re.sub('\u2019', "'", text)
    demojified_text = emoji.demojize(regex1)
    regex2 = re.sub(':', '', demojified_text)
    regex3 = re.sub('https://t.co/twitter_link', 'link', regex2)
    return regex3


def tokenize_text(text_list, tokenizer, pad_data=False):
    final = []
    for item in text_list:
        post_list = [replace_unicode(post[0]) for post in item[4]]
        
        final.append(replace_unicode(item[2]))
        final += post_list#list of all post texts from all users in the training set
    
    return tokenizer(final, add_special_tokens=False, padding=pad_data)


def fetch_data(datapath):
    file_dumps = []
    for filename in os.listdir(datapath):
        if filename.endswith(".json") and ('results' in filename):
            with open(datapath + filename, 'r', encoding='utf8') as f:
                file_dumps.append(json.load(f))

    user_posts = {}
    for file_dump in file_dumps:
        for post in file_dump['posts']:
            user = post['author_id']
            if user not in user_posts:
                user_posts[user] = []
            user_posts[user].append([post['text'], post['created_at']])#each user has a list of posts, each post is a list of [text, created_at]

    data = []
    for file_dump in file_dumps:
        for user in file_dump['users']:
            user_id = user['user_id']

            data.append([user_id, user['is_bot'], user['description'], user['location'], user_posts[user_id], user['z_score']])
            #the goal is to have a nested list with columns: user_id, is_bot, description, location, post_history_embedding
            #currently user_posts[user_id] is a list

    print('Data loaded from files...\n')
    return data

def set_positive_ex_ratio(data, ratio):
    positive_examples = [user_info for user_info in data if user_info[1]]
    negative_examples = [user_info for user_info in data if not user_info[1]]
    len_pos = len(positive_examples)
    len_data = len(data)

    if len_pos >= (ratio * len_data):
        return data

    len_to_set = round(len_pos / ratio + len_pos)
    choices = random.choices(negative_examples, k=len_to_set)
    return positive_examples + choices

if __name__ == '__main__':
    main()