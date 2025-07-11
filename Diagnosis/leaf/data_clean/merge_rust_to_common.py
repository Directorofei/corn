#!/usr/bin/env python3
"""
锈病数据合并脚本
将清洗后的data/rust/图片合并到datasets/Common_Rust/
并对合并后的Common_Rust进行最终清洗
"""

import os
import sys
import shutil
import hashlib
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

class RustDataMerger:
    """锈病数据合并器"""
    
    def __init__(self, rust_dir="data/rust", common_rust_dir="datasets/Common_Rust"):
        self.rust_dir = rust_dir
        self.common_rust_dir = common_rust_dir
        self.backup_rust_dir = os.path.join(rust_dir, "moved_to_common")
        
        self.stats = {
            'rust_files': 0,
            'common_files_before': 0,
            'files_moved': 0,
            'merge_duplicates': 0,
            'final_count': 0
        }
        
        # 确保目标目录存在
        if not os.path.exists(self.common_rust_dir):
            os.makedirs(self.common_rust_dir)
        
        # 创建备份目录
        if not os.path.exists(self.backup_rust_dir):
            os.makedirs(self.backup_rust_dir)
    
    def count_files(self, directory):
        """统计目录中的图片文件数量"""
        if not os.path.exists(directory):
            return 0
        
        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        count = 0
        for file in os.listdir(directory):
            if os.path.splitext(file)[1].lower() in valid_extensions:
                count += 1
        return count
    
    def get_unique_filename(self, target_dir, filename):
        """获取唯一的文件名，避免覆盖"""
        base_name, ext = os.path.splitext(filename)
        counter = 1
        new_filename = filename
        
        while os.path.exists(os.path.join(target_dir, new_filename)):
            new_filename = f"{base_name}_{counter}{ext}"
            counter += 1
        
        return new_filename
    
    def move_rust_files(self):
        """将rust文件移动到Common_Rust"""
        print("📦 Step 1: 移动锈病文件到Common_Rust...")
        
        # 统计初始文件数量
        self.stats['rust_files'] = self.count_files(self.rust_dir)
        self.stats['common_files_before'] = self.count_files(self.common_rust_dir)
        
        print(f"  📊 rust目录文件数: {self.stats['rust_files']}")
        print(f"  📊 Common_Rust现有文件数: {self.stats['common_files_before']}")
        
        if self.stats['rust_files'] == 0:
            print("  ⚠️  rust目录为空，无文件需要移动")
            return
        
        # 移动文件
        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        files_moved = 0
        
        for file in tqdm(os.listdir(self.rust_dir), desc="移动文件"):
            if os.path.splitext(file)[1].lower() in valid_extensions:
                src_path = os.path.join(self.rust_dir, file)
                
                # 获取唯一文件名
                unique_filename = self.get_unique_filename(self.common_rust_dir, file)
                dst_path = os.path.join(self.common_rust_dir, unique_filename)
                
                # 移动文件
                try:
                    shutil.move(src_path, dst_path)
                    
                    # 备份记录
                    backup_path = os.path.join(self.backup_rust_dir, f"{file} -> {unique_filename}")
                    with open(backup_path, 'w') as f:
                        f.write(f"Moved from: {src_path}\nMoved to: {dst_path}\n")
                    
                    files_moved += 1
                    
                    if unique_filename != file:
                        print(f"  📝 重命名: {file} -> {unique_filename}")
                        
                except Exception as e:
                    print(f"  ❌ 移动失败 {file}: {e}")
        
        self.stats['files_moved'] = files_moved
        print(f"  ✅ 成功移动 {files_moved} 个文件")
    
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
    
    def remove_merge_duplicates(self):
        """删除合并后的重复文件"""
        print("\n🔍 Step 2: 清理合并后的重复文件...")
        
        hashes = defaultdict(list)
        files_to_scan = []
        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        
        # 收集所有文件
        for file in os.listdir(self.common_rust_dir):
            if os.path.splitext(file)[1].lower() in valid_extensions:
                file_path = os.path.join(self.common_rust_dir, file)
                files_to_scan.append(file_path)
        
        print(f"  📊 检查 {len(files_to_scan)} 个文件的重复情况...")
        
        # 计算哈希值
        for filepath in tqdm(files_to_scan, desc="计算哈希"):
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
                    print(f"    🗑️  删除重复: {os.path.basename(duplicate_path)}")
                    try:
                        os.remove(duplicate_path)
                        duplicates_removed += 1
                    except OSError as e:
                        print(f"    ❌ 删除失败: {e}")
        
        self.stats['merge_duplicates'] = duplicates_removed
        print(f"  ✅ 合并去重完成，删除了 {duplicates_removed} 个重复文件")
    
    def remove_visual_duplicates(self, hash_size=8):
        """删除视觉重复的文件"""
        print("\n👁️  Step 3: 最终视觉去重...")
        
        hashes = defaultdict(list)
        files_to_scan = []
        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        
        # 收集所有文件
        for file in os.listdir(self.common_rust_dir):
            if os.path.splitext(file)[1].lower() in valid_extensions:
                file_path = os.path.join(self.common_rust_dir, file)
                files_to_scan.append(file_path)
        
        print(f"  📊 对 {len(files_to_scan)} 个文件进行视觉去重...")
        
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
                    print(f"    🗑️  删除视觉重复: {os.path.basename(duplicate_path)}")
                    try:
                        os.remove(duplicate_path)
                        duplicates_removed += 1
                    except OSError as e:
                        print(f"    ❌ 删除失败: {e}")
        
        print(f"  ✅ 视觉去重完成，删除了 {duplicates_removed} 个视觉重复文件")
    
    def get_final_stats(self):
        """获取最终统计"""
        self.stats['final_count'] = self.count_files(self.common_rust_dir)
    
    def print_final_report(self):
        """打印最终报告"""
        print("\n" + "="*60)
        print("🎉 锈病数据合并完成!")
        print("="*60)
        print(f"📊 合并统计:")
        print(f"  rust目录原文件数: {self.stats['rust_files']}")
        print(f"  Common_Rust原文件数: {self.stats['common_files_before']}")
        print(f"  成功移动文件数: {self.stats['files_moved']}")
        print(f"  合并后删除重复: {self.stats['merge_duplicates']}")
        print(f"  最终Common_Rust文件数: {self.stats['final_count']}")
        
        expected_total = self.stats['common_files_before'] + self.stats['files_moved']
        actual_total = self.stats['final_count'] + self.stats['merge_duplicates']
        
        print(f"\n📈 合并效果:")
        print(f"  预期合并总数: {expected_total}")
        print(f"  实际保留文件: {self.stats['final_count']}")
        print(f"  去重删除文件: {self.stats['merge_duplicates']}")
        print(f"  去重效率: {self.stats['merge_duplicates']/expected_total*100:.1f}%")
        
        print(f"\n📁 文件位置:")
        print(f"  最终锈病数据集: {self.common_rust_dir}")
        print(f"  移动记录备份: {self.backup_rust_dir}")
        print(f"  原rust目录: {self.rust_dir} (已清空)")
        
        print(f"\n🎯 数据集状态:")
        if self.stats['final_count'] >= 500:
            print("  ✅ 锈病样本数量充足 (≥500张)")
        elif self.stats['final_count'] >= 300:
            print("  ⚠️  锈病样本数量基本够用 (300-499张)")
        else:
            print("  ❌ 锈病样本数量不足 (<300张)，建议继续补充")
        
        print(f"\n🔄 下一步建议:")
        print("  1. 检查 datasets/Common_Rust/ 中的最终文件")
        print("  2. 可以开始训练多标签分类模型")
        print("  3. 如需要更多样本，可重复此流程")
        print("="*60)
    
    def run_complete_merge(self):
        """运行完整的合并流程"""
        print("🚀 开始锈病数据合并...")
        print(f"📂 源目录: {self.rust_dir}")
        print(f"📂 目标目录: {self.common_rust_dir}")
        
        # 检查目录
        if not os.path.exists(self.rust_dir):
            print(f"❌ 错误: 源目录 {self.rust_dir} 不存在")
            return False
        
        # 执行合并步骤
        self.move_rust_files()
        self.remove_merge_duplicates()
        self.remove_visual_duplicates()
        
        # 获取最终统计
        self.get_final_stats()
        
        # 打印报告
        self.print_final_report()
        
        return True

def main():
    """主函数"""
    print("🔄 锈病数据合并脚本")
    print("="*50)
    
    # 检查目录
    rust_dir = "data/rust"
    common_rust_dir = "datasets/Common_Rust"
    
    if not os.path.exists(rust_dir):
        print(f"❌ 错误: 源目录 {rust_dir} 不存在")
        print("请先运行锈病数据清洗脚本")
        return
    
    # 显示当前状态
    merger = RustDataMerger(rust_dir, common_rust_dir)
    rust_count = merger.count_files(rust_dir)
    common_count = merger.count_files(common_rust_dir)
    
    print(f"📊 当前状态:")
    print(f"  data/rust/ 文件数: {rust_count}")
    print(f"  datasets/Common_Rust/ 文件数: {common_count}")
    
    if rust_count == 0:
        print("\n⚠️  rust目录为空，可能已经移动或未进行清洗")
        print("如果需要重新处理，请检查 data/rust/backup_original/ 目录")
        return
    
    print(f"\n🔄 将执行以下合并步骤:")
    print("  1. 📦 移动rust文件到Common_Rust")
    print("  2. 🔍 清理合并后的重复文件")
    print("  3. 👁️  最终视觉去重")
    
    print(f"\n🚨 注意事项:")
    print("  • rust目录中的文件将被移动（不是复制）")
    print("  • 移动记录将保存到 data/rust/moved_to_common/")
    print("  • 会对合并后的数据进行最终去重")
    
    user_confirmation = input("\n确定要开始合并吗? (yes/no): ")
    
    if user_confirmation.lower() == 'yes':
        print("\n🚀 开始合并...")
        
        success = merger.run_complete_merge()
        
        if success:
            print("\n✅ 合并完成!")
            print("📝 建议下一步:")
            print("  1. 检查 datasets/Common_Rust/ 中的最终数据")
            print("  2. 可以开始使用更新后的数据集训练模型")
        else:
            print("\n❌ 合并过程中出现错误")
    else:
        print("\n❌ 用户取消操作")

if __name__ == "__main__":
    main() 