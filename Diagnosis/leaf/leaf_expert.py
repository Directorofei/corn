import gradio as gr
import torch
import sys
import os

# 智能路径修复：当直接运行此脚本时，将项目根目录添加到Python路径中
# 这确保了无论是作为模块导入还是直接运行，都能找到 'utils' 包。
if __name__ == "__main__" and __package__ is None:
    # __file__ 获取当前脚本的路径
    # os.path.dirname() 获取该路径的目录
    # '..' 代表上一级目录，即项目根目录
    # os.path.abspath() 获取绝对路径
    # sys.path.insert(0, ...) 将其添加到搜索路径的最前面
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.image_utils import preprocess_image
from utils.model_definitions import RTX3060OptimizedModel
from utils.knowledge_loader import get_knowledge_entry, get_sub_types, load_knowledge_base

# --- 模型和常量定义 ---
MODEL_PATH = 'leaf/models/best_model_rtx3060_stable.pth'
NUM_CLASSES = 4 
# 修正：根据用户的测试反馈，对调“健康”和“灰斑病”的位置，以匹配模型的实际输出。
CLASS_NAMES = ['健康', '锈病', '大斑病', '灰斑病']
DISEASE_NAME_MAP = {
    '大斑病': '斑病',
    '灰斑病': '斑病',
    '锈病': '锈病'
}

def load_leaf_model():
    """加载叶片病害诊断模型"""
    model = RTX3060OptimizedModel(num_classes=NUM_CLASSES, pretrained=False)
    checkpoint = torch.load(MODEL_PATH, map_location=torch.device('cpu'), weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    return model

# --- 全局加载 ---
# 1. 加载诊断模型
model = load_leaf_model()
# 2. **决定性修复**: 加载知识库到内存。这是之前所有问题的根源。
# 必须在程序启动时执行，以确保后续所有查询都有数据可用。
load_knowledge_base()


def predict_leaf_diseases(image_path: str, history: list):
    """
    接收图片，使用多标签模型进行预测，并生成一份完整的诊断报告。
    """
    history = history or []
    if not image_path:
        history.append({"role": "assistant", "content": "请上传一张图片。"})
        return history, gr.update(visible=True), gr.update(visible=False)

    # 用户上传图片
    history.append({"role": "user", "content": {"path": image_path, "mime_type": "image/jpeg"}})

    # 模型推理
    image_tensor = preprocess_image(image_path)
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.sigmoid(outputs).squeeze(0)

    # 处理诊断结果
    detected_indices = torch.where(probabilities > 0.5)[0]
    
    report = ""
    # 情况一：未检测到任何病害，或只有"健康"
    if len(detected_indices) == 0 or (len(detected_indices) == 1 and CLASS_NAMES[detected_indices[0]] == '健康'):
        health_confidence = probabilities[CLASS_NAMES.index('健康')].item()
        report = f"✅ **诊断结果：健康**\n\n根据模型分析，您的玉米叶片非常健康 (置信度: {health_confidence:.1%})。"
    
    # 情况二：检测到一种或多种病害
    else:
        # 步骤 1: 对模型输出进行分组和统一化
        detected_diseases = {CLASS_NAMES[i]: probabilities[i].item() for i in detected_indices if CLASS_NAMES[i] != '健康'}
        blight_diseases = {k: v for k, v in detected_diseases.items() if k in ['大斑病', '灰斑病']}
        other_diseases = {k: v for k, v in detected_diseases.items() if k not in ['大斑病', '灰斑病']}

        # 创建统一的待报告列表
        diagnoses_to_report = []
        
        # 处理斑病类别
        if blight_diseases:
            max_blight_confidence = max(blight_diseases.values())
            original_blight_names = list(blight_diseases.keys())
            diagnoses_to_report.append({
                'display_name': '斑病',
                'confidence': max_blight_confidence,
                'original_names': original_blight_names,
                'kb_main_name': '斑病' 
            })

        # 处理其他病害
        for name, conf in other_diseases.items():
            diagnoses_to_report.append({
                'display_name': name,
                'confidence': conf,
                'original_names': [name],
                'kb_main_name': DISEASE_NAME_MAP.get(name, name)
            })
        
        # 根据置信度排序
        diagnoses_to_report.sort(key=lambda x: x['confidence'], reverse=True)

        # 步骤 2: 生成报告
        report_parts = []
        for diag in diagnoses_to_report:
            part = f"### 诊断: {diag['display_name']} (置信度: {diag['confidence']:.1%})\n\n"
            
            symptoms_parts = []
            occurrence_parts = []
            
            # 改进的知识库查询逻辑
            all_kb_sub_types = get_sub_types(diag['kb_main_name'])
            
            for original_name in diag['original_names']:
                # 改进匹配逻辑：更灵活的匹配方式
                matched_sub_types = []
                for kb_sub_type_key in all_kb_sub_types:
                    # 更宽松的匹配条件
                    if (original_name in kb_sub_type_key or 
                        original_name.replace('病', '') in kb_sub_type_key or
                        any(keyword in kb_sub_type_key for keyword in original_name.replace('病', '').split('_'))):
                        matched_sub_types.append(kb_sub_type_key)
                
                # 如果没有匹配到，尝试使用主病害名
                if not matched_sub_types and diag['kb_main_name'] in all_kb_sub_types:
                    matched_sub_types = [diag['kb_main_name']]
                
                # 处理匹配到的亚种
                for sub_type_key in matched_sub_types:
                    entry = get_knowledge_entry(diag['kb_main_name'], sub_type_key)
                    
                    if entry:
                        symptoms = entry.get('核心症状')
                        if symptoms:
                            # 清理亚种名称用于显示
                            clean_name = sub_type_key.split('(')[0].strip()
                            clean_name = clean_name.replace("一、", "").replace("二、", "").replace("三、", "")
                            symptoms_parts.append(f"**{clean_name}**: {symptoms}")

                        occurrence = entry.get('发生规律')
                        if occurrence and occurrence not in occurrence_parts:
                            occurrence_parts.append(occurrence)

            # 如果没有找到任何症状信息，提供基本信息
            if not symptoms_parts:
                symptoms_parts.append(f"**{diag['display_name']}**: 知识库中暂无详细症状描述，建议结合田间实际情况进行判断。")

            # 组合信息
            if symptoms_parts:
                part += "**核心症状**:\n" + "\n\n".join(symptoms_parts) + "\n\n"
            
            if occurrence_parts:
                part += "**发生规律参考**:\n" + "\n\n".join(occurrence_parts) + "\n"
            else:
                part += "**发生规律参考**:\n请参考相关农业资料或咨询当地农技专家。\n"

            report_parts.append(part)

        # 生成最终报告
        if len(report_parts) > 1:
            report = f"🔍 **复合诊断报告**\n\n模型在图片中识别出多种病害特征，详情如下：\n\n---\n\n" + "\n\n---\n\n".join(report_parts)
        else:
            report = report_parts[0]

    history.append({"role": "assistant", "content": report})
    return history, gr.update(), gr.update()


def start_new_diagnosis():
    """重置UI以开始新的诊断。"""
    return [], gr.update(value=None), gr.update()


def create_leaf_expert_interface():
    with gr.Blocks(analytics_enabled=False) as interface:
        # 添加专家系统标题
        gr.HTML("""
        <div style="background: linear-gradient(135deg, #4CAF50, #2E7D32); color: white; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700;">🍃 玉米叶片病害诊断专家</h2>
            <p style="margin: 8px 0 0 0; font-size: 1.1rem; opacity: 0.9;">基于深度学习的叶片病害自动识别系统</p>
        </div>
        """)
        
        # 功能介绍卡片 - 绿色主题
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="hover-card" style="background: linear-gradient(135deg, #E8F5E8, #C8E6C9); border: 1px solid #A5D6A7; border-radius: 10px; padding: 15px; margin: 10px 0; text-align: center; transition: all 0.3s ease; cursor: pointer;">
                    <h4 style="color: #2E7D32; margin: 0 0 10px 0;">🔬 AI智能识别</h4>
                    <p style="margin: 0; font-size: 0.9rem;">上传叶片照片<br>智能识别病害类型<br>ConvNext深度学习</p>
                </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="hover-card" style="background: linear-gradient(135deg, #E8F5E8, #C8E6C9); border: 1px solid #A5D6A7; border-radius: 10px; padding: 15px; margin: 10px 0; text-align: center; transition: all 0.3s ease; cursor: pointer;">
                    <h4 style="color: #2E7D32; margin: 0 0 10px 0;">📊 详细分析报告</h4>
                    <p style="margin: 0; font-size: 0.9rem;">专业病害信息<br>发生规律分析<br>置信度评估</p>
                </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="hover-card" style="background: linear-gradient(135deg, #E8F5E8, #C8E6C9); border: 1px solid #A5D6A7; border-radius: 10px; padding: 15px; margin: 10px 0; text-align: center; transition: all 0.3s ease; cursor: pointer;">
                    <h4 style="color: #2E7D32; margin: 0 0 10px 0;">🎯 高准确率识别</h4>
                    <p style="margin: 0; font-size: 0.9rem;">支持斑病、锈病<br>健康状态判断<br>复合病害诊断</p>
                </div>
                """)
        
        # 主要功能区域
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 💬 诊断结果")
                chatbot = gr.Chatbot(
                    label="诊断对话", 
                    height=800,
                    bubble_full_width=False,
                    avatar_images=(None, "assets/bot.png"),
                    type="messages"
                )
                
            with gr.Column(scale=1):
                gr.Markdown("### 📸 图像上传与分析")
                
                # 图像上传区域
                image_input = gr.Image(
                    label="请上传玉米叶片照片", 
                    type="filepath",
                    height=300,
                    interactive=True
                )
                
                with gr.Row():
                    predict_btn = gr.Button(
                        "🔍 开始诊断", 
                        variant="primary",
                        size="lg",
                        elem_classes=["btn-primary"]
                    )
                    clear_btn = gr.Button(
                        "🔄 重新开始", 
                        variant="secondary",
                        elem_classes=["btn-secondary"]
                    )
                
                gr.Markdown("### 📚 使用说明")
                gr.HTML("""
                <div style="background: linear-gradient(135deg, #F1F8E9, #DCEDC8); border: 1px solid #AED581; border-radius: 8px; padding: 12px; margin: 10px 0;">
                    <h5 style="color: #33691E; margin: 0 0 8px 0;">📷 拍摄建议</h5>
                    <ul style="margin: 0; padding-left: 16px; color: #388E3C; font-size: 0.85rem;">
                        <li>选择病斑清晰可见的叶片</li>
                        <li>在自然光下拍摄，避免阴影</li>
                        <li>保持镜头稳定，图像清晰</li>
                        <li>支持JPG、PNG等格式</li>
                    </ul>
                </div>
                """)

                gr.Markdown("### 📚 专业信息查询")
                gr.HTML("""
                <div style="background: linear-gradient(135deg, #E8F5E8, #C8E6C9); border: 1px solid #A5D6A7; border-radius: 8px; padding: 12px; margin: 10px 0;">
                    <h5 style="color: #2E7D32; margin: 0 0 8px 0;">🔬 AI识别能力</h5>
                    <ul style="margin: 0; padding-left: 16px; color: #2E7D32; font-size: 0.85rem;">
                        <li><strong>斑病识别</strong>：大斑病、灰斑病等</li>
                        <li><strong>锈病识别</strong>：各种锈病类型</li>
                        <li><strong>健康判断</strong>：正常叶片状态</li>
                        <li><strong>复合诊断</strong>：多种病害共存</li>
                    </ul>
                </div>
                """)
        
        # 使用提示
        gr.HTML("""
        <div style="background: linear-gradient(135deg, #FFF3E0, #FFE0B2); border: 1px solid #FFCC02; border-radius: 10px; padding: 15px; margin: 20px 0;">
            <h4 style="color: #E65100; margin: 0 0 10px 0;">💡 AI诊断系统使用指南</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div>
                    <h5 style="color: #BF360C; margin: 0 0 5px 0;">🔍 支持病害类型：</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #BF360C; font-size: 0.9rem;">
                        <li><strong>斑病</strong>：包括大斑病、灰斑病等</li>
                        <li><strong>锈病</strong>：玉米锈病各种类型</li>
                        <li><strong>健康状态</strong>：识别正常健康叶片</li>
                        <li><strong>复合病害</strong>：多种病害共存诊断</li>
                    </ul>
                </div>
                <div>
                    <h5 style="color: #BF360C; margin: 0 0 5px 0;">🎯 技术特点：</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #BF360C; font-size: 0.9rem;">
                        <li><strong>ConvNext架构</strong>：先进的深度学习模型</li>
                        <li><strong>多标签识别</strong>：可同时识别多种病害</li>
                        <li><strong>置信度评估</strong>：提供识别可信度分数</li>
                        <li><strong>知识库整合</strong>：结合专业农业知识</li>
                    </ul>
                </div>
            </div>
            <div style="margin-top: 10px; padding: 8px; background: rgba(76, 175, 80, 0.1); border-radius: 6px;">
                <p style="margin: 0; font-size: 0.85rem; color: #2E7D32;"><strong>模型性能</strong>：单一病种分类准确率98.24%，复合病例识别准确率95.16%，基于严格筛选的高质量数据集训练。</p>
            </div>
        </div>
        """)
        
        # 功能兼容按钮 - 隐藏以保持界面整洁
        new_diagnosis_btn = gr.Button("开始新的诊断", visible=False)
        
        # 事件绑定
        predict_btn.click(
            fn=predict_leaf_diseases,
            inputs=[image_input, chatbot],
            outputs=[chatbot, image_input, new_diagnosis_btn]
        )
        
        clear_btn.click(
            fn=start_new_diagnosis,
            inputs=[],
            outputs=[chatbot, image_input, new_diagnosis_btn]
        )
        
        image_input.upload(
            fn=predict_leaf_diseases,
            inputs=[image_input, chatbot],
            outputs=[chatbot, image_input, new_diagnosis_btn]
        )
        
        new_diagnosis_btn.click(
            fn=start_new_diagnosis,
            inputs=[],
            outputs=[chatbot, image_input, new_diagnosis_btn]
        )
        
    return interface

# 添加主程序入口：使得该脚本可以直接运行以进行独立测试
if __name__ == "__main__":
    print("正在以独立模式启动玉米叶片病害诊断专家界面...")
    interface = create_leaf_expert_interface()
    # 使用share=True可以在局域网内访问，方便测试
    interface.launch(share=True)
