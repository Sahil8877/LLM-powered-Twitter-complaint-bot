from huggingface_hub import hf_hub_download
import os
import shutil

repo_id = "bartowski/Meta-Llama-3-8B-Instruct-GGUF"
filename = "Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"

os.makedirs("model", exist_ok=True)

cached_path = hf_hub_download(
    repo_id=repo_id,
    filename=filename
)

target_path = "model/" + filename

shutil.copy(cached_path, target_path)

print("Model copied to:", target_path)