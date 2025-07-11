import gradio as gr
import os
from utils.knowledge_loader import get_sub_types, get_knowledge_entry

# 定义该专家系统对应的知识库条目和图片路径
ROOT_DISEASE_CATEGORY = "根腐病"
IMAGE_PATH = "root/images"

def get_root_disease_list():
    """获取所有根部病害的亚类列表"""
    subtypes = get_sub_types(ROOT_DISEASE_CATEGORY)
    # 如果没有亚类，返回主类别
    return subtypes if subtypes else [ROOT_DISEASE_CATEGORY]

def analyze_root_symptoms(symptoms_input: str, history: list):
    """分析用户输入的根部症状并提供诊断建议"""
    history = history or []
    
    if not symptoms_input or not symptoms_input.strip():
        history.append({"role": "assistant", "content": "请描述您观察到的根部症状，我将根据描述帮您分析可能的病害。"})
        return history, ""
    
    history.append({"role": "user", "content": symptoms_input})
    
    # 获取根腐病信息
    entry = get_knowledge_entry(ROOT_DISEASE_CATEGORY, ROOT_DISEASE_CATEGORY)
    if not entry:
        history.append({"role": "assistant", "content": "抱歉，无法获取根部病害信息。"})
        return history, ""
    
    symptoms_lower = symptoms_input.lower().strip()
    
    # 根腐病关键词匹配
    keyword_matches = []
    matched_keywords = []
    
    # 关键词分析
    keywords = {
        '青枯型': ['青枯', '急性', '青灰', '失水', '短时间', '迅速', '开水', '霜打'],
        '黄枯型': ['黄枯', '慢性', '逐片', '变黄', '缓慢'],
        '根系症状': ['根系', '根部', '变褐', '腐烂', '次生根', '容易拔起'],
        '茎基部症状': ['茎基', '茎秆', '黄褐', '疏松', '维管束', '丝状', '中空'],
        '果穗症状': ['果穗', '苞叶', '干枯', '松散', '下垂', '籽粒', '干瘪'],
        '发病条件': ['连作', '高温', '多雨', '雨后', '骤晴', '升温', '低洼', '排水不良']
    }
    
    for category, category_keywords in keywords.items():
        for keyword in category_keywords:
            if keyword in symptoms_lower:
                if category not in keyword_matches:
                    keyword_matches.append(category)
                matched_keywords.append(keyword)
    
    # 生成诊断报告
    response = "## 🔍 根部病害症状分析\n\n"
    
    if matched_keywords:
        response += f"根据您描述的症状\"**{symptoms_input}**\"，我分析出以下特征：\n\n"
        
        # 根据匹配的关键词给出诊断建议
        if any(kw in matched_keywords for kw in ['青枯', '急性', '青灰', '失水', '短时间']):
            response += "### 🚨 疑似急性根腐病（青枯型）\n\n"
            response += "**特征匹配**: 您的描述符合急性根腐病的特征\n\n"
        elif any(kw in matched_keywords for kw in ['黄枯', '慢性', '逐片', '变黄']):
            response += "### ⚠️ 疑似慢性根腐病（黄枯型）\n\n"
            response += "**特征匹配**: 您的描述符合慢性根腐病的特征\n\n"
        else:
            response += "### 💡 根腐病相关症状\n\n"
            response += "**匹配特征**: " + ", ".join(matched_keywords) + "\n\n"
        
        # 添加完整的病害信息
        symptoms = entry.get('核心症状', '无详细症状描述。')
        occurrence = entry.get('发生规律', '无相关发生规律信息。')
        
        response += f"**完整症状对比**:\n{symptoms}\n\n"
        response += f"**发生规律参考**:\n{occurrence}\n\n"
        
        response += "---\n\n"
        response += "**诊断建议**:\n"
        response += "1. 请仔细检查植株根系是否变褐腐烂\n"
        response += "2. 观察茎基部是否有腐烂、疏松现象\n"
        response += "3. 注意发病时期和田间环境条件\n"
        response += "4. 如果是连作地块，需要特别注意\n\n"
        
        if any(kw in matched_keywords for kw in ['青枯', '急性']):
            response += "**紧急处理建议**:\n"
            response += "- 立即停止灌水，改善田间排水\n"
            response += "- 及时拔除病株，避免传播\n"
            response += "- 考虑使用杀菌剂进行土壤处理\n"
        
    else:
        response += "暂时无法根据您的描述确定具体的病害类型。\n\n"
        response += "**建议**:\n"
        response += "1. 请尝试更详细地描述症状，如：\n"
        response += "   - 植株叶片的颜色变化（青灰色还是黄色？）\n"
        response += "   - 枯死的速度（几天内还是逐渐的？）\n"
        response += "   - 根系和茎基部的状态\n"
        response += "2. 描述发病的环境条件（是否高温多雨？）\n"
        response += "3. 田间管理情况（是否连作？排水如何？）\n\n"
        response += "**根腐病典型症状提示**:\n"
        response += "- **青枯型**: 植株迅速失水变青灰色，如被开水烫过\n"
        response += "- **黄枯型**: 叶片逐片变黄，过程相对缓慢\n"
        response += "- **共同特征**: 根系变褐腐烂，茎基部疏松中空\n"
    
    history.append({"role": "assistant", "content": response})
    
    # 如果有症状匹配，也显示图像
    if matched_keywords:
        # 查找参考图片
        image_files = []
        if os.path.exists(IMAGE_PATH):
            for f in os.listdir(IMAGE_PATH):
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                    image_files.append(os.path.join(IMAGE_PATH, f))
        
        if image_files:
            return history, "", gr.update(visible=True, value=image_files)
    
    return history, "", gr.update()

def get_detailed_info(history: list):
    """获取根腐病的详细信息"""
    history = history or []
    
    history.append({"role": "user", "content": "查看根腐病详细信息"})
    
    entry = get_knowledge_entry(ROOT_DISEASE_CATEGORY, ROOT_DISEASE_CATEGORY)
    if not entry:
        response = "抱歉，无法获取根腐病的详细信息。"
        history.append({"role": "assistant", "content": response})
        return history, gr.update()
    
    symptoms = entry.get('核心症状', '无详细症状描述。')
    occurrence = entry.get('发生规律', '无相关发生规律信息。')
    
    response = f"## 📋 {ROOT_DISEASE_CATEGORY} 完整信息\n\n"
    response += f"### **核心症状**\n{symptoms}\n\n"
    response += f"### **发生规律**\n{occurrence}\n\n"
    response += "---\n\n"
    response += "**田间诊断要点**:\n"
    response += "1. **关键时期**: 玉米灌浆至乳熟期（8-9月）\n"
    response += "2. **典型症状**: 植株从上至下快速枯死（青枯型）或叶片逐片变黄（黄枯型）\n"
    response += "3. **确诊方法**: 拔起病株检查根系和茎基部腐烂情况\n"
    response += "4. **环境条件**: 前期干旱后期多雨，雨后骤晴易发病\n\n"
    response += "**防治建议**:\n"
    response += "- 避免连作，实行轮作\n"
    response += "- 改善田间排水，避免积水\n"
    response += "- 合理施肥，增强植株抗病性\n"
    response += "- 及时清除病残体\n\n"
    response += "💡 如果您想分析具体症状，请在上方文本框中描述您观察到的症状。"
    
    history.append({"role": "assistant", "content": response})
    
    # 查找参考图片 - 显示所有图像文件
    image_files = []
    if os.path.exists(IMAGE_PATH):
        for f in os.listdir(IMAGE_PATH):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                image_files.append(os.path.join(IMAGE_PATH, f))
    
    if image_files:
        return history, gr.update(visible=True, value=image_files)
    else:
        return history, gr.update()

def reset_root_conversation():
    """重置对话"""
    return [], "", gr.update()

def create_root_expert_interface():
    with gr.Blocks(analytics_enabled=False) as interface:
        # 添加专家系统标题
        gr.HTML("""
        <div style="background: linear-gradient(135deg, #795548, #5D4037); color: white; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700;">🌱 玉米根部病害诊断专家</h2>
            <p style="margin: 8px 0 0 0; font-size: 1.1rem; opacity: 0.9;">根部病害症状分析与诊断指导系统</p>
        </div>
        """)
        
        # 功能介绍卡片 - 棕色主题
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="hover-card" style="background: linear-gradient(135deg, #EFEBE9, #D7CCC8); border: 1px solid #BCAAA4; border-radius: 10px; padding: 15px; margin: 10px 0; text-align: center; transition: all 0.3s ease; cursor: pointer;">
                    <h4 style="color: #5D4037; margin: 0 0 10px 0;">🔍 智能症状识别</h4>
                    <p style="margin: 0; font-size: 0.9rem;">植株枯死深度分析<br>根系病变状态诊断<br>AI智能匹配病害类型</p>
                </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="hover-card" style="background: linear-gradient(135deg, #EFEBE9, #D7CCC8); border: 1px solid #BCAAA4; border-radius: 10px; padding: 15px; margin: 10px 0; text-align: center; transition: all 0.3s ease; cursor: pointer;">
                    <h4 style="color: #5D4037; margin: 0 0 10px 0;">📋 专业诊断指导</h4>
                    <p style="margin: 0; font-size: 0.9rem;">发病规律科学解析<br>防治措施精准建议<br>田间管理要点指导</p>
                </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="hover-card" style="background: linear-gradient(135deg, #EFEBE9, #D7CCC8); border: 1px solid #BCAAA4; border-radius: 10px; padding: 15px; margin: 10px 0; text-align: center; transition: all 0.3s ease; cursor: pointer;">
                    <h4 style="color: #5D4037; margin: 0 0 10px 0;">🎯 病害类型覆盖</h4>
                    <p style="margin: 0; font-size: 0.9rem;">青枯型根腐识别<br>黄枯型根腐诊断<br>综合性症状分析</p>
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
                    placeholder="请详细描述您观察到的症状，例如：'玉米植株叶片迅速变青灰色，根系变褐腐烂'",
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
                
                gr.Markdown("### 📚 详细信息")
                detail_btn = gr.Button(
                    "📋 查看根腐病完整信息", 
                    variant="secondary",
                    size="lg"
                )

                gr.Markdown("### 📚 专业信息查询")
                gr.HTML("""
                <div style="background: linear-gradient(135deg, #EFEBE9, #D7CCC8); border: 1px solid #BCAAA4; border-radius: 8px; padding: 12px; margin: 10px 0;">
                    <h5 style="color: #5D4037; margin: 0 0 8px 0;">🔍 诊断要点</h5>
                    <ul style="margin: 0; padding-left: 16px; color: #5D4037; font-size: 0.85rem;">
                        <li><strong>青枯型</strong>：急性枯死，青灰色</li>
                        <li><strong>黄枯型</strong>：慢性枯死，逐片变黄</li>
                        <li><strong>根系检查</strong>：变褐腐烂程度</li>
                        <li><strong>环境因素</strong>：雨后骤晴易发</li>
                    </ul>
                </div>
                """)
        
        # 图片展示区域
        gr.Markdown("### 📸 参考图片")
        gallery = gr.Gallery(
            label="典型根腐病症状对比", 
            visible=True,
            columns=2, 
            object_fit="contain", 
            height=500
        )
        
        # 使用提示
        gr.HTML("""
        <div style="background: linear-gradient(135deg, #FFF3E0, #FFE0B2); border: 1px solid #FFCC02; border-radius: 10px; padding: 15px; margin: 20px 0;">
            <h4 style="color: #E65100; margin: 0 0 10px 0;">💡 诊断要点提示</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div>
                    <h5 style="color: #BF360C; margin: 0 0 5px 0;">🔍 重点观察部位：</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #BF360C; font-size: 0.9rem;">
                        <li><strong>叶片变化</strong>：青灰色/黄色枯死症状</li>
                        <li><strong>根系状态</strong>：变褐/腐烂程度检查</li>
                        <li><strong>茎基部</strong>：是否疏松中空现象</li>
                        <li><strong>枯死速度</strong>：急性/慢性发病特征</li>
                    </ul>
                </div>
                <div>
                    <h5 style="color: #BF360C; margin: 0 0 5px 0;">🎯 关键词提示：</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #BF360C; font-size: 0.9rem;">
                        <li><strong>青枯型</strong>：急性、青灰、失水、短时间</li>
                        <li><strong>黄枯型</strong>：慢性、逐片、变黄、缓慢</li>
                        <li><strong>根部症状</strong>：变褐、腐烂、易拔起</li>
                        <li><strong>环境因素</strong>：连作、多雨、雨后骤晴</li>
                    </ul>
                </div>
            </div>
            <div style="margin-top: 10px; padding: 8px; background: rgba(121, 85, 72, 0.1); border-radius: 6px;">
                <p style="margin: 0; font-size: 0.85rem; color: #5D4037;"><strong>诊断要点</strong>：根腐病诊断需要结合地上部症状和地下部根系状态，重点关注发病时期和环境条件。</p>
            </div>
        </div>
        """)
        
        # 事件绑定
        analyze_btn.click(
            fn=analyze_root_symptoms,
            inputs=[symptoms_input, chatbot],
            outputs=[chatbot, symptoms_input, gallery]
        )
        
        symptoms_input.submit(
            fn=analyze_root_symptoms,
            inputs=[symptoms_input, chatbot],
            outputs=[chatbot, symptoms_input, gallery]
        )
        
        detail_btn.click(
            fn=get_detailed_info,
            inputs=[chatbot],
            outputs=[chatbot, gallery]
        )
        
        reset_btn.click(
            fn=reset_root_conversation,
            inputs=[],
            outputs=[chatbot, symptoms_input, gallery]
        )
        
    return interface
