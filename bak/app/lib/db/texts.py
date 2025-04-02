# 获取项目中所有原始文件
import os
from datetime import datetime

from bak.app.lib.db import get_project_root


async def get_files(project_id: str):
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