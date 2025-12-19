import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
import random

from tqdm.auto import tqdm

'''
Sources:
https://arxiv.org/pdf/1602.03483
https://arxiv.org/pdf/2009.12061
https://discuss.pytorch.org/t/jensen-shannon-divergence/2626/11
https://arxiv.org/pdf/1408.5882
'''
class conv_neural_network(nn.Module):
    def __init__(self, embedding_dim, num_filters_list=[128, 128, 128], kernel_sizes=[3,4,5]):
        super(conv_neural_network, self).__init__()

        self.filter_list = nn.ModuleList([
            nn.Conv1d(in_channels=embedding_dim,
                      out_channels=num_filters_list[i],
                      kernel_size=kernel_sizes[i])
            for i in range(len(num_filters_list))
        ])

        self.activation = nn.ReLU()

    def forward(self, x):
        #x has shape [number_of_samples, sentence_length, embedding_dim]
        x_reshaped = x.permute(0,2,1)# [num_samples, embed_dim, len]

        #shape [num_samples, num_filters, filter_out_size]
        filtered_list = [self.activation(convolution(x_reshaped)) for convolution in self.filter_list]
        #shape [num_samples, num_filters, 1]
        max_pooling = [F.max_pool1d(conv,kernel_size=conv.shape[2]) for conv in filtered_list]
        #shape [num_samples, total_num_filters]
        concat = torch.cat([pool.squeeze(dim=2) for pool in max_pooling], dim=1)

        return concat


class discriminator(nn.Module):
    def __init__(self, embedding_dim, num_filters_list=[128, 128, 128], kernel_sizes=[3,4,5], dropout=0.5):
        super().__init__()
        self.cnn = conv_neural_network(
            embedding_dim=embedding_dim,
            num_filters_list=num_filters_list,
            kernel_sizes=kernel_sizes
        )
        self.lin = nn.Linear(sum(num_filters_list) + embedding_dim, 1)
        self.dropout = nn.Dropout(p=dropout)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, token_emb, token_sentence_emb):
        '''
        token_emb: embedding of the token to compare
        token_sentence_emb: embedding of tokens in the target sentence [number_of_samples, sentence_length, embedding_dim]

        returns:
        p(token is in sentence)
        '''
        cnn = self.cnn
        lin = self.lin
        sigmoid = self.sigmoid

        sentence_pred_emb = cnn(token_sentence_emb)#[num_samples, total_num_filters]
        emb_cat = torch.cat([token_emb, sentence_pred_emb], dim=1)#[num_samples, total_num_filters + emb_dim]
        pred = lin(emb_cat)#[num_samples,1]

        return sigmoid(pred)


class JSD(nn.Module):
    def __init__(self):
        super(JSD, self).__init__()
        self.kl = nn.KLDivLoss(reduction='batchmean', log_target=True)

    def forward(self, p: torch.tensor, q: torch.tensor):
        p, q = p.view(-1, p.size(-1)), q.view(-1, q.size(-1))#reshape the tensors
        m = (0.5 * (p + q)).log()
        kl1 = self.kl(m, p.log())
        kl2 = self.kl(m, q.log())
        jsd = 0.5 * (kl1 + kl2)
        return jsd
    
class cnn_dataset(torch.utils.data.Dataset):
    def __init__(self, token_ids, counterexample_ids, sentence_ids):
        super().__init__()
        self.token_ids = token_ids
        self.sentence_ids = sentence_ids
        self.counterexample_ids = counterexample_ids
        assert len(token_ids) == len(sentence_ids)
        assert len(token_ids) == len(counterexample_ids)

    def __len__(self):
        return len(self.token_ids)

    def __getitem__(self, index):
        return self.token_ids[index], self.counterexample_ids[index], self.sentence_ids[index]


def collate_data(batch):
    token_ids = []
    sentence_ids = []
    counterexample_ids = []

    for in_id, out_id, sentence_id in batch:
        token_ids.append(in_id)
        counterexample_ids.append(out_id)
        sentence_ids.append(sentence_id)
    
    x_in = torch.tensor(token_ids, dtype=torch.int64)
    x_out = torch.tensor(counterexample_ids, dtype=torch.int64)
    y_ret = torch.tensor(sentence_ids, dtype=torch.int64)

    return x_in, x_out, y_ret


def preprocess_data(data):
    #want each line to be of the form
    #x: token_emb, y: sentence_token_emb, z: belongs_to
    from itertools import chain

    token_set = set(chain(*data))
    token_set.discard(0)
    tokens_unique = list(token_set)
    compare_ids = []
    counterexample_ids = []
    sentence_ids = []

    print('Preprocessing cnn data...')
    for token_ids in tqdm(data, miniters=20, leave=False):#create a dataset of size ~ num_samples * vocab_size
        if token_ids == []:
            continue
        counterexample = random.choice(tokens_unique)
        for id in token_ids:
            if id == 0:
                break
            if counterexample == id:
                counterexample = random.choice(tokens_unique)

        for id in token_ids:
            compare_ids.append(id)
            counterexample_ids.append(counterexample)
            sentence_ids.append(token_ids)
    print('Done, beginning training\n')

    return compare_ids, counterexample_ids, sentence_ids


def train_epoch(model, optimizer, embedding, loader, device):
    model.train()
    embedding.weight.requires_grad = False
    jsd = JSD()

    for x_in, x_out, y in tqdm(loader, miniters=20, leave=False):
        x_in, x_out, y = x_in.to(device), x_out.to(device), y.to(device)#xs: token_emb, y: sentence_token_emb
        x_in, x_out, y = embedding(x_in), embedding(x_out), embedding(y)#embed the token ids and the sentence (list of token ids)

        optimizer.zero_grad()

        prediction_in_words = model(x_in, y)
        prediction_out_words = model(x_out, y)
        loss = -jsd(prediction_in_words, prediction_out_words)#the paper says to maximise jsd so we minimize -jsd
        loss.backward()

        optimizer.step()
    
    return loss


def train_full(data, embedding, embedding_dim, num_epochs, batch_size, device, outpath, num_filters_list=[128, 128, 128], kernel_sizes=[3,4,5], dropout=0.5):
    compare_ids, counterexample_ids, sentence_ids = preprocess_data(data)

    loader = DataLoader(
        dataset=cnn_dataset(compare_ids, counterexample_ids, sentence_ids),
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collate_data
    )
    model = discriminator(
        embedding_dim=embedding_dim,
        num_filters_list=num_filters_list,
        kernel_sizes=kernel_sizes,
        dropout=dropout
    ).to(device)

    optimizer = torch.optim.SGD(model.parameters())
    
    print(f'Training model for {num_epochs} epochs:')
    for epoch in range(num_epochs):
        loss = train_epoch(
            model=model,
            loader=loader,
            embedding=embedding,
            optimizer=optimizer,
            device=device
            )
        print(f'Loss at epoch {epoch}: {loss}')
    
    if outpath:
        torch.save(model.state_dict(), outpath + f'cnn_{num_filters_list}f_{kernel_sizes}k_{embedding_dim}e.pt')
    
    return model
