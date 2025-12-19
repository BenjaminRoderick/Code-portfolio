import torch
import torch.nn as nn
from transformers import AutoTokenizer

# vocab_size = 151936
# dimensions = 1536
# embeddings_filename = r"embeddings_qwen.pth"
# tokenizer_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"

def load_embedding_model(vocab_size, emb_dim, embeddings_filename, tokenizer_name):
    # Load input embedding
    emb_weight = torch.load(embeddings_filename)
    if isinstance(emb_weight, dict) and "weight" in emb_weight:
        emb_weight = emb_weight["weight"]
    else:
        emb_weight = emb_weight
    assert emb_weight.shape == (vocab_size, emb_dim)

    embedding = nn.Embedding(num_embeddings=vocab_size, embedding_dim=emb_dim)
    embedding.weight.data = emb_weight.clone()
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)

    return embedding, tokenizer