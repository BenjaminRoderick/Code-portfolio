import numpy as np
import torch
import itertools
import random
import matplotlib.pyplot as plt

random.seed(42)

def find_similar_embeddings(model, tokenizer, target_embedding, n=10):
    """
    Find the n most similar embeddings to the target embedding using cosine similarity
    Args:
        target_embedding: The embedding vector to compare against
        n: Number of similar embeddings to return (default 3)
    Returns:
        List of tuples containing (word, similarity_score) sorted by similarity
    """
    # Convert target to tensor if not already
    if not isinstance(target_embedding, torch.Tensor):
        target_embedding = torch.tensor(target_embedding)

    # Get all embeddings from the model
    all_embeddings = model.embedding.weight

    # Compute cosine similarity between target and all embeddings
    similarities = torch.nn.functional.cosine_similarity(
        target_embedding.unsqueeze(0),
        all_embeddings
    )

    # Get top n similar embeddings
    top_n_similarities, top_n_indices = torch.topk(similarities, n)

    # Convert to word-similarity pairs
    results = []
    for idx, score in zip(top_n_indices, top_n_similarities):
        word = tokenizer.decode(idx)
        results.append((word, score.item()))

    return results


def prompt_to_embeddings(model, tokenizer, prompt:str):
    # tokenize the input text
    tokens = tokenizer(prompt, return_tensors="pt")
    input_ids = tokens['input_ids']

    # make a forward pass
    embeddings, _ = model(input_ids)

    # directly use the embeddings layer to get embeddings for the input_ids
    embeddings = embeddings

    # print each token
    token_id_list = tokenizer.encode(prompt, add_special_tokens=True)
    token_str = [tokenizer.decode(t_id, skip_special_tokens=True) for t_id in token_id_list]

    return token_id_list, embeddings, token_str


def find_similar_logits(model, tokenizer, embedding_vector, n=10):
    """
    Use unembedding (lm_head) to convert embedding_vector to logit and find top-k
    """
    if not isinstance(embedding_vector, torch.Tensor):
        embedding_vector = torch.tensor(embedding_vector)
    logits = model.unembedding(embedding_vector.unsqueeze(0))  # [1, vocab]
    topk = torch.topk(logits, n)
    results = []
    for idx, val in zip(topk.indices[0], topk.values[0]):
        word = tokenizer.decode(idx)
        results.append((word, val.item()))
    return results


def get_token_embedding(model, tokenizer, word):
    _, embedding_word, _ = prompt_to_embeddings(model, tokenizer, word)
    return embedding_word[0, -1, :]


def get_all_tokens(tokenizer):
    tokens = list(tokenizer.get_vocab().keys())
    return tokens


def token_len_one_verifier(tokenizer, word):
    tokens = tokenizer.tokenize(word)
    return len(tokens) == 1


# def test_combinations(model, tokenizer, words, embeddings, combination_sizes, top_n=30):
#     results = {}
#     words = sorted(words)

#     for size in combination_sizes:
#         print(f"\nCombination size: {size}")
#         results[size] = 0.0
#         combos = list(itertools.combinations(words, size))
        
#         if len(combos) > 1000:
#             combos = random.sample(combos, 1000)

#         for combo in combos:
#             # compute weighted average embedding
#             weights = torch.ones(size) / size
#             weighted_embedding = sum(weights[i] * embeddings[combo[i]] for i in range(size))

#             # get top N logits
#             top_words = find_similar_logits(model, tokenizer, weighted_embedding, n=top_n)

#             # count how many original combo words appear in top N
#             count_in_top = sum(1 for w, _ in top_words if w in combo)
#             results[size] += count_in_top / len(combos)

#     print(f"{results[size]}\n")

#     return results

def test_combinations(
    word_list,
    model,
    tokenizer,
    n_values=[3, 5, 10, 15, 20],
    num_trials=100,
    top_k=30,
    superposition_mode='uniform'
):
    """
    Run superposition experiments on a given vocabulary list.

    For each n in n_values:
      - Randomly sample n words (single-token only)
      - Build uniform superposition (mean embedding)
      - Use unembedding to get logits and take top_k
      - Count how many sampled words appear in top_k (by token id)
      - Average the success counts over num_trials

    Returns:
      dict: { n: average_success_count }

    Notes:
      - Uses existing helpers where applicable:
          * token_len_one_verifier
          * get_token_embedding (as a stand-in for get_embedding_from_word)
        We compute top-k indices directly via model.unembedding to avoid
        string matching issues (leading spaces, special tokens) and to mirror
        the requested "top_k_indices(logits)" behavior.
    """

    # Filter word_list to single-token words only
    candidates = [w for w in word_list if token_len_one_verifier(tokenizer, w)]

    if not candidates:
        raise ValueError("No single-token words available after filtering. Please adjust word_list.")

    precomputed = {}
    for w in candidates:
        tok_ids = tokenizer.encode(w, add_special_tokens=False)
        if len(tok_ids) != 1:
            continue
        tok_id = tok_ids[0]
        emb = get_token_embedding(model, tokenizer, w)
        precomputed[w] = {"id": tok_id, "emb": emb}

    candidates = [w for w in candidates if w in precomputed]
    if not candidates:
        raise ValueError("No valid single-token words with embeddings. Please adjust word_list.")

    results = {}

    for n in n_values:
        if n <= 0:
            results[n] = 0.0
            continue
        if n > len(candidates):
            print(f"[test_combinations] Skipping n={n}: only {len(candidates)} single-token candidates available.")
            continue

        total_success = 0.0

        for _ in range(num_trials):
            sampled_words = random.sample(candidates, n)

            emb_stack = torch.stack([precomputed[w]["emb"] for w in sampled_words], dim=0)
            if superposition_mode == 'uniform':
                combined_emb = emb_stack.mean(dim=0)
            elif superposition_mode == 'random':
                weights = np.random.rand(n)
                weights = torch.nn.functional.softmax(torch.tensor(weights))
                combined_emb = torch.matmul(torch.transpose(emb_stack, 0, 1), weights.float())

            if not isinstance(combined_emb, torch.Tensor):
                combined_emb = torch.tensor(combined_emb)
            logits = model.unembedding(combined_emb.unsqueeze(0))  # [1, vocab]
            topk = torch.topk(logits, top_k)
            top_indices = set(topk.indices[0].tolist())

            sampled_ids = [precomputed[w]["id"] for w in sampled_words]
            success_count = sum(1 for tid in sampled_ids if tid in top_indices)

            total_success += success_count

        avg_success = total_success / float(num_trials)
        results[n] = avg_success

    return results


def plot_results(results_dict, title="Experiment Result"):
    """
    Plot a line chart from a dict {n: average_success}.

    - x-axis: number of superposed tokens (n)
    - y-axis: average success count (captured in top_k)
    - default style: line with markers, grid on
    - annotate each point with its value
    - can be called multiple times to overlay multiple lines

    The function uses the provided `title` as the line label so that multiple
    calls can show multiple categories in a legend. The overall axes title is
    set once (if not already set) to "Superposition Success vs Token Count".
    """
    if not isinstance(results_dict, dict) or len(results_dict) == 0:
        raise ValueError("results_dict must be a non-empty dict mapping n -> average_success.")

    xs = sorted(results_dict.keys())
    ys = [results_dict[n] for n in xs]

    ax = plt.gca()

    ax.plot(xs, ys, marker="o", linewidth=2, label=title)

    ax.set_xlabel("Number of superposed tokens (n)")
    ax.set_ylabel("Average success count (top_k hits)")

    if not ax.get_title():
        ax.set_title("Superposition Success vs Token Count")

    ax.grid(True, linestyle="--", alpha=0.4)

    for x, y in zip(xs, ys):
        ax.annotate(f"{y:.2f}", (x, y), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=9)

    ax.legend(frameon=False)