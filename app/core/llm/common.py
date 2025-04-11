import json
from typing import Optional, Union, Dict


def extract_json_from_llm_output(output: str) -> Optional[Union[Dict, list]]:
    """从 LLM 输出中提取 JSON"""
    # 先尝试直接 parse
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        pass

    json_start = output.find('```json')
    json_end = output.rfind('```')
    if json_start != -1 and json_end != -1:
        json_string = output[json_start + 7:json_end]
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as error:
            print('解析 JSON 时出错:', str(error))
    return None

def extract_think_chain(text: str) -> str:
    """提取思维链内容"""
    start_tags = ["<think>", "<thinking>"]
    end_tags = ["</think>", "</thinking>"]
    start_index = -1
    end_index = -1
    used_start_tag = ""
    used_end_tag = ""

    for i, start_tag in enumerate(start_tags):
        current_start_index = text.find(start_tag)
        if current_start_index != -1:
            start_index = current_start_index
            used_start_tag = start_tag
            used_end_tag = end_tags[i]
            break

    if start_index == -1:
        return ""

    end_index = text.find(used_end_tag, start_index + len(used_start_tag))

    if end_index == -1:
        return ""

    return text[start_index + len(used_start_tag):end_index].strip()

def extract_answer(text: str) -> str:
    """提取答案内容"""
    start_tags = ["<think>", "<thinking>"]
    end_tags = ["</think>", "</thinking>"]
    for start, end in zip(start_tags, end_tags):
        if start in text and end in text:
            parts_before = text.split(start)
            parts_after = parts_before[1].split(end)
            return f"{parts_before[0].strip()} {parts_after[1].strip()}".strip()
    return text