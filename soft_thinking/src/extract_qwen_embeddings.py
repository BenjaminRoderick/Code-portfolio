import torch
import os
from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM

#should try other maybe larger models
tokenizer_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
filename_safe = tokenizer_name.replace("/", "_")
model_name = tokenizer_name

# Load the tokenizer
tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)

vocab_size = tokenizer.vocab_size
print("Vocab size:", vocab_size)

# Load the pre-trained model
model = AutoModelForCausalLM.from_pretrained(model_name)

embedding_dim = model.model.embed_tokens.weight.shape
print("Embedding dimension:", embedding_dim)

# extract embedding
embeddings = model.model.embed_tokens.weight
print(f"Extracted Embeddings Layer for {model_name}: {embeddings}")
torch.save(embeddings.detach().cpu(), os.path.join(f"{filename_safe}_embeddings_qwen.pth"))

# extract unembedding
unembedding = model.lm_head.weight
print(f"Extracted Unembeddings Layer for {model_name}: {unembedding}")
torch.save(unembedding.detach().cpu(), os.path.join(f"{filename_safe}_unembeddings_qwen.pth"))