import os
from typing import List, Dict, Any

from .base import get_project_root, ensure_dir, read_json_file, write_json_file


async def get_questions(project_id: str) -> List[Dict[str, Any]]:
    """
    获取项目的所有问题
    Args:
        project_id: 项目ID
    Returns:
        问题列表
    """
    project_root = await get_project_root()
    project_path = os.path.join(project_root, project_id)
    questions_path = os.path.join(project_path, 'questions.json')
    questions = await read_json_file(questions_path)
    return questions or []


async def save_questions(project_id: str, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    保存项目的问题列表
    Args:
        project_id: 项目ID
        questions: 问题列表
    Returns:
        保存后的问题列表
    """
    project_root = await get_project_root()
    project_path = os.path.join(project_root, project_id)
    questions_path = os.path.join(project_path, 'questions.json')

    await ensure_dir(project_path)

    try:
        await write_json_file(questions_path, questions)
        return questions
    except Exception as error:
        print('保存问题列表失败:', str(error))
        raise


async def add_questions_for_chunk(project_id: str, chunk_id: str, new_questions: List[Dict[str, Any]]) -> List[
    Dict[str, Any]]:
    """
    添加问题到项目
    Args:
        project_id: 项目ID
        chunk_id: 文本块ID
        new_questions: 新问题列表
    Returns:
        更新后的问题列表
    """
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


async def get_questions_for_chunk(project_id: str, chunk_id: str) -> List[Dict[str, Any]]:
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


async def delete_questions_for_chunk(project_id: str, chunk_id: str) -> List[Dict[str, Any]]:
    """
    删除指定文本块的问题
    Args:
        project_id: 项目ID
        chunk_id: 文本块ID
    Returns:
        更新后的问题列表
    """
    questions = await get_questions(project_id)
    updated_questions = [item for item in questions if item['chunkId'] != chunk_id]
    return await save_questions(project_id, updated_questions)


async def delete_question(project_id: str, question_id: str, chunk_id: str) -> List[Dict[str, Any]]:
    """
    删除单个问题
    Args:
        project_id: 项目ID
        question_id: 问题ID
        chunk_id: 文本块ID
    Returns:
        更新后的问题列表
    """
    questions = await get_questions(project_id)

    # 找到包含该问题的文本块
    chunk_index = next((i for i, item in enumerate(questions) if item['chunkId'] == chunk_id), -1)

    if chunk_index == -1:
        # 如果没有找到文本块，返回原有问题列表
        return questions

    # 复制问题列表，避免直接修改原有对象
    updated_questions = questions.copy()
    chunk = updated_questions[chunk_index].copy()

    # 从文本块中移除指定问题
    chunk['questions'] = [q for q in chunk['questions'] if q['question'] != question_id]

    # 更新文本块
    updated_questions[chunk_index] = chunk

    # 如果文本块中没有问题了，可以选择移除该文本块
    # 这里选择保留空文本块，以便后续可能添加新问题

    return await save_questions(project_id, updated_questions)


async def batch_delete_questions(project_id: str, questions_to_delete: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    批量删除问题
    Args:
        project_id: 项目ID
        questions_to_delete: 要删除的问题数组，每个元素包含 questionId 和 chunkId
    Returns:
        更新后的问题列表
    """
    questions = await get_questions(project_id)

    # 对每个要删除的问题，从其所属的文本块中移除
    for question_info in questions_to_delete:
        question_id = question_info['questionId']
        chunk_id = question_info['chunkId']

        # 找到包含该问题的文本块
        chunk_index = next((i for i, item in enumerate(questions) if item['chunkId'] == chunk_id), -1)

        if chunk_index != -1:
            # 复制文本块对象
            chunk = questions[chunk_index].copy()

            # 从文本块中移除指定问题
            chunk['questions'] = [q for q in chunk['questions'] if q['question'] != question_id]

            # 更新文本块
            questions[chunk_index] = chunk

    # 保存更新后的问题列表
    return await save_questions(project_id, questions)