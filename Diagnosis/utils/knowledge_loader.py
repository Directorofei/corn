from pathlib import Path
import re
from typing import Dict, List, Optional

# 全局变量，用于缓存加载的知识库
_KNOWLEDGE_BASE: Dict[str, Dict] = {}

def _parse_markdown_file(file_path: Path) -> Dict:
    """解析单个markdown文件，提取结构化数据。"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    data = {}
    # 文件名作为主标题（病害名）
    disease_name = file_path.stem
    data['name'] = disease_name
    data['description'] = ''
    data['sub_types'] = {}

    current_section = None
    current_sub_type = None
    content_accumulator = []

    # 状态机：'description', 'sub_type_content'
    state = 'description' 

    for line in lines:
        line = line.strip()
        if not line or line == '---':
            continue

        # 一级标题被忽略，因为我们用文件名
        if line.startswith('# '):
            continue

        # 二级标题 ## 表示一个亚种或一个主要部分
        if line.startswith('## '):
            # 先保存上一部分的内容
            if current_section and current_sub_type and content_accumulator:
                data['sub_types'][current_sub_type][current_section] = '\n'.join(content_accumulator).strip()
            content_accumulator = []

            section_title = line[3:].strip()
            
            # 更精确的判断逻辑：识别亚种标题
            # 亚种标题通常包含序号（一、二、三、1.、2.、3.等）或者以病害名结尾
            if (('一、' in section_title or '二、' in section_title or '三、' in section_title or
                 '1.' in section_title or '2.' in section_title or '3.' in section_title) or
                (section_title.endswith('病') or section_title.endswith('虫') or section_title.endswith('害')) and
                not section_title in ['核心症状', '发生规律', '诊断要点', '防治建议', '田间诊断要点']):
                
                # 这是一个新的亚种
                current_sub_type = section_title
                if current_sub_type not in data['sub_types']:
                    data['sub_types'][current_sub_type] = {}
                current_section = None # 新亚种开始，重置当前区域
                state = 'sub_type_content'
            else: 
                # 这是一个内容区域，如"核心症状"、"发生规律"等
                if current_sub_type is None:
                    # 如果没有当前亚种，创建以文件名为名的默认亚种
                    current_sub_type = disease_name
                    if current_sub_type not in data['sub_types']:
                        data['sub_types'][current_sub_type] = {}
                current_section = section_title
                state = 'sub_type_content'

        # 三级标题 ### 现在作为内容区域标题处理
        elif line.startswith('### '):
            # 先保存上一部分的内容
            if current_section and current_sub_type and content_accumulator:
                data['sub_types'][current_sub_type][current_section] = '\n'.join(content_accumulator).strip()
            content_accumulator = []

            section_title = line[4:].strip()
            # 如果没有当前亚种，创建以文件名为名的默认亚种
            if current_sub_type is None:
                current_sub_type = disease_name
                if current_sub_type not in data['sub_types']:
                    data['sub_types'][current_sub_type] = {}
            current_section = section_title
            state = 'sub_type_content'
        else:
            if state == 'description':
                 data['description'] += line + '\n'
            elif state == 'sub_type_content':
                content_accumulator.append(line)

    # 保存循环结束后最后一部分的内容
    if current_section and current_sub_type and content_accumulator:
        data['sub_types'][current_sub_type][current_section] = '\n'.join(content_accumulator).strip()

    # 如果解析后没有亚种，但文件内容存在（针对无任何##标题的纯文本文件），说明是单体病害文件
    if not data['sub_types'] and data['description']:
         data['sub_types'][disease_name] = {'核心症状': data['description'].strip()}
         data['description'] = '' # 清空外层描述

    return {disease_name: data}

def load_knowledge_base(path: str = "knowledge_base"):
    """加载指定路径下的所有.md文件到知识库。"""
    global _KNOWLEDGE_BASE
    if _KNOWLEDGE_BASE:
        return
    
    kb_path = Path(path)
    if not kb_path.exists():
        print(f"知识库路径 {path} 不存在。")
        return

    full_kb = {}
    for md_file in kb_path.glob("*.md"):
        parsed_data = _parse_markdown_file(md_file)
        full_kb.update(parsed_data)
    _KNOWLEDGE_BASE = full_kb
    print(f"知识库加载完成，共加载了 {len(_KNOWLEDGE_BASE)} 个条目。")


def get_knowledge_entry(disease_name: str, sub_type_name: Optional[str] = None) -> Optional[Dict[str, str]]:
    """
    健壮地获取知识条目。
    - 如果只提供 disease_name，返回主条目。
    - 如果提供 sub_type_name，返回对应的亚种条目。
    """
    main_entry = _KNOWLEDGE_BASE.get(disease_name)
    if not main_entry:
        return None
    
    if sub_type_name:
        return main_entry.get("sub_types", {}).get(sub_type_name)
    
    # 如果没有指定亚种，则返回包含所有信息的完整主条目
    return main_entry


def get_sub_types(disease_name: str) -> List[str]:
    """获取指定病害下的所有亚种名称列表。"""
    main_entry = get_knowledge_entry(disease_name)
    if main_entry and "sub_types" in main_entry:
        return list(main_entry["sub_types"].keys())
    return []

def get_disease_description(disease_name: str) -> str:
    """获取病害的顶层描述。"""
    main_entry = get_knowledge_entry(disease_name)
    if main_entry and "description" in main_entry:
        return main_entry["description"]
    return "" 

# 添加调试函数
def debug_knowledge_base():
    """调试函数，打印知识库的结构"""
    print("=== 知识库结构调试 ===")
    for disease_name, disease_data in _KNOWLEDGE_BASE.items():
        print(f"\n病害: {disease_name}")
        print(f"  描述: {disease_data.get('description', '无')[:50]}...")
        print(f"  亚种数量: {len(disease_data.get('sub_types', {}))}")
        for sub_type, sub_data in disease_data.get('sub_types', {}).items():
            print(f"    亚种: {sub_type}")
            for section, content in sub_data.items():
                print(f"      {section}: {content[:30]}...") 