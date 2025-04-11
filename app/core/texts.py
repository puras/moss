# 获取适合的数据存储目录
import logging
import os
import hashlib  # 新增导入
from typing import Union, List, Any, Dict

from app.core.base import ensure_dir


def get_db_directory():
    return os.path.join(os.getcwd(), 'local-db')

# 获取项目中所有原始文件
async def get_files(project_id: str) -> List[dict[str, Any]]:
    project_root = get_db_directory()
    project_path = os.path.join(project_root, project_id)
    files_dir = os.path.join(project_path, 'files')

    if not os.path.exists(files_dir):
        return []

    files = os.listdir(files_dir)
    file_stats = []

    for file_name in files:
        # 跳过非文件项目
        file_path = os.path.join(files_dir, file_name)
        if not os.path.isfile(file_path):
            continue

        # 只返回Markdown文件，跳过其他文件
        if not file_name.endswith('.md'):
            continue

        stats = os.stat(file_path)
        file_stats.append({
            'id': hashlib.md5(file_name.encode()).hexdigest(),
            'name': file_name,
            'path': file_path,
            'size': stats.st_size
        })

    return file_stats

# 根据hash值获取原始文件
async def get_file_by_hash(project_id: str, file_hash: str) -> dict[str, str]:
    files = await get_files(project_id)
    for file_info in files:
        if file_info['id'] == file_hash:
            return file_info
    return None

# 保存上传的原始文件
async def save_file(project_id: str, file_buffer: Union[bytes, str], file_name: str) -> dict[str, str]:
    project_root = get_db_directory()
    project_path = os.path.join(project_root, project_id)
    files_dir = os.path.join(project_path, 'files')

    await ensure_dir(files_dir)

    file_path = os.path.join(files_dir, file_name)

    # 根据file_buffer类型决定写入模式
    mode = 'wb' if isinstance(file_buffer, bytes) else 'w'
    encoding = None if isinstance(file_buffer, bytes) else 'utf-8'

    with open(file_path, mode, encoding=encoding) as f:
        f.write(file_buffer)

    return {
        'name': file_name,
        'path': file_path
    }

# 获取项目中所有文本片段的ID
async def get_text_chunk_ids(project_id: str) -> List[str]:
    project_root = get_db_directory()
    project_path = os.path.join(project_root, project_id)
    chunks_dir = os.path.join(project_path, 'chunks')

    if not os.path.exists(chunks_dir):
        return []

    files = os.listdir(chunks_dir)
    return [file.replace('.txt', '') for file in files if file.endswith('.txt')]

# 获取文本片段
async def get_text_chunk(project_id: str, chunk_id: str):
    # project_root = await get_project_root()
    project_root = get_db_directory()
    project_path = os.path.join(project_root, project_id)
    chunk_path = os.path.join(project_path, 'chunks', f"{chunk_id}.txt")

    try:
        if not os.path.exists(chunk_path):
            return None

        with open(chunk_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            'id': chunk_id,
            'content': content,
            'path': chunk_path
        }
    except Exception:
        return None

# 保存文本片段
async def save_text_chunk(project_id: str, chunk_id: str, content: str) -> dict[str, str]:
    project_root = get_db_directory()
    project_path = os.path.join(project_root, project_id)
    chunks_dir = os.path.join(project_path, 'chunks')

    await ensure_dir(chunks_dir)

    chunk_path = os.path.join(chunks_dir, f"{chunk_id}.txt")
    with open(chunk_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return {'id': chunk_id, 'path': chunk_path}