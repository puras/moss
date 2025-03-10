from unsloth import FastLanguageModel

max_seq_length = 2048
dtype = None
load_in_4bit = True


model_name = "DeepSeek-R1-Distill-Qwen-1.5B-ming"
save_model_name = model_name + "_merged-16bit"

alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_name, # YOUR MODEL YOU USED FOR TRAINING
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit
)
FastLanguageModel.for_inference(model) # Enable native 2x faster inference

# alpaca_prompt = You MUST copy from above!
inputs = tokenizer(
[
    alpaca_prompt.format(
        "What is a famous tall tower in Paris?", # instruction
        "", # input
        "", # output - leave this blank for generation!
    )
], return_tensors = "pt").to("cuda")

outputs = model.generate(**inputs, max_new_tokens = 64, use_cache = True)
tokenizer.batch_decode(outputs)

model.save_pretrained_merged(save_model_name, tokenizer, save_method = "merged_16bit")

# model.save_pretrained_gguf("Llama-3.2-3B-Instruct-moss_q4_k_m", tokenizer, quantization_method = "q4_k_m")
# print(tokenizer._ollama_modelfile)