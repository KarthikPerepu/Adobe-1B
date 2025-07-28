# Filename: download_model.py
from sentence_transformers import SentenceTransformer

model_name = 'all-MiniLM-L6-v2'
model = SentenceTransformer(model_name)
model.save(f'models/{model_name}')
print(f"Model '{model_name}' downloaded and saved to 'models/' directory.")