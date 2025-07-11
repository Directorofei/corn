#!/usr/bin/env python3
"""
锈病数据集小角度旋转清洗脚本
专门清理四个角都有黑色三角形的图像（包括小角度旋转）
"""

import os
import sys
from PIL import Image
from tqdm import tqdm

# 检查依赖项
try:
    from PIL import Image
except ImportError:
    print("❌ 缺少必要的库")
    print("请安装: pip install Pillow")
    sys.exit(1)

class SmallRotationCleaner:
    """小角度旋转图片清洗器"""
    
    def __init__(self, rust_dir="data/rust"):
        self.rust_dir = rust_dir
        self.stats = {
            'scanned_files': 0,
            'removed_files': 0,
            'final_count': 0
        }
    
    def is_pixel_dark(self, pixel, threshold=5):
        """检查像素是否为纯黑色（严格阈值）"""
        if isinstance(pixel, int):
            return pixel <= threshold
        elif isinstance(pixel, (tuple, list)):
            return all(p <= threshold for p in pixel[:3])
        return False
    
    def check_corner_black_triangle(self, img, corner_x, corner_y, width, height, check_size=25):
        """检查指定角落是否有纯黑色三角形区域"""
        black_count = 0
        total_count = 0
        
        # 根据角落位置确定检查区域
        if corner_x == 0 and corner_y == 0:
            # 左上角 - 检查三角形区域
            for x in range(min(check_size, width)):
                for y in range(min(check_size, height)):
                    if x + y < check_size:  # 三角形区域
                        pixel = img.getpixel((x, y))
                        if self.is_pixel_dark(pixel):
                            black_count += 1
                        total_count += 1
        elif corner_x == width - 1 and corner_y == 0:
            # 右上角
            for x in range(max(0, width - check_size), width):
                for y in range(min(check_size, height)):
                    if (width - 1 - x) + y < check_size:  # 三角形区域
                        pixel = img.getpixel((x, y))
                        if self.is_pixel_dark(pixel):
                            black_count += 1
                        total_count += 1
        elif corner_x == 0 and corner_y == height - 1:
            # 左下角
            for x in range(min(check_size, width)):
                for y in range(max(0, height - check_size), height):
                    if x + (height - 1 - y) < check_size:  # 三角形区域
                        pixel = img.getpixel((x, y))
                        if self.is_pixel_dark(pixel):
                            black_count += 1
                        total_count += 1
        elif corner_x == width - 1 and corner_y == height - 1:
            # 右下角
            for x in range(max(0, width - check_size), width):
                for y in range(max(0, height - check_size), height):
                    if (width - 1 - x) + (height - 1 - y) < check_size:  # 三角形区域
                        pixel = img.getpixel((x, y))
                        if self.is_pixel_dark(pixel):
                            black_count += 1
                        total_count += 1
        
        # 如果三角形区域中超过60%的像素是纯黑色，则认为是黑角
        if total_count > 0:
            black_ratio = black_count / total_count
            return black_ratio > 0.6
        return False
    
    def has_all_black_corners(self, image_path, check_size=20):
        """检查图片四个角是否都有黑色三角形"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                
                # 图片太小则跳过
                if width < check_size * 2 or height < check_size * 2:
                    return False, []
                
                # 检查四个角落
                corners = [
                    (0, 0),                    # 左上角
                    (width-1, 0),              # 右上角
                    (0, height-1),             # 左下角
                    (width-1, height-1),       # 右下角
                ]
                
                black_corners = 0
                corner_details = []
                
                for corner_x, corner_y in corners:
                    has_black = self.check_corner_black_triangle(img, corner_x, corner_y, width, height, check_size)
                    if has_black:
                        black_corners += 1
                    corner_details.append(has_black)
                
                # 如果四个角都有黑色三角形，则认为是旋转图片
                return black_corners == 4, corner_details
                
        except Exception as e:
            print(f"  ❌ 检查图片失败 {image_path}: {e}")
            return False, []
    
    def clean_small_rotations(self):
        """清理小角度旋转的图片"""
        print("🔍 开始检测小角度旋转图片...")
        
        files_to_scan = []
        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        
        for file in os.listdir(self.rust_dir):
            if os.path.splitext(file)[1].lower() in valid_extensions:
                file_path = os.path.join(self.rust_dir, file)
                files_to_scan.append(file_path)
        
        self.stats['scanned_files'] = len(files_to_scan)
        print(f"  📊 需要检查 {len(files_to_scan)} 张图片")
        
        files_to_remove = []
        
        # 检查每张图片的四个角
        for filepath in tqdm(files_to_scan, desc="检测黑角"):
            has_all_black, corner_details = self.has_all_black_corners(filepath)
            if has_all_black:
                files_to_remove.append(filepath)
                filename = os.path.basename(filepath)
                print(f"  🔍 发现四角黑色: {filename}")
        
        # 删除检测到的旋转图片
        print(f"\n🗑️  准备删除 {len(files_to_remove)} 张四角黑色图片...")
        
        for filepath in files_to_remove:
            filename = os.path.basename(filepath)
            try:
                os.remove(filepath)
                print(f"  🗑️  删除: {filename}")
                self.stats['removed_files'] += 1
            except OSError as e:
                print(f"  ❌ 删除失败 {filename}: {e}")
        
        print(f"\n✅ 小角度旋转清理完成，删除了 {self.stats['removed_files']} 张图片")
    
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
        print("🎯 小角度旋转清理完成!")
        print("="*60)
        print(f"📊 二次清洗统计:")
        print(f"  检查文件数: {self.stats['scanned_files']}")
        print(f"  删除文件数: {self.stats['removed_files']}")
        print(f"  最终文件数: {self.stats['final_count']}")
        
        if self.stats['scanned_files'] > 0:
            removal_rate = self.stats['removed_files'] / self.stats['scanned_files'] * 100
            print(f"  清理比率: {removal_rate:.1f}%")
        
        print(f"\n📁 文件位置:")
        print(f"  清洗后文件: {self.rust_dir}")
        
        print(f"\n🔄 下一步建议:")
        if self.stats['final_count'] >= 500:
            print("  ✅ 锈病样本数量充足，可以进行合并")
        elif self.stats['final_count'] >= 300:
            print("  ⚠️  锈病样本数量基本够用，建议合并")
        else:
            print("  ❌ 锈病样本数量较少，可能需要更多数据")
        
        print("  1. 手动检查剩余图片质量")
        print("  2. 运行合并脚本: python data_clean/merge_rust_to_common.py")
        print("="*60)
    
    def run_complete_cleaning(self):
        """运行完整的清洗流程"""
        self.clean_small_rotations()
        self.get_final_count()
        self.print_final_report()

def main():
    """主函数"""
    print("🎯 锈病数据集小角度旋转清洗脚本")
    print("="*50)
    
    # 检查rust目录
    rust_dir = "data/rust"
    if not os.path.exists(rust_dir):
        print(f"❌ 错误: 未找到目录 {rust_dir}")
        return
    
    # 显示当前文件数量
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    current_count = sum(1 for f in os.listdir(rust_dir) 
                       if os.path.splitext(f)[1].lower() in valid_extensions)
    
    print(f"📊 当前锈病数据集包含 {current_count} 张图片")
    print("\n🔄 将执行小角度旋转检测:")
    print("  • 检查每张图片的四个角落")
    print("  • 寻找黑色三角形区域（70%阈值）")
    print("  • 删除四角都有黑色三角形的图片")
    print("  • 包括15度以下的小角度旋转")
    
    print("\n🚨 注意事项:")
    print("  • 这是二次精细清洗")
    print("  • 专门针对小角度旋转图片")
    print("  • 删除的图片无法恢复（原始备份在backup_original/）")
    
    user_confirmation = input("\n确定要开始小角度旋转清洗吗? (yes/no): ")
    
    if user_confirmation.lower() == 'yes':
        print("\n🚀 开始小角度旋转清洗...")
        
        cleaner = SmallRotationCleaner(rust_dir)
        cleaner.run_complete_cleaning()
        
        print("\n✅ 二次清洗完成!")
    else:
        print("\n❌ 用户取消操作")

if __name__ == "__main__":
    main() 