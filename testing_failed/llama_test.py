from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load LLaMA-2 Model (Meta AI)
model_name = "TheBloke/Llama-2-7B-GGUF"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32, device_map="cpu")  # Runs on CPU

# Function to Generate AI Prompts
def generate_prompt():
    input_text = "Generate a thoughtful journaling prompt for self-reflection:"
    input_ids = tokenizer(input_text, return_tensors="pt").input_ids
    output = model.generate(input_ids, max_length=50)
    return tokenizer.decode(output[0], skip_special_tokens=True)

# Test Prompt Generation
print(generate_prompt())
