import numpy as np

def nms(bounding_boxes, IOU=0.5):
    """
    执行非极大值抑制 (NMS)。
    
    参数:
        bounding_boxes (list): 形状为 (N, 6) 的列表，其中 N 是边界框的数量，
                               每个边界框由 [x_min, y_min, x_max, y_max, confidence, class_id] 表示。
        IOU (float): IoU 阈值，用于决定哪些边界框应该被移除。
    
    返回:
        picked_boxes (list): 经过 NMS 处理后保留的边界框列表。
    """
    if len(bounding_boxes) == 0:
        return []

    # 将输入转换为 NumPy 数组
    boxes = np.array(bounding_boxes)

    # 提取坐标和置信度
    start_x = boxes[:, 0]
    start_y = boxes[:, 1]
    end_x = boxes[:, 2]
    end_y = boxes[:, 3]
    score = boxes[:, 4]

    # 计算边界框的面积
    areas = (end_x - start_x + 1) * (end_y - start_y + 1)

    # 按置信度分数降序排序
    order = np.argsort(score)[::-1]

    # 保留的边界框
    keep = []

    while order.size > 0:
        # 选择当前置信度最高的边界框
        i = order[0]
        keep.append(i)

        # 计算该边界框与其他所有边界框的 IoU
        xx1 = np.maximum(start_x[i], start_x[order[1:]])
        yy1 = np.maximum(start_y[i], start_y[order[1:]])
        xx2 = np.minimum(end_x[i], end_x[order[1:]])
        yy2 = np.minimum(end_y[i], end_y[order[1:]])

        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        inter = w * h

        # 计算并集面积
        union = areas[i] + areas[order[1:]] - inter

        # 计算 IoU
        iou = inter / union

        # 移除 IoU 大于阈值的边界框
        inds = np.where(iou <= IOU)[0]
        order = order[inds + 1]

    # 返回保留的边界框
    return [bounding_boxes[i] for i in keep]

# 示例用法
if __name__ == "__main__":
    # 假设我们有以下边界框
    boxes = [
        [1043.937744140625, 1471.193603515625, 1952.7567138671875, 2048.0, 0.9850043058395386, 11.0],
        [671.1224365234375, 293.60595703125, 1633.6971435546875, 1015.9605712890625, 0.47715455293655396, 5.0],
        [671.77880859375, 293.96441650390625, 1632.813232421875, 1006.5716552734375, 0.2893308997154236, 5.0]
    ]

    # 执行 NMS
    picked_boxes = nms(boxes, IOU=0.5)

    # 输出结果
    print("保留的边界框:", picked_boxes)