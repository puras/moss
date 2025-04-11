import logging
import math

from fastapi import APIRouter, HTTPException

from app.core.llm.common import extract_json_from_llm_output
from app.core.llm.llm import LLMClient
from app.core.llm.question import get_question_prompt
from app.core.llm.question_en import get_question_en_prompt
from app.core.question import get_questions, get_questions_for_chunk, add_questions_for_chunk
from app.core.texts import get_text_chunk, get_text_chunk_ids

router = APIRouter()

@router.get("")
async def get_question_list():
    project_id = "000000"
    ret = await get_questions(project_id)
    return ret

@router.get("by_chunk/{chunk_id}")
async def get_question_by_chunk(chunk_id: str):
    project_id = "000000"
    ret = await get_questions_for_chunk(project_id, chunk_id)
    return ret

@router.post("/gen_chunk/{chunk_id}")
async def gen_chunk(chunk_id: str):
    project_id = "000000"
    client = LLMClient({
        "provider": "Ollama",
        "endpoint": "http://192.168.4.30:11434",
        "api_key": "EMPTY",
        "model": "deepseek-r1:32b"
    })
    language = '中文'
    task_config = {
        "text_split_min_length": 1500,
        "text_split_max_length": 2000,
        "question_generation_length": 240,
        "huggingface_token": '',
        "concurrency_limit": 5
    }
    question_generation_length = task_config['question_generation_length']
    results = []
    errors = []
    chunk = await get_text_chunk(project_id, chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="chunk not found")

    logging.info(chunk)

    try:
        # 根据文本长度自动计算问题数量
        question_number = math.floor(len(chunk['content']) / question_generation_length)

        # 根据语言选择相应的提示词函数
        prompt_func = get_question_en_prompt if language == 'en' else get_question_prompt
        # 生成问题
        prompt = prompt_func(chunk['content'], question_number, language)
        print('prompt')
        print("=" * 30)
        print(prompt)
        response = await client.get_response(prompt)
        print('response')
        print("=" * 30)
        print(response)

        # 从LLM输出中提取JSON格式的问题列表
        questions = extract_json_from_llm_output(response)

        if questions and isinstance(questions, list):
            # 保存问题到数据库
            await add_questions_for_chunk(project_id, chunk['id'], questions)

            results.append({
                'chunkId': chunk['id'],
                'success': True,
                'questions': questions,
                'total': len(questions)
            })
        else:
            errors.append({
                'chunkId': chunk['id'],
                'error': '解析问题失败'
            })
    except Exception as error:
        print(chunk)
        print(f"为文本块 {chunk['id']} 生成问题出错:", str(error))
        errors.append({
            'chunkId': chunk['id'],
            'error': str(error) or '生成问题失败'
        })

@router.post("/gen")
async def gen_questions():
    project_id = "000000"

    chunk_ids = await get_text_chunk_ids(project_id)

    if not chunk_ids:
        return []

    client = LLMClient({
        "provider": "Ollama",
        "endpoint": "http://192.168.4.30:11434",
        "api_key": "EMPTY",
        "model": "deepseek-r1:32b"
    })
    language = '中文'
    task_config = {
        "text_split_min_length": 1500,
        "text_split_max_length": 2000,
        "question_generation_length": 240,
        "huggingface_token": '',
        "concurrency_limit": 5
    }
    question_generation_length = task_config['question_generation_length']
    results = []
    errors = []

    for chunk_id in chunk_ids:
        chunk = await get_text_chunk(project_id, chunk_id)
        if not chunk:
            raise HTTPException(status_code=404, detail="chunk not found")

        try:
            # 根据文本长度自动计算问题数量
            question_number = math.floor(len(chunk['content']) / question_generation_length)

            # 根据语言选择相应的提示词函数
            prompt_func = get_question_en_prompt if language == 'en' else get_question_prompt
            # 生成问题
            prompt = prompt_func(chunk['content'], question_number, language)
            print('prompt')
            print("=" * 30)
            print(prompt)
            response = await client.get_response(prompt)
            print('response')
            print("=" * 30)
            print(response)

            # 从LLM输出中提取JSON格式的问题列表
            questions = extract_json_from_llm_output(response)
            logging.info(f"questions: {questions}")

            if isinstance(questions, dict):
                qs = questions["questions"]
                new_questions = []
                for question in qs:
                    if isinstance(question, dict):
                        question = question['question']
                        new_questions.append(question)
                    else:
                        new_questions.append(question)

                questions = new_questions

            logging.info(f"after questions:{questions}")

            if questions and isinstance(questions, list):
                # 保存问题到数据库
                await add_questions_for_chunk(project_id, chunk['id'], questions)

                results.append({
                    'chunkId': chunk['id'],
                    'success': True,
                    'questions': questions,
                    'total': len(questions)
                })
            else:
                errors.append({
                    'chunkId': chunk['id'],
                    'error': '解析问题失败'
                })
        except Exception as error:
            print(chunk)
            print(f"为文本块 {chunk['id']} 生成问题出错:", str(error))
            errors.append({
                'chunkId': chunk['id'],
                'error': str(error) or '生成问题失败'
            })

    return {
        "results": results,
        "errors": errors
    }