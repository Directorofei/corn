import gradio as gr
import os
import time
import asyncio
from utils.knowledge_loader import get_sub_types, get_knowledge_entry

# 定义该专家系统对应的知识库条目和图片路径
STEM_DISEASE_CATEGORY = "黑粉病"
IMAGE_PATH = "stem/images"

def get_stem_disease_list():
    """获取所有茎/穗部病害的亚类列表"""
    return get_sub_types(STEM_DISEASE_CATEGORY)

def analyze_symptoms(symptoms_input: str, history: list):
    """分析用户输入的症状并提供诊断建议"""
    history = history or []
    
    if not symptoms_input or not symptoms_input.strip():
        history.append({"role": "assistant", "content": "请描述您观察到的症状，我将根据描述帮您分析可能的病害。"})
        return history, "", gr.update(visible=False)
    
    # 模拟processing时间，增加用户体验
    time.sleep(0.8)
    
    history.append({"role": "user", "content": symptoms_input})
    
    # 获取所有可能的病害类型
    disease_subtypes = get_stem_disease_list()
    
    # 简单的关键词匹配分析
    symptoms_lower = symptoms_input.lower().strip()
    
    # 改进的关键词匹配规则
    keyword_matches = []
    
    for subtype in disease_subtypes:
        entry = get_knowledge_entry(STEM_DISEASE_CATEGORY, subtype)
        if entry:
            match_score = 0
            matched_keywords = []
            
            # 检查症状描述中的关键词
            core_symptoms = entry.get('核心症状', '').lower()
            
            # 丝黑穗病关键词（更灵活的匹配）
            if '丝黑穗' in subtype:
                # 主要关键词（权重较高）
                primary_keywords = ['黑粉', '黑色', '粉末', '果穗', '花丝', '黑包', '黑团', '黑块', '黑灰', '粉状', '粉尘', '包子', '肿包']
                # 次要关键词（权重较低）
                secondary_keywords = ['刺猬', '短粗', '畸形', '系统', '全株', '变形', '异常', '矮化', '侏儒', '短小', '粗短', '变样', '奇形', '怪状', '不正常', '发育不良']
                # 扩展匹配词（容错匹配）
                fuzzy_keywords = ['枯死', '枯萎', '萎蔫', '死亡', '坏死', '腐烂', '腐败', '变质', '病变', '感染', '发病', '生病']
                
                for keyword in primary_keywords:
                    if keyword in symptoms_lower:
                        match_score += 2
                        matched_keywords.append(keyword)
                
                for keyword in secondary_keywords:
                    if keyword in symptoms_lower:
                        match_score += 1
                        matched_keywords.append(keyword)
                
                for keyword in fuzzy_keywords:
                    if keyword in symptoms_lower:
                        match_score += 0.5
                        matched_keywords.append(keyword)
            
            # 瘤黑粉病关键词（更灵活的匹配）
            elif '瘤黑粉' in subtype:
                # 主要关键词
                primary_keywords = ['瘤', '肿瘤', '灰包', '肿胀', '包状', '肿包', '瘤状', '包块', '灰色', '灰白', '鼓包', '凸起', '隆起']
                # 次要关键词
                secondary_keywords = ['白色', '淡绿', '局部', '茎', '叶', '伤口', '膨大', '膨胀', '增厚', '变厚', '肿大', '粗大', '异常', '突出', '凸出']
                # 扩展匹配词
                fuzzy_keywords = ['病斑', '斑点', '斑块', '病变', '变色', '发病', '感染', '症状', '异常', '不正常', '有问题']
                
                for keyword in primary_keywords:
                    if keyword in symptoms_lower:
                        match_score += 2
                        matched_keywords.append(keyword)
                
                for keyword in secondary_keywords:
                    if keyword in symptoms_lower:
                        match_score += 1
                        matched_keywords.append(keyword)
                
                for keyword in fuzzy_keywords:
                    if keyword in symptoms_lower:
                        match_score += 0.5
                        matched_keywords.append(keyword)
            
            # 即使没有精确匹配，也可以通过模糊匹配给予一定分数
            if match_score == 0:
                # 模糊匹配常见描述
                fuzzy_matches = []
                
                # 更宽泛的颜色匹配
                if any(color in symptoms_lower for color in ['黑', '灰', '褐', '棕', '暗']):
                    if any(texture in symptoms_lower for texture in ['粉', '色', '状', '样', '像']):
                        fuzzy_matches.append('颜色异常')
                
                # 更宽泛的形状匹配
                if any(shape in symptoms_lower for shape in ['变形', '异常', '畸形', '不正常', '奇怪', '怪异', '变样', '不对', '有问题']):
                    fuzzy_matches.append('形状异常')
                
                # 更宽泛的肿胀匹配
                if any(swelling in symptoms_lower for swelling in ['肿', '包', '胀', '大', '厚', '凸', '鼓', '突', '隆']):
                    fuzzy_matches.append('肿胀状况')
                
                # 通用病害词汇
                if any(disease in symptoms_lower for disease in ['病', '坏', '烂', '死', '枯', '萎', '变', '问题', '不好', '异常']):
                    fuzzy_matches.append('病害征象')
                
                if fuzzy_matches:
                    match_score = 1
                    matched_keywords.extend(fuzzy_matches)
            
            if match_score > 0:
                keyword_matches.append({
                    'subtype': subtype,
                    'score': match_score,
                    'keywords': matched_keywords,
                    'entry': entry
                })
    
    # 按匹配分数排序
    keyword_matches.sort(key=lambda x: x['score'], reverse=True)
    
    # 生成诊断报告
    response = "## 🔍 症状分析报告\n\n"
    
    # 只有在有较高匹配度时才显示匹配结果
    high_quality_matches = [m for m in keyword_matches if m['score'] >= 1.5]  # 降低阈值从2到1.5
    
    if high_quality_matches:
        response += f"根据您描述的症状\"{symptoms_input}\"，我分析出以下可能的病害：\n\n"
        
        for i, match in enumerate(high_quality_matches[:2]):  # 显示前两个最匹配的
            subtype = match['subtype']
            score = match['score']
            keywords = match['keywords']
            entry = match['entry']
            
            response += f"### {i+1}. {subtype}\n"
            response += f"**匹配度**: {score} 个关键词 ({', '.join(keywords)})\n\n"
            
            # 添加详细信息
            symptoms = entry.get('核心症状', '无详细症状描述。')
            occurrence = entry.get('发生规律', '无相关发生规律信息。')
            
            response += f"**核心症状对比**:\n{symptoms}\n\n"
            response += f"**发生规律参考**:\n{occurrence}\n\n"
            
            # 查找对应图片 - 显示所有图像文件
            image_files = []
            if os.path.exists(IMAGE_PATH):
                for f in os.listdir(IMAGE_PATH):
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                        image_files.append(os.path.join(IMAGE_PATH, f))
            
            if image_files:
                response += f"**参考图片**: 请查看下方图片库中的 {subtype} 典型症状\n\n"
            
            response += "---\n\n"
        
        response += "请对照以上信息，结合田间实际情况进行确认。如果需要进一步诊断，请提供更多细节。"
    else:
        # 检查是否有低匹配度的结果
        if keyword_matches:
            response += f"根据您描述的症状\"{symptoms_input}\"，检测到一些相关特征，但匹配度较低：\n\n"
            for match in keyword_matches[:1]:  # 只显示最匹配的一个
                response += f"- **{match['subtype']}**: 匹配特征 ({', '.join(match['keywords'])})\n"
            response += "\n请参考下方详细信息进行对比确认。\n\n"
        else:
            response += "暂时无法根据您的描述匹配到具体的病害类型。\n\n"
        response += "**建议**:\n"
        response += "1. 请尝试更详细地描述症状特征\n"
        response += "2. 可以描述病害发生的时期、部位、形状、颜色等\n"
        response += "3. 您也可以直接选择下方的病害类型进行对比\n\n"
        response += "**常见茎穗病害提示**:\n"
        
        # 提供基本的病害信息
        for subtype in disease_subtypes:
            entry = get_knowledge_entry(STEM_DISEASE_CATEGORY, subtype)
            if entry:
                response += f"- **{subtype}**: 主要特征是"
                symptoms = entry.get('核心症状', '')
                if symptoms:
                    # 提取简要特征
                    if '丝黑穗' in subtype:
                        response += "整个果穗变成黑粉包，短粗畸形，无花丝\n"
                    elif '瘤黑粉' in subtype:
                        response += "植株各部位形成肿瘤状灰包\n"
                    else:
                        response += f"{symptoms[:50]}...\n"
    
    history.append({"role": "assistant", "content": response})
    
    # 如果有症状匹配，也显示图像
    if high_quality_matches or keyword_matches:
        # 查找参考图片
        image_files = []
        if os.path.exists(IMAGE_PATH):
            for f in os.listdir(IMAGE_PATH):
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                    image_files.append(os.path.join(IMAGE_PATH, f))
        
        if image_files:
            return history, "", gr.update(visible=True, value=image_files)
    
    return history, "", gr.update()

def get_disease_details(choice: str, history: list):
    """获取特定病害的详细信息"""
    history = history or []
    
    if not choice:
        history.append({"role": "assistant", "content": "请选择一个病害类型，我将为您详细介绍。"})
        return history, gr.update()
    
    # 模拟processing时间
    time.sleep(0.5)
    
    history.append({"role": "user", "content": f"查看{choice}的详细信息"})
    
    # 获取知识库条目
    entry = get_knowledge_entry(STEM_DISEASE_CATEGORY, choice)
    if not entry:
        response = f"抱歉，无法在知识库中找到'{choice}'的详细信息。"
        history.append({"role": "assistant", "content": response})
        return history, gr.update()
    
    symptoms = entry.get('核心症状', '无详细症状描述。')
    occurrence = entry.get('发生规律', '无相关发生规律信息。')
    
    response = f"## 📋 {choice} 详细信息\n\n"
    response += f"### **核心症状**\n{symptoms}\n\n"
    response += f"### **发生规律**\n{occurrence}\n\n"
    response += "---\n\n"
    response += "**诊断建议**:\n"
    response += "1. 请仔细对比您田间观察到的症状与上述描述\n"
    response += "2. 注意观察病害发生的时期和环境条件\n"
    response += "3. 如有疑问，建议咨询当地农技专家或拍照进一步确认\n\n"
    response += "💡 如果您想分析症状，可以在上方文本框中描述您观察到的具体症状。"
    
    history.append({"role": "assistant", "content": response})
    
    # 查找对应图片 - 显示所有图像文件
    image_files = []
    if os.path.exists(IMAGE_PATH):
        for f in os.listdir(IMAGE_PATH):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                image_files.append(os.path.join(IMAGE_PATH, f))
    
    if image_files:
        return history, gr.update(visible=True, value=image_files)
    else:
        return history, gr.update()

def reset_conversation():
    """重置对话"""
    return [], "", None, gr.update()

def create_stem_expert_interface():
    disease_list = get_stem_disease_list()

    with gr.Blocks(analytics_enabled=False) as interface:
        # 添加专家系统标题 - 暖灰蓝色主题
        gr.HTML("""
        <div style="background: linear-gradient(135deg, #546E7A, #37474F); color: white; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700;">🌾 玉米茎穗病害诊断专家</h2>
            <p style="margin: 8px 0 0 0; font-size: 1.1rem; opacity: 0.9;">智能茎穗病害症状分析与诊断系统</p>
        </div>
        """)
        
        # 功能介绍卡片 - 暖灰蓝色主题
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="hover-card" style="background: linear-gradient(135deg, #F5F7FA, #E8EAF6); border: 1px solid #B0BEC5; border-radius: 10px; padding: 15px; margin: 10px 0; text-align: center; transition: all 0.3s ease; cursor: pointer;">
                    <h4 style="color: #37474F; margin: 0 0 10px 0;">🔍 智能症状分析</h4>
                    <p style="margin: 0; font-size: 0.9rem;">描述茎穗症状特征<br>AI智能匹配病害类型<br>提供置信度评估</p>
                </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="hover-card" style="background: linear-gradient(135deg, #F5F7FA, #E8EAF6); border: 1px solid #B0BEC5; border-radius: 10px; padding: 15px; margin: 10px 0; text-align: center; transition: all 0.3s ease; cursor: pointer;">
                    <h4 style="color: #37474F; margin: 0 0 10px 0;">📋 专业诊断建议</h4>
                    <p style="margin: 0; font-size: 0.9rem;">详细病害信息展示<br>发生规律科学解析<br>防治建议精准推荐</p>
                </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="hover-card" style="background: linear-gradient(135deg, #F5F7FA, #E8EAF6); border: 1px solid #B0BEC5; border-radius: 10px; padding: 15px; margin: 10px 0; text-align: center; transition: all 0.3s ease; cursor: pointer;">
                    <h4 style="color: #37474F; margin: 0 0 10px 0;">🎯 主要病害覆盖</h4>
                    <p style="margin: 0; font-size: 0.9rem;">丝黑穗病识别<br>瘤黑粉病诊断<br>图像对比参考</p>
                </div>
                """)
        
        # 主要功能区域
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 💬 诊断对话")
                chatbot = gr.Chatbot(
                    label="诊断对话", 
                    height=600,
                    bubble_full_width=False,
                    avatar_images=(None, "assets/bot.png"),
                    type="messages"
                )
                
            with gr.Column(scale=1):
                gr.Markdown("### 📝 症状输入与分析")
                
                # 症状输入区域
                symptoms_input = gr.Textbox(
                    label="症状描述",
                    placeholder="请详细描述您观察到的症状，例如：'果穗变成黑粉包，短粗畸形，无花丝'",
                    lines=4,
                    interactive=True,
                    elem_classes=["modern-input"]
                )
                
                with gr.Row():
                    analyze_btn = gr.Button(
                        "🔍 分析症状", 
                        variant="primary",
                        size="lg",
                        elem_classes=["btn-primary"]
                    )
                    reset_btn = gr.Button(
                        "🔄 重新开始", 
                        variant="secondary",
                        elem_classes=["btn-secondary"]
                    )
                
                gr.Markdown("### 🎯 病害类型快速选择")
                disease_radio = gr.Radio(
                    label="或直接选择病害类型查看详细信息", 
                    choices=disease_list,
                    interactive=True
                )
        
        # 图片展示区域
        gr.Markdown("### 📸 参考图片")
        gallery = gr.Gallery(
            label="典型茎穗病害症状对比", 
            visible=True,
            columns=2, 
            object_fit="contain", 
            height=500
        )
        
        # 使用提示
        gr.HTML("""
        <div style="background: linear-gradient(135deg, #FFF3E0, #FFE0B2); border: 1px solid #FFCC02; border-radius: 10px; padding: 15px; margin: 20px 0;">
            <h4 style="color: #E65100; margin: 0 0 10px 0;">💡 使用指南与诊断提示</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div>
                    <h5 style="color: #BF360C; margin: 0 0 5px 0;">🔍 症状描述建议：</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #BF360C; font-size: 0.9rem;">
                        <li><strong>部位描述</strong>：详细说明病害发生部位（茎部、穗部、叶片等）</li>
                        <li><strong>外观特征</strong>：描述颜色、形状、质地、大小等外观特征</li>
                        <li><strong>发生情况</strong>：说明发病时期、扩散程度、影响范围</li>
                        <li><strong>环境条件</strong>：提及天气、土壤、栽培条件等</li>
                    </ul>
                </div>
                <div>
                    <h5 style="color: #BF360C; margin: 0 0 5px 0;">🎯 关键词识别提示：</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #BF360C; font-size: 0.9rem;">
                        <li><strong>丝黑穗病</strong>：黑粉、畸形、短粗、花丝、刺猬状</li>
                        <li><strong>瘤黑粉病</strong>：肿瘤、灰包、肿胀、局部、膨大</li>
                        <li><strong>通用特征</strong>：变形、异常、包状、粉末状</li>
                        <li><strong>时期特征</strong>：苗期、拔节期、抽穗期、灌浆期</li>
                    </ul>
                </div>
            </div>
            <div style="margin-top: 10px; padding: 8px; background: rgba(84, 110, 122, 0.1); border-radius: 6px;">
                <p style="margin: 0; font-size: 0.85rem; color: #37474F;"><strong>智能分析特色</strong>：结合症状描述、关键词识别、模糊匹配等多种算法，提供匹配度评分和图像对比功能。</p>
            </div>
        </div>
        """)
        
        # 事件绑定
        analyze_btn.click(
            fn=analyze_symptoms,
            inputs=[symptoms_input, chatbot],
            outputs=[chatbot, symptoms_input, gallery]
        )
        
        symptoms_input.submit(
            fn=analyze_symptoms,
            inputs=[symptoms_input, chatbot],
            outputs=[chatbot, symptoms_input, gallery]
        )
        
        disease_radio.change(
            fn=get_disease_details,
            inputs=[disease_radio, chatbot],
            outputs=[chatbot, gallery]
        )
        
        reset_btn.click(
            fn=reset_conversation,
            inputs=[],
            outputs=[chatbot, symptoms_input, disease_radio, gallery]
        )
        
    return interface
