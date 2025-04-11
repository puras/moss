"""
Markdown目录提取模块
"""
import re
from typing import List, Dict, Any, Optional, Union


def extract_table_of_contents(text: str, options: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    提取Markdown文档的目录结构
    Args:
        text: Markdown文本
        options: 配置选项
            maxLevel: 提取的最大标题级别，默认为6
            includeLinks: 是否包含锚点链接，默认为True
            flatList: 是否返回扁平列表，默认为False（返回嵌套结构）
    Returns:
        目录结构数组
    """
    options = options or {}
    max_level = options.get('maxLevel', 6)
    include_links = options.get('includeLinks', True)
    flat_list = options.get('flatList', False)

    # 匹配标题的正则表达式
    heading_regex = re.compile(r'^(#{1,6})\s+(.+?)(?:\s*\{#[\w-]+\})?\s*$', re.MULTILINE)
    toc_items = []

    for match in heading_regex.finditer(text):
        level = len(match.group(1))

        # 如果标题级别超过了设定的最大级别，则跳过
        if level > max_level:
            continue

        title = match.group(2).strip()
        position = match.start()

        # 生成锚点ID（用于链接）
        anchor_id = generate_anchor_id(title)

        toc_items.append({
            'level': level,
            'title': title,
            'position': position,
            'anchorId': anchor_id,
            'children': []
        })

    # 如果需要返回扁平列表，直接返回处理后的结果
    if flat_list:
        return [{
            'level': item['level'],
            'title': item['title'],
            'position': item['position'],
            'link': f"#{item['anchorId']}" if include_links else None
        } for item in toc_items]

    # 构建嵌套结构
    return build_nested_toc(toc_items, include_links)

def generate_anchor_id(title: str) -> str:
    """
    生成标题的锚点ID
    Args:
        title: 标题文本
    Returns:
        生成的锚点ID
    """
    return re.sub(
        r'^\-+|\-+$',
        '',
        re.sub(
            r'\-+',
            '-',
            re.sub(
                r'[^\w\-]',
                '',
                re.sub(
                    r'\s+',
                    '-',
                    title.lower()
                )
            )
        )
    )

def build_nested_toc(items: List[Dict[str, Any]], include_links: bool) -> List[Dict[str, Any]]:
    """
    构建嵌套的目录结构
    Args:
        items: 扁平的目录项数组
        include_links: 是否包含链接
    Returns:
        嵌套的目录结构
    """
    result = []
    stack = [{'level': 0, 'children': result}]

    for item in items:
        toc_item = {
            'title': item['title'],
            'level': item['level'],
            'position': item['position'],
            'children': []
        }

        if include_links:
            toc_item['link'] = f"#{item['anchorId']}"

        # 找到当前项的父级
        while stack[-1]['level'] >= item['level']:
            stack.pop()

        # 将当前项添加到父级的children中
        stack[-1]['children'].append(toc_item)

        # 将当前项入栈
        stack.append(toc_item)

    return result

def toc_to_markdown(toc: List[Dict[str, Any]], options: Dict[str, Any] = None) -> str:
    """
    将目录结构转换为Markdown格式
    Args:
        toc: 目录结构（嵌套或扁平）
        options: 配置选项
            isNested: 是否为嵌套结构，默认为True
            includeLinks: 是否包含链接，默认为True
    Returns:
        Markdown格式的目录
    """
    options = options or {}
    is_nested = options.get('isNested', True)
    include_links = options.get('includeLinks', True)

    if is_nested:
        return nested_toc_to_markdown(toc, 0, include_links)
    else:
        return flat_toc_to_markdown(toc, include_links)

def nested_toc_to_markdown(items: List[Dict[str, Any]], indent: int = 0, include_links: bool = True) -> str:
    """
    将嵌套的目录结构转换为Markdown格式
    """
    result = ''
    indent_str = '  ' * indent

    # 添加数据验证
    if not isinstance(items, list):
        print('Warning: items is not a list in nested_toc_to_markdown')
        return result

    for item in items:
        title_text = f"[{item['title']}]({item['link']})" if include_links and 'link' in item else item['title']
        result += f"{indent_str}- {title_text}\n"

        if item.get('children') and len(item['children']) > 0:
            result += nested_toc_to_markdown(item['children'], indent + 1, include_links)

    return result

def flat_toc_to_markdown(items: List[Dict[str, Any]], include_links: bool = True) -> str:
    """
    将扁平的目录结构转换为Markdown格式
    """
    result = ''

    for item in items:
        indent = '  ' * (item['level'] - 1)
        title_text = f"[{item['title']}]({item['link']})" if include_links and 'link' in item else item['title']
        result += f"{indent}- {title_text}\n"

    return result
