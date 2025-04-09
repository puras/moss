"""
Markdown文档分割模块
"""
import re
from app.lib.split.markdown import summary


def split_long_section(section, max_split_length):
    """
    分割超长段落
    Args:
        section (dict): 段落对象
        max_split_length (int): 最大分割字数
    Returns:
        list: 分割后的段落数组
    """
    content = section['content']
    paragraphs = re.split(r'\n\n+', content)
    result = []
    current_chunk = ''

    for paragraph in paragraphs:
        # 如果当前段落本身超过最大长度，可能需要进一步拆分
        if len(paragraph) > max_split_length:
            # 如果当前块不为空，先加入结果
            if len(current_chunk) > 0:
                result.append(current_chunk)
                current_chunk = ''

            # 对超长段落进行分割（例如，按句子或固定长度）
            sentence_split = re.findall(r'[^.!?]+[.!?]+', paragraph) or [paragraph]

            # 处理分割后的句子
            sentence_chunk = ''
            for sentence in sentence_split:
                if len(sentence_chunk + sentence) <= max_split_length:
                    sentence_chunk += sentence
                else:
                    if len(sentence_chunk) > 0:
                        result.append(sentence_chunk)
                    # 如果单个句子超过最大长度，可能需要进一步拆分
                    if len(sentence) > max_split_length:
                        # 简单地按固定长度分割
                        for i in range(0, len(sentence), max_split_length):
                            result.append(sentence[i:i + max_split_length])
                    else:
                        sentence_chunk = sentence

            if len(sentence_chunk) > 0:
                current_chunk = sentence_chunk
        elif len(current_chunk + '\n\n' + paragraph) <= max_split_length:
            # 如果添加当前段落不超过最大长度，则添加到当前块
            current_chunk = current_chunk + '\n\n' + paragraph if len(current_chunk) > 0 else paragraph
        else:
            # 如果添加当前段落超过最大长度，则将当前块加入结果，并重新开始一个新块
            result.append(current_chunk)
            current_chunk = paragraph

    # 添加最后一个块（如果有）
    if len(current_chunk) > 0:
        result.append(current_chunk)

    return result

def process_sections(sections, outline, min_split_length, max_split_length):
    """
    处理段落，根据最小和最大分割字数进行分割
    Args:
        sections (list): 段落数组
        outline (list): 目录大纲
        min_split_length (int): 最小分割字数
        max_split_length (int): 最大分割字数
    Returns:
        list: 处理后的段落数组
    """
    # 预处理：将相邻的小段落合并
    preprocessed_sections = []
    current_section = None

    for section in sections:
        content_length = len(section['content'].strip())

        if content_length < min_split_length and current_section:
            # 如果当前段落小于最小长度且有累积段落，尝试合并
            heading_str = '#' * section['level'] + ' ' + section['heading'] + '\n' if section.get('heading') else ''
            merged_content = f"{current_section['content']}\n\n{heading_str}{section['content']}"

            if len(merged_content) <= max_split_length:
                # 如果合并后不超过最大长度，则合并
                current_section['content'] = merged_content
                if section.get('heading'):
                    if 'headings' not in current_section:
                        current_section['headings'] = []
                    current_section['headings'].append({
                        'heading': section['heading'],
                        'level': section['level'],
                        'position': section['position']
                    })
                continue

        # 如果无法合并，则开始新的段落
        if current_section:
            preprocessed_sections.append(current_section)

        current_section = section.copy()
        current_section['headings'] = ([{
            'heading': section['heading'],
            'level': section['level'],
            'position': section['position']
        }] if section.get('heading') else [])

    # 添加最后一个段落
    if current_section:
        preprocessed_sections.append(current_section)

    result = []
    accumulated_section = None  # 用于累积小于最小分割字数的段落

    for section in preprocessed_sections:
        content_length = len(section['content'].strip())

        # 检查是否需要累积段落
        if content_length < min_split_length:
            # 如果还没有累积过段落，创建新的累积段落
            if not accumulated_section:
                accumulated_section = {
                    'heading': section.get('heading'),
                    'level': section.get('level'),
                    'content': section['content'],
                    'position': section.get('position'),
                    'headings': [{
                        'heading': section['heading'],
                        'level': section['level'],
                        'position': section['position']
                    }] if section.get('heading') else []
                }
            else:
                # 已经有累积段落，将当前段落添加到累积段落中
                heading_str = '#' * section['level'] + ' ' + section['heading'] + '\n' if section.get('heading') else ''
                accumulated_section['content'] += f"\n\n{heading_str}{section['content']}"
                if section.get('heading'):
                    accumulated_section['headings'].append({
                        'heading': section['heading'],
                        'level': section['level'],
                        'position': section['position']
                    })

            # 只有当累积内容达到最小长度时才处理
            accumulated_length = len(accumulated_section['content'].strip())
            if accumulated_length >= min_split_length:
                summary_text = summary.generate_enhanced_summary(accumulated_section, outline)

                if accumulated_length > max_split_length:
                    # 如果累积段落超过最大长度，进一步分割
                    sub_sections = split_long_section(accumulated_section, max_split_length)

                    for j, sub_section in enumerate(sub_sections):
                        result.append({
                            'summary': f"{summary_text} - Part {j + 1}/{len(sub_sections)}",
                            'content': sub_section
                        })
                else:
                    # 添加到结果中
                    result.append({
                        'summary': summary_text,
                        'content': accumulated_section['content']
                    })

                accumulated_section = None  # 重置累积段落

            continue

        # 如果有累积的段落，先处理它
        if accumulated_section:
            summary_text = summary.generate_enhanced_summary(accumulated_section, outline)
            accumulated_length = len(accumulated_section['content'].strip())

            if accumulated_length > max_split_length:
                # 如果累积段落超过最大长度，进一步分割
                sub_sections = split_long_section(accumulated_section, max_split_length)

                for j, sub_section in enumerate(sub_sections):
                    result.append({
                        'summary': f"{summary_text} - Part {j + 1}/{len(sub_sections)}",
                        'content': sub_section
                    })
            else:
                # 添加到结果中
                result.append({
                    'summary': summary_text,
                    'content': accumulated_section['content']
                })

            accumulated_section = None  # 重置累积段落

        # 处理当前段落
        # 如果段落长度超过最大分割字数，需要进一步分割
        if content_length > max_split_length:
            sub_sections = split_long_section(section, max_split_length)

            # 为当前段落创建一个标准的headings数组
            if not section.get('headings') and section.get('heading'):
                section['headings'] = [{
                    'heading': section['heading'],
                    'level': section['level'],
                    'position': section['position']
                }]

            for i, sub_section in enumerate(sub_sections):
                summary_text = summary.generate_enhanced_summary(section, outline, i + 1, len(sub_sections))
                result.append({
                    'summary': summary_text,
                    'content': sub_section
                })
        else:
            # 为当前段落创建一个标准的headings数组
            if not section.get('headings') and section.get('heading'):
                section['headings'] = [{
                    'heading': section['heading'],
                    'level': section['level'],
                    'position': section['position']
                }]

            # 生成增强的摘要并添加到结果
            summary_text = summary.generate_enhanced_summary(section, outline)
            heading_str = '#' * section['level'] + ' ' + section['heading'] + '\n' if section.get('heading') else ''
            content = f"{heading_str}{section['content']}"

            result.append({
                'summary': summary_text,
                'content': content
            })

    # 处理最后剩余的小段落
    if accumulated_section:
        if result:
            # 尝试将剩余的小段落与最后一个结果合并
            last_result = result[-1]
            merged_content = f"{last_result['content']}\n\n{accumulated_section['content']}"

            if len(merged_content) <= max_split_length:
                # 如果合并后不超过最大长度，则合并
                summary_text = summary.generate_enhanced_summary({
                    **accumulated_section,
                    'content': merged_content
                }, outline)

                result[-1] = {
                    'summary': summary_text,
                    'content': merged_content
                }
            else:
                # 如果合并后超过最大长度，将accumulated_section作为单独的段落添加
                summary_text = summary.generate_enhanced_summary(accumulated_section, outline)
                heading_str = '#' * accumulated_section['level'] + ' ' + accumulated_section['heading'] + '\n' if accumulated_section.get('heading') else ''
                content = f"{heading_str}{accumulated_section['content']}"
                result.append({
                    'summary': summary_text,
                    'content': content
                })
        else:
            # 如果result为空，直接添加accumulated_section
            summary_text = summary.generate_enhanced_summary(accumulated_section, outline)
            heading_str = '#' * accumulated_section['level'] + ' ' + accumulated_section['heading'] + '\n' if accumulated_section.get('heading') else ''
            content = f"{heading_str}{accumulated_section['content']}"
            result.append({
                'summary': summary_text,
                'content': content
            })

    return result