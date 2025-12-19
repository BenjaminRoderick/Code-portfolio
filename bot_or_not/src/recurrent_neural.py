import torch
import torch.nn as nn
import torch.nn.functional as F
from datetime import datetime, timedelta
import re
import random
from tqdm.auto import tqdm

class recurrent_neural_network(nn.Module):
    def __init__(self, cnn_dim: int, hidden_dim: int):
        super().__init__()
        self.input_dim = 2*cnn_dim + 2#post embedding + bio embedding + post time + user z score
        self.hidden_dim = hidden_dim
        self.lin_dim = int(hidden_dim * 3/4)
        self.rnn = nn.RNN(
            input_size=self.input_dim,
            hidden_size=hidden_dim,
            nonlinearity='relu'
            )

        self.lin1 = nn.Linear(
            in_features=hidden_dim,
            out_features=self.lin_dim
        )

        self.lin2 = nn.Linear(
            in_features= self.lin_dim,
            out_features= self.lin_dim
        )

        self.lin3 = nn.Linear(
            in_features= self.lin_dim,
            out_features=1
        )
        self.sigmoid = nn.Sigmoid()
        self.nonlinearity = nn.ReLU()

    def forward(self, x):
        h_0 = torch.zeros(1, self.hidden_dim).to(x.device)
        out, _ = self.rnn(x, h_0)
        pred1 = self.nonlinearity(self.lin1(out[0]))
        pred2 = self.nonlinearity(self.lin2(pred1))
        pred3 = self.sigmoid(self.lin3(pred2))
        return pred3
    

def preprocess_data(data, tokenizer):
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
        bio = re.sub('\u2019', "'", user_info[2])
        z_score = user_info[5]
        posts_sub = [re.sub('\u2019', "'", post[0]) for post in user_info[4]]
        tokenized_posts_and_bio = tokenizer([bio] + posts_sub, add_special_tokens=False, padding=True)

        bios = []
        posts = []
        since_last = []
        z_scores = []
        for i in range(len(user_info[4])):
            post_time = datetime.strptime(user_info[4][i][1],"%Y-%m-%dT%H:%M:%S.000Z")
            if len(posts) == 0:
                since_last_post = 0
            else:
                since_last_post = (post_time - last_post_time) / timedelta(minutes=1)#convert the difference to minutes

            last_post_time = post_time
            bios.append(tokenized_posts_and_bio['input_ids'][0])
            posts.append(tokenized_posts_and_bio['input_ids'][i+1])
            since_last.append(since_last_post)
            z_scores.append(z_score)
            #[tokenized_posts_and_bio[0], tokenized_posts_and_bio[i+1], since_last_post, z_score]
        final_user_list.append([bios, posts, since_last, z_scores])

        if user_info[1]:
            final_label_list.append(1)
        else:
            final_label_list.append(0)
    
    print('Preprocessing finished\n')
    return final_user_list, final_label_list


def train_full(data, tokenizer, embedding, cnn, cnn_dim, hidden_dim, num_epochs, batch_size, device, outpath, learning_rate=0.01):
    processed_inputs, targets = preprocess_data(data, tokenizer)

    rnn = recurrent_neural_network(cnn_dim=cnn_dim, hidden_dim=hidden_dim).to(device)
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
                    bios_cnn, posts_cnn = cnn(bios_emb), cnn(posts_emb)
                
                input_tensor = torch.cat((bios_cnn, posts_cnn, since_tensor.reshape(-1,1), z_tensor.reshape(-1,1)), dim=1)
                output = rnn(input_tensor)
                target = torch.tensor(targets[index]).float().unsqueeze(0).to(device)
                loss = F.binary_cross_entropy(output, target).clamp(min=1e-8)
                batch_loss += loss

            batch_loss.backward()
            optimizer.step()
        
        print(f'Final batch loss of epoch {iter}: {batch_loss}')

    torch.save(rnn.state_dict(), outpath + f'rnn_cnn{cnn_dim}_h{hidden_dim}.pt')
    return rnn