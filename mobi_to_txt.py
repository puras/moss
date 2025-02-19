import mobi 
import html2text
import os

# 输入和输出文件路径
input_file = 'books/外国教育思想通史（全十卷）.mobi'
output_file = 'output/外国教育思想通史（全十卷）.txt'

# 确保输出目录存在
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# 转换过程
temp_dir, filepath = mobi.extract(input_file)
with open(filepath, 'r') as file:
    content = file.read()
    
# 转换HTML为纯文本
text_content = html2text.html2text(content)

# 保存到文件
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(text_content)

print(f"转换完成，文件已保存到：{output_file}")