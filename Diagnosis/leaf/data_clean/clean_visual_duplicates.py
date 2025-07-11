import os
from PIL import Image
import imagehash
from tqdm import tqdm
from collections import defaultdict
import sys

# 检查依赖项
try:
    from PIL import Image
    import imagehash
except ImportError:
    print("此脚本需要 'Pillow' 和 'imagehash' 库")
    print("请使用以下命令安装: pip install Pillow imagehash")
    sys.exit(1)

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

def find_and_remove_visual_duplicates(root_folder, hash_size=8):
    """
    通过感知哈希查找并删除视觉上重复的图片。
    支持新的数据集目录结构，包括复合病例。
    """
    hashes = defaultdict(list)
    files_to_scan = []
    category_stats = defaultdict(int)
    
    # 定义预期的目录结构
    expected_dirs = [
        'Healthy',
        'Common_Rust',
        'Blight',
        'Gray_Leaf_Spot',
        'Compound_Cases/Blight_Rust',
        'Compound_Cases/Gray_Spot_Rust'
    ]
    
    print("🔍 检查数据集目录结构...")
    for expected_dir in expected_dirs:
        dir_path = os.path.join(root_folder, expected_dir)
        if os.path.exists(dir_path):
            print(f"  ✅ 找到: {expected_dir}")
        else:
            print(f"  ⚠️  缺失: {expected_dir}")
    
    # 1. 收集所有图片文件的路径
    print("\n📂 Step 1: 扫描图片文件...")
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    for subdir, _, files in os.walk(root_folder):
        for file in files:
            if os.path.splitext(file)[1].lower() in valid_extensions:
                file_path = os.path.join(subdir, file)
                files_to_scan.append(file_path)
                category = get_category_from_path(file_path)
                category_stats[category] += 1
    
    if not files_to_scan:
        print("❌ 未找到图片文件。")
        return

    # 显示扫描统计
    print(f"\n📊 扫描统计:")
    print(f"  总图片数: {len(files_to_scan)}")
    for category, count in category_stats.items():
        print(f"  {category}: {count} 张")
    
    # 特别提醒锈病样本数量
    rust_count = category_stats.get('Common_Rust', 0)
    if rust_count < 500:
        print(f"\n⚠️  注意: 锈病样本数量较少({rust_count}张)，建议补充更多样本")
        print("   视觉去重将特别小心处理锈病样本")

    # 2. 计算感知哈希值并找出重复项
    print(f"\n🔍 Step 2: 计算感知哈希值 (hash_size={hash_size})...")
    for filepath in tqdm(files_to_scan, desc="处理图片"):
        try:
            with Image.open(filepath) as img:
                # 使用pHash (Perceptual Hash)
                file_hash = imagehash.phash(img, hash_size=hash_size)
                hashes[file_hash].append(filepath)
        except Exception as e:
            print(f"\n❌ 无法处理文件 {filepath}: {e}")
            
    # 3. 删除视觉上重复的文件
    print(f"\n🧹 Step 3: 删除视觉重复文件...")
    duplicates_removed_count = 0
    category_duplicates = defaultdict(int)
    rust_preserved = 0
    
    for file_hash, file_paths in tqdm(hashes.items(), desc="清理重复项"):
        if len(file_paths) > 1:
            # 特殊处理：如果包含锈病样本，优先保留锈病样本
            rust_files = [f for f in file_paths if get_category_from_path(f) == 'Common_Rust']
            if rust_files and rust_count < 500:
                # 锈病样本不足时，优先保留锈病样本
                files_to_keep = rust_files[0]
                rust_preserved += 1
                print(f"\n  🔥 优先保留锈病样本: {files_to_keep}")
            else:
                # 保留第一个文件
                files_to_keep = file_paths[0]
                keep_category = get_category_from_path(files_to_keep)
                print(f"\n  📌 保留: {files_to_keep} [{keep_category}]")
            
            for duplicate_path in file_paths[1:]:
                if duplicate_path != files_to_keep:
                    dup_category = get_category_from_path(duplicate_path)
                    print(f"    🗑️  删除 (视觉相似): {duplicate_path} [{dup_category}]")
                    category_duplicates[dup_category] += 1
                    
                    try:
                        os.remove(duplicate_path)
                        duplicates_removed_count += 1
                    except OSError as e:
                        print(f"    ❌ 删除失败: {duplicate_path}: {e}")
    
    # 4. 最终统计
    print(f"\n" + "="*60)
    print(f"🎉 视觉去重完成!")
    print(f"总处理图片: {len(files_to_scan)}")
    print(f"唯一图片 (视觉): {len(hashes)}")
    print(f"视觉重复项删除: {duplicates_removed_count}")
    
    if rust_preserved > 0:
        print(f"🔥 锈病样本保护: {rust_preserved} 个重复组中优先保留了锈病样本")
    
    print(f"\n📊 各类别删除统计:")
    for category, count in category_duplicates.items():
        print(f"  {category}: 删除了 {count} 张视觉重复图片")
    
    # 最终各类别剩余数量
    print(f"\n📈 清理后各类别剩余数量:")
    final_stats = defaultdict(int)
    for file_hash, file_paths in hashes.items():
        if file_paths:  # 确保列表不为空
            category = get_category_from_path(file_paths[0])
            final_stats[category] += 1
    
    for category, count in final_stats.items():
        print(f"  {category}: {count} 张")
    
    print("="*60)

if __name__ == "__main__":
    dataset_directory = 'datasets'
    
    if not os.path.isdir(dataset_directory):
        print(f"❌ 错误: 未找到 '{dataset_directory}' 目录")
        print("请确保此脚本与 'datasets' 文件夹在同一目录中")
    else:
        print("🎯 --- 视觉去重脚本 ---")
        print("此脚本识别并删除视觉相似的图片 (如翻转、旋转)")
        print("它使用感知哈希(pHash)来查找这些'孪生'图片")
        print("\n支持的数据集结构:")
        print("  - Healthy/")
        print("  - Common_Rust/")
        print("  - Blight/")
        print("  - Gray_Leaf_Spot/")
        print("  - Compound_Cases/Blight_Rust/")
        print("  - Compound_Cases/Gray_Spot_Rust/")
        print("\n🚨 警告: 此操作将永久删除文件")
        print("🔥 特别注意: 锈病样本不足时将优先保留锈病样本")
        
        user_confirmation = input("\n确定要继续吗? (yes/no): ")
        
        if user_confirmation.lower() == 'yes':
            print("\n🚀 开始视觉去重处理...")
            find_and_remove_visual_duplicates(dataset_directory, hash_size=8)
        else:
            print("\n❌ 用户取消操作") 