"""
AKO 标注 OCR 识别器
从图纸中提取尺寸标注、标高标注、文字注释
"""

import re
import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from ako_drawing_kit import DrawingData, TextEntity, DimensionEntity, Point2D


@dataclass
class DimensionInfo:
    """标注信息"""
    dim_id: str
    text: str
    value: float = 0.0
    unit: str = "mm"
    dim_type: str = "linear"  # linear, height, area, elevation
    position: Point2D = field(default_factory=lambda: Point2D(0, 0))
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "dim_id": self.dim_id,
            "text": self.text,
            "value": self.value,
            "unit": self.unit,
            "dim_type": self.dim_type,
            "position": {"x": self.position.x, "y": self.position.y},
            "confidence": round(self.confidence, 2),
        }


@dataclass
class ElevationInfo:
    """标高信息"""
    elev_id: str
    value: float = 0.0  # 米
    position: Point2D = field(default_factory=lambda: Point2D(0, 0))
    label: str = ""
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "elev_id": self.elev_id,
            "value": self.value,
            "position": {"x": self.position.x, "y": self.position.y},
            "label": self.label,
            "confidence": round(self.confidence, 2),
        }


@dataclass
class TextAnnotation:
    """文字注释"""
    ann_id: str
    text: str
    position: Point2D = field(default_factory=lambda: Point2D(0, 0))
    category: str = "general"  # general, room_name, material, note
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "ann_id": self.ann_id,
            "text": self.text,
            "position": {"x": self.position.x, "y": self.position.y},
            "category": self.category,
            "confidence": round(self.confidence, 2),
        }


@dataclass
class OCRResult:
    """OCR识别结果"""
    dimensions: List[DimensionInfo] = field(default_factory=list)
    elevations: List[ElevationInfo] = field(default_factory=list)
    annotations: List[TextAnnotation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "dimensions": [d.to_dict() for d in self.dimensions],
            "elevations": [e.to_dict() for e in self.elevations],
            "annotations": [a.to_dict() for a in self.annotations],
            "summary": {
                "dimension_count": len(self.dimensions),
                "elevation_count": len(self.elevations),
                "annotation_count": len(self.annotations),
            }
        }

    def save_json(self, output: str):
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        return output


class AnnotationOCR:
    """标注OCR识别器"""

    # 房间名称关键词
    ROOM_KEYWORDS = [
        "客厅", "卧室", "厨房", "卫生间", "书房", "餐厅", "阳台",
        "玄关", "走廊", "楼梯间", "电梯间", "办公室", "会议室",
        "储藏室", "车库", "门厅", "过道",
    ]

    # 材料关键词
    MATERIAL_KEYWORDS = [
        "混凝土", "钢筋", "砖", "砂浆", "防水", "保温",
        "瓷砖", "木地板", "涂料", "玻璃", "铝合金",
    ]

    def __init__(self):
        self._dim_idx = 0
        self._elev_idx = 0
        self._ann_idx = 0

    def recognize(self, drawing: DrawingData) -> OCRResult:
        """从图纸数据中识别所有标注"""
        result = OCRResult()

        # 从DIMENSION实体提取标注
        result.dimensions.extend(self._extract_dimensions(drawing))

        # 从TEXT实体提取标高和注释
        result.elevations.extend(self._extract_elevations(drawing))
        result.annotations.extend(self._extract_annotations(drawing))

        return result

    def _extract_dimensions(self, drawing: DrawingData) -> List[DimensionInfo]:
        """从标注实体提取尺寸"""
        dims = []

        for dim in drawing.dimensions:
            value = self._parse_dimension_value(dim.text, dim.value)
            info = DimensionInfo(
                dim_id=f"dim_{self._dim_idx:03d}",
                text=dim.text,
                value=value,
                dim_type="linear",
                confidence=0.95 if value > 0 else 0.5,
            )
            dims.append(info)
            self._dim_idx += 1

        # 从文字中提取可能的尺寸标注
        dim_pattern = re.compile(r'(\d+\.?\d*)\s*(mm|cm|m|MM|CM|M)?')
        for text in drawing.texts:
            match = dim_pattern.match(text.text.strip())
            if match and not self._is_room_name(text.text):
                value = float(match.group(1))
                unit = (match.group(2) or "mm").lower()
                if unit == "cm":
                    value *= 10
                elif unit == "m":
                    value *= 1000

                info = DimensionInfo(
                    dim_id=f"dim_{self._dim_idx:03d}",
                    text=text.text.strip(),
                    value=value,
                    unit="mm",
                    position=text.position,
                    confidence=0.80,
                )
                dims.append(info)
                self._dim_idx += 1

        return dims

    def _extract_elevations(self, drawing: DrawingData) -> List[ElevationInfo]:
        """从文字中提取标高"""
        elevations = []
        elev_pattern = re.compile(r'[±\-]?\d+\.\d+')
        elev_keywords = ["标高", "EL", "H=", "±0.000", "%%p"]

        for text in drawing.texts:
            t = text.text.strip()

            # 检查是否包含标高关键词
            is_elev = any(kw in t for kw in elev_keywords)
            if not is_elev:
                continue

            # 提取数值
            match = elev_pattern.search(t)
            if match:
                value = float(match.group())
                info = ElevationInfo(
                    elev_id=f"elev_{self._elev_idx:03d}",
                    value=value,
                    position=text.position,
                    label=t,
                    confidence=0.90,
                )
                elevations.append(info)
                self._elev_idx += 1

        return elevations

    def _extract_annotations(self, drawing: DrawingData) -> List[TextAnnotation]:
        """从文字中提取注释"""
        annotations = []

        for text in drawing.texts:
            t = text.text.strip()
            if not t or len(t) < 1:
                continue

            # 分类
            category = self._classify_text(t)

            ann = TextAnnotation(
                ann_id=f"ann_{self._ann_idx:03d}",
                text=t,
                position=text.position,
                category=category,
                confidence=0.95,
            )
            annotations.append(ann)
            self._ann_idx += 1

        return annotations

    def _classify_text(self, text: str) -> str:
        """文字分类"""
        if self._is_room_name(text):
            return "room_name"
        if self._is_material(text):
            return "material"
        if re.match(r'^[\d\.]+$', text):
            return "dimension"
        if any(kw in text for kw in ["注", "说明", "备注", "详见"]):
            return "note"
        return "general"

    def _is_room_name(self, text: str) -> bool:
        return any(kw in text for kw in self.ROOM_KEYWORDS)

    def _is_material(self, text: str) -> bool:
        return any(kw in text for kw in self.MATERIAL_KEYWORDS)

    def _parse_dimension_value(self, text: str, fallback: float = 0.0) -> float:
        """解析标注数值"""
        if not text:
            return fallback

        # 尝试直接解析
        try:
            return float(text)
        except ValueError:
            pass

        # 提取数字部分
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            return float(match.group(1))

        return fallback

    def get_area_summary(self, ocr_result: OCRResult) -> Dict[str, float]:
        """获取面积相关标注汇总"""
        areas = {}
        for dim in ocr_result.dimensions:
            if "面积" in dim.text or "m²" in dim.text or "㎡" in dim.text:
                areas[dim.text] = dim.value
        return areas
