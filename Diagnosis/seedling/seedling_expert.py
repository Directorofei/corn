import gradio as gr
import os
from utils.knowledge_loader import get_sub_types, get_knowledge_entry

# 定义该专家系统对应的知识库条目和图片路径
SEEDLING_DISEASE_CATEGORY = "苗枯病"
IMAGE_PATH = "seedling/images"

def get_seedling_disease_list():
    """获取所有苗期病害的亚类列表"""
    subtypes = get_sub_types(SEEDLING_DISEASE_CATEGORY)
    return subtypes if subtypes else [SEEDLING_DISEASE_CATEGORY]

def analyze_seedling_symptoms(symptoms_input: str, history: list):
    """分析用户输入的苗期症状并提供诊断建议"""
    history = history or []
    
    if not symptoms_input or not symptoms_input.strip():
        history.append({"role": "assistant", "content": "请描述您观察到的苗期症状，我将根据描述帮您分析可能的病害。"})
        return history, ""
    
    history.append({"role": "user", "content": symptoms_input})
    
    # 获取苗枯病信息
    entry = get_knowledge_entry(SEEDLING_DISEASE_CATEGORY, SEEDLING_DISEASE_CATEGORY)
    if not entry:
        history.append({"role": "assistant", "content": "抱歉，无法获取苗期病害信息。"})
        return history, ""
    
    symptoms_lower = symptoms_input.lower().strip()
    
    # 苗枯病关键词匹配
    keyword_matches = []
    matched_keywords = []
    
    # 关键词分析 - 大幅扩展关键词范围
    keywords = {
        '烂种': ['烂种', '种子', '腐烂', '不出苗', '缺苗', '断垄', '萌发', '烂籽', '坏种', '种烂', '籽烂', '种子烂', '种腐', '没出苗', '出不了苗', '苗不齐', '苗不全', '缺株', '断行', '发芽', '出芽', '萌芽'],
        '芽腐': ['芽腐', '幼芽', '出土前', '变褐', '腐烂', '死亡', '芽烂', '芽坏', '芽死', '嫩芽', '小芽', '出土', '露土', '破土', '褐色', '棕色', '暗色', '腐败', '烂掉', '坏死', '死掉'],
        '苗枯': ['苗枯', '幼苗', '出土后', '心叶', '萎蔫', '干枯', '死亡', '苗死', '苗坏', '苗烂', '小苗', '嫩苗', '出苗', '露苗', '心叶', '中心叶', '萎缩', '枯萎', '干死', '枯死', '死苗', '坏苗'],
        '根部症状': ['根系', '根部', '褐色', '暗褐色', '腐烂', '根子', '根茎', '根须', '棕色', '暗色', '腐败', '烂根', '坏根', '根烂', '根坏', '根死', '根变'],
        '茎基部症状': ['茎基部', '水渍状', '淡褐色', '黄褐色', '软化', '坏死', '变细', '茎基', '基部', '茎部', '杆基', '秆基', '水浸', '湿润', '褐色', '棕色', '软烂', '软化', '变软', '细化', '变瘦', '死亡', '坏死'],
        '地上部症状': ['叶片', '变黄', '干枯', '整株死亡', '容易拔起', '叶子', '叶', '发黄', '黄化', '黄叶', '叶黄', '枯干', '干燥', '枯萎', '萎蔫', '全株', '整个', '整棵', '拔出', '松动', '不牢', '易拔'],
        '发病条件': ['低温', '高湿', '倒春寒', '地温低', '阴雨', '土壤湿', '通气性差', '播种深', '覆土厚', '温度低', '气温低', '冷', '寒', '湿度大', '潮湿', '水分多', '春寒', '降温', '土温', '地温', '雨天', '下雨', '降雨', '雨季', '土湿', '土壤水分', '透气差', '不透气', '种深', '播深', '埋深', '土厚', '盖土厚']
    }
    
    # 扩展匹配 - 增加容错匹配
    extended_keywords = {
        '病害通用词汇': ['病', '坏', '烂', '死', '枯', '萎', '变', '问题', '不好', '异常', '发病', '生病', '感染', '病变', '有病', '不对', '奇怪', '怪异', '不正常'],
        '颜色变化': ['黄', '褐', '棕', '灰', '黑', '暗', '变色', '颜色', '色变', '发黄', '发褐', '发黑', '发灰', '变暗'],
        '质地变化': ['软', '硬', '烂', '腐', '变质', '软化', '硬化', '腐烂', '腐败', '变软', '变硬', '质变'],
        '生长状态': ['枯死', '枯萎', '萎蔫', '死亡', '坏死', '腐烂', '腐败', '变质', '干枯', '干燥', '失水', '脱水', '萎缩', '凋谢', '凋萎', '不长', '长不好', '生长差'],
        '环境因子': ['温度', '湿度', '水分', '土壤', '天气', '气候', '环境', '条件', '冷', '热', '湿', '干', '雨', '晴', '阴', '风']
    }
    
    for category, category_keywords in keywords.items():
        for keyword in category_keywords:
            if keyword in symptoms_lower:
                if category not in keyword_matches:
                    keyword_matches.append(category)
                matched_keywords.append(keyword)
    
    # 检查扩展关键词
    for category, category_keywords in extended_keywords.items():
        for keyword in category_keywords:
            if keyword in symptoms_lower:
                if category not in keyword_matches:
                    keyword_matches.append(category)
                matched_keywords.append(keyword)
    
    # 生成诊断报告
    response = "## 🔍 苗期病害症状分析\n\n"
    
    if matched_keywords:
        response += f"根据您描述的症状\"**{symptoms_input}**\"，我分析出以下特征：\n\n"
        
        # 根据匹配的关键词给出诊断建议
        if any(kw in matched_keywords for kw in ['烂种', '种子', '不出苗', '缺苗']):
            response += "### 🚨 疑似烂种\n\n"
            response += "**特征匹配**: 您的描述符合烂种症状\n"
            response += "**主要特征**: 种子在萌发前就被病菌侵染腐烂，导致无法出苗\n\n"
        elif any(kw in matched_keywords for kw in ['芽腐', '幼芽', '出土前', '变褐']):
            response += "### ⚠️ 疑似芽腐\n\n"
            response += "**特征匹配**: 您的描述符合芽腐症状\n"
            response += "**主要特征**: 种子萌发但幼芽在出土前变褐腐烂死亡\n\n"
        elif any(kw in matched_keywords for kw in ['苗枯', '幼苗', '出土后', '心叶']):
            response += "### 💡 疑似苗枯\n\n"
            response += "**特征匹配**: 您的描述符合苗枯症状\n"
            response += "**主要特征**: 幼苗出土后根茎腐烂，叶片萎蔫干枯\n\n"
        else:
            response += "### 🔍 苗枯病相关症状\n\n"
            response += "**匹配特征**: " + ", ".join(matched_keywords) + "\n\n"
        
        # 添加完整的病害信息
        symptoms = entry.get('核心症状', '无详细症状描述。')
        occurrence = entry.get('发生规律', '无相关发生规律信息。')
        
        response += f"**完整症状对比**:\n{symptoms}\n\n"
        response += f"**发生规律参考**:\n{occurrence}\n\n"
        
        response += "---\n\n"
        response += "**诊断建议**:\n"
        response += "1. 检查种子质量和处理情况\n"
        response += "2. 观察田间地温和土壤湿度\n"
        response += "3. 检查播种深度和覆土厚度\n"
        response += "4. 注意近期的天气变化（是否有倒春寒）\n\n"
        
        # 根据症状类型给出具体建议
        if any(kw in matched_keywords for kw in ['低温', '倒春寒', '地温低']):
            response += "**环境因子分析**:\n"
            response += "- 低温是苗期病害的主要诱因\n"
            response += "- 建议等待地温回升后再补种\n"
            response += "- 考虑使用地膜覆盖提高地温\n"
        
        if any(kw in matched_keywords for kw in ['高湿', '土壤湿', '阴雨']):
            response += "**湿度管理建议**:\n"
            response += "- 及时排水，避免田间积水\n"
            response += "- 适当控制灌溉，待土壤稍干后再灌\n"
            response += "- 增加田间通风，降低湿度\n"
        
    else:
        response += "暂时无法根据您的描述确定具体的病害类型。\n\n"
        response += "**建议**:\n"
        response += "1. 请尝试更详细地描述症状，如：\n"
        response += "   - 是否出苗？（烂种、芽腐、苗枯的区别）\n"
        response += "   - 幼苗的根系和茎基部状态\n"
        response += "   - 叶片的颜色和萎蔫程度\n"
        response += "2. 描述环境条件：\n"
        response += "   - 播种时的土壤温度和湿度\n"
        response += "   - 近期天气情况（是否有倒春寒、连续阴雨等）\n"
        response += "3. 田间管理情况：\n"
        response += "   - 播种深度和覆土厚度\n"
        response += "   - 种子处理情况\n"
        response += "   - 田间排水状况\n\n"
        response += "**苗枯病典型症状提示**:\n"
        response += "- **烂种**: 种子萌发前腐烂，无法出苗\n"
        response += "- **芽腐**: 种子萌发但幼芽出土前腐烂\n"
        response += "- **苗枯**: 幼苗出土后根茎腐烂，叶片萎蔫干枯\n"
    
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

def get_seedling_detailed_info(history: list):
    """获取苗枯病的详细信息"""
    history = history or []
    
    history.append({"role": "user", "content": "查看苗枯病详细信息"})
    
    entry = get_knowledge_entry(SEEDLING_DISEASE_CATEGORY, SEEDLING_DISEASE_CATEGORY)
    if not entry:
        response = "抱歉，无法获取苗枯病的详细信息。"
        history.append({"role": "assistant", "content": response})
        return history, gr.update()
    
    symptoms = entry.get('核心症状', '无详细症状描述。')
    occurrence = entry.get('发生规律', '无相关发生规律信息。')
    
    response = f"## 📋 {SEEDLING_DISEASE_CATEGORY} 完整信息\n\n"
    response += f"### **核心症状**\n{symptoms}\n\n"
    response += f"### **发生规律**\n{occurrence}\n\n"
    response += "---\n\n"
    response += "**田间诊断要点**:\n"
    response += "1. **关键时期**: 玉米播种至5叶期前\n"
    response += "2. **典型症状**: 根据发病阶段分为烂种、芽腐、苗枯三种类型\n"
    response += "3. **确诊方法**: 挖取种子或幼苗检查腐烂情况\n"
    response += "4. **环境条件**: 低温高湿，尤其是倒春寒天气\n\n"
    response += "**预防措施**:\n"
    response += "- 选择抗病品种和优质种子\n"
    response += "- 种子包衣或药剂处理\n"
    response += "- 适期播种，避免过早播种\n"
    response += "- 合理播种深度，一般2-3cm\n"
    response += "- 改善田间排水，避免积水\n"
    response += "- 使用地膜覆盖提高地温\n\n"
    response += "**补救措施**:\n"
    response += "- 及时排水降湿\n"
    response += "- 缺苗严重时适时补种\n"
    response += "- 叶面喷施叶面肥增强抗性\n\n"
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

def reset_seedling_conversation():
    """重置对话"""
    return [], "", gr.update()

def create_seedling_expert_interface():
    with gr.Blocks(analytics_enabled=False) as interface:
        # 添加专家系统标题
        gr.HTML("""
        <div style="background: linear-gradient(135deg, #2196F3, #1976D2); color: white; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700;">🌿 玉米苗期病害诊断专家</h2>
            <p style="margin: 8px 0 0 0; font-size: 1.1rem; opacity: 0.9;">苗期病害早期识别与防治指导系统</p>
        </div>
        """)
        
        # 功能介绍卡片 - 蓝色主题
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="hover-card" style="background: linear-gradient(135deg, #E3F2FD, #BBDEFB); border: 1px solid #90CAF9; border-radius: 10px; padding: 15px; margin: 10px 0; text-align: center; transition: all 0.3s ease; cursor: pointer;">
                    <h4 style="color: #1976D2; margin: 0 0 10px 0;">🔍 智能早期诊断</h4>
                    <p style="margin: 0; font-size: 0.9rem;">烂种、芽腐症状分析<br>苗枯病害类型判定<br>AI智能匹配诊断系统</p>
                </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="hover-card" style="background: linear-gradient(135deg, #E3F2FD, #BBDEFB); border: 1px solid #90CAF9; border-radius: 10px; padding: 15px; margin: 10px 0; text-align: center; transition: all 0.3s ease; cursor: pointer;">
                    <h4 style="color: #1976D2; margin: 0 0 10px 0;">🌡️ 环境因素分析</h4>
                    <p style="margin: 0; font-size: 0.9rem;">温湿度影响深度评估<br>播种条件科学诊断<br>环境防控措施建议</p>
                </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="hover-card" style="background: linear-gradient(135deg, #E3F2FD, #BBDEFB); border: 1px solid #90CAF9; border-radius: 10px; padding: 15px; margin: 10px 0; text-align: center; transition: all 0.3s ease; cursor: pointer;">
                    <h4 style="color: #1976D2; margin: 0 0 10px 0;">🛡️ 综合防治方案</h4>
                    <p style="margin: 0; font-size: 0.9rem;">种子处理核心技术<br>田间管理专业指导<br>补救措施精准建议</p>
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
                    placeholder="请详细描述您观察到的症状，例如：'种子不出苗，挖出来发现变黑腐烂'",
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
                
                gr.Markdown("### 📚 专业信息查询")
                detail_btn = gr.Button(
                    "📋 查看苗枯病完整信息", 
                    variant="secondary",
                    size="lg"
                )
        
        # 图片展示区域
        gr.Markdown("### 📸 参考图片")
        gallery = gr.Gallery(
            label="典型苗期病害症状对比", 
            visible=True,
            columns=2, 
            object_fit="contain", 
            height=500
        )
        
        # 使用提示
        gr.HTML("""
        <div style="background: linear-gradient(135deg, #FFF3E0, #FFE0B2); border: 1px solid #FFCC02; border-radius: 10px; padding: 15px; margin: 20px 0;">
            <h4 style="color: #E65100; margin: 0 0 10px 0;">💡 苗期诊断要点</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div>
                    <h5 style="color: #BF360C; margin: 0 0 5px 0;">症状分类：</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #BF360C; font-size: 0.9rem;">
                        <li><strong>烂种</strong>：种子萌发前腐烂，无法出苗</li>
                        <li><strong>芽腐</strong>：幼芽出土前变褐腐烂死亡</li>
                        <li><strong>苗枯</strong>：幼苗出土后根茎腐烂</li>
                        <li>描述时请注明发病阶段和部位</li>
                    </ul>
                </div>
                <div>
                    <h5 style="color: #BF360C; margin: 0 0 5px 0;">环境因素：</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #BF360C; font-size: 0.9rem;">
                        <li><strong>温度</strong>：低温、倒春寒影响</li>
                        <li><strong>湿度</strong>：土壤过湿、排水不良</li>
                        <li><strong>播种</strong>：深度过深、覆土过厚</li>
                        <li><strong>种子</strong>：质量、处理情况</li>
                    </ul>
                </div>
            </div>
            <div style="margin-top: 10px; padding: 8px; background: rgba(33, 150, 243, 0.1); border-radius: 6px;">
                <p style="margin: 0; font-size: 0.85rem; color: #1565C0;"><strong>提示</strong>：苗期病害多与播种条件和天气变化密切相关，描述时请包含播种时间、土壤条件、天气情况等信息。</p>
            </div>
        </div>
        """)
        
        # 事件绑定
        analyze_btn.click(
            fn=analyze_seedling_symptoms,
            inputs=[symptoms_input, chatbot],
            outputs=[chatbot, symptoms_input, gallery]
        )
        
        symptoms_input.submit(
            fn=analyze_seedling_symptoms,
            inputs=[symptoms_input, chatbot],
            outputs=[chatbot, symptoms_input, gallery]
        )
        
        detail_btn.click(
            fn=get_seedling_detailed_info,
            inputs=[chatbot],
            outputs=[chatbot, gallery]
        )
        
        reset_btn.click(
            fn=reset_seedling_conversation,
            inputs=[],
            outputs=[chatbot, symptoms_input, gallery]
        )
        
    return interface
