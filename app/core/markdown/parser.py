import re

def extract_outline(text):
    """

    :param text:
    :return:
    """
    outline_regex = re.compile(r'^(#{1,6})\s+(.+?)(?:\s*\{#[\w-]+\})?\s*$', re.MULTILINE)
    outline = []
    for match in outline_regex.finditer(text):
        level = len(match.group(1))
        title = match.group(2).strip()
        outline.append({
            'level': level,
            'title': title,
            'position': match.start()
        })
    return outline


def split_by_headings(text, outline):
    if len(outline) == 0:
        return [{
            'heading': None,
            'level': 0,
            'content': text.strip(),
            'position': 0
        }]

    sections = []

    # 处理第一个标题前的内容
    if outline[0]['position'] > 0:
        front_matter = text[0:outline[0]['position']].strip()
        if len(front_matter) > 0:
            sections.append({
                'heading': None,
                'level': 0,
                'content': front_matter,
                'position': 0
            })

    # 遍历每个标题进行分割
    for i in range(len(outline)):
        current = outline[i]
        next_item = outline[i + 1] if i < len(outline) - 1 else None

        # 获取标题行并计算内容起始位置
        heading_line = text[current['position']:].split('\n')[0]
        start_pos = current['position'] + len(heading_line) + 1
        end_pos = next_item['position'] if next_item else len(text)

        # 提取内容并存入列表
        content = text[start_pos:end_pos].strip()
        sections.append({
            'heading': current['title'],
            'level': current['level'],
            'content': content,
            'position': current['position']
        })

    return sections