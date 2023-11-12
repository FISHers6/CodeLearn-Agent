import os
import re
from typing import List

def process_file_paths(file_paths: str) -> List[str]:
    # 用于存储处理后的路径
    processed_paths = []
    
    # 使用正则表达式来分割字符串，处理多种可能的分隔符
    paths = re.split(r'[ ,;]+', file_paths)
    
    for path in paths:
        # 删除路径两侧可能存在的多余空格
        path = path.strip()
        
        if not path:
            continue  # 跳过空字符串
        
        # 将路径分割为组件
        path_components = re.split(r'[\\/]', path)
        
        # 使用 os.path.join 和 os.sep 来连接路径组件
        normalized_path = os.path.join(*path_components)
        
        # 将处理后的路径添加到结果列表中
        processed_paths.append(normalized_path)
    
    # 移除重复的路径
    processed_paths = list(set(processed_paths))
    
    return processed_paths