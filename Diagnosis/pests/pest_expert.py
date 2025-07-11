import gradio as gr
from PIL import Image
import torch
from utils.image_utils import preprocess_image
from utils.model_definitions import RTX3060OptimizedModel
from utils.knowledge_loader import get_knowledge_entry

# --- 模型和常量定义 ---
MODEL_PATH = 'pests/models/best_pest_model.pth'
NUM_CLASSES = 3 
CLASS_NAMES = ['玉米粘虫', '玉米螟', '玉米蓟马']

# 添加模型预测类名与知识库键名的映射
PEST_KNOWLEDGE_MAP = {
    '玉米粘虫': '粘虫',
    '玉米螟': '玉米螟',
    '玉米蓟马': '蓟马'
}

def load_pest_model():
    """加载害虫识别模型"""
    model = RTX3060OptimizedModel(num_classes=NUM_CLASSES, pretrained=False)
    try:
        checkpoint = torch.load(MODEL_PATH, map_location=torch.device('cpu'), weights_only=False)
        if 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
        else:
            state_dict = checkpoint
        
        model.load_state_dict(state_dict)
        model.eval()
        return model
    except FileNotFoundError:
        print(f"错误：害虫模型文件未找到，路径: {MODEL_PATH}")
        return "not_found"
    except Exception as e:
        print(f"加载害虫模型时发生未知错误: {e}")
        return "load_error"

# 全局加载模型
model = load_pest_model()

def predict_pest(image_path: str, history: list):
    """
    接收图片，使用模型进行预测，并结合知识库返回图文并茂的诊断报告。
    """
    history = history or []
    if not image_path:
        history.append({"role": "assistant", "content": "请上传一张害虫图片。"})
        return history, gr.update(visible=True), gr.update(visible=False)

    history.append({"role": "user", "content": {"path": image_path, "mime_type": "image/jpeg"}})

    if isinstance(model, str):
        error_msg = "抱歉，由于找不到模型文件，诊断功能暂时无法使用。" if model == "not_found" else "抱歉，加载模型时出现内部错误。"
        history.append({"role": "assistant", "content": error_msg})
        return history, gr.update(visible=True), gr.update(visible=False)

    image_tensor = preprocess_image(image_path)
    if image_tensor is None:
        history.append({"role": "assistant", "content": "无法处理您上传的图片，请检查图片文件是否有效。"})
        return history, gr.update(visible=True), gr.update(visible=False)

    try:
        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted_class_idx = torch.max(probabilities, 1)
            
        predicted_class_name = CLASS_NAMES[predicted_class_idx.item()]
        confidence_score = confidence.item()

        # 使用映射关系查找知识库
        kb_key = PEST_KNOWLEDGE_MAP.get(predicted_class_name, predicted_class_name)
        
        # 设置置信度阈值
        is_low_confidence = confidence_score < 0.4
        
        # 生成诊断报告
        final_report = ""
        if is_low_confidence:
            final_report += f"⚠️ **结果不确定**\n\n模型识别最可能的目标是 **{predicted_class_name}**，但置信度较低({confidence_score:.1%})。\n\n请结合下面的描述和图片进行人工判断。\n\n---\n\n"
        
        # 查找知识库条目 - 需要指定亚种名称
        entry = get_knowledge_entry(kb_key, kb_key)
        if not entry:
            final_report += f"### 诊断报告：{predicted_class_name}\n\n"
            final_report += f"*模型置信度: {confidence_score:.1%}*\n\n"
            final_report += "**核心症状与危害**:\n知识库中暂无该害虫的详细信息，建议结合实际情况进行判断。\n\n"
            final_report += "**发生规律参考**:\n请参考相关农业资料或咨询当地农技专家。"
        else:
            # 获取知识库信息
            symptoms = entry.get('核心症状', '无详细症状描述。')
            occurrence = entry.get('发生规律', '无相关发生规律信息。')
            
            # 生成完整报告
            final_report += f"### 诊断报告：{predicted_class_name}\n\n"
            final_report += f"*模型置信度: {confidence_score:.1%}*\n\n"
            final_report += f"**核心症状与危害**:\n{symptoms}\n\n"
            final_report += f"**发生规律参考**:\n{occurrence}"
        
        history.append({"role": "assistant", "content": final_report})
        return history, gr.update(), gr.update()

    except Exception as e:
        print(f"害虫诊断过程中发生错误: {e}")
        history.append({"role": "assistant", "content": f"抱歉，在诊断过程中发生了错误：{str(e)}"})
        return history, gr.update(), gr.update()

def start_new_pest_diagnosis():
    """重置UI以开始新的诊断。"""
    return [], gr.update(value=None), gr.update()

def create_pest_expert_interface():
    with gr.Blocks(analytics_enabled=False) as interface:
        # 添加专家系统标题
        gr.HTML("""
        <div style="background: linear-gradient(135deg, #FF9800, #F57C00); color: white; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700;">🐛 玉米害虫诊断专家</h2>
            <p style="margin: 8px 0 0 0; font-size: 1.1rem; opacity: 0.9;">专业的害虫识别与防治指导系统</p>
        </div>
        """)
        
        # 功能介绍卡片 - 橙色主题
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="hover-card" style="background: linear-gradient(135deg, #FFF3E0, #FFE0B2); border: 1px solid #FFCC02; border-radius: 10px; padding: 15px; margin: 10px 0; text-align: center; transition: all 0.3s ease; cursor: pointer;">
                    <h4 style="color: #E65100; margin: 0 0 10px 0;">🔍 精准识别系统</h4>
                    <p style="margin: 0; font-size: 0.9rem;">上传害虫照片<br>智能识别害虫种类<br>AI深度学习模型</p>
                </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="hover-card" style="background: linear-gradient(135deg, #FFF3E0, #FFE0B2); border: 1px solid #FFCC02; border-radius: 10px; padding: 15px; margin: 10px 0; text-align: center; transition: all 0.3s ease; cursor: pointer;">
                    <h4 style="color: #E65100; margin: 0 0 10px 0;">📋 防治指导建议</h4>
                    <p style="margin: 0; font-size: 0.9rem;">生活习性分析<br>科学防治建议<br>危害程度评估</p>
                </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="hover-card" style="background: linear-gradient(135deg, #FFF3E0, #FFE0B2); border: 1px solid #FFCC02; border-radius: 10px; padding: 15px; margin: 10px 0; text-align: center; transition: all 0.3s ease; cursor: pointer;">
                    <h4 style="color: #E65100; margin: 0 0 10px 0;">🎯 主要害虫覆盖</h4>
                    <p style="margin: 0; font-size: 0.9rem;">粘虫、玉米螟<br>蓟马等识别<br>高准确率判断</p>
                </div>
                """)
        
        # 主要功能区域
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 💬 识别结果")
                chatbot = gr.Chatbot(
                    label="诊断对话", 
                    height=800,
                    bubble_full_width=False,
                    avatar_images=(None, "assets/bot.png"),
                    type="messages"
                )
                
            with gr.Column(scale=1):
                gr.Markdown("### 📸 害虫图像上传与识别")
                
                # 图像上传区域
                image_input = gr.Image(
                    label="请上传害虫照片", 
                    type="filepath",
                    height=300,
                    interactive=True
                )
                
                with gr.Row():
                    predict_btn = gr.Button(
                        "🔍 开始识别", 
                        variant="primary",
                        size="lg",
                        elem_classes=["btn-primary"]
                    )
                    clear_btn = gr.Button(
                        "🔄 重新开始", 
                        variant="secondary",
                        elem_classes=["btn-secondary"]
                    )
                
                gr.Markdown("### 📚 拍摄指南")
                gr.HTML("""
                <div style="background: linear-gradient(135deg, #FFF8E1, #FFECB3); border: 1px solid #FFD54F; border-radius: 8px; padding: 12px; margin: 10px 0;">
                    <h5 style="color: #F57C00; margin: 0 0 8px 0;">📷 拍摄建议</h5>
                    <ul style="margin: 0; padding-left: 16px; color: #EF6C00; font-size: 0.85rem;">
                        <li>选择害虫特征清晰可见的角度</li>
                        <li>近距离拍摄，突出形态特征</li>
                        <li>确保光线充足，避免阴影</li>
                        <li>支持JPG、PNG等格式</li>
                    </ul>
                </div>
                """)

                gr.Markdown("### 📚 专业信息查询")
                gr.HTML("""
                <div style="background: linear-gradient(135deg, #FFF3E0, #FFE0B2); border: 1px solid #FFCC02; border-radius: 8px; padding: 12px; margin: 10px 0;">
                    <h5 style="color: #E65100; margin: 0 0 8px 0;">🐛 识别范围</h5>
                    <ul style="margin: 0; padding-left: 16px; color: #E65100; font-size: 0.85rem;">
                        <li><strong>玉米粘虫</strong>：夜蛾科害虫识别</li>
                        <li><strong>玉米螟</strong>：钻蛀性害虫检测</li>
                        <li><strong>玉米蓟马</strong>：刺吸式害虫判断</li>
                        <li><strong>形态分析</strong>：98.37%准确率</li>
                    </ul>
                </div>
                """)
        
        # 使用提示
        gr.HTML("""
        <div style="background: linear-gradient(135deg, #FFF3E0, #FFE0B2); border: 1px solid #FFCC02; border-radius: 10px; padding: 15px; margin: 20px 0;">
            <h4 style="color: #E65100; margin: 0 0 10px 0;">💡 AI害虫识别系统使用指南</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div>
                    <h5 style="color: #BF360C; margin: 0 0 5px 0;">🔍 支持害虫类型：</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #BF360C; font-size: 0.9rem;">
                        <li><strong>玉米粘虫</strong>：夜蛾科害虫，幼虫取食叶片</li>
                        <li><strong>玉米螟</strong>：钻蛀性害虫，钻蛀茎秆</li>
                        <li><strong>玉米蓟马</strong>：刺吸式害虫，危害叶片</li>
                        <li><strong>形态识别</strong>：基于害虫外观特征判断</li>
                    </ul>
                </div>
                <div>
                    <h5 style="color: #BF360C; margin: 0 0 5px 0;">🎯 识别技术特点：</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #BF360C; font-size: 0.9rem;">
                        <li><strong>深度学习</strong>：ConvNext网络架构</li>
                        <li><strong>置信度评估</strong>：提供识别可信度</li>
                        <li><strong>知识库整合</strong>：结合害虫生物学知识</li>
                        <li><strong>五折交叉验证</strong>：98.37%识别准确率</li>
                    </ul>
                </div>
            </div>
            <div style="margin-top: 10px; padding: 8px; background: rgba(255, 152, 0, 0.1); border-radius: 6px;">
                <p style="margin: 0; font-size: 0.85rem; color: #E65100;"><strong>识别提示</strong>：害虫识别效果最佳的照片应包含害虫的完整形态特征，建议在田间发现害虫时立即拍摄。</p>
            </div>
        </div>
        """)
        
        # 功能兼容按钮 - 隐藏以保持界面整洁
        new_diagnosis_btn = gr.Button("开始新的诊断", visible=False)
        
        # 事件绑定
        predict_btn.click(
            fn=predict_pest,
            inputs=[image_input, chatbot],
            outputs=[chatbot, image_input, new_diagnosis_btn]
        )
        
        clear_btn.click(
            fn=start_new_pest_diagnosis,
            inputs=[],
            outputs=[chatbot, image_input, new_diagnosis_btn]
        )
        
        image_input.upload(
            fn=predict_pest,
            inputs=[image_input, chatbot],
            outputs=[chatbot, image_input, new_diagnosis_btn]
        )
        
        new_diagnosis_btn.click(
            fn=start_new_pest_diagnosis,
            inputs=[],
            outputs=[chatbot, image_input, new_diagnosis_btn]
        )
        
    return interface
