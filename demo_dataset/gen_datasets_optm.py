import json
import logging
import os
import re
import time
from typing import Dict, List
import queue
import concurrent.futures

import backoff
from openai import OpenAI
import pyarrow as pa
import pyarrow.parquet as pq

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

model = "/mnt/DeepSeek-R1-Distill-Qwen-32B"
entries_per_file = 1

openai_api_base = "http://42.248.142.34:11180/v1"
openai_api_key = ""
client = OpenAI(
    api_key='ollama',
    base_url=openai_api_base,
)


def read_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        info = f.read()
    return info


@backoff.on_exception(backoff.expo, Exception, max_tries=3)
def generate_single_entry(text: str) -> Dict:
    prompt = f"""
    基于以下文本，生成1个用于指令数据集的高质量条目。条目应该直接关联到给定的文本内容，提出相关的问题或任务。
    请确保生成多样化的指令类型，例如：
    - 分析类："分析..."
    - 比较类："比较..."
    - 解释类："解释..."
    - 评价类："评价..."
    - 问答类："为什么..."

    文本内容：
    {text}

    请以下面的格式生成条目，确保所有字段都有适当的内容：
    {{
        "instruction": "使用上述多样化的指令类型之一，提出一个具体的、与文本相关的问题或任务",
        "input": "如果需要额外的上下文信息，请在这里提供，否则留空",
        "output": "对instruction的详细回答或任务的完成结果"
    }}
    确保所有生成的内容都与给定的文本直接相关，生成的是有效的JSON格式，并且内容高质量、准确、详细。
    """

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4098
        )
        logger.info(f"API响应: {resp.choices[0].message.content}")

        json_match = re.search(r'\{.*\}', resp.choices[0].message.content, re.DOTALL)
        if json_match:
            entry = json.loads(json_match.group())
            required_keys = ["instruction", "input", "output"]
            if isinstance(entry, dict) and all(key in entry for key in required_keys):
                if entry['input'].strip():
                    entry[
                        'text'] = f"Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.### Instruction: {entry['instruction']}\n### Input: {entry['input']}\n### Response: {entry['output']}"
                else:
                    entry[
                        'text'] = f"Below is an instruction that describes a task. Write a response that appropriately completes the request.### Instruction: {entry['instruction']}\n### Input: {entry['input']}\n### Response: {entry['output']}"
                logger.info("成功生成完整条目")
                return entry
            else:
                logger.error("无法从API响应中提取有效的JSON")
                return {}

    except Exception as ex:
        logger.error(f"生成条目时发生错误:{str(ex)}")


class GenDatasets:
    def __init__(self, input_folder: str, workers=4):
        self.input_folder = input_folder
        self.workers = workers
        self.dataset = queue.Queue()

    def process_file(self, filename: str):
        file_path = os.path.join(self.input_folder, filename)
        logger.info(f"正在处理文件: {filename}")
        text = read_file(file_path)
        for j in range(entries_per_file):
            logger.info(f"  生成第 {j + 1}/{entries_per_file} 个条目")
            entry = generate_single_entry(text)
            if entry and all(key in entry for key in ["instruction", "input", "output", "text"]):
                self.dataset.put(entry)
                logger.info(f"  成功生成1个完整条目")
            else:
                logger.warning(f"  跳过不完整条目")
            time.sleep(2)

    @property
    def return_list(self):
        dataset_list = []
        while not self.dataset.empty():
            dataset_list.append(self.dataset.get())
        return dataset_list

    def generate(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = [executor.submit(self.process_file, filename) for filename in os.listdir(self.input_folder) if
                       filename.endswith(".txt")]
            concurrent.futures.wait(futures)
        return self.return_list




def save_dataset_as_parquet(dataset: List[Dict], output_file: str):
    schema = pa.schema([
        ('instruction', pa.string()),
        ('input', pa.string()),
        ('output', pa.string()),
        ('text', pa.string()),
    ])

    arrays = [
        pa.array([entry['instruction'] for entry in dataset]),
        pa.array([entry['input'] for entry in dataset]),
        pa.array([entry['output'] for entry in dataset]),
        pa.array([entry['text'] for entry in dataset])
    ]

    table = pa.Table.from_arrays(arrays, schema=schema)
    pq.write_table(table, output_file)


if __name__ == "__main__":
    input_folder = r"C:\code\Trans2txt\opt\output"
    output_path = r"C:\code\Trans2txt\opt\result.txt"

    logger.info("开始生成数据集")
    gen = GenDatasets(input_folder)
    dataset = gen.generate()
    # print(f'dataset: {dataset}')
    save_dataset_as_parquet(dataset, output_path)
    logger.info(f"数据集已生成并保存到 {output_path}")
    logger.info(f"共生成 {len(dataset)} 个有效条目")
