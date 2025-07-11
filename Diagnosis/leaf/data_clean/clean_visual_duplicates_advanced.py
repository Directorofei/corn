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

def find_and_remove_advanced_duplicates(root_folder, hash_size=8):
    """
    通过感知哈希查找并删除视觉上重复（包括镜像翻转）的图片。
    支持新的数据集目录结构，包括复合病例。
    """
    seen_hashes = set()
    files_to_delete = []
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
        print("   高级去重将特别小心处理锈病样本")

    # 2. 智能识别重复项（包括镜像）
    print(f"\n🔍 Step 2: 执行高级重复检测 (hash_size={hash_size})...")
    category_deleted = defaultdict(int)
    rust_preserved = 0
    
    for filepath in tqdm(files_to_scan, desc="处理图片"):
        try:
            with Image.open(filepath) as img:
                # 计算原图和水平翻转图的哈希值
                original_hash = imagehash.phash(img, hash_size=hash_size)
                
                # 检查原图哈希或翻转图哈希是否已存在
                if original_hash in seen_hashes:
                    category = get_category_from_path(filepath)
                    
                    # 特殊处理锈病样本
                    if category == 'Common_Rust' and rust_count < 500:
                        print(f"\n  🔥 保护锈病样本: 跳过删除 {filepath}")
                        rust_preserved += 1
                        continue
                    
                    files_to_delete.append(filepath)
                    category_deleted[category] += 1
                else:
                    # 如果都不存在，这是一个新图片，将其哈希加入库中
                    flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)
                    flipped_hash = imagehash.phash(flipped_img, hash_size=hash_size)
                    seen_hashes.add(original_hash)
                    seen_hashes.add(flipped_hash) # 把翻转后的哈希也加入，这样后续无论是遇到原图还是翻转图都能识别
        except Exception as e:
            print(f"\n❌ 无法处理文件 {filepath}: {e}")
            
    # 3. 删除被标记为重复的文件
    print(f"\n🗑️  Step 3: 发现 {len(files_to_delete)} 个视觉重复文件待删除...")
    if not files_to_delete:
        print("✅ 未发现重复项。您的数据集很干净!")
        return
    
    print(f"\n📊 各类别重复文件统计:")
    for category, count in category_deleted.items():
        print(f"  {category}: {count} 张重复文件")
    
    if rust_preserved > 0:
        print(f"\n🔥 锈病样本保护: 跳过删除了 {rust_preserved} 张锈病重复样本")
        
    for duplicate_path in tqdm(files_to_delete, desc="删除重复项"):
        try:
            os.remove(duplicate_path)
        except OSError as e:
            print(f"    ❌ 删除失败: {duplicate_path}: {e}")
    
    # 4. 最终统计
    print(f"\n" + "="*60)
    print(f"🎉 高级视觉去重完成!")
    print(f"总处理图片: {len(files_to_scan)}")
    print(f"唯一图片 (清理镜像/重复后): {len(files_to_scan) - len(files_to_delete)}")
    print(f"重复图片 (包括镜像) 删除: {len(files_to_delete)}")
    
    if rust_preserved > 0:
        print(f"🔥 锈病样本保护: {rust_preserved} 张")
    
    print(f"\n📊 各类别删除统计:")
    for category, count in category_deleted.items():
        print(f"  {category}: 删除了 {count} 张重复图片")
    
    # 最终各类别剩余数量
    print(f"\n📈 清理后各类别剩余数量:")
    final_stats = defaultdict(int)
    remaining_files = []
    
    # 重新扫描剩余文件
    for subdir, _, files in os.walk(root_folder):
        for file in files:
            if os.path.splitext(file)[1].lower() in valid_extensions:
                file_path = os.path.join(subdir, file)
                category = get_category_from_path(file_path)
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
        print("🎯 --- 高级视觉去重脚本 ---")
        print("此脚本识别并删除视觉相似的图片，包括水平镜像翻转")
        print("\n支持的数据集结构:")
        print("  - Healthy/")
        print("  - Common_Rust/")
        print("  - Blight/")
        print("  - Gray_Leaf_Spot/")
        print("  - Compound_Cases/Blight_Rust/")
        print("  - Compound_Cases/Gray_Spot_Rust/")
        print("\n🚨 警告: 此操作将永久删除文件")
        print("🔥 特别注意: 锈病样本不足时将跳过锈病重复样本的删除")
        
        user_confirmation = input("\n确定要继续吗? (yes/no): ")
        
        if user_confirmation.lower() == 'yes':
            print("\n🚀 开始高级视觉去重处理...")
            find_and_remove_advanced_duplicates(dataset_directory, hash_size=8)
        else:
            print("\n❌ 用户取消操作") 