import json
import logging
import os
from typing import Any

from app.core.markdown.spliter import split_markdown
from app.core.markdown.topic import extract_table_of_contents, toc_to_markdown
from app.core.texts import get_db_directory, ensure_dir, get_file_by_hash, save_text_chunk


async def split_project_file(project_id: str, file_hash: str) -> dict[str, Any]:
    """
    分割项目中的Markdown文件
    Args:
        project_id: 项目ID
        file_name: 文件名
    Returns:
        Dict: 分割结果
    """
    try:
        # 获取项目根目录
        project_root = get_db_directory()
        project_path = os.path.join(project_root, project_id)

        task_config = {
            'textSplitMinLength': 1500,
            'textSplitMaxLength': 2000
        }

        # 获取分割参数
        min_length = task_config.get('textSplitMinLength', 1500)
        max_length = task_config.get('textSplitMaxLength', 2000)

        # 确保chunks目录存在
        chunks_dir = os.path.join(project_path, 'chunks')
        await ensure_dir(chunks_dir)

        # 保存所有分割结果
        saved_chunks = []
        file_content = ""

        file = await get_file_by_hash(project_id, file_hash)

        if file is None:
            raise FileNotFoundError(f"文件不存在")

        # 检查文件是否存在
        if not os.path.exists(file['path']):
            raise FileNotFoundError(f"文件 {file['name']} 不存在")

        file_name = file['name']

        # 读取文件内容
        with open(file['path'], 'r', encoding='utf-8') as f:
            file_content = f.read()

        # 分割文本
        split_result = split_markdown(file_content, min_length, max_length)

        # 保存分割结果到chunks目录
        chunks = []
        for index, part in enumerate(split_result):
            chunk_id = f"{os.path.splitext(os.path.basename(file['name']))[0]}-part-{index + 1}"
            await save_text_chunk(project_id, chunk_id, part['result'])

            chunks.append({
                'id': chunk_id,
                'content': part['content'],
                'summary': part['summary'],
                'length': len(part['content']),
                'fileName': file['name']
            })

        # 将当前文件的分割结果添加到总结果中
        saved_chunks.extend(chunks)

        # 提取目录结构
        toc_json = extract_table_of_contents(file_content)
        toc = toc_to_markdown(toc_json, {'isNested': True})

        # 保存目录结构到单独的toc文件夹
        toc_dir = os.path.join(project_path, 'toc')
        await ensure_dir(toc_dir)
        toc_path = os.path.join(toc_dir, f"{os.path.splitext(os.path.basename(file_name))[0]}-toc.json")

        with open(toc_path, 'w', encoding='utf-8') as f:
            json.dump(toc_json, f, ensure_ascii=False, indent=2)

        return {
            'fileName': file['name'],
            'totalChunks': len(saved_chunks),
            'chunks': saved_chunks,
            'toc': toc
        }

    except Exception as error:
        print('文本分割出错:', str(error))
        raise