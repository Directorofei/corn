import os
import sys
from PIL import Image
from tqdm import tqdm
from collections import defaultdict

# 检查依赖项
try:
    from PIL import Image
except ImportError:
    print("此脚本需要 'Pillow' 库")
    print("请使用以下命令安装: pip install Pillow")
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

def is_pixel_dark(pixel, threshold=10):
    """检查一个像素是否足够黑"""
    if isinstance(pixel, int):  # Grayscale
        return pixel <= threshold
    elif isinstance(pixel, (tuple, list)):  # RGB or RGBA
        return all(p <= threshold for p in pixel[:3])
    return False

def is_rotated_with_black_corners(image_path, threshold=10, corner_offset=5):
    """
    检查一张图片的四个角是否都有黑色填充。
    corner_offset 用于检查离绝对角落稍偏一点的位置，以增加鲁棒性。
    """
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            
            # 如果图片太小，可能不适用此逻辑，直接跳过
            if width < corner_offset * 4 or height < corner_offset * 4:
                return False

            # 定义四个角的坐标
            corners = [
                (corner_offset, corner_offset),                              # Top-left
                (width - 1 - corner_offset, corner_offset),                  # Top-right
                (corner_offset, height - 1 - corner_offset),                 # Bottom-left
                (width - 1 - corner_offset, height - 1 - corner_offset),     # Bottom-right
            ]
            
            # 检查是否所有角的像素都是黑色的
            for x, y in corners:
                pixel = img.getpixel((x, y))
                if not is_pixel_dark(pixel, threshold):
                    # 只要有一个角不是黑的，就认为不是目标图片
                    return False
            
            # 如果所有角都是黑的，则判定为是
            return True
    except Exception:
        # 无法打开或处理的图片，直接跳过
        return False

def find_and_remove_rotated_images(root_folder):
    """
    查找并删除所有带有旋转产生的黑边/黑角的图片。
    支持新的数据集目录结构，包括复合病例。
    """
    files_to_remove = []
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

    # 2. 检查每张图片是否有黑角
    print(f"\n🔍 Step 2: 检查旋转产生的黑角...")
    category_rotated = defaultdict(int)
    
    for filepath in tqdm(files_to_scan, desc="分析图片"):
        if is_rotated_with_black_corners(filepath):
            files_to_remove.append(filepath)
            category = get_category_from_path(filepath)
            category_rotated[category] += 1

    # 3. 报告并请求确认
    print(f"\n📋 Step 3: 发现 {len(files_to_remove)} 张疑似旋转伪影图片")
    
    if not files_to_remove:
        print("✅ 未发现带有黑角的图片。您的数据集在此方面很干净。")
        return

    print(f"\n📊 各类别疑似旋转图片统计:")
    for category, count in category_rotated.items():
        print(f"  {category}: {count} 张")
    
    # 特别提醒锈病样本
    rust_rotated = category_rotated.get('Common_Rust', 0)
    if rust_rotated > 0 and rust_count < 500:
        print(f"\n🔥 警告: 发现 {rust_rotated} 张锈病样本有黑角，而锈病样本总数较少")
        print("   建议仔细检查是否真的需要删除这些样本")

    print(f"\n🚨 这些图片将被永久删除")
    user_confirmation = input("确定要继续删除吗? (yes/no): ")

    # 4. 执行删除
    if user_confirmation.lower() == 'yes':
        print(f"\n🗑️  Step 4: 删除识别出的文件...")
        category_deleted = defaultdict(int)
        
        for file_path in tqdm(files_to_remove, desc="删除文件"):
            try:
                category = get_category_from_path(file_path)
                os.remove(file_path)
                category_deleted[category] += 1
            except OSError as e:
                print(f"    ❌ 删除失败: {file_path}: {e}")
        
        # 最终统计
        print(f"\n" + "="*60)
        print(f"🎉 旋转图片清理完成!")
        print(f"成功删除 {sum(category_deleted.values())} 个文件")
        
        print(f"\n📊 各类别删除统计:")
        for category, count in category_deleted.items():
            print(f"  {category}: 删除了 {count} 张旋转图片")
        
        # 最终各类别剩余数量
        print(f"\n📈 清理后各类别剩余数量:")
        for category, original_count in category_stats.items():
            deleted_count = category_deleted.get(category, 0)
            remaining_count = original_count - deleted_count
            print(f"  {category}: {remaining_count} 张 (删除了{deleted_count}张)")
        
        print("="*60)
    else:
        print("\n❌ 用户取消操作")
        
    print(f"\n✅ 旋转图片扫描完成")

if __name__ == "__main__":
    dataset_directory = 'datasets'
    
    if not os.path.isdir(dataset_directory):
        print(f"❌ 错误: 未找到 '{dataset_directory}' 目录")
        print("请确保此脚本与 'datasets' 文件夹在同一目录中")
    else:
        print("🎯 --- 旋转图片清理脚本 ---")
        print("此脚本检测并删除可能被旋转的图片，")
        print("通过检查四个角是否有黑色填充来识别旋转伪影")
        print("\n支持的数据集结构:")
        print("  - Healthy/")
        print("  - Common_Rust/")
        print("  - Blight/")
        print("  - Gray_Leaf_Spot/")
        print("  - Compound_Cases/Blight_Rust/")
        print("  - Compound_Cases/Gray_Spot_Rust/")
        print("\n🚨 警告: 此操作将永久删除文件")
        print("🔥 特别注意: 会特别关注锈病样本的删除情况")
        
        find_and_remove_rotated_images(dataset_directory) 