from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load DeepSeek-V3 Model with trust_remote_code=True
model_name = "deepseek-ai/deepseek-v3"
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)  # Allow remote code execution
model = AutoModelForCausalLM.from_pretrained(model_name, 
                                             torch_dtype=torch.float16, 
                                             device_map="auto", 
                                             trust_remote_code=True)  # Required to execute custom code

# Function to Generate AI Prompts
def generate_journal_prompt():
    input_text = "Generate a self-reflective journaling prompt:"
    input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to("cuda")

    output = model.generate(input_ids, max_length=50)
    prompt = tokenizer.decode(output[0], skip_special_tokens=True)
    return prompt

# Test Prompt Generation
print(generate_journal_prompt())


