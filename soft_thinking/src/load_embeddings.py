import torch
import torch.nn as nn
from transformers import AutoTokenizer

# vocab_size = 151936
# dimensions = 1536
# embeddings_filename = r"embeddings_qwen.pth"
# tokenizer_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"

def load_embedding_model(vocab_size, dimensions, embeddings_filename, unembeddings_filename, tokenizer_name):
    
    class SimpleModel(nn.Module):
        def __init__(self, vocab_size, embedding_dim):
            # super(EmbeddingModel, self).__init__()
            super().__init__()
            self.embedding = nn.Embedding(num_embeddings=vocab_size, embedding_dim=embedding_dim)
            self.unembedding = nn.Linear(embedding_dim, vocab_size, bias=False)

        def forward(self, input_ids):
            x = self.embedding(input_ids)
            logits = self.unembedding(x)
            return x, logits

    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)

#     # Load the saved embeddings from the file
#     saved_embeddings = torch.load(embeddings_filename)

#     # Ensure the 'weight' key exists in the saved embeddings dictionary
#     if 'weight' not in saved_embeddings:
#         raise KeyError("The saved embeddings file does not contain 'weight' key.")

#     embeddings_tensor = saved_embeddings['weight']

#     # Check if the dimensions match
#     if embeddings_tensor.size() != (vocab_size, dimensions):
#         raise ValueError(f"The dimensions of the loaded embeddings do not match the model's expected dimensions ({vocab_size}, {dimensions}).")

    # Load input embedding
    emb_weight = torch.load(embeddings_filename)
    if isinstance(emb_weight, dict) and "weight" in emb_weight:
        emb_weight = emb_weight["weight"]
    else:
        emb_weight = emb_weight
    assert emb_weight.shape == (vocab_size, dimensions)

    # Load unembedding
    unemb_weight = torch.load(unembeddings_filename)
    if isinstance(unemb_weight, dict) and "weight" in unemb_weight:
        unemb_weight = unemb_weight["weight"]
    assert unemb_weight.shape == (vocab_size, dimensions)

    # Build the model
    # model = EmbeddingModel(vocab_size, dimensions)
    model = SimpleModel(vocab_size, dimensions)
    model.embedding.weight.data = emb_weight.clone()
    model.unembedding.weight.data = unemb_weight.clone()

    model.eval()
    return model, tokenizer