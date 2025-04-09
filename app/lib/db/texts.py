import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from app.lib.db import get_project_root
from app.lib.db.base import ensure_dir

# 保存文本片段
async def save_text_chunk(project_id: str, chunk_id: str, content: str) -> Dict[str, str]:
    project_root = await get_project_root()
    project_path = os.path.join(project_root, project_id)
    chunks_dir = os.path.join(project_path, 'chunks')

    await ensure_dir(chunks_dir)

    chunk_path = os.path.join(chunks_dir, f"{chunk_id}.txt")
    with open(chunk_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return {'id': chunk_id, 'path': chunk_path}

# 获取文本片段
async def get_text_chunk(project_id: str, chunk_id: str) -> Optional[Dict[str, str]]:
    project_root = await get_project_root()
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

# 获取项目中所有文本片段的ID
async def get_text_chunk_ids(project_id: str) -> List[str]:
    project_root = await get_project_root()
    project_path = os.path.join(project_root, project_id)
    chunks_dir = os.path.join(project_path, 'chunks')

    if not os.path.exists(chunks_dir):
        return []

    files = os.listdir(chunks_dir)
    return [file.replace('.txt', '') for file in files if file.endswith('.txt')]

# 保存上传的原始文件
async def save_file(project_id: str, file_buffer: Union[bytes, str], file_name: str) -> Dict[str, str]:
    project_root = await get_project_root()
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

# 获取项目中所有原始文件
async def get_files(project_id: str) -> List[Dict[str, Any]]:
    project_root = await get_project_root()
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
            'name': file_name,
            'path': file_path,
            'size': stats.st_size,
            'createdAt': datetime.fromtimestamp(stats.st_ctime)
        })

    return file_stats

# 删除项目中的原始文件及相关的文本块
async def delete_file(project_id: str, file_name: str) -> Dict[str, Any]:
    project_root = await get_project_root()
    project_path = os.path.join(project_root, project_id)
    files_dir = os.path.join(project_path, 'files')
    chunks_dir = os.path.join(project_path, 'chunks')
    toc_dir = os.path.join(project_path, 'toc')

    # 确保目录存在
    await ensure_dir(toc_dir)

    # 删除原始文件
    file_path = os.path.join(files_dir, file_name)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as error:
        print(f"删除文件 {file_name} 失败:", str(error))
        # 如果文件不存在，继续处理

    # 删除相关的TOC文件
    base_name = os.path.splitext(file_name)[0]
    toc_path = os.path.join(files_dir, f"{base_name}-toc.json")
    try:
        if os.path.exists(toc_path):
            os.remove(toc_path)
    except Exception:
        # 如果TOC文件不存在，继续处理
        pass

    # 删除相关的文本块
    try:
        if os.path.exists(chunks_dir):
            chunks = os.listdir(chunks_dir)

            # 过滤出与该文件相关的文本块
            related_chunks = [chunk for chunk in chunks
                              if chunk.startswith(f"{base_name}-part-") and chunk.endswith('.txt')]

            # 删除相关的文本块
            for chunk in related_chunks:
                chunk_path = os.path.join(chunks_dir, chunk)
                os.remove(chunk_path)
    except Exception as error:
        print(f"删除文件 {file_name} 相关的文本块失败:", str(error))

    return {'success': True, 'fileName': file_name}