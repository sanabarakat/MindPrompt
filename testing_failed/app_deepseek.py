import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load DeepSeek-V3 Model
model_name = "deepseek-ai/deepseek-v3"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")

st.title("AI-Powered Journaling with DeepSeek-V3")

# Generate AI Prompts
def generate_prompt():
    input_text = "Generate a meaningful journaling prompt for self-reflection:"
    input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to("cuda")
    output = model.generate(input_ids, max_length=50)
    return tokenizer.decode(output[0], skip_special_tokens=True)

if st.button("Generate AI Prompt"):
    prompt = generate_prompt()
    st.write("Suggested Prompt:", prompt)
