import os
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import streamlit as st

# Define the local model path (Update this based on your system)
MODEL_PATH = os.path.expanduser("~/.cache/huggingface/hub/models--meta-llama--Llama-2-7b-chat-hf")

@st.cache_resource()  # Cache the model so it loads only once
def load_llama():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float32,  # Use float32 for CPU execution
        device_map="cpu",  # Force CPU mode (macOS-friendly)
        local_files_only=True  # Ensure local model usage (no downloads)
    )
    return model, tokenizer

# Load the model once
model, tokenizer = load_llama()

# Function to generate AI-powered journaling prompts
def generate_prompt():
    input_text = "Generate a meaningful journaling prompt for self-reflection:"
    input_ids = tokenizer(input_text, return_tensors="pt").input_ids
    output = model.generate(input_ids, max_length=50)
    return tokenizer.decode(output[0], skip_special_tokens=True)
