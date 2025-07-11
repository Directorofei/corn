import torch
import os
from utils.model_definitions import RTX3060OptimizedModel # 假设使用相同的模型结构

# --- 模型常量 ---
MODEL_PATH = "pests/models/best_model.pth" # 占位符路径
CLASS_NAMES = ['蓟马', '粘虫', '玉米螟', '健康'] # 假设的分类，顺序需要和模型训练时一致
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- 单例模式加载模型 ---
MODEL_INSTANCE = None

def load_pest_model():
    """
    加载害虫识别模型到全局单例。
    如果模型文件不存在或加载失败，会打印错误信息。
    """
    global MODEL_INSTANCE
    if MODEL_INSTANCE is not None:
        return MODEL_INSTANCE

    if not os.path.exists(MODEL_PATH):
        print(f"错误: 害虫模型文件未找到于 '{MODEL_PATH}'")
        MODEL_INSTANCE = "not_found"
        return MODEL_INSTANCE

    try:
        print("正在加载害虫诊断模型...")
        # 假设类别数为 CLASS_NAMES 的长度
        model = RTX3060OptimizedModel(num_classes=len(CLASS_NAMES), pretrained=False)
        
        # 加载整个checkpoint
        checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)
        
        # 兼容不同保存方式
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
        else:
            model.load_state_dict(checkpoint)
            
        model.to(DEVICE)
        model.eval()
        MODEL_INSTANCE = model
        print(f"害虫模型已成功加载到 {DEVICE}")
    except Exception as e:
        print(f"加载害虫模型时出错: {e}")
        MODEL_INSTANCE = "error"
    
    return MODEL_INSTANCE 