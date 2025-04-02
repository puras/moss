import os

from flask import Blueprint, request
from werkzeug.utils import secure_filename

from bak.app.lib.db import get_project_root, ensure_dir
from bak.app.lib.db.project import get_project, update_project
from bak.app.lib.db.texts import get_files
from bak.app.utils.async_utils import async_route
from bak.app.utils.response import R

file_bp = Blueprint('file', __name__, url_prefix='/projects/<int:project_id>/files')

@file_bp.route('', methods=['GET'])
@async_route
async def get_list(project_id):
    project_id = str(project_id)
    files = await get_files(project_id)
    return R.ok(files)


@file_bp.route('', methods=['POST'])
@async_route
async def upload(project_id):
    """上传文件"""
    project_id = str(project_id)
    print('文件上传请求开始处理, 参数:', project_id)

    print('开始获取项目信息, project_id:', project_id)
    proj = await get_project(project_id)
    print(proj)
    if not proj:
        print('项目不存在，返回404错误')
        return R.not_found('项目不存在')

    print('项目信息获取成功:', proj.get('name') or project_id)

    try:
        print('尝试使用备用方法处理文件上传...')

        # 检查请求头中是否包含文件名
        encoded_file_name = request.headers.get('x-file-name')

        # 直接从请求体中读取二进制数据
        print('开始读取请求体数据...')
        if 'file' not in request.files:
            return R.bad_request('没有文件上传')

        file = request.files['file']
        if file.filename == '':
            return R.bad_request('没有选择文件')

        if not file:
            return R.bad_request('无效文件')

        file_name = secure_filename(file.filename)

        # 检查文件类型
        if not file_name.endswith('.md'):
            print('文件类型不支持:', file_name)
            return R.bad_request('只支持上传Markdown文件')

        # 保存文件
        print('获取项目根目录...')
        project_root = await get_project_root()
        print('项目根目录:', project_root)
        project_path = os.path.join(project_root, project_id)
        files_dir = os.path.join(project_path, 'files')
        print('文件将保存到:', files_dir)

        print('确保目录存在...')
        await ensure_dir(files_dir)
        print('目录已确认存在')

        file_path = os.path.join(files_dir, file_name)
        print('开始写入文件:', file_path)
        file.save(file_path)
        print('文件写入成功')

        # 更新项目配置，添加上传的文件记录
        print('更新项目配置...')
        uploaded_files = proj.get('uploadedFiles', [])
        if file_name not in uploaded_files:
            uploaded_files.append(file_name)

            # 更新项目配置
            print('保存更新后的项目配置...')
            proj['uploadedFiles'] = uploaded_files
            await update_project(project_id, proj)
            print('项目配置更新成功')
        else:
            print('文件已存在于项目配置中，无需更新')

        print('文件上传处理完成，返回成功响应')
        return R.ok({
            'message': '文件上传成功',
            'fileName': file_name,
            'filePath': file_path
        })
    except Exception as error:
        print('上传文件处理过程中出错:', str(error))
        import traceback
        print('错误堆栈:', traceback.format_exc())
        return R.server_error(f'文件上传失败: {str(error) or "未知错误"}')

# @file_bp.route('<', methods=['POST'])
# def delete():
#     return R.ok()