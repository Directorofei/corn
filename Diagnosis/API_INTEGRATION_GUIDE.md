# 🔌 玉米病虫害诊断智能体 - 后端API对接指南

## 📋 概述

本文档为后台管理系统和第三方开发者提供详细的API对接说明。我们的系统基于Gradio框架构建，提供了五个独立的专家系统模块，每个模块都可以独立调用和集成。

## 🏗️ 系统架构

### 核心组件
```
玉米病虫害诊断系统
├── 叶片病害专家 (AI图像识别)
├── 害虫识别专家 (AI图像识别)  
├── 茎穗病害专家 (症状文本分析)
├── 根部病害专家 (症状文本分析)
└── 苗期病害专家 (症状文本分析)
```

### 技术栈
- **后端**: Python + Gradio
- **AI框架**: PyTorch + ConvNext
- **数据格式**: JSON + Base64图像
- **部署**: 本地服务器/云服务器

## 🚀 快速集成

### 1. 环境准备

**服务器要求**:
- Python 3.8+
- PyTorch 1.9+
- GPU内存 4GB+ (推荐)
- RAM 8GB+

**启动服务**:
```bash
# 克隆项目
git clone [repository-url]
cd corn-disease-diagnosis

# 安装依赖
pip install -r requirements.txt

# 启动API服务
python app.py --server_name=0.0.0.0 --server_port=7860
```

### 2. 服务验证

服务启动后，访问 `http://your-server:7860` 确认服务正常运行。

## 📡 API接口规范

### 接口调用方式

我们的系统基于Gradio构建，支持以下调用方式：

#### 方式一：HTTP API调用 (推荐)
```python
import requests
import base64
import json

# 基础URL
BASE_URL = "http://your-server:7860"

# 获取API信息
response = requests.get(f"{BASE_URL}/api")
print(response.json())
```

#### 方式二：Python SDK调用
```python
from gradio_client import Client

client = Client("http://your-server:7860")
```

#### 方式三：直接函数调用 (服务器内部)
```python
# 导入专家系统模块
from leaf.leaf_expert import predict_leaf_diseases
from pests.pest_expert import predict_pest
# ... 其他专家系统
```

## 🍃 叶片病害专家系统

### 功能描述
使用ConvNext深度学习模型识别玉米叶片病害，支持多标签分类。

### API调用

#### HTTP请求
```bash
curl -X POST "http://your-server:7860/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ...",
      []
    ],
    "fn_index": 0
  }'
```

#### Python调用
```python
from gradio_client import Client
import base64

client = Client("http://your-server:7860")

# 方法1：直接传图片文件路径
result = client.predict(
    image_path="/path/to/leaf_image.jpg",
    history=[],
    api_name="/predict_leaf_diseases"
)

# 方法2：Base64编码图片
with open("leaf_image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()
    
result = client.predict(
    image_path=f"data:image/jpeg;base64,{image_data}",
    history=[],
    api_name="/predict_leaf_diseases"
)
```

#### 直接函数调用
```python
from leaf.leaf_expert import predict_leaf_diseases

# 调用预测函数
history = []
updated_history, image_update, button_update = predict_leaf_diseases(
    image_path="/path/to/image.jpg",
    history=history
)

# 从history中提取诊断结果
diagnosis_result = updated_history[-1]["content"]
print(diagnosis_result)
```

### 输入参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| image_path | string | 是 | 图片文件路径或Base64编码 |
| history | list | 否 | 对话历史，默认为空列表 |

### 返回数据
```json
{
  "history": [
    {
      "role": "user",
      "content": {"path": "image.jpg", "mime_type": "image/jpeg"}
    },
    {
      "role": "assistant", 
      "content": "### 诊断报告：斑病 (置信度: 85.2%)\n\n**核心症状**:\n病斑为两端尖削的长椭圆形..."
    }
  ],
  "image_update": null,
  "button_update": null
}
```

### 识别能力
- **支持病害**: 健康、锈病、大斑病、灰斑病
- **准确率**: 98.24%
- **支持格式**: JPG, PNG, JPEG
- **图片要求**: 分辨率 224x224+ 

## 🐛 害虫识别专家系统

### 功能描述
识别玉米常见害虫，提供害虫信息和防治建议。

### API调用

#### Python调用
```python
from gradio_client import Client

client = Client("http://your-server:7860")

result = client.predict(
    image_path="/path/to/pest_image.jpg",
    history=[],
    api_name="/predict_pest"
)
```

#### 直接函数调用
```python
from pests.pest_expert import predict_pest

history = []
updated_history, image_update, button_update = predict_pest(
    image_path="/path/to/pest_image.jpg", 
    history=history
)

diagnosis_result = updated_history[-1]["content"]
```

### 输入参数
同叶片专家系统

### 返回数据格式
```json
{
  "history": [
    {
      "role": "assistant",
      "content": "### 诊断报告：玉米粘虫\n\n*模型置信度: 92.5%*\n\n**核心症状与危害**:\n幼虫咀嚼叶片..."
    }
  ]
}
```

### 识别能力
- **支持害虫**: 玉米粘虫、玉米螟、玉米蓟马
- **准确率**: 98.37%
- **建议图片**: 害虫特征清晰可见的近景照片

## 🌾 茎穗病害专家系统

### 功能描述
基于症状描述分析茎穗部病害，主要诊断黑粉病类病害。

### API调用

#### Python调用
```python
from gradio_client import Client

client = Client("http://your-server:7860")

result = client.predict(
    symptoms_input="果穗变成黑色粉末状，短粗畸形",
    history=[],
    api_name="/analyze_symptoms"
)
```

#### 直接函数调用
```python
from stem.stem_expert import analyze_symptoms

history = []
updated_history, input_clear, image_update = analyze_symptoms(
    symptoms_input="果穗变成黑色粉末状，短粗畸形",
    history=history
)

diagnosis_result = updated_history[-1]["content"]
```

### 输入参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symptoms_input | string | 是 | 症状描述文本 |
| history | list | 否 | 对话历史 |

### 返回数据格式
```json
{
  "history": [
    {
      "role": "assistant",
      "content": "## 🔍 症状分析报告\n\n根据您描述的症状\"果穗变成黑色粉末状\"，我分析出以下可能的病害：\n\n### 1. 玉米丝黑穗病\n**匹配度**: 3个关键词..."
    }
  ],
  "input_clear": "",
  "image_update": null
}
```

### 关键词识别
系统支持广泛的症状描述词汇：
- **颜色词**: 黑、灰、褐、棕、暗、发黄、变色等
- **形状词**: 畸形、变形、肿胀、包状、异常等  
- **质地词**: 粉末、粉状、腐烂、软化等
- **通用词**: 病变、感染、枯萎、死亡等

## 🌱 根部病害专家系统

### 功能描述
诊断根腐病，区分青枯型和黄枯型。

### API调用

#### Python调用
```python
result = client.predict(
    symptoms_input="植株叶片迅速变青灰色，根系变褐腐烂",
    history=[],
    api_name="/analyze_root_symptoms"
)
```

#### 直接函数调用
```python
from root.root_expert import analyze_root_symptoms

updated_history, input_clear, image_update = analyze_root_symptoms(
    symptoms_input="植株叶片迅速变青灰色，根系变褐腐烂",
    history=[]
)
```

### 关键特征识别
- **青枯型**: 急性、迅速、青灰色、失水快速等
- **黄枯型**: 慢性、逐渐、发黄、缓慢等
- **根系症状**: 根烂、变褐、腐败、松动等
- **环境因子**: 高温、多雨、连作、排水不良等

## 🌿 苗期病害专家系统

### 功能描述
诊断苗期病害，包括烂种、芽腐、苗枯。

### API调用

#### Python调用
```python
result = client.predict(
    symptoms_input="种子播种后不出苗，挖出来发现种子腐烂", 
    history=[],
    api_name="/analyze_seedling_symptoms"
)
```

### 诊断范围
- **烂种**: 种子萌发前腐烂
- **芽腐**: 萌发后出土前死亡
- **苗枯**: 出土后幼苗枯死

## 🔧 高级集成方案

### 1. 批量处理接口

如需批量处理大量图片或文本，建议：

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def batch_process_images(image_paths):
    """批量处理图片"""
    with ThreadPoolExecutor(max_workers=4) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor, 
                predict_leaf_diseases, 
                img_path, 
                []
            ) 
            for img_path in image_paths
        ]
        results = await asyncio.gather(*tasks)
    return results
```

### 2. 微服务化部署

每个专家系统可以独立部署为微服务：

```bash
# 仅启动叶片专家
python -c "
from leaf.leaf_expert import create_leaf_expert_interface
import gradio as gr
interface = create_leaf_expert_interface()
interface.launch(server_name='0.0.0.0', server_port=7861)
"

# 仅启动害虫专家 
python -c "
from pests.pest_expert import create_pest_expert_interface
import gradio as gr
interface = create_pest_expert_interface()
interface.launch(server_name='0.0.0.0', server_port=7862)
"
```

### 3. 负载均衡配置

使用Nginx进行负载均衡：

```nginx
upstream corn_diagnosis {
    server 127.0.0.1:7860 weight=1;
    server 127.0.0.1:7861 weight=1; 
    server 127.0.0.1:7862 weight=1;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://corn_diagnosis;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 性能优化建议

### 1. 图片预处理
在发送图片前进行预处理可提升性能：

```python
from PIL import Image
import io
import base64

def optimize_image(image_path, max_size=800):
    """优化图片大小"""
    with Image.open(image_path) as img:
        # 调整尺寸
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # 转换为RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # 压缩质量
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=True)
        
        # 转换为Base64
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/jpeg;base64,{img_str}"
```

### 2. 缓存机制
对于重复的图片或症状描述，建议实现缓存：

```python
import hashlib
import pickle
from functools import lru_cache

class DiagnosisCache:
    def __init__(self, cache_size=1000):
        self.cache = {}
        self.max_size = cache_size
    
    def get_cache_key(self, data):
        """生成缓存键"""
        if isinstance(data, str):
            return hashlib.md5(data.encode()).hexdigest()
        else:
            return hashlib.md5(pickle.dumps(data)).hexdigest()
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value):
        if len(self.cache) >= self.max_size:
            # 简单的LRU策略
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[key] = value

# 使用示例
cache = DiagnosisCache()

def cached_predict(image_path, history):
    cache_key = cache.get_cache_key(image_path)
    result = cache.get(cache_key)
    
    if result is None:
        result = predict_leaf_diseases(image_path, history)
        cache.set(cache_key, result)
    
    return result
```

## 🔒 安全考虑

### 1. 图片安全
- 限制上传图片大小 (建议 < 10MB)
- 验证图片格式和内容
- 防止路径遍历攻击

```python
import os
from PIL import Image

def validate_image(image_path):
    """验证图片安全性"""
    # 检查文件大小
    if os.path.getsize(image_path) > 10 * 1024 * 1024:  # 10MB
        raise ValueError("图片过大")
    
    # 验证图片格式
    try:
        with Image.open(image_path) as img:
            img.verify()
    except Exception:
        raise ValueError("无效图片格式")
    
    # 检查路径安全
    if '..' in image_path or image_path.startswith('/'):
        raise ValueError("非法路径")
```

### 2. 输入验证
```python
def validate_symptoms_input(text):
    """验证症状输入"""
    if not text or len(text.strip()) == 0:
        raise ValueError("症状描述不能为空")
    
    if len(text) > 1000:
        raise ValueError("症状描述过长")
    
    # 过滤恶意内容
    dangerous_patterns = ['<script', 'javascript:', 'onclick=']
    text_lower = text.lower()
    
    for pattern in dangerous_patterns:
        if pattern in text_lower:
            raise ValueError("包含非法内容")
    
    return text.strip()
```

## 🐛 错误处理

### 常见错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查输入参数格式 |
| 404 | 模型文件未找到 | 确认模型文件已正确放置 |
| 500 | 内部服务器错误 | 查看服务器日志 |
| 503 | 服务不可用 | 检查服务状态和资源使用 |

### 错误处理示例
```python
try:
    result = predict_leaf_diseases(image_path, history)
except FileNotFoundError:
    return {"error": "图片文件未找到", "code": 404}
except ValueError as e:
    return {"error": str(e), "code": 400}
except Exception as e:
    logger.error(f"诊断失败: {e}")
    return {"error": "内部服务器错误", "code": 500}
```

## 📋 测试用例

### 单元测试示例
```python
import unittest
from leaf.leaf_expert import predict_leaf_diseases

class TestLeafExpert(unittest.TestCase):
    
    def test_healthy_leaf_prediction(self):
        """测试健康叶片识别"""
        result = predict_leaf_diseases("test_images/healthy_leaf.jpg", [])
        self.assertIn("健康", result[0][-1]["content"])
    
    def test_blight_prediction(self):
        """测试斑病识别"""
        result = predict_leaf_diseases("test_images/blight_leaf.jpg", [])
        self.assertIn("斑病", result[0][-1]["content"])
    
    def test_invalid_image(self):
        """测试无效图片处理"""
        result = predict_leaf_diseases("invalid_path.jpg", [])
        self.assertIn("请上传", result[0][-1]["content"])

if __name__ == '__main__':
    unittest.main()
```

### API测试脚本
```python
import requests
import base64
import json

def test_api_endpoint():
    """测试API端点"""
    base_url = "http://localhost:7860"
    
    # 测试健康检查
    response = requests.get(f"{base_url}/api")
    assert response.status_code == 200
    
    # 测试图片诊断
    with open("test_leaf.jpg", "rb") as f:
        img_data = base64.b64encode(f.read()).decode()
    
    payload = {
        "data": [f"data:image/jpeg;base64,{img_data}", []],
        "fn_index": 0
    }
    
    response = requests.post(f"{base_url}/api/predict", json=payload)
    assert response.status_code == 200
    
    result = response.json()
    assert "data" in result
    print("API测试通过！")

if __name__ == "__main__":
    test_api_endpoint()
```



### 社区支持
- **GitHub讨论区**: 分享使用经验和最佳实践
- **技术博客**: 详细的技术文章和案例分析
- **在线文档**: 实时更新的API文档

---

<div align="center">
  <strong>🤖 让AI赋能农业智能化 🌽</strong>
</div> 