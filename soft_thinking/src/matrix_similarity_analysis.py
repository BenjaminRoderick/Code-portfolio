import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
import os

# Define model paths
MODEL_PATHS = {
    "DeepSeek-R1-Distill-Qwen-1.5B": "/home/comp/f2256768/SCCOT/models/deepseek_1.5b",
    "DeepSeek-R1-Distill-Qwen-7B": "/home/comp/f2256768/SCCOT/models/deepseek_7b",
    "Qwen3-4B": "/home/comp/f2256768/SCCOT/models/qwen3_4b"
}

def analyze_model_matrices(model_name, model_path):
    print(f"==================================================")
    print(f"Analyzing: {model_name}")
    # print(f"Path: {model_path}")
    print(f"==================================================")

    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype="auto",
            trust_remote_code=True,
            device_map="auto"
        )
    except Exception as e:
        print(f"Error loading model {model_name}: {e}")
        return

    # Extract matrices
    try:
        embeddings = model.model.embed_tokens.weight
        unembeddings = model.lm_head.weight
        bias = model.lm_head.bias
    except AttributeError:
        embeddings = model.get_input_embeddings().weight
        unembeddings = model.get_output_embeddings().weight
        bias = model.get_output_embeddings().bias if hasattr(model.get_output_embeddings(), 'bias') else None

    E = embeddings.detach().float()
    U = unembeddings.detach().float().to(E.device)

    # 1. Basic Checks
    print(f"\n[1] Basic Structure")
    print(f"Embedding Shape:   {E.shape}")
    print(f"Unembedding Shape: {U.shape}")
    print(f"Tie Word Embeddings Config: {getattr(model.config, 'tie_word_embeddings', 'Unknown')}")

    if E.shape == U.shape:
        print("Shapes match directly.")
    elif E.shape == U.t().shape:
        print("Shapes are transposed. Transposing U to match E.")
        U = U.t()
    else:
        print("Shapes do NOT match.")

    # Identity check
    if embeddings is unembeddings:
        print("Weights are TIED (Same object in memory).")
    elif torch.allclose(E, U, atol=1e-5):
        print("Weights are distinct objects but numerically identical.")
    else:
        print("Weights are UNTIED and distinct.")

    # Bias check
    if bias is not None:
        print(f"Unembedding Bias: Present (Shape: {bias.shape})")
    else:
        print("Unembedding Bias: None")

    # 2. Global Distance
    print(f"\n[2] Global Distance Metrics")
    frob_dist = torch.linalg.matrix_norm(E - U, ord='fro')
    e_norm = torch.linalg.matrix_norm(E, ord='fro')
    rel_dist = frob_dist / e_norm
    print(f"Frobenius Distance: {frob_dist:.4f}")
    print(f"Relative Distance:  {rel_dist:.4f}")

    # 3. Cosine Similarity Analysis
    print(f"\n[3] Cosine Similarity Analysis")
    cos_sims_list = []
    chunk_size = 10000
    for i in range(0, E.shape[0], chunk_size):
        end = min(i + chunk_size, E.shape[0])
        chunk_E = E[i:end]
        chunk_U = U[i:end]
        chunk_sim = F.cosine_similarity(chunk_E, chunk_U, dim=1)
        cos_sims_list.append(chunk_sim)
    
    cos_sims = torch.cat(cos_sims_list)
    avg_cos_sim = cos_sims.mean().item()
    print(f"Average Cosine Similarity: {avg_cos_sim:.4f}")

    # 4. Norm Analysis
    print(f"\n[4] Norm Analysis")
    e_norms = torch.norm(E, dim=1)
    u_norms = torch.norm(U, dim=1)
    print(f"Avg Embedding Norm:   {e_norms.mean().item():.4f}")
    print(f"Avg Unembedding Norm: {u_norms.mean().item():.4f}")

    # 5. Element-wise Similarity Analysis
    print(f"\n[5] Element-wise Similarity Analysis")
    
    max_diff = 0.0
    mean_diff_accum = 0.0
    total_elements = E.numel()
    
    chunk_size = 100000 # Elements, not rows, or rows depending on implementation. Let's do rows.
    chunk_rows = 5000
    
    # Counters for tolerance checks
    tol_counts = {1e-5: 0, 1e-4: 0, 1e-3: 0, 1e-2: 0}
    
    for i in range(0, E.shape[0], chunk_rows):
        end = min(i + chunk_rows, E.shape[0])
        chunk_E = E[i:end]
        chunk_U = U[i:end]
        
        chunk_diff = torch.abs(chunk_E - chunk_U)
        
        # Update max
        current_max = chunk_diff.max().item()
        if current_max > max_diff:
            max_diff = current_max
            
        # Update mean accumulator
        mean_diff_accum += chunk_diff.sum().item()
        
        # Update tolerance counts
        for tol in tol_counts:
            tol_counts[tol] += (chunk_diff < tol).sum().item()

        del chunk_diff, chunk_E, chunk_U
        
    mean_diff = mean_diff_accum / total_elements
    print(f"Max Absolute Difference: {max_diff:.6f}")
    print(f"Mean Absolute Difference: {mean_diff:.6f}")
    
    for tol in [1e-5, 1e-4, 1e-3, 1e-2]:
        close_ratio = (tol_counts[tol] / total_elements) * 100
        print(f"Elements within {tol}: {close_ratio:.2f}%")
    # 6. torch.allclose Analysis
    print(f"\n[6] torch.allclose Analysis")
    # Test various tolerance levels to see when they are considered 'close'
    # default allclose: rtol=1e-05, atol=1e-08
    tolerances = [
        (1e-5, 1e-8, "Default"),
        (1e-4, 1e-5, "Relaxed"),
        (1e-3, 1e-4, "Loose"),
        (1e-2, 1e-3, "Very Loose"),
        (0.1, 0.1, "Coarse")
    ]
    
    print(f"{'rtol':<10} {'atol':<10} {'Description':<12} {'Result'}")
    print("-" * 45)
    
    # Custom chunked allclose implementation to avoid OOM
    def chunked_allclose(tensor_a, tensor_b, rtol, atol, chunk_size=100000):
        for i in range(0, tensor_a.shape[0], chunk_size):
            end = min(i + chunk_size, tensor_a.shape[0])
            chunk_a = tensor_a[i:end]
            chunk_b = tensor_b[i:end]
            if not torch.allclose(chunk_a, chunk_b, rtol=rtol, atol=atol):
                return False
        return True

    for rtol, atol, desc in tolerances:
        # Use chunked check instead of full matrix check
        is_close = chunked_allclose(E, U, rtol=rtol, atol=atol, chunk_size=5000)
        print(f"{rtol:<10} {atol:<10} {desc:<12} {is_close}")

    # Clean up memory
    del model, embeddings, unembeddings, E, U, cos_sims, e_norms, u_norms
    torch.cuda.empty_cache()

if __name__ == "__main__":
    # Redirect stdout to a log file in the models directory
    import sys
    
    output_dir = "/home/comp/f2256768/SCCOT/models"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    log_file_path = os.path.join(output_dir, "matrix_similarity_analysis.log")
    
    class Tee(object):
        def __init__(self, *files):
            self.files = files
        def write(self, obj):
            for f in self.files:
                f.write(obj)
                f.flush() # If you want the output to be visible immediately
        def flush(self) :
            for f in self.files:
                f.flush()

    f = open(log_file_path, 'w')
    original_stdout = sys.stdout
    sys.stdout = Tee(sys.stdout, f)
    
    print(f"Logging output to: {log_file_path}")

    try:
        for name, path in MODEL_PATHS.items():
            analyze_model_matrices(name, path)
    finally:
        sys.stdout = original_stdout
        f.close()
