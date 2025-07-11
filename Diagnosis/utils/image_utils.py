import torch
from torchvision import transforms
from PIL import Image

def preprocess_image(image_path):
    """
    对输入的单张图片进行预处理，使其符合PyTorch模型的输入要求。
    :param image_path: PIL Image an object or a path to an image file.
    :return: a tensor ready for the model.
    """
    
    # 定义图像变换
    preprocess = transforms.Compose([
        transforms.Resize(256),             # 调整图像大小到 256x256
        transforms.CenterCrop(224),         # 中心裁剪到 224x224
        transforms.ToTensor(),              # 转换为张量
        transforms.Normalize(               # 标准化
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    # 如果输入是路径，则打开图片
    if isinstance(image_path, str):
        try:
            image = Image.open(image_path).convert('RGB')
        except FileNotFoundError:
            print(f"Error: The file {image_path} was not found.")
            return None
    else:
        # 假设输入已经是PIL Image对象
        image = image_path.convert('RGB')


    # 应用变换并增加一个batch维度
    image_tensor = preprocess(image)
    return image_tensor.unsqueeze(0)  # 增加批次维度 (B, C, H, W)

if __name__ == '__main__':
    # 一个简单的测试
    # 在models文件夹下放一张测试图片 test.jpg
    # test_tensor = preprocess_image('../models/test.jpg')
    # if test_tensor is not None:
    #     print(test_tensor.shape)
    pass
