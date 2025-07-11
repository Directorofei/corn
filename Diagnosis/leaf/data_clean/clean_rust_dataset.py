#!/usr/bin/env python3
"""
锈病数据集专用清洗脚本
对data/rust文件夹进行完整的自动清洗
包括基础去重、视觉去重、旋转图片清理等
"""

import os
import sys
import hashlib
import shutil
from PIL import Image
import imagehash
from tqdm import tqdm
from collections import defaultdict

# 检查依赖项
try:
    from PIL import Image
    import imagehash
except ImportError:
    print("❌ 缺少必要的库")
    print("请安装: pip install Pillow imagehash")
    sys.exit(1)

class RustDatasetCleaner:
    """锈病数据集清洗器"""
    
    def __init__(self, rust_dir="data/rust"):
        self.rust_dir = rust_dir
        self.backup_dir = os.path.join(rust_dir, "backup_original")
        self.stats = {
            'original_count': 0,
            'md5_duplicates': 0,
            'visual_duplicates': 0,
            'rotated_images': 0,
            'advanced_duplicates': 0,
            'final_count': 0
        }
        
        # 创建备份目录
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            
    def backup_original_files(self):
        """备份原始文件"""
        print("📦 Step 1: 备份原始文件...")
        
        if os.listdir(self.backup_dir):
            print("  ✅ 备份已存在，跳过备份步骤")
            return
        
        files_to_backup = []
        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        
        for file in os.listdir(self.rust_dir):
            if os.path.splitext(file)[1].lower() in valid_extensions:
                files_to_backup.append(file)
        
        self.stats['original_count'] = len(files_to_backup)
        print(f"  🔢 发现 {len(files_to_backup)} 张原始图片")
        
        for file in tqdm(files_to_backup, desc="备份文件"):
            src = os.path.join(self.rust_dir, file)
            dst = os.path.join(self.backup_dir, file)
            shutil.copy2(src, dst)
        
        print(f"  ✅ 备份完成，原始文件保存在: {self.backup_dir}")
    
    def calculate_md5(self, file_path, chunk_size=8192):
        """计算文件的MD5哈希值"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_md5.update(chunk)
        except IOError:
            return None
        return hash_md5.hexdigest()
    
    def remove_md5_duplicates(self):
        """删除MD5重复的文件"""
        print("\n🔍 Step 2: MD5基础去重...")
        
        hashes = defaultdict(list)
        files_to_scan = []
        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        
        for file in os.listdir(self.rust_dir):
            if os.path.splitext(file)[1].lower() in valid_extensions:
                file_path = os.path.join(self.rust_dir, file)
                files_to_scan.append(file_path)
        
        # 计算哈希值
        for filepath in tqdm(files_to_scan, desc="计算MD5"):
            file_hash = self.calculate_md5(filepath)
            if file_hash:
                hashes[file_hash].append(filepath)
        
        # 删除重复文件
        duplicates_removed = 0
        for file_hash, file_paths in hashes.items():
            if len(file_paths) > 1:
                # 保留第一个文件，删除其余的
                files_to_keep = file_paths[0]
                print(f"  📌 保留: {os.path.basename(files_to_keep)}")
                
                for duplicate_path in file_paths[1:]:
                    print(f"    🗑️  删除: {os.path.basename(duplicate_path)}")
                    try:
                        os.remove(duplicate_path)
                        duplicates_removed += 1
                    except OSError as e:
                        print(f"    ❌ 删除失败: {e}")
        
        self.stats['md5_duplicates'] = duplicates_removed
        print(f"  ✅ MD5去重完成，删除了 {duplicates_removed} 个重复文件")
    
    def remove_visual_duplicates(self, hash_size=8):
        """删除视觉重复的文件"""
        print("\n👁️  Step 3: 视觉去重...")
        
        hashes = defaultdict(list)
        files_to_scan = []
        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        
        for file in os.listdir(self.rust_dir):
            if os.path.splitext(file)[1].lower() in valid_extensions:
                file_path = os.path.join(self.rust_dir, file)
                files_to_scan.append(file_path)
        
        # 计算感知哈希值
        for filepath in tqdm(files_to_scan, desc="计算感知哈希"):
            try:
                with Image.open(filepath) as img:
                    file_hash = imagehash.phash(img, hash_size=hash_size)
                    hashes[file_hash].append(filepath)
            except Exception as e:
                print(f"  ❌ 无法处理 {filepath}: {e}")
        
        # 删除重复文件
        duplicates_removed = 0
        for file_hash, file_paths in hashes.items():
            if len(file_paths) > 1:
                files_to_keep = file_paths[0]
                print(f"  📌 保留: {os.path.basename(files_to_keep)}")
                
                for duplicate_path in file_paths[1:]:
                    print(f"    🗑️  删除: {os.path.basename(duplicate_path)}")
                    try:
                        os.remove(duplicate_path)
                        duplicates_removed += 1
                    except OSError as e:
                        print(f"    ❌ 删除失败: {e}")
        
        self.stats['visual_duplicates'] = duplicates_removed
        print(f"  ✅ 视觉去重完成，删除了 {duplicates_removed} 个重复文件")
    
    def is_pixel_dark(self, pixel, threshold=15):
        """检查像素是否为黑色（降低阈值提高敏感度）"""
        if isinstance(pixel, int):
            return pixel <= threshold
        elif isinstance(pixel, (tuple, list)):
            return all(p <= threshold for p in pixel[:3])
        return False
    
    def check_corner_black_triangle(self, img, corner_x, corner_y, width, height, check_size=20):
        """检查指定角落是否有黑色三角形区域"""
        black_count = 0
        total_count = 0
        
        # 根据角落位置确定检查区域
        if corner_x == 0 and corner_y == 0:
            # 左上角
            for x in range(min(check_size, width)):
                for y in range(min(check_size, height)):
                    if x + y < check_size:  # 三角形区域
                        pixel = img.getpixel((x, y))
                        if self.is_pixel_dark(pixel):
                            black_count += 1
                        total_count += 1
        elif corner_x == width-1 and corner_y == 0:
            # 右上角
            for x in range(max(0, width-check_size), width):
                for y in range(min(check_size, height)):
                    if (width-1-x) + y < check_size:  # 三角形区域
                        pixel = img.getpixel((x, y))
                        if self.is_pixel_dark(pixel):
                            black_count += 1
                        total_count += 1
        elif corner_x == 0 and corner_y == height-1:
            # 左下角
            for x in range(min(check_size, width)):
                for y in range(max(0, height-check_size), height):
                    if x + (height-1-y) < check_size:  # 三角形区域
                        pixel = img.getpixel((x, y))
                        if self.is_pixel_dark(pixel):
                            black_count += 1
                        total_count += 1
        elif corner_x == width-1 and corner_y == height-1:
            # 右下角
            for x in range(max(0, width-check_size), width):
                for y in range(max(0, height-check_size), height):
                    if (width-1-x) + (height-1-y) < check_size:  # 三角形区域
                        pixel = img.getpixel((x, y))
                        if self.is_pixel_dark(pixel):
                            black_count += 1
                        total_count += 1
        
        # 如果黑色像素占比超过70%，认为是黑色三角形
        if total_count > 0:
            black_ratio = black_count / total_count
            return black_ratio >= 0.7
        return False
    
    def is_rotated_with_black_corners(self, image_path, check_size=20):
        """检查图片四个角是否都有黑色三角形（改进版）"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                
                # 图片太小则跳过
                if width < check_size * 2 or height < check_size * 2:
                    return False
                
                # 检查四个角落
                corners = [
                    (0, 0),                    # 左上角
                    (width-1, 0),              # 右上角
                    (0, height-1),             # 左下角
                    (width-1, height-1),       # 右下角
                ]
                
                black_corners = 0
                for corner_x, corner_y in corners:
                    if self.check_corner_black_triangle(img, corner_x, corner_y, width, height, check_size):
                        black_corners += 1
                
                # 如果四个角都有黑色三角形，则认为是旋转图片
                return black_corners == 4
                
        except Exception as e:
            print(f"  ❌ 检查图片失败 {image_path}: {e}")
            return False
    
    def remove_rotated_images(self):
        """删除有黑角的旋转图片"""
        print("\n🔲 Step 4: 清理旋转图片...")
        
        files_to_scan = []
        files_to_remove = []
        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        
        for file in os.listdir(self.rust_dir):
            if os.path.splitext(file)[1].lower() in valid_extensions:
                file_path = os.path.join(self.rust_dir, file)
                files_to_scan.append(file_path)
        
        # 检查黑角
        for filepath in tqdm(files_to_scan, desc="检查黑角"):
            if self.is_rotated_with_black_corners(filepath):
                files_to_remove.append(filepath)
        
        # 删除有黑角的文件
        for filepath in files_to_remove:
            print(f"  🗑️  删除黑角图片: {os.path.basename(filepath)}")
            try:
                os.remove(filepath)
            except OSError as e:
                print(f"    ❌ 删除失败: {e}")
        
        self.stats['rotated_images'] = len(files_to_remove)
        print(f"  ✅ 旋转图片清理完成，删除了 {len(files_to_remove)} 个黑角图片")
    
    def remove_advanced_duplicates(self, hash_size=8):
        """删除高级重复（包括镜像）"""
        print("\n🎭 Step 5: 高级视觉去重...")
        
        seen_hashes = set()
        files_to_delete = []
        files_to_scan = []
        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        
        for file in os.listdir(self.rust_dir):
            if os.path.splitext(file)[1].lower() in valid_extensions:
                file_path = os.path.join(self.rust_dir, file)
                files_to_scan.append(file_path)
        
        # 检测镜像重复
        for filepath in tqdm(files_to_scan, desc="检测镜像重复"):
            try:
                with Image.open(filepath) as img:
                    original_hash = imagehash.phash(img, hash_size=hash_size)
                    
                    if original_hash in seen_hashes:
                        files_to_delete.append(filepath)
                    else:
                        flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)
                        flipped_hash = imagehash.phash(flipped_img, hash_size=hash_size)
                        seen_hashes.add(original_hash)
                        seen_hashes.add(flipped_hash)
            except Exception as e:
                print(f"  ❌ 无法处理 {filepath}: {e}")
        
        # 删除重复文件
        for filepath in files_to_delete:
            print(f"  🗑️  删除镜像重复: {os.path.basename(filepath)}")
            try:
                os.remove(filepath)
            except OSError as e:
                print(f"    ❌ 删除失败: {e}")
        
        self.stats['advanced_duplicates'] = len(files_to_delete)
        print(f"  ✅ 高级去重完成，删除了 {len(files_to_delete)} 个镜像重复文件")
    
    def get_final_count(self):
        """获取最终文件数量"""
        count = 0
        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        
        for file in os.listdir(self.rust_dir):
            if os.path.splitext(file)[1].lower() in valid_extensions:
                count += 1
        
        self.stats['final_count'] = count
        return count
    
    def print_final_report(self):
        """打印最终报告"""
        print("\n" + "="*60)
        print("🎉 锈病数据集清洗完成!")
        print("="*60)
        print(f"📊 清洗统计:")
        print(f"  原始文件数: {self.stats['original_count']}")
        print(f"  MD5重复删除: {self.stats['md5_duplicates']}")
        print(f"  视觉重复删除: {self.stats['visual_duplicates']}")
        print(f"  旋转图片删除: {self.stats['rotated_images']}")
        print(f"  高级重复删除: {self.stats['advanced_duplicates']}")
        print(f"  最终文件数: {self.stats['final_count']}")
        
        total_removed = (self.stats['md5_duplicates'] + 
                        self.stats['visual_duplicates'] + 
                        self.stats['rotated_images'] + 
                        self.stats['advanced_duplicates'])
        
        print(f"\n📈 清洗效果:")
        print(f"  总删除文件: {total_removed}")
        print(f"  清洗比率: {total_removed/self.stats['original_count']*100:.1f}%")
        print(f"  保留比率: {self.stats['final_count']/self.stats['original_count']*100:.1f}%")
        
        print(f"\n📁 文件位置:")
        print(f"  清洗后文件: {self.rust_dir}")
        print(f"  原始备份: {self.backup_dir}")
        
        print(f"\n🔄 下一步建议:")
        print("  1. 手动检查剩余图片，剔除不符合锈病标签的图像")
        print("  2. 将清洗后的图片合并到 datasets/Common_Rust/")
        print("  3. 对 Common_Rust 再次进行自动清洗")
        print("="*60)
    
    def run_complete_cleaning(self):
        """运行完整的清洗流程"""
        print("🚀 开始锈病数据集自动清洗...")
        print(f"📂 目标目录: {self.rust_dir}")
        
        # 检查目录是否存在
        if not os.path.exists(self.rust_dir):
            print(f"❌ 错误: 目录 {self.rust_dir} 不存在")
            return False
        
        # 执行清洗步骤
        self.backup_original_files()
        self.remove_md5_duplicates()
        self.remove_visual_duplicates()
        self.remove_rotated_images()
        self.remove_advanced_duplicates()
        
        # 获取最终统计
        self.get_final_count()
        
        # 打印报告
        self.print_final_report()
        
        return True

def main():
    """主函数"""
    print("🎯 锈病数据集专用清洗脚本")
    print("="*50)
    
    # 检查rust目录
    rust_dir = "data/rust"
    if not os.path.exists(rust_dir):
        print(f"❌ 错误: 未找到目录 {rust_dir}")
        print("请确保您已将锈病数据集放在 data/rust/ 目录中")
        return
    
    # 显示当前文件数量
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    current_count = sum(1 for f in os.listdir(rust_dir) 
                       if os.path.splitext(f)[1].lower() in valid_extensions)
    
    print(f"📊 当前锈病数据集包含 {current_count} 张图片")
    print("\n🔄 将执行以下清洗步骤:")
    print("  1. 📦 备份原始文件")
    print("  2. 🔍 MD5基础去重")
    print("  3. 👁️  视觉去重")
    print("  4. 🔲 旋转图片清理")
    print("  5. 🎭 高级视觉去重")
    
    print("\n🚨 注意事项:")
    print("  • 原始文件将备份到 data/rust/backup_original/")
    print("  • 清洗过程不可逆，请确保重要数据已备份")
    print("  • 清洗完成后请手动检查剩余图片质量")
    
    user_confirmation = input("\n确定要开始自动清洗吗? (yes/no): ")
    
    if user_confirmation.lower() == 'yes':
        print("\n🚀 开始自动清洗...")
        
        cleaner = RustDatasetCleaner(rust_dir)
        success = cleaner.run_complete_cleaning()
        
        if success:
            print("\n✅ 自动清洗完成!")
            print("📝 建议下一步:")
            print("  1. 检查 data/rust/ 中的剩余图片")
            print("  2. 手动剔除不符合锈病标签的图像")
            print("  3. 运行合并脚本将清洗后的图片移动到 datasets/Common_Rust/")
        else:
            print("\n❌ 清洗过程中出现错误")
    else:
        print("\n❌ 用户取消操作")

if __name__ == "__main__":
    main() 