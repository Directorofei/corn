import torch.nn as nn
import timm

class RTX3060OptimizedModel(nn.Module):
    """针对RTX 3060优化的模型架构"""
    def __init__(self, model_name='convnext_base_in22k', num_classes=4, pretrained=False):
        """
        初始化模型。
        注意：在推理时，pretrained应设为False，因为我们将加载已经训练好的权重。
        """
        super().__init__()
        self.backbone = timm.create_model(model_name, pretrained=pretrained)
        
        # 获取特征维度
        if hasattr(self.backbone, 'head'):
            if hasattr(self.backbone.head, 'fc'):
                in_features = self.backbone.head.fc.in_features
                self.backbone.head.fc = nn.Identity()
            else:
                in_features = self.backbone.head.in_features
                self.backbone.head = nn.Identity()
        else:
            in_features = self.backbone.classifier.in_features
            self.backbone.classifier = nn.Identity()
        
        # 多标签分类头（ConvNeXt Base版本优化）
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(in_features, in_features // 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(in_features // 2, in_features // 4),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(in_features // 4, num_classes)
        )
        
    def forward(self, x):
        features = self.backbone(x)
        return self.classifier(features) 