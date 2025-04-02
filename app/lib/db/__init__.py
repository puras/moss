import os
import json
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Any, Dict, Optional


# 获取适合的数据存储目录
def get_db_directory():
    return os.path.join(os.getcwd(), 'local-db')


# 项目根目录
PROJECT_ROOT = get_db_directory()

# 获取项目根目录
async def get_project_root():
    return PROJECT_ROOT


# 确保数据库目录存在
async def ensure_db_exists():
    try:
        if not os.path.exists(PROJECT_ROOT):
            os.makedirs(PROJECT_ROOT, exist_ok=True)
    except Exception as error:
        print(f"确保数据库目录存在时出错: {str(error)}")


# 读取JSON文件
async def read_json_file(file_path):
    try:
        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()
            return json.loads(data)
    except Exception as error:
        print(f"读取JSON文件 {file_path} 出错: {str(error)}")
        return None


# 写入JSON文件
async def write_json_file(file_path, data):
    # 使用临时文件策略，避免写入中断导致文件损坏
    fd, temp_file_path = tempfile.mkstemp(suffix='.tmp')
    os.close(fd)

    try:
        # 序列化为JSON字符串
        json_string = json.dumps(data, ensure_ascii=False, indent=2)

        # 先写入临时文件
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            f.write(json_string)

        # 从临时文件读取内容并验证
        try:
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                written_content = f.read()
                json.loads(written_content)  # 验证JSON是否有效

            # 验证通过后，原子性地重命名文件替换原文件
            # 确保目标目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            shutil.move(temp_file_path, file_path)
        except Exception as validation_error:
            # 验证失败，删除临时文件并抛出错误
            try:
                os.unlink(temp_file_path)
            except:
                pass
            raise ValueError(f"写入的JSON文件内容无效: {str(validation_error)}")

        return data
    except Exception as error:
        print(f"写入JSON文件 {file_path} 失败: {str(error)}")
        raise
    finally:
        # 确保临时文件被删除
        try:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        except:
            pass


# 确保目录存在
async def ensure_dir(dir_path):
    try:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
    except Exception as error:
        print(f"确保目录 {dir_path} 存在时出错: {str(error)}")