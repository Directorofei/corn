import os
from PIL import Image
import imagehash
from tqdm import tqdm
from collections import defaultdict
import sys
from itertools import combinations

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

def get_hash_variants(image, hash_size):
    """为一张图片计算其所有8种对称变换的哈希值"""
    hashes = set()
    # expand=True 确保旋转后的图片尺寸正确，不会被裁剪
    rotations = [
        image,
        image.rotate(90, expand=True),
        image.rotate(180),
        image.rotate(270, expand=True)
    ]
    
    for img in rotations:
        # 添加原图和水平翻转图的哈希
        hashes.add(imagehash.phash(img, hash_size=hash_size))
        hashes.add(imagehash.phash(img.transpose(Image.FLIP_LEFT_RIGHT), hash_size=hash_size))
        
    return list(hashes)

def find_and_remove_deep_duplicates(root_folder, hash_size=8, threshold=5):
    """
    通过模糊匹配感知哈希（汉明距离）来查找并删除视觉上高度相似的图片
    （包括旋转、翻转、轻微噪点、变换等）。
    支持新的数据集目录结构，包括复合病例。
    """
    image_data = []
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
        print("   深度去重将特别保护锈病样本")

    # 2. 为每张图片计算其所有变换的哈希值
    print(f"\n🔍 Step 2: 计算图片所有变换的哈希值 (hash_size={hash_size})...")
    for filepath in tqdm(files_to_scan, desc="计算哈希"):
        try:
            with Image.open(filepath) as img:
                # 转换为灰度图可以提高哈希的稳定性
                hash_variants = get_hash_variants(img.convert("L"), hash_size)
                category = get_category_from_path(filepath)
                image_data.append({'path': filepath, 'variants': hash_variants, 'category': category})
        except Exception as e:
            print(f"\n❌ 无法处理文件 {filepath}: {e}")

    # 3. 使用汉明距离查找相似图片组
    print(f"\n🔍 Step 3: 查找相似图片 (汉明距离 <= {threshold})...")
    
    duplicates_to_remove = set()
    category_duplicates = defaultdict(int)
    rust_protected = 0
    
    # O(n^2 * k) 的比较，其中 k 是哈希变体的数量
    for i in tqdm(range(len(image_data)), desc="比较图片"):
        path_i = image_data[i]['path']
        category_i = image_data[i]['category']
        
        if path_i in duplicates_to_remove:
            continue
            
        variants_i = image_data[i]['variants']
        # 只取 j 的主哈希进行比较，可以极大地加速，且结果基本一致
        primary_hash_i = variants_i[0]
        
        for j in range(i + 1, len(image_data)):
            path_j = image_data[j]['path']
            category_j = image_data[j]['category']
            
            if path_j in duplicates_to_remove:
                continue
            
            variants_j = image_data[j]['variants']
            
            # 检查 i 的主哈希是否与 j 的任何变体相似
            for hash_j in variants_j:
                if (primary_hash_i - hash_j) <= threshold:
                    # 找到了相似项，决定删除哪个
                    
                    # 特殊保护锈病样本
                    if rust_count < 500:
                        if category_i == 'Common_Rust' and category_j != 'Common_Rust':
                            # 保留锈病样本i，删除j
                            duplicates_to_remove.add(path_j)
                            category_duplicates[category_j] += 1
                            rust_protected += 1
                            break
                        elif category_j == 'Common_Rust' and category_i != 'Common_Rust':
                            # 保留锈病样本j，删除i
                            duplicates_to_remove.add(path_i)
                            category_duplicates[category_i] += 1
                            rust_protected += 1
                            break
                        elif category_i == 'Common_Rust' and category_j == 'Common_Rust':
                            # 两个都是锈病样本，只删除j（保留较早的）
                            duplicates_to_remove.add(path_j)
                            category_duplicates[category_j] += 1
                            break
                    
                    # 常规处理：将 j 标记为待删除，然后停止比较 j
                    duplicates_to_remove.add(path_j)
                    category_duplicates[category_j] += 1
                    break
    
    # 4. 删除被标记为重复的文件
    print(f"\n🗑️  Step 4: 发现 {len(duplicates_to_remove)} 张高度相似图片 (包括变换) 待删除...")
    if not duplicates_to_remove:
        print("✅ 未发现高度相似的重复项。您的数据集非常干净!")
        return
    
    print(f"\n📊 各类别重复文件统计:")
    for category, count in category_duplicates.items():
        print(f"  {category}: {count} 张高度相似文件")
    
    if rust_protected > 0:
        print(f"\n🔥 锈病样本保护: 在 {rust_protected} 个相似组中优先保留了锈病样本")
        
    for duplicate_path in tqdm(list(duplicates_to_remove), desc="删除文件"):
        try:
            os.remove(duplicate_path)
        except OSError as e:
            print(f"    ❌ 删除失败: {duplicate_path}: {e}")

    # 5. 最终统计
    print(f"\n" + "="*60)
    print(f"🎉 深度去重扫描完成")
    print(f"总处理图片: {len(files_to_scan)}")
    print(f"唯一图片 (深度清理后): {len(files_to_scan) - len(duplicates_to_remove)}")
    print(f"高度相似图片删除: {len(duplicates_to_remove)}")
    
    if rust_protected > 0:
        print(f"🔥 锈病样本保护: {rust_protected} 组")
    
    print(f"\n📊 各类别删除统计:")
    for category, count in category_duplicates.items():
        print(f"  {category}: 删除了 {count} 张高度相似图片")
    
    # 最终各类别剩余数量
    print(f"\n📈 清理后各类别剩余数量:")
    final_stats = defaultdict(int)
    
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
        print("🎯 --- 深度视觉去重脚本 ---")
        print("此脚本识别并删除高度相似的图片，")
        print("包括旋转 (90/180/270度)、翻转或有轻微噪点的图片")
        print("它通过比较所有对称变换来工作")
        print("\n支持的数据集结构:")
        print("  - Healthy/")
        print("  - Common_Rust/")
        print("  - Blight/")
        print("  - Gray_Leaf_Spot/")
        print("  - Compound_Cases/Blight_Rust/")
        print("  - Compound_Cases/Gray_Spot_Rust/")
        print("\n🚨 警告: 这是最终和最激进的清理步骤。将永久删除文件")
        print("🔥 特别注意: 会特别保护锈病样本")
        
        user_confirmation = input("\n确定要继续吗? (yes/no): ")
        
        if user_confirmation.lower() == 'yes':
            print("\n🚀 开始深度视觉去重处理...")
            # 使用一个相对保守但有效的阈值
            find_and_remove_deep_duplicates(dataset_directory, hash_size=8, threshold=5)
        else:
            print("\n❌ 用户取消操作") 