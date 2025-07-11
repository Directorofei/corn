#!/usr/bin/env python3
"""
玉米病害数据集清洗主脚本
支持新的数据集目录结构，包括复合病例
特别关注锈病样本的数量和质量
"""

import os
import sys
import subprocess
from collections import defaultdict

def get_category_from_path(file_path):
    """从文件路径中提取类别信息"""
    path_parts = file_path.replace('\\', '/').split('/')
    if 'Healthy' in path_parts:
        return 'Healthy'
    elif 'Common_Rust' in path_parts:
        return 'Common_Rust'
    elif 'Blight' in path_parts:
        return 'Blight'
    elif 'Gray_Leaf_Spot' in path_parts:
        return 'Gray_Leaf_Spot'
    elif 'Blight_Rust' in path_parts:
        return 'Blight_Rust'
    elif 'Gray_Spot_Rust' in path_parts:
        return 'Gray_Spot_Rust'
    else:
        return 'Unknown'

def check_dataset_structure(dataset_dir):
    """检查数据集目录结构"""
    expected_dirs = [
        'Healthy',
        'Common_Rust',
        'Blight', 
        'Gray_Leaf_Spot',
        'Compound_Cases/Blight_Rust',
        'Compound_Cases/Gray_Spot_Rust'
    ]
    
    print("🔍 检查数据集目录结构...")
    existing_dirs = []
    missing_dirs = []
    
    for expected_dir in expected_dirs:
        dir_path = os.path.join(dataset_dir, expected_dir)
        if os.path.exists(dir_path):
            print(f"  ✅ 找到: {expected_dir}")
            existing_dirs.append(expected_dir)
        else:
            print(f"  ⚠️  缺失: {expected_dir}")
            missing_dirs.append(expected_dir)
    
    return existing_dirs, missing_dirs

def scan_dataset_stats(dataset_dir):
    """扫描数据集统计信息"""
    print("\n📊 扫描数据集统计...")
    category_stats = defaultdict(int)
    total_files = 0
    
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    
    for subdir, _, files in os.walk(dataset_dir):
        for file in files:
            if os.path.splitext(file)[1].lower() in valid_extensions:
                file_path = os.path.join(subdir, file)
                category = get_category_from_path(file_path)
                category_stats[category] += 1
                total_files += 1
    
    print(f"  总图片数: {total_files}")
    for category, count in sorted(category_stats.items()):
        print(f"  {category}: {count} 张")
    
    # 特别分析锈病样本情况
    rust_count = category_stats.get('Common_Rust', 0)
    print(f"\n🔥 锈病样本分析:")
    if rust_count < 300:
        print(f"  ❌ 严重不足: 只有 {rust_count} 张，强烈建议补充到500+张")
    elif rust_count < 500:
        print(f"  ⚠️  数量偏少: {rust_count} 张，建议补充到500+张")
    else:
        print(f"  ✅ 数量充足: {rust_count} 张")
    
    return category_stats, total_files

def run_cleaning_script(script_name):
    """运行清洗脚本"""
    script_path = os.path.join('data_clean', script_name)
    if not os.path.exists(script_path):
        print(f"❌ 脚本不存在: {script_path}")
        return False
    
    try:
        print(f"\n🚀 运行脚本: {script_name}")
        result = subprocess.run([sys.executable, script_path], check=True)
        print(f"✅ 脚本 {script_name} 执行完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 脚本执行失败: {e}")
        return False

def display_menu():
    """显示菜单选项"""
    print("\n" + "="*60)
    print("🎯 玉米病害数据集清洗管理器")
    print("="*60)
    print("请选择清洗步骤:")
    print("0. 📊 扫描数据集统计")
    print("1. 🧹 基础去重 (MD5哈希)")
    print("2. 👁️  视觉去重 (感知哈希)")
    print("3. 🎭 高级视觉去重 (包含镜像)")
    print("4. 🔄 深度去重 (所有变换)")
    print("5. 🔲 旋转图片清理 (黑角检测)")
    print("6. 🚀 完整清洗流程 (推荐)")
    print("7. ❓ 查看各脚本说明")
    print("8. 🚪 退出")
    print("="*60)

def show_script_descriptions():
    """显示各脚本的详细说明"""
    descriptions = {
        "基础去重": "基于MD5哈希删除完全相同的文件，最安全的去重方式",
        "视觉去重": "基于感知哈希删除视觉相似的图片，可处理轻微变换",
        "高级视觉去重": "检测并删除镜像翻转的重复图片",
        "深度去重": "最强大的去重，包括旋转、翻转、缩放等所有变换",
        "旋转图片清理": "专门清理有黑边/黑角的旋转图片",
        "完整清洗流程": "按推荐顺序执行所有清洗步骤"
    }
    
    print("\n📖 清洗脚本说明:")
    print("-" * 50)
    for name, desc in descriptions.items():
        print(f"• {name}: {desc}")
    
    print(f"\n🔥 特别提醒:")
    print("• 所有脚本都会特别关注锈病样本的数量")
    print("• 当锈病样本不足500张时，会优先保留锈病样本")
    print("• 建议按顺序执行: 基础去重 → 视觉去重 → 旋转清理")

def run_complete_cleaning():
    """运行完整的清洗流程"""
    print("\n🚀 开始完整清洗流程...")
    
    scripts = [
        ("clean_duplicates.py", "基础去重"),
        ("clean_visual_duplicates.py", "视觉去重"),
        ("clean_rotated_images.py", "旋转图片清理"),
        ("clean_visual_duplicates_advanced.py", "高级视觉去重")
    ]
    
    for script, description in scripts:
        print(f"\n" + "-"*50)
        print(f"执行: {description}")
        print("-"*50)
        
        if not run_cleaning_script(script):
            print(f"❌ {description} 执行失败，停止流程")
            return False
        
        # 每步之后显示统计
        print(f"\n📊 {description} 完成后的统计:")
        scan_dataset_stats('datasets')
        
        input(f"\n按 Enter 继续下一步...")
    
    print(f"\n🎉 完整清洗流程执行完成!")
    return True

def main():
    """主函数"""
    # 检查数据集目录
    dataset_dir = 'datasets'
    if not os.path.exists(dataset_dir):
        print(f"❌ 错误: 未找到 '{dataset_dir}' 目录")
        print("请确保此脚本与 'datasets' 文件夹在同一目录中")
        return
    
    # 检查目录结构
    existing_dirs, missing_dirs = check_dataset_structure(dataset_dir)
    
    if missing_dirs:
        print(f"\n⚠️  警告: 缺失以下目录: {', '.join(missing_dirs)}")
        print("脚本仍可运行，但只会处理现有目录")
    
    # 初始统计
    initial_stats, initial_total = scan_dataset_stats(dataset_dir)
    
    while True:
        display_menu()
        
        try:
            choice = input("\n请输入选择 (0-8): ").strip()
            
            if choice == '0':
                scan_dataset_stats(dataset_dir)
                
            elif choice == '1':
                run_cleaning_script('clean_duplicates.py')
                
            elif choice == '2':
                run_cleaning_script('clean_visual_duplicates.py')
                
            elif choice == '3':
                run_cleaning_script('clean_visual_duplicates_advanced.py')
                
            elif choice == '4':
                run_cleaning_script('clean_deep_duplicates.py')
                
            elif choice == '5':
                run_cleaning_script('clean_rotated_images.py')
                
            elif choice == '6':
                run_complete_cleaning()
                
            elif choice == '7':
                show_script_descriptions()
                
            elif choice == '8':
                print("\n👋 退出清洗管理器")
                break
                
            else:
                print("❌ 无效选择，请输入 0-8")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，退出清洗管理器")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
    
    # 最终统计对比
    print(f"\n📈 最终统计对比:")
    final_stats, final_total = scan_dataset_stats(dataset_dir)
    
    print(f"\n清洗前后对比:")
    print(f"  总图片数: {initial_total} → {final_total} (净删除: {initial_total - final_total})")
    
    for category in initial_stats:
        initial_count = initial_stats.get(category, 0)
        final_count = final_stats.get(category, 0)
        diff = initial_count - final_count
        print(f"  {category}: {initial_count} → {final_count} (删除: {diff})")

if __name__ == "__main__":
    main() 