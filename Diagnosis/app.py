import gradio as gr
from pathlib import Path

# 导入我们的专家系统模块
from leaf.leaf_expert import create_leaf_expert_interface
from pests.pest_expert import create_pest_expert_interface
from stem.stem_expert import create_stem_expert_interface
from root.root_expert import create_root_expert_interface
from seedling.seedling_expert import create_seedling_expert_interface
from utils.knowledge_loader import load_knowledge_base

# 在应用启动时加载知识库，确保所有模块都能访问到
load_knowledge_base()

# 现代化CSS样式 - 包含全面的前端优化
custom_css = """
/* 全局背景优化 - 修复动画显示，中性蓝灰色系 */
body, html {
    background: linear-gradient(-45deg, #9db4c6, #b5c7d1, #c8d4db, #d1dae0, #bac8d3, #a6b8c8) !important;
    background-size: 400% 400% !important;
    animation: gradientBG 20s ease infinite !important;
    margin: 0 !important;
    padding: 0 !important;
    min-height: 100vh !important;
}

/* 强制为Gradio应用背景动画 */
#root, .gradio-container, .gradio-container > div {
    background: transparent !important;
}

/* 确保动画容器覆盖整个界面 */
.gradio-container::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(-45deg, #9db4c6, #b5c7d1, #c8d4db, #d1dae0, #bac8d3, #a6b8c8);
    background-size: 400% 400%;
    animation: gradientBG 20s ease infinite;
    z-index: -1;
}

@keyframes gradientBG {
    0% {
        background-position: 0% 50%;
    }
    25% {
        background-position: 100% 50%;
    }
    50% {
        background-position: 100% 100%;
    }
    75% {
        background-position: 0% 100%;
    }
    100% {
        background-position: 0% 50%;
    }
}

/* 全局样式 */
* {
    box-sizing: border-box;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.gradio-container {
    max-width: 1400px !important;
    margin: 0 auto !important;
    background: rgba(255, 255, 255, 0.95) !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    min-height: 100vh;
    padding: 20px !important;
    backdrop-filter: blur(10px);
    box-shadow: 0 0 40px rgba(0, 0, 0, 0.1) !important;
    border-radius: 20px !important;
    margin-top: 20px !important;
    margin-bottom: 20px !important;
}

/* 主标题样式 - 现代化卡片设计 */
.main-header {
    background: linear-gradient(135deg, #4CAF50, #2E7D32) !important;
    color: white !important;
    padding: 30px !important;
    text-align: center !important;
    border-radius: 16px !important;
    margin-bottom: 30px !important;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08) !important;
    position: relative;
    overflow: hidden;
    animation: fadeInUp 0.6s ease-out;
}

.main-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: shimmer 3s infinite;
}

.main-header h1 {
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3) !important;
}

.main-header p {
    font-size: 1.1rem !important;
    margin: 10px 0 0 0 !important;
    opacity: 0.9 !important;
}

/* 导航栏样式增强 */
.tab-nav {
    background: rgba(255, 255, 255, 0.95) !important;
    border-radius: 16px !important;
    padding: 8px !important;
    margin-bottom: 25px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
    backdrop-filter: blur(10px) !important;
}

.tab-nav button {
    background: transparent !important;
    border: 2px solid transparent !important;
    border-radius: 12px !important;
    padding: 16px 24px !important;
    margin: 4px !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    color: #495057 !important;
    transition: all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    cursor: pointer !important;
    position: relative !important;
    overflow: hidden !important;
}

.tab-nav button:hover {
    transform: translateY(-6px) scale(1.05) !important;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15) !important;
    background: rgba(255, 255, 255, 0.9) !important;
    border-color: #007bff !important;
}

.tab-nav button.selected {
    background: linear-gradient(135deg, #007bff, #0056b3) !important;
    color: white !important;
    border-color: #007bff !important;
    box-shadow: 0 8px 25px rgba(0, 123, 255, 0.3) !important;
}

.tab-nav button.selected:hover {
    transform: translateY(-6px) scale(1.05) !important;
    box-shadow: 0 12px 35px rgba(0, 123, 255, 0.4) !important;
}

/* 内容区域样式 */
.tab-content {
    background: white !important;
    border-radius: 12px !important;
    padding: 20px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05) !important;
    margin-top: 20px !important;
    border: 1px solid #e9ecef !important;
}

/* 现代化按钮样式 */
.btn-primary {
    background: linear-gradient(135deg, #007bff, #0056b3) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 28px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    color: white !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 2px 12px rgba(0, 123, 255, 0.25) !important;
    position: relative;
    overflow: hidden;
    min-height: 48px;
}

.btn-primary::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    transition: width 0.6s, height 0.6s;
}

.btn-primary:active::before {
    width: 300px;
    height: 300px;
}

.btn-primary:hover {
    background: linear-gradient(135deg, #0056b3, #004085) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 16px rgba(0, 123, 255, 0.35) !important;
}

.btn-secondary {
    background: linear-gradient(135deg, #6c757d, #5a6268) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    color: white !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 2px 12px rgba(108, 117, 125, 0.25) !important;
    position: relative;
    overflow: hidden;
    min-height: 48px;
}

.btn-secondary::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    transition: width 0.6s, height 0.6s;
}

.btn-secondary:active::before {
    width: 300px;
    height: 300px;
}

.btn-secondary:hover {
    background: linear-gradient(135deg, #5a6268, #495057) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 16px rgba(108, 117, 125, 0.35) !important;
}

/* 现代化输入框样式 */
.input-text {
    border: 2px solid rgba(224, 224, 224, 0.6) !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    font-size: 1rem !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    background: rgba(255, 255, 255, 0.95) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    backdrop-filter: blur(10px);
}

.input-text:focus {
    border-color: #4CAF50 !important;
    box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1), 0 2px 12px rgba(0, 0, 0, 0.1) !important;
    outline: none !important;
    transform: translateY(-1px) !important;
}

/* 现代化聊天框样式 */
.chat-container {
    border: 1px solid rgba(232, 245, 232, 0.6) !important;
    border-radius: 16px !important;
    background: rgba(255, 255, 255, 0.95) !important;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08) !important;
    backdrop-filter: blur(10px);
    animation: fadeInUp 0.6s ease-out 0.2s both;
}

/* 现代化图片库样式 */
.image-gallery {
    border: 1px solid rgba(232, 245, 232, 0.6) !important;
    border-radius: 16px !important;
    background: rgba(255, 255, 255, 0.95) !important;
    padding: 20px !important;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08) !important;
    backdrop-filter: blur(10px);
    animation: fadeInUp 0.6s ease-out 0.3s both;
}

.image-gallery img {
    border-radius: 8px !important;
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
}

.image-gallery img:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15) !important;
}

/* 现代化卡片样式 */
.info-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(248, 249, 250, 0.9)) !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    border-radius: 12px !important;
    padding: 18px !important;
    margin: 12px 0 !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
    backdrop-filter: blur(10px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    animation: fadeInUp 0.6s ease-out both;
}

.info-card:hover {
    transform: translateY(-3px) scale(1.005) !important;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15) !important;
    border-color: #007bff !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .gradio-container {
        max-width: 100% !important;
        margin: 0 !important;
        padding: 10px !important;
    }
    
    .main-header h1 {
        font-size: 2rem !important;
    }
    
    .tab-nav button {
        padding: 10px 15px !important;
        font-size: 0.9rem !important;
    }
}

/* 动画效果 */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeIn 0.5s ease-out !important;
}

/* 增强的hover效果 */
.info-card {
    transition: all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    cursor: pointer !important;
    position: relative !important;
    overflow: hidden !important;
}

.info-card:hover {
    transform: translateY(-8px) scale(1.015) !important;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15) !important;
    border-color: #007bff !important;
}

.info-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transition: left 0.8s;
}

.info-card:hover::before {
    left: 100%;
}

.hover-card {
    transition: all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    cursor: pointer !important;
    position: relative !important;
    overflow: hidden !important;
}

.hover-card:hover {
    transform: translateY(-3px) scale(1.005) !important;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.10) !important;
    filter: brightness(1.05) !important;
}

.hover-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
    transition: left 0.8s;
}

.hover-card:hover::before {
    left: 100%;
}

/* 专家系统图标 */
.expert-icon {
    font-size: 2rem !important;
    margin-right: 10px !important;
    vertical-align: middle !important;
}

/* 状态指示器 */
.status-indicator {
    display: inline-block !important;
    width: 12px !important;
    height: 12px !important;
    border-radius: 50% !important;
    margin-right: 8px !important;
    animation: pulse 2s infinite;
}

.status-online {
    background: #4CAF50 !important;
    box-shadow: 0 0 8px rgba(76, 175, 80, 0.5) !important;
}

.status-processing {
    background: #FF9800 !important;
    box-shadow: 0 0 8px rgba(255, 152, 0, 0.5) !important;
}

/* 进度指示器 */
.progress-container {
    width: 100%;
    height: 4px;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 2px;
    overflow: hidden;
    margin: 10px 0;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #4CAF50, #2E7D32);
    border-radius: 2px;
    animation: progress 2s ease-in-out infinite;
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-left: 4px solid #4CAF50;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 20px auto;
}

/* 动画关键帧 */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes shimmer {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

@keyframes progress {
    0% { width: 0%; }
    50% { width: 100%; }
    100% { width: 0%; }
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (min-width: 1600px) {
    .gradio-container {
        max-width: 1600px !important;
    }
}

@media (min-width: 1920px) {
    .gradio-container {
        max-width: 1800px !important;
    }
}

/* 移动端响应式 */
@media (max-width: 768px) {
    .gradio-container {
        max-width: 100% !important;
        margin: 10px !important;
        padding: 15px !important;
        border-radius: 15px !important;
    }
    
    .main-header {
        padding: 20px !important;
    }
    
    .main-header h1 {
        font-size: 1.8rem !important;
    }
    
    .tab-nav {
        padding: 10px !important;
    }
    
    .tab-nav button {
        padding: 12px 16px !important;
        font-size: 0.9rem !important;
        margin: 2px !important;
        min-height: 44px !important;
    }
    
    .btn-primary, .btn-secondary {
        padding: 12px 20px !important;
        font-size: 1rem !important;
        min-height: 44px !important;
    }
    
    .input-text {
        padding: 12px 16px !important;
        font-size: 1rem !important;
    }
    
    .info-card {
        padding: 15px !important;
        margin: 10px 0 !important;
    }
}

@media (max-width: 480px) {
    .main-header h1 {
        font-size: 1.5rem !important;
    }
    
    .tab-nav button {
        padding: 10px 12px !important;
        font-size: 0.8rem !important;
        min-height: 40px !important;
    }
    
    .btn-primary, .btn-secondary {
        padding: 10px 16px !important;
        font-size: 0.9rem !important;
        min-height: 40px !important;
    }
}

/* 可访问性优化 */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}

/* 焦点指示器 */
button:focus,
input:focus,
textarea:focus,
select:focus {
    outline: 2px solid #4CAF50 !important;
    outline-offset: 2px !important;
}

/* 高对比度模式支持 */
@media (prefers-contrast: high) {
    .info-card {
        border: 2px solid #2E7D32 !important;
    }
    
    .btn-primary, .btn-secondary {
        border: 2px solid transparent !important;
    }
    
    .input-text {
        border: 2px solid #2E7D32 !important;
    }
}

/* 减少动画偏好支持 */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* 打字机效果 */
.typewriter {
    overflow: hidden;
    border-right: 2px solid #4CAF50;
    white-space: nowrap;
    margin: 0 auto;
    letter-spacing: 0.1em;
    animation: typing 3.5s steps(40, end), blink-caret 0.75s step-end infinite;
}

@keyframes typing {
    from { width: 0; }
    to { width: 100%; }
}

@keyframes blink-caret {
    from, to { border-color: transparent; }
    50% { border-color: #4CAF50; }
}
"""

def create_welcome_interface():
    """创建欢迎界面"""
    with gr.Blocks() as welcome:
        gr.HTML("""
        <div class="main-header fade-in">
            <h1>🌽 玉米病虫害诊断智能体</h1>
            <p>基于AI技术的专业玉米病虫害识别与诊断系统</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="info-card" style="background: linear-gradient(135deg, #E8F5E8, #C8E6C9); border: 1px solid #A5D6A7; border-left: 4px solid #4CAF50;">
                    <h3 style="color: #2E7D32;">🔬 专业诊断</h3>
                    <p style="color: #388E3C;">采用先进的深度学习技术，结合专业农业知识，为您提供准确的病虫害诊断服务。</p>
                </div>
                """)
                
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="info-card" style="background: linear-gradient(135deg, #E3F2FD, #BBDEFB); border: 1px solid #90CAF9; border-left: 4px solid #2196F3;">
                    <h3 style="color: #1976D2;">🎯 多维分析</h3>
                    <p style="color: #1565C0;">涵盖叶片、根部、茎穗、苗期等多个部位，以及主要害虫的全面诊断分析。</p>
                </div>
                """)
                
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="info-card" style="background: linear-gradient(135deg, #FFF3E0, #FFE0B2); border: 1px solid #FFCC02; border-left: 4px solid #FF9800;">
                    <h3 style="color: #E65100;">📊 详细报告</h3>
                    <p style="color: #EF6C00;">提供详细的病害信息、发生规律、防治建议等专业指导内容。</p>
                </div>
                """)
        
        gr.HTML("""
        <div class="info-card" style="margin-top: 20px; background: linear-gradient(135deg, #F3E5F5, #E1BEE7); border: 1px solid #CE93D8; border-left: 4px solid #9C27B0;">
            <h3 style="color: #7B1FA2;">🚀 使用指南</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 15px;">
                <div style="background: linear-gradient(135deg, #E8F5E8, #C8E6C9); border: 1px solid #A5D6A7; border-radius: 8px; padding: 15px; border-left: 4px solid #4CAF50;">
                    <h4 style="color: #2E7D32;">🍃 叶片病害诊断</h4>
                    <p style="color: #388E3C;">• 上传玉米叶片照片进行AI识别<br>• 支持斑病、锈病、健康状态判断<br>• 提供详细的病害信息和防治建议</p>
                </div>
                <div style="background: linear-gradient(135deg, #FFF3E0, #FFE0B2); border: 1px solid #FFCC02; border-radius: 8px; padding: 15px; border-left: 4px solid #FF9800;">
                    <h4 style="color: #E65100;">🐛 害虫诊断</h4>
                    <p style="color: #EF6C00;">• 上传害虫照片进行识别<br>• 支持粘虫、玉米螟、蓟马等<br>• 提供害虫生活习性和防治方法</p>
                </div>
                <div style="background: linear-gradient(135deg, #F5F7FA, #E8EAF6); border: 1px solid #B0BEC5; border-radius: 8px; padding: 15px; border-left: 4px solid #546E7A;">
                    <h4 style="color: #37474F;">🌾 茎穗病害诊断</h4>
                    <p style="color: #455A64;">• 描述症状进行智能分析<br>• 支持丝黑穗病、瘤黑粉病<br>• 提供典型病例图片对比</p>
                </div>
                <div style="background: linear-gradient(135deg, #EFEBE9, #D7CCC8); border: 1px solid #BCAAA4; border-radius: 8px; padding: 15px; border-left: 4px solid #795548;">
                    <h4 style="color: #5D4037;">🌱 根部病害诊断</h4>
                    <p style="color: #6D4C41;">• 描述根部异常症状<br>• 智能分析根腐病类型<br>• 提供发病规律和防治建议</p>
                </div>
                <div style="background: linear-gradient(135deg, #E3F2FD, #BBDEFB); border: 1px solid #90CAF9; border-radius: 8px; padding: 15px; border-left: 4px solid #2196F3;">
                    <h4 style="color: #1976D2;">🌿 苗期病害诊断</h4>
                    <p style="color: #1565C0;">• 分析幼苗期病害症状<br>• 识别苗枯病、烂种等问题<br>• 提供播种和管理建议</p>
                </div>
            </div>
        </div>
        """)
        
        # 添加技术细节介绍 - 移除hover效果类
        gr.HTML("""
        <div class="info-card" style="margin-top: 20px; background: linear-gradient(135deg, #f8f9fa, #e3f2fd); border: 1px solid #bbdefb;">
            <h3>🏆 核心技术优势</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-top: 15px;">
                <div>
                    <h4 style="color: #1976d2;">🧠 ConvNext深度学习架构</h4>
                    <p style="text-align: justify;">采用<strong>ConvNext</strong>作为核心识别模型，这是Meta AI在2022年发布的现代化卷积神经网络，结合了Vision Transformer的优势与CNN的高效性，在图像识别任务上超越了传统ResNet和EfficientNet架构。</p>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li><strong>宏观设计</strong>：采用分层结构，逐步下采样特征图</li>
                        <li><strong>微观设计</strong>：使用大尺寸卷积核(7×7)和深度可分离卷积</li>
                        <li><strong>优化策略</strong>：LayerNorm标准化 + GELU激活函数</li>
                        <li><strong>性能特点</strong>：参数效率高，推理速度快，精度优异</li>
                    </ul>
                </div>
                <div>
                    <h4 style="color: #388e3c;">📊 模型性能表现</h4>
                    <div style="background: white; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0;">
                        <div style="margin-bottom: 15px;">
                            <h5 style="color: #2e7d32; margin: 0 0 5px 0;">🍃 叶片病害识别模型</h5>
                            <p style="margin: 0; font-size: 0.9rem;">• <strong>单一病种分类准确率：98.24%</strong><br>• <strong>复合病例识别准确率：95.16%</strong><br>• 支持斑病、锈病、健康状态多标签识别</p>
                        </div>
                        <div>
                            <h5 style="color: #f57c00; margin: 0 0 5px 0;">🐛 害虫识别模型</h5>
                            <p style="margin: 0; font-size: 0.9rem;">• <strong>分类准确率：98.37%</strong>（五折交叉验证）<br>• 支持粘虫、玉米螟、蓟马等主要害虫识别<br>• 采用数据增强技术提升小样本学习能力</p>
                        </div>
                    </div>
                </div>
            </div>
            <div style="margin-top: 15px; padding: 10px; background: rgba(25, 118, 210, 0.1); border-radius: 8px; border-left: 4px solid #1976d2;">
                <p style="margin: 0; font-size: 0.9rem; color: #1565c0;"><strong>数据集优势</strong>：经过严格筛选的高质量数据集，包含多种光照条件、拍摄角度和病害严重程度的样本，确保模型在实际应用中的稳定性和可靠性。</p>
            </div>
        </div>
        """)
        
        gr.HTML("""
        <div style="text-align: center; margin-top: 30px; padding: 20px; background: linear-gradient(135deg, #E8F5E8, #F1F8E9); border-radius: 10px; border: 1px solid #A5D6A7; box-shadow: 0 2px 10px rgba(76, 175, 80, 0.1);">
            <h3 style="color: #2E7D32; margin-bottom: 20px;">🎖️ 系统特色</h3>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin-top: 15px;">
                <div style="text-align: center; margin: 10px; background: linear-gradient(135deg, #E3F2FD, #BBDEFB); border: 1px solid #90CAF9; border-radius: 8px; padding: 15px; min-width: 120px;">
                    <div class="status-indicator status-online"></div>
                    <strong style="color: #1976D2;">AI识别</strong><br>
                    <small style="color: #1565C0;">深度学习模型</small>
                </div>
                <div style="text-align: center; margin: 10px; background: linear-gradient(135deg, #FFF3E0, #FFE0B2); border: 1px solid #FFCC02; border-radius: 8px; padding: 15px; min-width: 120px;">
                    <div class="status-indicator status-processing"></div>
                    <strong style="color: #E65100;">症状分析</strong><br>
                    <small style="color: #EF6C00;">智能关键词匹配</small>
                </div>
                <div style="text-align: center; margin: 10px; background: linear-gradient(135deg, #F3E5F5, #E1BEE7); border: 1px solid #CE93D8; border-radius: 8px; padding: 15px; min-width: 120px;">
                    <div class="status-indicator status-online"></div>
                    <strong style="color: #7B1FA2;">专业知识</strong><br>
                    <small style="color: #8E24AA;">农业专家审核</small>
                </div>
                <div style="text-align: center; margin: 10px; background: linear-gradient(135deg, #EFEBE9, #D7CCC8); border: 1px solid #BCAAA4; border-radius: 8px; padding: 15px; min-width: 120px;">
                    <div class="status-indicator status-processing"></div>
                    <strong style="color: #5D4037;">图像对比</strong><br>
                    <small style="color: #6D4C41;">典型病例展示</small>
                </div>
            </div>
        </div>
        """)
        
    return welcome

def create_enhanced_leaf_interface():
    """创建增强的叶片专家界面"""
    leaf_interface = create_leaf_expert_interface()
    
    # 添加专家系统标题
    with gr.Blocks() as enhanced_leaf:
        gr.HTML("""
        <div style="background: linear-gradient(135deg, #4CAF50, #2E7D32); color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
            <h2><span class="expert-icon">🍃</span>玉米叶片病害诊断专家</h2>
            <p>基于深度学习的叶片病害自动识别系统</p>
        </div>
        """)
        
        # 嵌入原始界面
        leaf_interface.render()
        
    return enhanced_leaf

def create_enhanced_pest_interface():
    """创建增强的害虫专家界面"""
    pest_interface = create_pest_expert_interface()
    
    with gr.Blocks() as enhanced_pest:
        gr.HTML("""
        <div style="background: linear-gradient(135deg, #FF9800, #F57C00); color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
            <h2><span class="expert-icon">🐛</span>玉米害虫诊断专家</h2>
            <p>专业的害虫识别与防治指导系统</p>
        </div>
        """)
        
        pest_interface.render()
        
    return enhanced_pest

def create_enhanced_stem_interface():
    """创建增强的茎穗专家界面"""
    stem_interface = create_stem_expert_interface()
    
    with gr.Blocks() as enhanced_stem:
        gr.HTML("""
        <div style="background: linear-gradient(135deg, #546E7A, #37474F); color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
            <h2><span class="expert-icon">🌾</span>玉米茎穗病害诊断专家</h2>
            <p>智能茎穗病害症状分析与诊断系统</p>
        </div>
        """)
        
        stem_interface.render()
        
    return enhanced_stem

def create_enhanced_root_interface():
    """创建增强的根部专家界面"""
    root_interface = create_root_expert_interface()
    
    with gr.Blocks() as enhanced_root:
        gr.HTML("""
        <div style="background: linear-gradient(135deg, #795548, #5D4037); color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
            <h2><span class="expert-icon">🌱</span>玉米根部病害诊断专家</h2>
            <p>根部病害症状分析与诊断指导系统</p>
        </div>
        """)
        
        root_interface.render()
        
    return enhanced_root

def create_enhanced_seedling_interface():
    """创建增强的苗期专家界面"""
    seedling_interface = create_seedling_expert_interface()
    
    with gr.Blocks() as enhanced_seedling:
        gr.HTML("""
        <div style="background: linear-gradient(135deg, #2196F3, #1976D2); color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
            <h2><span class="expert-icon">🌿</span>玉米苗期病害诊断专家</h2>
            <p>苗期病害早期识别与防治指导系统</p>
        </div>
        """)
        
        seedling_interface.render()
        
    return enhanced_seedling

# 创建主应用程序
with gr.Blocks(css=custom_css, title="玉米病虫害诊断智能体", theme=gr.themes.Soft()) as demo:
    # 创建TabbedInterface
    with gr.Tabs():
        with gr.TabItem("🏠 首页"):
            create_welcome_interface()
            
        with gr.TabItem("🍃 叶片病害"):
            create_leaf_expert_interface()
            
        with gr.TabItem("🐛 害虫诊断"):
            create_pest_expert_interface()
            
        with gr.TabItem("🌾 茎穗病害"):
            create_stem_expert_interface()
            
        with gr.TabItem("🌱 根部病害"):
            create_root_expert_interface()
            
        with gr.TabItem("🌿 苗期病害"):
            create_seedling_expert_interface()
    
    # 添加现代化页脚
    gr.HTML("""
    <div style="text-align: center; padding: 25px; margin-top: 40px; background: linear-gradient(135deg, rgba(248, 249, 250, 0.95), rgba(233, 236, 239, 0.95)); color: #495057; border-radius: 16px; border: 1px solid rgba(222, 226, 230, 0.6); box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08); backdrop-filter: blur(10px); animation: fadeInUp 0.6s ease-out 0.5s both;">
        <p style="margin: 0 0 10px 0; font-size: 1rem; font-weight: 600;">
            🌽 玉米病虫害诊断智能体
        </p>
        <p style="margin: 0; font-size: 0.9rem; font-weight: 500;">
            基于AI技术的农业诊断系统 | 
            <span style="opacity: 0.8; color: #6c757d;">Powered by ConvNext & Agricultural Expertise</span>
        </p>
        <div style="margin-top: 15px; display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
            <span style="font-size: 0.8rem; color: #6c757d;">🚀 现代化UI</span>
            <span style="font-size: 0.8rem; color: #6c757d;">📱 响应式设计</span>
            <span style="font-size: 0.8rem; color: #6c757d;">♿ 可访问性优化</span>
            <span style="font-size: 0.8rem; color: #6c757d;">🎨 微交互动画</span>
        </div>
    </div>
    """)
    
    # 添加JavaScript增强功能
    demo.load(
        fn=lambda: None,
        js="""
        function initializeEnhancements() {
            console.log('🚀 初始化现代化前端增强功能...');
            
            // 1. 键盘导航支持
            document.addEventListener('keydown', function(e) {
                // Ctrl+Enter 快速提交
                if (e.ctrlKey && e.key === 'Enter') {
                    const activeElement = document.activeElement;
                    if (activeElement && activeElement.tagName === 'TEXTAREA') {
                        const submitBtn = activeElement.closest('.gradio-container').querySelector('button[variant="primary"]');
                        if (submitBtn) {
                            submitBtn.click();
                            console.log('⚡ 快捷键提交触发');
                        }
                    }
                }
                
                // Tab键导航增强
                if (e.key === 'Tab') {
                    const focusableElements = document.querySelectorAll('button, input, textarea, select, [tabindex]:not([tabindex="-1"])');
                    const currentIndex = Array.from(focusableElements).indexOf(document.activeElement);
                    
                    if (e.shiftKey && currentIndex === 0) {
                        e.preventDefault();
                        focusableElements[focusableElements.length - 1].focus();
                    } else if (!e.shiftKey && currentIndex === focusableElements.length - 1) {
                        e.preventDefault();
                        focusableElements[0].focus();
                    }
                }
            });
            
            // 2. 焦点管理和视觉反馈
            const focusableElements = document.querySelectorAll('button, input, textarea, select');
            focusableElements.forEach(element => {
                element.addEventListener('focus', function() {
                    this.style.transform = 'scale(1.02)';
                    this.setAttribute('aria-expanded', 'true');
                });
                
                element.addEventListener('blur', function() {
                    this.style.transform = 'scale(1)';
                    this.setAttribute('aria-expanded', 'false');
                });
            });
            
            // 3. 按钮波纹效果增强
            const buttons = document.querySelectorAll('button');
            buttons.forEach(button => {
                button.addEventListener('click', function(e) {
                    const ripple = document.createElement('span');
                    const rect = this.getBoundingClientRect();
                    const size = Math.max(rect.width, rect.height);
                    const x = e.clientX - rect.left - size / 2;
                    const y = e.clientY - rect.top - size / 2;
                    
                    ripple.style.cssText = `
                        position: absolute;
                        width: ${size}px;
                        height: ${size}px;
                        left: ${x}px;
                        top: ${y}px;
                        background: rgba(255, 255, 255, 0.6);
                        border-radius: 50%;
                        transform: scale(0);
                        animation: ripple 0.6s linear;
                        pointer-events: none;
                    `;
                    
                    this.appendChild(ripple);
                    
                    setTimeout(() => {
                        ripple.remove();
                    }, 600);
                });
            });
            
            // 4. 图片懒加载和淡入效果
            const observerOptions = {
                root: null,
                rootMargin: '50px',
                threshold: 0.1
            };
            
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.style.opacity = '0';
                        img.style.transition = 'opacity 0.5s ease-in-out';
                        
                        setTimeout(() => {
                            img.style.opacity = '1';
                        }, 100);
                        
                        imageObserver.unobserve(img);
                    }
                });
            }, observerOptions);
            
            // 观察所有图片
            const images = document.querySelectorAll('img');
            images.forEach(img => {
                imageObserver.observe(img);
            });
            
            // 5. 输入框智能提示
            const textareas = document.querySelectorAll('textarea');
            textareas.forEach(textarea => {
                textarea.addEventListener('input', function() {
                    const value = this.value.toLowerCase();
                    const suggestions = [];
                    
                    // 根据输入内容提供智能建议
                    if (value.includes('黄') || value.includes('枯')) {
                        suggestions.push('💡 建议描述：叶片发黄、枯萎的具体部位和程度');
                    }
                    if (value.includes('斑') || value.includes('点')) {
                        suggestions.push('💡 建议描述：斑点的颜色、形状、大小和分布');
                    }
                    if (value.includes('虫') || value.includes('蛀')) {
                        suggestions.push('💡 建议描述：虫害的发生部位和虫体特征');
                    }
                    
                    // 显示建议（可以进一步开发）
                    if (suggestions.length > 0) {
                        console.log('🔍 智能建议:', suggestions);
                    }
                });
            });
            
            // 6. 滚动时的视差效果
            window.addEventListener('scroll', function() {
                const scrolled = window.pageYOffset;
                const rate = scrolled * -0.5;
                
                const header = document.querySelector('.main-header');
                if (header) {
                    header.style.transform = `translateY(${rate}px)`;
                }
            });
            
            // 7. 状态指示器动画
            const statusIndicators = document.querySelectorAll('.status-indicator');
            statusIndicators.forEach(indicator => {
                indicator.style.animation = 'pulse 2s infinite';
            });
            
            // 8. 动态添加CSS样式
            const style = document.createElement('style');
            style.textContent = `
                @keyframes ripple {
                    to {
                        transform: scale(4);
                        opacity: 0;
                    }
                }
                
                .gradio-container .prose {
                    color: inherit !important;
                }
                
                .gradio-container button:focus-visible {
                    outline: 2px solid #4CAF50 !important;
                    outline-offset: 2px !important;
                }
                
                .gradio-container input:focus-visible,
                .gradio-container textarea:focus-visible {
                    outline: 2px solid #4CAF50 !important;
                    outline-offset: 2px !important;
                }
            `;
            document.head.appendChild(style);
            
            console.log('✅ 现代化前端增强功能初始化完成！');
        }
        
        // 延迟初始化以确保DOM完全加载
        setTimeout(initializeEnhancements, 1000);
        """
)

if __name__ == "__main__":
    # 启动应用
    demo.launch(
        debug=True,
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False
    ) 