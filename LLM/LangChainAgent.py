from together import Together
from langchain_together import TogetherEmbeddings

from transformers import AutoTokenizer, AutoModel

from langchain_core.vectorstores import InMemoryVectorStore

from langchain_core.documents import Document

# Load the Sentence Transformer model
import re
import os
import dotenv

dotenv.load_dotenv()

options = [
    "next instruction",
    "previous instruction",
    "repeat instruction",
    "list ingredients",
    "current temperature",
    "time remaining",
    "start timer",
    "stop timer",
    "add ingredient",
    "remove ingredient",
    "recommend recipe",
    "measure ingredient",
    "add allergy",
    "remove allergy"
]

COMMAND_SIMILARITY_THRESHOLD = 0.95

if not os.getenv("TOGETHER_API_KEY"):
    raise ValueError("TOGETHER_API_KEY environment variable not set")

'''
Map Command Version with embeddings and simple vector search

try:
    embeddings = TogetherEmbeddings(
        model="togethercomputer/m2-bert-80M-8k-retrieval",
    )
except Exception as e:
    raise ValueError("Failed to load embeddings")

try:
    vectorstore = InMemoryVectorStore.from_texts(
        texts=options,
        embedding=embeddings,
    )
except Exception as e:
    raise ValueError("Failed to load vectorstore")

def mapCommand(inputString) -> str:
    results = vectorstore.similarity_search_with_score(
        query=inputString, k=1
    )
    for command, score in results:
        print("Command " + inputString + " mapped to " + command.page_content + " with score " + str(score))
        return command.page_content if score > COMMAND_SIMILARITY_THRESHOLD else None
    return None
'''

try:
# Load the Sentence Transformer model
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)   
except Exception as e:
    raise ValueError("Failed to load model")
class SentenceTransformerEmbeddings(TogetherEmbeddings):
    def __init__(self, model):
        self.model = model

    def embed_documents(self, texts):
        """Generate embeddings for a list of documents."""
        return self.model.encode(texts, convert_to_tensor=False).tolist()

    def embed_query(self, text):
        """Generate an embedding for a single query."""
        return self.model.encode(text, convert_to_tensor=False).tolist()

try:
    embedding_function = SentenceTransformerEmbeddings(model)
    embeddings = model.encode(options)
    
except Exception as e:
    raise ValueError("Failed to load vectorstore with options")

def mapCommand(inputString) -> str:
    inputEmbedding = model.encode(inputString)
    similarities = model.similarity(inputEmbedding, embeddings)
    mxScore = 0
    closestCommand = None
    for idx, score in enumerate(similarities[0]):
        if score > mxScore and score > COMMAND_SIMILARITY_THRESHOLD:
            mxScore = score
            closestCommand = options[similarities[0].index(idx)]
    
    if closestCommand is not None:
        print("Command " + inputString + " mapped to " + closestCommand + " with score " + str(mxScore))
        return closestCommand
    
    return None