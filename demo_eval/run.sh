#!/bin/bash

python run.py \
    --datasets demo_gsm8k_chat_gen demo_math_chat_gen \
    --hf-type chat \
    --hf-path deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B \
    --debug