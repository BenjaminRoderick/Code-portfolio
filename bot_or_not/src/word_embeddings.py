import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader

from tqdm.auto import tqdm

class tweet_dataset(torch.utils.data.Dataset):
    def __init__(self, sources, targets):
        self.sources = sources
        self.targets = targets
        assert len(sources) == len(targets)

    def __len__(self):
        return len(self.sources)

    def __getitem__(self, index):
        return self.sources[index], self.targets[index]

class skipgram_model(nn.Module):
    def __init__(self, num_words, embed_dim):
        super().__init__()#initialise nn.Module super class

        self.embedding = nn.Embedding(num_words, embed_dim)
        self.projection = nn.Linear(embed_dim, num_words, bias=False)

        self.bind_weights()

    def bind_weights(self):
        emb = self.get_emb()
        proj = self.get_proj()

        proj.weight = emb.weight

    def get_emb(self):
        return self.embedding

    def get_proj(self):
        return self.projection

    def forward(self, x):
        emb = self.embedding
        proj = self.projection

        x_emb = emb(x)
        return proj(x_emb)

def train_epoch(model, loader, optimizer, device):
    model.train()

    for x, y in tqdm(loader, miniters=20, leave=False):
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()

        prediction = model(x)
        loss = F.cross_entropy(prediction, y)
        loss.backward()

        optimizer.step()

    return loss

def train_full(data, num_words, num_epochs, batch_size, device, embed_dim = 128, outpath = None, window_size = 2):
    targets, sources = preprocess_data(data, window_size)
    loader = DataLoader(
        tweet_dataset(sources=sources, targets=targets),
        batch_size=batch_size,
        shuffle=True
    )
    model = skipgram_model(num_words=num_words, embed_dim=embed_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters())

    print(f'Training model for {num_epochs} epochs:')
    for epoch in range(num_epochs):
        loss = train_epoch(model, loader, optimizer, device)
        print(f'Loss at epoch {epoch}: {loss}')
    
    if outpath:
        torch.save(model.state_dict(), outpath + f'skipgram_{window_size}wx{embed_dim}e.pt')
    
    return model


def preprocess_data(data, window_size):
    sources = []
    targets = []

    for sentence_ids in data:
        expanded_sources, expanded_targets = expand_data(sentence_ids, window_size)
        sources += expanded_sources
        targets += expanded_targets

    return targets, sources

def expand_data(ids, window_size):
    current = []
    surrounding = []

    for i in range(window_size, len(ids) - window_size):
        temp_surr = ids[i - window_size: i] + ids[i + 1: i + window_size + 1]
        surrounding += temp_surr
        current += [ids[i]] * len(temp_surr)

    return surrounding, current

def test_model(model, data, device, window_size = 2):
    targets, sources = preprocess_data(data, window_size)
    loader = DataLoader(
        tweet_dataset(sources=sources, targets=targets),
        batch_size=32,
    )

    model.eval()

    with torch.no_grad():
        total_cross_entropy_loss = 0
        print('Evaluating model on test data')
        for x, y in tqdm(loader, miniters=20, leave=False):
            x, y = x.to(device), y.to(device)
            pred = model(x)
            loss = F.cross_entropy(pred, y)
            total_cross_entropy_loss += torch.sum(loss)

    return total_cross_entropy_loss

def gs_get_best_model(train_ids, test_ids, num_words, device, outpath):
    os.makedirs(outpath + 'gridsearch_results/', exist_ok=True)
    loss_data = []

    for window_size in [2,3,4]:
        for embed_dim in [128, 192, 256]:
            print(f'Performing grid search on parameters:\nWindow size: {window_size}\nEmbedding dimension: {embed_dim}\n')
            model = train_full(
                train_ids,
                num_words=num_words,
                num_epochs=4,
                batch_size=32,
                device=device,
                embed_dim=embed_dim,
                window_size=window_size,
                outpath=outpath + 'gridsearch_results/'
            )
            loss = test_model(model, test_ids, device, window_size)
            print(f'Test loss is: {loss}')
            loss_data.append([window_size, embed_dim, loss])
    
    min_val_log = [0,0,0]
    with open(outpath + 'loss_data.txt', 'w') as f:
        for log_entry in loss_data:
            f.write(f'window size:{log_entry[0]}, embedding dimension:{log_entry[1]}, loss:{log_entry[2]}\n')
            if log_entry[2] < min_val_log[2] or min_val_log[2] == 0:
                min_val_log = log_entry

    return min_val_log
    

if __name__ == '__main__':
    print('Wrong file')