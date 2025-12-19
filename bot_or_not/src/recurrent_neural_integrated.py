import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from datetime import datetime, timedelta
import re
import random
from tqdm.auto import tqdm

import conv_neural

class recurrent_neural_network(nn.Module):
    def __init__(self, cnn_dim: int, hidden_dim: int, cnn:conv_neural.conv_neural_network):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.cnn = cnn
        self.rnn = nn.RNN(
            input_size=cnn_dim + 1,#because only the posts and times go through the rnn
            hidden_size=hidden_dim,
            nonlinearity='relu'
            )

        self.lin1 = nn.Linear(
            in_features=(hidden_dim + cnn_dim + 1),#concatenate other info
            out_features=hidden_dim
        )

        self.lin2 = nn.Linear(
            in_features=hidden_dim,
            out_features=hidden_dim
        )

        self.lin3 = nn.Linear(
            in_features=hidden_dim,
            out_features=1
        )
        self.sigmoid = nn.Sigmoid()
        self.nonlinearity = nn.ReLU()

    def forward(self, posts, bio, since_tensor, z_score):
        x = self.cnn(posts)
        y = self.cnn(bio.unsqueeze(0))
        rnn_in = torch.cat((x, since_tensor), dim=1)

        h_0 = torch.zeros(1, self.hidden_dim).to(x.device)
        out, _ = self.rnn(rnn_in, h_0)
        pred_in = torch.cat((out[0], y.flatten(), z_score.flatten()), dim=0)
        pred1 = self.nonlinearity(self.lin1(pred_in))
        pred2 = self.nonlinearity(self.lin2(pred1))
        pred3 = self.sigmoid(self.lin3(pred2))
        return pred3
    

def preprocess_data(data, tokenizer, sub_fun=None):
    '''
    data has shape:
    [
        [user_id, is_bot, bio, location, [post_list], z_score]
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
    print('Preprocessing data...')
    final_user_list = []
    final_label_list = []

    for user_info in tqdm(data, leave=False):
        if sub_fun:
            bio = sub_fun(user_info[2])
            posts_sub = [sub_fun(post[0]) for post in user_info[4]]
        else:
            bio = re.sub('\u2019', "'", user_info[2])
            posts_sub = [re.sub('\u2019', "'", post[0]) for post in user_info[4]]
        z_score = user_info[5]
        tokenized_posts_and_bio = tokenizer([bio] + posts_sub, add_special_tokens=False, padding=True)

        posts = []
        since_last = []
        for i in range(len(user_info[4])):
            post_time = datetime.strptime(user_info[4][i][1],"%Y-%m-%dT%H:%M:%S.000Z")
            if len(posts) == 0:
                since_last_post = 0
            else:
                since_last_post = (post_time - last_post_time) / timedelta(minutes=1)#convert the difference to minutes

            last_post_time = post_time
            posts.append(tokenized_posts_and_bio['input_ids'][i+1])
            since_last.append(since_last_post)
            #[tokenized_posts_and_bio[0], tokenized_posts_and_bio[i+1], since_last_post, z_score]
        final_user_list.append([tokenized_posts_and_bio['input_ids'][0], posts, since_last, z_score])

        if user_info[1]:
            final_label_list.append(1)
        else:
            final_label_list.append(0)
    
    print('Preprocessing finished\n')
    return final_user_list, final_label_list


def train_full(data, tokenizer, embedding, cnn, cnn_dim, hidden_dim, num_epochs, batch_size, device, outpath, learning_rate=0.01, sub_fun=None, save_file=None):
    processed_inputs, targets = preprocess_data(data, tokenizer, sub_fun=sub_fun)

    rnn = recurrent_neural_network(cnn_dim=cnn_dim, hidden_dim=hidden_dim, cnn=cnn).to(device)
    optimizer = torch.optim.SGD(rnn.parameters(), lr=learning_rate)
    rnn.train()

    print(f'Training model for {num_epochs} epochs:')
    for iter in range(num_epochs):
        rnn.zero_grad()

        batches = list(range(len(processed_inputs)))
        random.shuffle(batches)

        for start in tqdm(range(0, len(targets), batch_size), leave=False):
            batch_inds = batches[start: start + batch_size]
            batch_loss = 0

            for index in batch_inds:
                bios, posts, since_lasts, z_scores = processed_inputs[index]
                bios_tensor = torch.tensor(bios).to(device)
                posts_tensor = torch.tensor(posts).to(device)
                since_tensor = torch.tensor(since_lasts).to(device)
                z_tensor = torch.tensor(z_scores).to(device)

                with torch.no_grad():
                    bios_emb, posts_emb = embedding(bios_tensor), embedding(posts_tensor)
                
                output = rnn(posts_emb, bios_emb, since_tensor.reshape(-1,1), z_tensor.reshape(-1,1))
                target = torch.tensor(targets[index]).float().unsqueeze(0).to(device)
                loss = F.binary_cross_entropy(output, target).clamp(min=1e-8)
                batch_loss += loss

            batch_loss.backward()
            optimizer.step()
        
        print(f'Final batch loss of epoch {iter}: {batch_loss}')

    if save_file:
        torch.save(rnn.state_dict(), outpath + f'{save_file}.pt')
    else:
        torch.save(rnn.state_dict(), outpath + 'integrated_rnn.pt')
    return rnn

def test_rnn(data, embedding, model, device, tokenizer, replace_unicode, thresh=0.5, save_output=False):
    marked_account = []

    processed_inputs, user_ids = preprocess_data_test(data, tokenizer, replace_unicode)

    for index in tqdm(range(len(processed_inputs))):
        bios, posts, since_lasts, z_scores = processed_inputs[index]
        bios_tensor = torch.tensor(bios).to(device)
        posts_tensor = torch.tensor(posts).to(device)
        since_tensor = torch.tensor(since_lasts).to(device)
        z_tensor = torch.tensor(z_scores).to(device)

        with torch.no_grad():
            bios_emb, posts_emb = embedding(bios_tensor), embedding(posts_tensor)

            pred = model(posts_emb, bios_emb, since_tensor.reshape(-1,1), z_tensor.reshape(-1,1)).item()
            marked_account.append(
                {
                    "user_id": user_ids[index],
                    "confidence": pred,
                    "bot": (pred >= thresh)
                }
            )

    detect_dict = {user['user_id']: [user['bot'], user['confidence']] for user in marked_account}
    false_positives = 0
    true_positives = 0
    false_negatives= 0
    true_negatives = 0
    avg_conf_pos = 0
    avg_conf_neg = 0
    min_val_is_bot = 1
    max_val_is_bot = 0
    pred_on_real_users = []
    if save_output:
        user_export = []

    for user in tqdm(data):
        if user[1]:
            pred = detect_dict[user[0]][1]
            #print(pred)
            avg_conf_pos += pred
            if pred < min_val_is_bot:
                min_val_is_bot = pred
            if pred > max_val_is_bot:
                max_val_is_bot = pred

            if detect_dict[user[0]][0]:#predicted is bot (tp)
                true_positives += 1
            else:
                false_negatives += 1
        else:
            avg_conf_neg += detect_dict[user[0]][1]
            pred_on_real_users.append(detect_dict[user[0]][1])
            if detect_dict[user[0]][0]:#predicted is bot (fp)
                false_positives += 1
            else:
                true_negatives += 1

        if save_output:
            user_export.append([user[0], user[1], detect_dict[user[0]][1], detect_dict[user[0]][0]])

    pred_real_users_array = np.array(pred_on_real_users)
    percentile_90 = np.percentile(pred_real_users_array, 90)
    percentile_95 = np.percentile(pred_real_users_array, 95)
    percentile_99 = np.percentile(pred_real_users_array, 99)
    max_pred = np.max(pred_real_users_array)
    avg_conf_pos = avg_conf_pos / (true_positives + false_negatives)
    avg_conf_neg = avg_conf_neg / (false_positives + true_negatives)
    print(f'isbot-conf: {avg_conf_pos}')
    print(f'nobot-conf: {avg_conf_neg}')
    print(f'tp:{true_positives}\nfn:{false_negatives}\nfp:{false_positives}\ntn:{true_negatives}')
    print(f'Maximum confidence prediction on real user: {max_pred}\n90th percentile prediction on real user: {percentile_90}')
    print(f'Minimum prediction for a bot user: {min_val_is_bot}\nMaximum prediction for a bot user: {max_val_is_bot}')

    stats_dict = {
        'TP': true_positives,
        'FP': false_positives,
        'TN': true_negatives,
        'FN': false_negatives,
        '90th_percentile': percentile_90,
        '95th_percentile': percentile_95,
        '99th_percentile': percentile_99,
        'maximum_prediction_human': max_pred,
        'average_confidence_bot': avg_conf_pos,
        'average_confidence_human': avg_conf_neg
    }

    if save_output:
        return stats_dict, user_export
    else:
        return stats_dict


def preprocess_data_test(data, tokenizer, sub_fun=None):
    '''
    data has shape:
    [
        [user_id, is_bot, bio, location, [post_list], z_score]
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
    print('Preprocessing data...')
    final_user_list = []
    final_id_list = []

    for user_info in tqdm(data, leave=False):
        if sub_fun:
            bio = sub_fun(user_info[2])
            posts_sub = [sub_fun(post[0]) for post in user_info[4]]
        else:
            bio = re.sub('\u2019', "'", user_info[2])
            posts_sub = [re.sub('\u2019', "'", post[0]) for post in user_info[4]]
        z_score = user_info[5]
        tokenized_posts_and_bio = tokenizer([bio] + posts_sub, add_special_tokens=False, padding=True)

        posts = []
        since_last = []
        for i in range(len(user_info[4])):
            post_time = datetime.strptime(user_info[4][i][1],"%Y-%m-%dT%H:%M:%S.000Z")
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
    
    print('Preprocessing finished\n')
    return final_user_list, final_id_list