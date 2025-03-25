import os
import time
from typing import Any

from app.lib.db import ensure_db_exists, get_project_root, write_json_file, read_json_file


async def get_projects() -> list[dict[str, Any]]:
    """
    获取所有项目
    Returns:
        List[Dict]: 项目列表
    """
    """
        获取所有项目
        Returns:
            List[Dict]: 项目列表
        """
    await ensure_db_exists()

    projects = []

    # 读取所有项目目录
    project_root = await get_project_root()
    items = os.listdir(project_root)

    for item in items:
        project_path = os.path.join(project_root, item)
        if os.path.isdir(project_path):
            config_path = os.path.join(project_path, 'config.json')
            config_data = await read_json_file(config_path)

            if config_data:
                projects.append({
                    'id': item,
                    **config_data
                })

    return projects

async def create_project(project_data: dict[str, Any]) -> dict[str, Any]:
    """
    创建新项目
    Args:
        project_data: 项目数据
    Returns:
        Dict: 创建的项目信息
    """
    await ensure_db_exists()

    project_id = str(int(time.time() * 1000))
    project_root = await get_project_root()
    project_dir = os.path.join(project_root, project_id)

    # 创建项目目录
    os.makedirs(project_dir, exist_ok=True)

    # 创建子目录
    os.makedirs(os.path.join(project_dir, 'files'), exist_ok=True)  # 原始文件
    os.makedirs(os.path.join(project_dir, 'chunks'), exist_ok=True)  # 分割后的文本片段

    # 创建项目配置文件
    config_path = os.path.join(project_dir, 'config.json')
    await write_json_file(config_path, project_data)

    # 创建空的问题列表文件
    questions_path = os.path.join(project_dir, 'questions.json')
    await write_json_file(questions_path, [])

    # 创建空的标签树文件
    tags_path = os.path.join(project_dir, 'tags.json')
    await write_json_file(tags_path, [])

    # 创建空的数据集结果文件
    datasets_path = os.path.join(project_dir, 'datasets.json')
    await write_json_file(datasets_path, [])

    if project_data.get('modelConfig'):
        model_config_path = os.path.join(project_dir, 'model-config.json')
        await write_json_file(model_config_path, project_data['modelConfig'])

    return {'id': project_id, **project_data}