from vllm import LLM, SamplingParams

prompts = [
    "Hello, My name is",
    "The president of the United States is",
    "The capital of France is",
    "The future of AI is",
    "你好",
    "你是谁",
    "9.11与9.9哪个更大",
]

sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

# llm = LLM(model='facebook/opt-125m')
# llm = LLM(model='deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B')
llm = LLM(model='Qwen/Qwen2.5-1.5B-Instruct')

outputs = llm.generate(prompts, sampling_params)
for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"Prompt: {prompt}, Generated text: {generated_text!r}")