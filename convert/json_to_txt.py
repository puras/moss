import json
import os
from datetime import datetime

def process_json_files(input_dir='news', output_file='output/news.txt'):
    """
    将News目录下的所有JSON文件合并成一个TXT文件
    """
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 获取所有JSON文件
    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for json_file in sorted(json_files):
            file_path = os.path.join(input_dir, json_file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 写入JSON内容
                    if isinstance(data, list):
                        # 如果是数组，遍历处理每个项目
                        for item in data:
                            if isinstance(item, dict):
                                for key, value in item.items():
                                    out_file.write(f"{key}: {value}\n")
                            else:
                                out_file.write(f"{item}\n")
                            out_file.write("\n")
                    elif isinstance(data, dict):
                        # 如果是字典，直接处理键值对
                        for key, value in data.items():
                            out_file.write(f"{key}: {value}\n")
                    
                    out_file.write("\n")
                    
            except Exception as e:
                print(f"处理文件 {json_file} 时出错: {str(e)}")
                
    print(f"处理完成，输出文件：{output_file}")

if __name__ == "__main__":
    # 生成带时间戳的输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'output/news.txt'
    
    process_json_files(output_file=output_file)