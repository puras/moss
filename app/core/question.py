import logging
import os
from typing import List, Any

from app.core.base import read_json_file, ensure_dir, write_json_file
from app.lib.db import get_db_directory


async def get_questions(project_id: str) -> List[dict[str, Any]]:
    """
    获取项目的所有问题
    Args:
        project_id: 项目ID
    Returns:
        问题列表
    """
    # project_root = await get_project_root()
    project_root = get_db_directory()
    project_path = os.path.join(project_root, project_id)
    questions_path = os.path.join(project_path, 'questions.json')
    logging.info(f"questions_path: {questions_path}")
    questions = await read_json_file(questions_path)
    return questions or []

async def get_questions_for_chunk(project_id: str, chunk_id: str) -> List[dict[str, Any]]:
    """
    获取指定文本块的问题
    Args:
        project_id: 项目ID
        chunk_id: 文本块ID
    Returns:
        问题列表
    """
    questions = await get_questions(project_id)
    chunk_questions = next((item for item in questions if item['chunkId'] == chunk_id), None)
    return chunk_questions['questions'] if chunk_questions else []

async def add_questions_for_chunk(project_id: str, chunk_id: str, new_questions: List[dict[str, Any]]) -> List[dict[str, Any]]:
    """
    添加问题到项目
    Args:
        project_id: 项目ID
        chunk_id: 文本块ID
        new_questions: 新问题列表
    Returns:
        更新后的问题列表
    """

    format_new_questions = new_questions
    for question in new_questions:
        if isinstance(question, dict):
            question = question['question']
        format_new_questions.append(question)

    new_questions = format_new_questions

    questions = await get_questions(project_id)

    # 检查是否已存在该文本块的问题
    existing_index = next((i for i, item in enumerate(questions) if item['chunkId'] == chunk_id), -1)

    if existing_index >= 0:
        # 更新现有问题
        questions[existing_index]['questions'] = new_questions
    else:
        # 添加新问题
        questions.append({
            'chunkId': chunk_id,
            'questions': new_questions
        })

    return await save_questions(project_id, questions)

async def save_questions(project_id: str, questions: List[dict[str, Any]]) -> List[dict[str, Any]]:
    """
    保存项目的问题列表
    Args:
        project_id: 项目ID
        questions: 问题列表
    Returns:
        保存后的问题列表
    """
    # project_root = await get_project_root()
    project_root = get_db_directory()
    project_path = os.path.join(project_root, project_id)
    questions_path = os.path.join(project_path, 'questions.json')

    await ensure_dir(project_path)

    try:
        await write_json_file(questions_path, questions)
        return questions
    except Exception as error:
        print('保存问题列表失败:', str(error))
        raise