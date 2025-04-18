# -*- coding: utf-8 -*-
"""OOPs RAG ChatBot.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1JwFgtgpgwu8Bb-WqDa-n11h9mVmscUN-
"""

#   PART A

# Install necessary libraries
%pip install PyPDF2 openai faiss-cpu
%pip install --upgrade openai
# Import necessary libraries
import PyPDF2
import openai
import numpy as np
import faiss
import os
from openai import OpenAI
os.environ["OPENAI_API_KEY"] = "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"  # Replace with your OpenAI API key

client = OpenAI()

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

# Function to split text into smaller chunks
def split_text_into_chunks(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks


# Generate embeddings for text chunks
def generate_embeddings(chunks):
    embeddings = []
    for chunk in chunks:
        response = client.embeddings.create(
            input=chunk,
            model="text-embedding-ada-002"
        )
        embedding = response.data[0].embedding
        embeddings.append(embedding)
    return embeddings

# Save embeddings and text chunks into a FAISS index
def save_embeddings_to_faiss(embeddings, index_path):
    dimension = len(embeddings[0])  # Embedding vector size
    if os.path.exists(index_path):
        faiss_index = faiss.read_index(index_path)
    else:
        index = faiss.IndexFlatL2(dimension)
        faiss_index = faiss.IndexIDMap(index)

    ids = list(range(faiss_index.ntotal, faiss_index.ntotal + len(embeddings)))
    faiss_index.add_with_ids(np.array(embeddings).astype("float32"), np.array(ids))
    faiss.write_index(faiss_index, index_path)

# Process a PDF and store embeddings and chunks
def process_pdf_and_store_embeddings(pdf_path, index_path, text_chunks_path):

    text = extract_text_from_pdf(pdf_path)
    chunks = split_text_into_chunks(text)

    # Generate embeddings
    embeddings = generate_embeddings(chunks)

    # Save embeddings and text chunks
    save_embeddings_to_faiss(embeddings, index_path)
    with open(text_chunks_path, "w") as f:
        for chunk in chunks:
            f.write(chunk + "\n")
    print(f"Processed and stored embeddings and text chunks for {pdf_path}")

#Example Usage
pdf_path = "/content/data.pdf"
index_path = "/content/faiss_index"
text_chunks_path = "/content/text_chunks"
process_pdf_and_store_embeddings(pdf_path, index_path, text_chunks_path)

# PART B


# Load FAISS index
def load_faiss_index(index_path):
    return faiss.read_index(index_path)

# Load text chunks from file
def load_text_chunks(text_chunks_path):
    with open(text_chunks_path, "r") as f:
        return [line.strip() for line in f.readlines()]

# Generate embeddings for a query
def generate_query_embedding(query):
    response = client.embeddings.create(
        input=query,
        model="text-embedding-ada-002"
    )
    query_embedding = np.array(response.data[0].embedding).astype("float32").reshape(1, -1)
    return query_embedding

# Search FAISS index for relevant chunks
def search_faiss_index(faiss_index, query_embedding, k=5):
    distances, indices = faiss_index.search(query_embedding, k)
    return indices[0]  # Return indices of top-k results

# Generate a response using relevant text chunks
def generate_response(query, relevant_chunks):
    context = " ".join(relevant_chunks)
    prompt = f"Context: {context}\n\nQuery: {query}\nAnswer:"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[ {"role": "system", "content": "You are a concise assistant. Provide brief and to-the-point answers."},
         {"role": "user", "content": prompt}],
        max_tokens=200
    )
    return response.choices[0].message.content

# Handle query with pre-computed embeddings and text chunks
def answer_query(query, index_path, text_chunks_path, k=5):
    # Load stored data
    faiss_index = load_faiss_index(index_path)
    text_chunks = load_text_chunks(text_chunks_path)

    # Generate query embedding
    query_embedding = generate_query_embedding(query)

    # Search FAISS index
    relevant_indices = search_faiss_index(faiss_index, query_embedding, k)

    # Retrieve relevant chunks
    relevant_chunks = [text_chunks[i] for i in relevant_indices if i < len(text_chunks)]

    # Generate response
    return generate_response(query, relevant_chunks)

#Example Usuage
index_path = "/content/faiss_index"
text_chunks_path = "/content/text_chunks"
query = "Who is the instructor in charge and what are evaluative components."
answer = answer_query(query, index_path, text_chunks_path, k=5)
print("Generated Answer:", answer)
