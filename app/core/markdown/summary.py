"""
摘要生成模块
"""


def generate_enhanced_summary(section, outline, part_index=None, total_parts=None):
    """
    生成段落增强摘要，包含该段落中的所有标题
    Args:
        section (dict): 段落对象
        outline (list): 目录大纲
        part_index (int, optional): 子段落索引
        total_parts (int, optional): 子段落总数
    Returns:
        str: 生成的增强摘要
    """
    # 如果是文档前言
    if (not section.get('heading') and section.get('level') == 0) or (
            not section.get('headings') and not section.get('heading')):
        # 获取文档标题（如果存在）
        doc_title = outline[0]['title'] if outline and outline[0]['level'] == 1 else '文档'
        return f"{doc_title} 前言"

    # 如果有headings数组，使用它
    if section.get('headings') and len(section['headings']) > 0:
        # 按照级别和位置排序标题
        sorted_headings = sorted(section['headings'],
                                 key=lambda x: (x['level'], x['position']))

        # 构建所有标题包含的摘要
        headings_map = {}  # 用于去重

        # 首先处理每个标题，找到其完整路径
        for heading in sorted_headings:
            # 跳过空标题
            if not heading.get('heading'):
                continue

            # 查找当前标题在大纲中的位置
            heading_index = next((i for i, item in enumerate(outline)
                                  if item['title'] == heading['heading'] and
                                  item['level'] == heading['level']), -1)

            if heading_index == -1:
                # 如果在大纲中找不到，直接使用当前标题
                headings_map[heading['heading']] = heading['heading']
                continue

            # 查找所有上级标题
            path_parts = []
            parent_level = heading['level'] - 1

            for i in range(heading_index - 1, -1, -1):
                if outline[i]['level'] == parent_level:
                    path_parts.insert(0, outline[i]['title'])
                    parent_level -= 1
                if parent_level <= 0:
                    break

            # 添加当前标题
            path_parts.append(heading['heading'])

            # 生成完整路径并存储到字典中
            full_path = ' > '.join(path_parts)
            headings_map[full_path] = full_path

        # 将所有标题路径转换为列表并按间隔符数量排序（表示层级深度）
        paths = sorted(headings_map.values(),
                       key=lambda x: (x.count('>'), x))

        # 如果没有有效的标题，返回默认摘要
        if not paths:
            return section.get('heading', '未命名段落')

        # 如果是单个标题，直接返回
        if len(paths) == 1:
            summary = paths[0]
            # 如果是分段的部分，添加Part信息
            if part_index is not None and total_parts > 1:
                summary += f" - Part {part_index}/{total_parts}"
            return summary

        # 如果有多个标题，生成多标题摘要
        summary = ""

        # 尝试找到公共前缀
        first_path = paths[0]
        segments = first_path.split(' > ')

        for i in range(len(segments) - 1):
            prefix = ' > '.join(segments[:i + 1])
            is_common_prefix = True

            for path in paths[1:]:
                if not path.startswith(prefix + ' > '):
                    is_common_prefix = False
                    break

            if is_common_prefix:
                summary = prefix + ' > ['
                # 添加非公共部分
                unique_parts = [path[len(prefix) + 3:] for path in paths]
                summary += ', '.join(unique_parts) + ']'
                break

        # 如果没有公共前缀，使用完整列表
        if not summary:
            summary = ', '.join(paths)

        # 如果是分段的部分，添加Part信息
        if part_index is not None and total_parts > 1:
            summary += f" - Part {part_index}/{total_parts}"

        return summary

    # 兼容旧逻辑，当没有headings数组时
    if not section.get('heading') and section.get('level') == 0:
        return '文档前言'

    # 查找当前段落在大纲中的位置
    current_heading_index = next((i for i, item in enumerate(outline)
                                  if item['title'] == section.get('heading') and
                                  item['level'] == section.get('level')), -1)

    if current_heading_index == -1:
        return section.get('heading', '未命名段落')

    # 查找所有上级标题
    parent_headings = []
    parent_level = section.get('level', 0) - 1

    for i in range(current_heading_index - 1, -1, -1):
        if outline[i]['level'] == parent_level:
            parent_headings.insert(0, outline[i]['title'])
            parent_level -= 1
        if parent_level <= 0:
            break

    # 构建摘要
    summary = ''

    if parent_headings:
        summary = ' > '.join(parent_headings) + ' > '

    summary += section['heading']

    # 如果是分段的部分，添加Part信息
    if part_index is not None and total_parts > 1:
        summary += f" - Part {part_index}/{total_parts}"

    return summary
