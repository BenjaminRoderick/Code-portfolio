import os
import re
import json
import random
from argparse import ArgumentParser
import torch
from transformers import AutoTokenizer
from sklearn.model_selection import train_test_split
import warnings
import copy

import word_embeddings
import conv_neural
import recurrent_neural
import recurrent_neural_integrated

EMBED_DIM = 128

#source: https://ijarcce.com/wp-content/uploads/2025/04/IJARCCE.2025.14459.pdf

def main(grid_search = False):
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
    #take 80% of all users for training, 20% for testing

    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased', extra_special_tokens={'twitter_link': 'https://t.co/twitter_link'})

    tokenized_train_text = tokenize_text(train, tokenizer)
    tokenized_test_text = tokenize_text(test, tokenizer)

    num_words = len(tokenizer)

    if grid_search:
        model_params = word_embeddings.gs_get_best_model(tokenized_train_text['input_ids'], tokenized_test_text['input_ids'], num_words, device, outpath)
        print(f'Best model has parameters and loss: {model_params}')
    else:
        #train word2vec model on all posts from users in the training set
        #TODO: fix the dataloader for training word embeddings: some posts end up getting added letter-by-letter
        model_found = False

        for filename in os.listdir(outpath):
            if filename.endswith('.pt') and filename.startswith('skipgram'):
                model_sg = word_embeddings.skipgram_model(num_words=num_words, embed_dim=EMBED_DIM).to(device)
                model_sg.load_state_dict(torch.load(outpath + filename, weights_only=True))
                model_found = True
                print(f'Model loaded from file: {filename}\n')
                break

        if not model_found:
            print(f'No model found, training a new model and saving it to:\n{outpath}\n')
            model_sg = word_embeddings.train_full(
                data=tokenized_train_text['input_ids'],
                num_words=num_words,
                num_epochs=10,
                batch_size=32,
                device=device,
                embed_dim=EMBED_DIM,
                window_size=2,
                outpath=outpath
                )

            total_loss = word_embeddings.test_model(model_sg, tokenized_test_text['input_ids'], device, window_size=2)
            print(f'Model loss is: {total_loss}\n')
    
    model_sg.eval()

    model_found = False
    tokenized_train_text_padded = tokenize_text(train, tokenizer, pad_data=True)
    tokenized_test_text_padded = tokenize_text(test, tokenizer, pad_data=True)
    for filename in os.listdir(outpath):
        if filename.endswith('.pt') and filename.startswith('cnn_'):
            model_disc = conv_neural.discriminator(embedding_dim=EMBED_DIM).to(device)
            model_disc.load_state_dict(torch.load(outpath + filename, weights_only=True))
            model_found = True
            print(f'Model loaded from file: {filename}\n')
            break

    if not model_found:
        print(f'No model found, training a new model and saving it to:\n{outpath}\n')
        model_disc = conv_neural.train_full(
            data=tokenized_train_text_padded['input_ids'],
            embedding=model_sg.embedding,
            embedding_dim=EMBED_DIM,
            num_epochs=10,
            batch_size=128,
            device=device,
            outpath=outpath,
            num_filters_list=[EMBED_DIM]*3,#this value is also used in the RNN so update it there too if changed
            kernel_sizes=[3,4,5],
            dropout=0.5
        )
        total_sim = conv_neural.test_cnn(tokenized_test_text_padded['input_ids'], model_sg.embedding, model_disc.cnn, device)
        print(f'Average cosine similarity: {total_sim}')
    model_disc.eval()

    model_found = False
    for filename in os.listdir(outpath):
        if filename.endswith('.pt') and filename.startswith('rnn_'):
            model_rnn = recurrent_neural.recurrent_neural_network(cnn_dim=3*EMBED_DIM, hidden_dim=EMBED_DIM)
            model_rnn.load_state_dict(torch.load(outpath + filename, weights_only=True))
            model_found = True
            print(f'Model loaded from file: {filename}\n')
            break

    if not model_found:
        print(f'No model found, training a new model and saving it to:\n{outpath}\n')
        #modified_data = augment_positives(train)
        model_rnn = recurrent_neural.train_full(
            data=train,
            tokenizer=tokenizer,
            embedding=model_sg.embedding,
            cnn=model_disc.cnn,
            cnn_dim=3*EMBED_DIM,
            hidden_dim=EMBED_DIM,
            num_epochs=10,
            batch_size=32,
            device=device,
            outpath=outpath,
            learning_rate=0.01
        )
    model_rnn.eval()

    model_found = False
    for filename in os.listdir(outpath):
        if filename.endswith('.pt') and filename.startswith('integrated_rnn'):
            model_rnn = recurrent_neural_integrated.recurrent_neural_network(cnn_dim=3*EMBED_DIM, hidden_dim=EMBED_DIM, cnn=model_disc.cnn)
            model_rnn.load_state_dict(torch.load(outpath + filename, weights_only=True))
            model_found = True
            print(f'Model loaded from file: {filename}\n')
            break

    if not model_found:
        print(f'No model found, training a new model and saving it to:\n{outpath}\n')
        #modified_data = augment_positives(train)
        model_rnn = recurrent_neural_integrated.train_full(
            data=train,
            tokenizer=tokenizer,
            embedding=model_sg.embedding,
            cnn=model_disc.cnn,
            cnn_dim=3*EMBED_DIM,
            hidden_dim=2*EMBED_DIM,
            num_epochs=10,
            batch_size=32,
            device=device,
            outpath=outpath,
            learning_rate=0.01
        )

    print('Bye! :)')


def fetch_data(datapath):
    detector_file_dumps = []
    for filename in os.listdir(datapath):
        if filename.endswith(".json") and filename.startswith("detector_"):
            with open(datapath + filename, 'r') as f:
                detector_file_dumps.append(json.load(f))
    
    
    results_file_dumps = []
    for filename in os.listdir(datapath):
        if filename.endswith(".json") and filename.startswith("results_"):
            with open(datapath + filename, 'r') as f:
                results_file_dumps.append(json.load(f))


    user_posts = {}
    for file_dump in detector_file_dumps:
        for post in file_dump['posts']:
            user = post['author_id']
            if user not in user_posts:
                user_posts[user] = []
            user_posts[user].append([post['text'], post['created_at']])#each user has a list of posts, each post is a list of [text, created_at]

    data = []
    for file_dump in results_file_dumps:
        for user in file_dump['users']:
            user_id = user['user_id']

            data.append([user_id, user['is_bot'], user['description'], user['location'], user_posts[user_id], user['z_score']])
            #the goal is to have a nested list with columns: user_id, is_bot, description, location, post_history_embedding
            #currently user_posts[user_id] is a list

    print('Data loaded from files...\n')
    return data


def tokenize_text(text_list, tokenizer, pad_data=False):
    final = []
    for item in text_list:
        post_list = [re.sub('\u2019', "'", post[0]) for post in item[4]]
        
        final.append(re.sub('\u2019', "'", item[2]))
        final += post_list#list of all post texts from all users in the training set
    
    return tokenizer(final, add_special_tokens=False, padding=pad_data)

def tokenize_text_dmatrix(text_list, tokenizer, pad_data=False):
    final = []
    for item in text_list:
        item_subbed = re.sub('\u2019', "'", item[0])
        
        final += item_subbed#list of all post texts from all users in the training set
    
    return tokenizer(final, add_special_tokens=False, padding=pad_data)

def augment_positives(data, factor=2):
    out_list = copy.deepcopy(data)
    for user in data:
        if user[1]:
            for i in range(factor):
                out_list.append([f'{user[0]}_{i}'] + user[1:])
    return out_list
    

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-g', '--grid_search', action='store_true', help='Perform grid search to find the best model')
    args = parser.parse_args()
    grid_search = args.grid_search
    main(grid_search)