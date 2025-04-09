import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from lib.db.projects import get_project
from lib.db.questions import get_questions_for_chunk
from lib.split.markdown import split_markdown
from lib.split.markdown.toc import extract_table_of_contents, toc_to_markdown
from .db.base import get_project_root, ensure_dir, read_json_file
from .db.texts import save_text_chunk, get_files

# 导入Markdown分割工具

async def split_project_file(project_id: str, file_name: str) -> Dict[str, Any]:
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
        project_root = await get_project_root()
        project_path = os.path.join(project_root, project_id)

        # 获取文件列表
        files = await get_files(project_id)
        project = await get_project(project_id)
        file_name = project['name']

        # 获取任务配置
        task_config_path = os.path.join(project_path, 'task-config.json')
        try:
            if os.path.exists(task_config_path):
                with open(task_config_path, 'r', encoding='utf-8') as f:
                    task_config = json.load(f)
            else:
                # 如果配置文件不存在，使用默认配置
                task_config = {
                    'textSplitMinLength': 1500,
                    'textSplitMaxLength': 2000
                }
        except Exception:
            # 如果配置文件不存在，使用默认配置
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
        files_content = ""

        # 循环处理每个文件
        for file in files:
            # 检查文件是否存在
            if not os.path.exists(file['path']):
                raise FileNotFoundError(f"文件 {file['name']} 不存在")

            # 读取文件内容
            with open(file['path'], 'r', encoding='utf-8') as f:
                file_content = f.read()

            files_content += file_content

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
        toc_json = extract_table_of_contents(files_content)
        toc = toc_to_markdown(toc_json, {'isNested': True})

        # 保存目录结构到单独的toc文件夹
        toc_dir = os.path.join(project_path, 'toc')
        await ensure_dir(toc_dir)
        toc_path = os.path.join(toc_dir, f"{os.path.splitext(os.path.basename(file_name))[0]}-toc.json")

        with open(toc_path, 'w', encoding='utf-8') as f:
            json.dump(toc_json, f, ensure_ascii=False, indent=2)

        return {
            'fileName': file_name,
            'totalChunks': len(saved_chunks),
            'chunks': saved_chunks,
            'toc': toc
        }

    except Exception as error:
        print('文本分割出错:', str(error))
        raise


async def get_project_chunks(project_id: str) -> Dict[str, Any]:
    """
    获取项目中的所有文本块
    Args:
        project_id: 项目ID
    Returns:
        Dict: 文本块详细信息
    """
    try:
        project_root = await get_project_root()
        project_path = os.path.join(project_root, project_id)
        chunks_dir = os.path.join(project_path, 'chunks')
        toc_dir = os.path.join(project_path, 'toc')
        project = await get_project(project_id)

        # 检查chunks目录是否存在
        if not os.path.exists(chunks_dir):
            return {'chunks': []}

        # 读取所有文本块文件
        files = os.listdir(chunks_dir)
        chunk_files = [f for f in files if f.endswith('.txt')]

        # 按文件名分组文本块
        chunks_by_file = {}

        for chunk_file in chunk_files:
            chunk_id = os.path.splitext(chunk_file)[0]
            chunk_path = os.path.join(chunks_dir, chunk_file)

            with open(chunk_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 从文本块ID中提取文件名
            # 格式为: filename-part-X
            import re
            file_name_match = re.match(r'(.+)-part-\d+', chunk_id)
            file_name = f"{file_name_match.group(1)}.md" if file_name_match else None

            if file_name:
                if file_name not in chunks_by_file:
                    chunks_by_file[file_name] = []

                questions = await get_questions_for_chunk(project_id, chunk_id)

                chunks_by_file[file_name].append({
                    'id': chunk_id,
                    'content': content[:200] + ('...' if len(content) > 200 else ''),
                    'summary': content[:100] + ('...' if len(content) > 100 else ''),
                    'length': len(content),
                    'fileName': file_name,
                    'questions': questions
                })

        # 读取所有TOC文件
        toc_by_file = {}
        if os.path.exists(toc_dir):
            toc_files = os.listdir(toc_dir)

            for toc_file in toc_files:
                if toc_file.endswith('-toc.json'):
                    toc_path = os.path.join(toc_dir, toc_file)
                    file_name = f"{os.path.splitext(toc_file)[0][:-4]}.md"

                    try:
                        with open(toc_path, 'r', encoding='utf-8') as f:
                            toc_by_file[file_name] = json.load(f)
                    except json.JSONDecodeError as e:
                        print(f"解析TOC文件 {toc_file} 出错:", str(e))

        tocs = ""
        if files:
            project_name_md = f"{project['name']}.md"
            if project_name_md in toc_by_file:
                tocs = toc_to_markdown(toc_by_file[project_name_md], {'isNested': True})

        # 整合结果
        file_result = {
            'fileName': f"{project['name']}.md",
            'totalChunks': 0,
            'chunks': [],
            'toc': tocs
        }

        # 取出所有chunks
        for file_name, chunks in chunks_by_file.items():
            file_result['totalChunks'] += len(chunks)
            file_result['chunks'].extend(chunks)

        return {
            'fileResult': file_result,
            'chunks': [os.path.splitext(f)[0] for f in chunk_files]
        }

    except Exception as error:
        print('获取文本块出错:', str(error))
        raise


async def get_chunk_content(project_id: str, chunk_id: str) -> Dict[str, Any]:
    """
    获取文本块内容
    Args:
        project_id: 项目ID
        chunk_id: 文本块ID
    Returns:
        Dict: 文本块内容
    """
    try:
        project_root = await get_project_root()
        project_path = os.path.join(project_root, project_id)
        chunk_path = os.path.join(project_path, 'chunks', f"{chunk_id}.txt")

        if not os.path.exists(chunk_path):
            raise FileNotFoundError(f"文本块 {chunk_id} 不存在")

        with open(chunk_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            'id': chunk_id,
            'content': content
        }

    except Exception as error:
        print('获取文本块内容出错:', str(error))
        raise