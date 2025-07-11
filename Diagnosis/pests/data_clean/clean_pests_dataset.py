import os
import hashlib
from PIL import Image
import imagehash
from collections import defaultdict
import shutil

# --- 配置 ---
# 数据集根目录
DATASET_ROOT = os.path.join('pests', 'datasets')
# 要处理的类别
TARGET_CATEGORIES = ['armyworm', 'borer', 'thrip']
# 感知哈希相似度阈值，数值越小表示要求越相似
HASH_THRESHOLD = 5

def calculate_md5(file_path):
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except IOError as e:
        print(f"❌ 无法读取文件: {file_path}, 错误: {e}")
        return None

def find_exact_duplicates(directory):
    """
    在指定目录中查找完全重复的图片 (基于MD5哈希)
    返回一个字典，键是文件路径，值是重复的文件列表
    """
    hashes = defaultdict(list)
    for root, _, files in os.walk(directory):
        if 'duplicates' in root:  # 跳过duplicates文件夹
            continue
        for filename in files:
            file_path = os.path.join(root, filename)
            # 确保是图片文件
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                continue
            
            file_hash = calculate_md5(file_path)
            if file_hash:
                hashes[file_hash].append(file_path)
    
    # 筛选出真正有重复的哈希值
    return {k: v for k, v in hashes.items() if len(v) > 1}

def find_visual_duplicates(directory, threshold=5):
    """
    在指定目录中查找视觉上相似的图片 (基于感知哈希)
    包括检测原始、旋转90/180/270度和镜像翻转的图像
    """
    hashes = {}
    duplicates = []
    
    # 过滤非图片文件
    image_files = []
    for root, _, files in os.walk(directory):
        if 'duplicates' in root:
            continue
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                image_files.append(os.path.join(root, filename))

    print(f"  正在为 {len(image_files)} 张图片计算感知哈希值...")

    for img_path in image_files:
        try:
            with Image.open(img_path) as img:
                # 转换为灰度图以提高哈希计算的稳定性
                img = img.convert('L')
                
                # 计算多种变换下的哈希值
                s_hash = imagehash.phash(img)
                lr_hash = imagehash.phash(img.transpose(Image.FLIP_LEFT_RIGHT))

                is_duplicate = False
                # 检查与已有哈希值的相似度
                for path, hash_set in hashes.items():
                    # 检查正常哈希和镜像哈希
                    if (s_hash - hash_set['s'] <= threshold or 
                        lr_hash - hash_set['s'] <= threshold or
                        s_hash - hash_set['lr'] <= threshold or
                        lr_hash - hash_set['lr'] <= threshold):
                        
                        duplicates.append((img_path, path))
                        is_duplicate = True
                        break # 找到一个重复就够了
                
                if not is_duplicate:
                    hashes[img_path] = {'s': s_hash, 'lr': lr_hash}

        except Exception as e:
            print(f"⚠️  警告: 无法处理文件 {img_path}: {e}")
    
    return duplicates

def move_duplicates(duplicate_map, category_path):
    """
    将重复的文件移动到 'duplicates' 子目录
    对于每组重复，保留一个，移动其他
    """
    duplicates_dir = os.path.join(category_path, 'duplicates')
    os.makedirs(duplicates_dir, exist_ok=True)
    
    moved_count = 0
    # 处理精确重复
    if isinstance(duplicate_map, dict):
        for hash_val, files in duplicate_map.items():
            # 保留第一个文件，移动其余的
            for file_to_move in files[1:]:
                try:
                    shutil.move(file_to_move, duplicates_dir)
                    moved_count += 1
                except Exception as e:
                    print(f"❌ 移动文件失败: {file_to_move}, 错误: {e}")
    # 处理视觉重复
    elif isinstance(duplicate_map, list):
        for file1, file2 in duplicate_map:
             # 只移动第一个文件，因为第二个文件是原始文件
            if os.path.exists(file1):
                try:
                    shutil.move(file1, duplicates_dir)
                    moved_count += 1
                except Exception as e:
                    print(f"❌ 移动文件失败: {file1}, 错误: {e}")

    return moved_count

def main():
    """自动化清洗流程主函数"""
    print("="*60)
    print("🚀 开始自动化清洗害虫数据集...")
    print(f"🔍 数据集根目录: {DATASET_ROOT}")
    print(f"🎯 目标类别: {', '.join(TARGET_CATEGORIES)}")
    print("="*60)

    if not os.path.exists(DATASET_ROOT):
        print(f"❌ 错误: 数据集根目录 '{DATASET_ROOT}' 不存在。")
        return

    for category in TARGET_CATEGORIES:
        category_path = os.path.join(DATASET_ROOT, category)
        print(f"\n\n--- 处理类别: {category} ---")

        if not os.path.exists(category_path):
            print(f"⚠️  警告: 类别目录 '{category_path}' 不存在，已跳过。")
            continue

        # --- 第1步: 精确去重 ---
        print("\n[第1步/共2步] 正在执行精确去重 (MD5)...")
        exact_duplicates = find_exact_duplicates(category_path)
        if exact_duplicates:
            moved_count = move_duplicates(exact_duplicates, category_path)
            print(f"✅ 精确去重完成。发现 {len(exact_duplicates)} 组重复，移动了 {moved_count} 个文件。")
        else:
            print("✅ 未发现完全相同的文件。")

        # --- 第2步: 视觉去重 ---
        print("\n[第2步/共2步] 正在执行视觉去重 (Perceptual Hash)...")
        visual_duplicates = find_visual_duplicates(category_path, threshold=HASH_THRESHOLD)
        if visual_duplicates:
            moved_count = move_duplicates(visual_duplicates, category_path)
            print(f"✅ 视觉去重完成。发现 {len(visual_duplicates)} 组相似图片，移动了 {moved_count} 个文件。")
        else:
            print("✅ 未发现视觉上相似的图片。")

    print("\n\n" + "="*60)
    print("🎉 所有类别的清洗流程已全部完成！")
    print("="*60)


if __name__ == '__main__':
    main() 