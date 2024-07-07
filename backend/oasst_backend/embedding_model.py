"""
Just follow the existing pattern used to create the databse engine, 
which also needs to be global and initiated only once.

The pattern is just to keep it global in a file. Can then create a dependency if wee need in a route. 
"""
import os
from sentence_transformers import SentenceTransformer

# TODO remove after dev, or make it configurable
LOCAL_MODEL_PATH = "/Users/einar/git/Open-Assistant-g11/_notebooks/RAG/multilingual-e5-large-instruct_local"
MODEL_NAME = "intfloat/multilingual-e5-large-instruct"

if os.path.exists(LOCAL_MODEL_PATH):
    model = SentenceTransformer(LOCAL_MODEL_PATH, local_files_only=True)
else:
    # download from huggingface, can take a while
    model = SentenceTransformer(MODEL_NAME)
