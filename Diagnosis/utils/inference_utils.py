import numpy as np

def apply_disease_logic_constraints(preds, threshold=0.5):
    """
    应用疾病优先策略：避免漏诊，解决正常叶片与患病的逻辑冲突
    
    Args:
        preds: 4分类预测概率 [健康, 锈病, 大斑病, 灰斑病] (numpy array)
        threshold: 判断阈值，默认0.5
    
    Returns:
        约束后的预测概率 (numpy array)
    """
    if preds.ndim == 1:
        preds = preds.reshape(1, -1) # 保证输入是二维的

    constrained_preds = preds.copy()
    
    # 疾病优先策略：避免漏诊
    # 计算任意疾病的最大概率
    max_disease_prob = np.maximum.reduce([preds[:, 1], preds[:, 2], preds[:, 3]], axis=0)
    healthy_prob = preds[:, 0]
    
    # 如果疾病概率 > threshold，强制正常叶片概率降低
    disease_positive = max_disease_prob > threshold
    constrained_preds[disease_positive, 0] = np.minimum(
        constrained_preds[disease_positive, 0], 
        threshold * 0.8  # 降低到阈值的80%
    )
    
    # 如果正常叶片概率显著高于疾病概率，才认为是健康
    # 正常叶片概率必须比最大疾病概率高出一定margin
    margin = 0.15  # 15%的margin
    healthy_dominant = (healthy_prob > max_disease_prob + margin) & (healthy_prob > threshold)
    constrained_preds[healthy_dominant, 1:] *= 0.3  # 大幅降低疾病概率
    
    return constrained_preds 