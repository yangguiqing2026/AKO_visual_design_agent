"""
AKO 图纸解析引擎 - DXF/DWG 文件解析
支持从CAD图纸中提取图层、几何元素、标注信息
"""

import os
import json
import math
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path


@dataclass
class Point2D:
    """二维点"""
    x: float
    y: float

    def distance_to(self, other: 'Point2D') -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


@dataclass
class Line2D:
    """二维线段"""
    start: Point2D
    end: Point2D
    layer: str = ""

    @property
    def length(self) -> float:
        return self.start.distance_to(self.end)

    @property
    def angle(self) -> float:
        """线段角度（度）"""
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        return math.degrees(math.atan2(dy, dx))

    @property
    def midpoint(self) -> Point2D:
        return Point2D((self.start.x + self.end.x) / 2, (self.start.y + self.end.y) / 2)


@dataclass
class Arc2D:
    """二维圆弧"""
    center: Point2D
    radius: float
    start_angle: float  # 度
    end_angle: float    # 度
    layer: str = ""


@dataclass
class TextEntity:
    """文字实体"""
    position: Point2D
    text: str
    height: float = 2.5
    layer: str = ""
    rotation: float = 0.0


@dataclass
class DimensionEntity:
    """标注实体"""
    text: str
    value: float
    start: Point2D
    end: Point2D
    dim_type: str = "linear"  # linear, aligned, angular, radius
    layer: str = ""


@dataclass
class BlockReference:
    """块参照"""
    name: str
    position: Point2D
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    rotation: float = 0.0
    layer: str = ""
    attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class LayerInfo:
    """图层信息"""
    name: str
    color: int = 7  # 默认白色
    linetype: str = "Continuous"
    entity_count: int = 0


@dataclass
class DrawingData:
    """图纸解析结果"""
    filename: str = ""
    layers: Dict[str, LayerInfo] = field(default_factory=dict)
    lines: List[Line2D] = field(default_factory=list)
    arcs: List[Arc2D] = field(default_factory=list)
    texts: List[TextEntity] = field(default_factory=list)
    dimensions: List[DimensionEntity] = field(default_factory=list)
    blocks: List[BlockReference] = field(default_factory=list)
    extents: Tuple[float, float, float, float] = (0, 0, 0, 0)  # minx, miny, maxx, maxy

    def to_dict(self) -> dict:
        """转为字典"""
        return {
            "filename": self.filename,
            "layers": {k: {"name": v.name, "color": v.color, "linetype": v.linetype, "entity_count": v.entity_count}
                       for k, v in self.layers.items()},
            "line_count": len(self.lines),
            "arc_count": len(self.arcs),
            "text_count": len(self.texts),
            "dimension_count": len(self.dimensions),
            "block_count": len(self.blocks),
            "extents": list(self.extents),
        }

    def save_json(self, output: str):
        """保存解析结果为JSON"""
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        return output


class DrawingParser:
    """图纸解析器"""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.ext = Path(filepath).suffix.lower()
        self.data = DrawingData(filename=os.path.basename(filepath))

    def parse(self) -> DrawingData:
        """解析图纸文件"""
        if self.ext == ".dxf":
            return self._parse_dxf()
        elif self.ext == ".dwg":
            return self._parse_dwg()
        elif self.ext == ".pdf":
            return self._parse_pdf()
        else:
            raise ValueError(f"不支持的文件格式: {self.ext}")

    def _parse_dxf(self) -> DrawingData:
        """解析DXF文件"""
        try:
            import ezdxf
        except ImportError:
            print("[警告] ezdxf 未安装，使用简化解析器")
            return self._parse_dxf_fallback()

        doc = ezdxf.readfile(self.filepath)
        msp = doc.modelspace()

        # 解析图层
        for layer in doc.layers:
            self.data.layers[layer.dxf.name] = LayerInfo(
                name=layer.dxf.name,
                color=layer.dxf.color,
                linetype=layer.dxf.linetype if hasattr(layer.dxf, 'linetype') else "Continuous",
            )

        # 解析实体
        for entity in msp:
            dxftype = entity.dxftype()
            layer = entity.dxf.layer if hasattr(entity.dxf, 'layer') else ""

            if dxftype == "LINE":
                line = Line2D(
                    start=Point2D(entity.dxf.start.x, entity.dxf.start.y),
                    end=Point2D(entity.dxf.end.x, entity.dxf.end.y),
                    layer=layer,
                )
                self.data.lines.append(line)

            elif dxftype == "ARC":
                arc = Arc2D(
                    center=Point2D(entity.dxf.center.x, entity.dxf.center.y),
                    radius=entity.dxf.radius,
                    start_angle=entity.dxf.start_angle,
                    end_angle=entity.dxf.end_angle,
                    layer=layer,
                )
                self.data.arcs.append(arc)

            elif dxftype in ("TEXT", "MTEXT"):
                text = entity.dxf.text if dxftype == "TEXT" else entity.text
                pos = entity.dxf.insert
                h = entity.dxf.height if hasattr(entity.dxf, 'height') else 2.5
                self.data.texts.append(TextEntity(
                    position=Point2D(pos.x, pos.y),
                    text=text,
                    height=h,
                    layer=layer,
                ))

            elif dxftype == "DIMENSION":
                dim_text = entity.dxf.text if hasattr(entity.dxf, 'text') and entity.dxf.text else ""
                try:
                    val = entity.dxf.actual_measurement if hasattr(entity.dxf, 'actual_measurement') else 0
                except Exception:
                    val = 0
                self.data.dimensions.append(DimensionEntity(
                    text=dim_text,
                    value=val,
                    start=Point2D(0, 0),
                    end=Point2D(0, 0),
                    layer=layer,
                ))

            elif dxftype == "INSERT":
                block_ref = BlockReference(
                    name=entity.dxf.name,
                    position=Point2D(entity.dxf.insert.x, entity.dxf.insert.y),
                    scale=(
                        entity.dxf.xscale if hasattr(entity.dxf, 'xscale') else 1.0,
                        entity.dxf.yscale if hasattr(entity.dxf, 'yscale') else 1.0,
                        1.0,
                    ),
                    rotation=entity.dxf.rotation if hasattr(entity.dxf, 'rotation') else 0.0,
                    layer=layer,
                )
                # 提取属性
                if hasattr(entity, 'attribs'):
                    for attrib in entity.attribs:
                        block_ref.attributes[attrib.dxf.tag] = attrib.dxf.text
                self.data.blocks.append(block_ref)

        # 更新图层实体计数
        for entity_list_name in ["lines", "arcs", "texts", "dimensions", "blocks"]:
            for entity in getattr(self.data, entity_list_name):
                if entity.layer in self.data.layers:
                    self.data.layers[entity.layer].entity_count += 1

        # 计算范围
        self._compute_extents()

        return self.data

    def _parse_dxf_fallback(self) -> DrawingData:
        """简化DXF解析器（不依赖ezdxf）"""
        with open(self.filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # 简单提取TEXT实体
        lines = content.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line == "TEXT":
                # 尝试提取后续坐标和文字
                text_val = ""
                x, y = 0.0, 0.0
                for j in range(i + 1, min(i + 20, len(lines))):
                    if lines[j].strip() == "1":
                        if j + 1 < len(lines):
                            text_val = lines[j + 1].strip()
                    elif lines[j].strip() == "10":
                        if j + 1 < len(lines):
                            try:
                                x = float(lines[j + 1].strip())
                            except ValueError:
                                pass
                    elif lines[j].strip() == "20":
                        if j + 1 < len(lines):
                            try:
                                y = float(lines[j + 1].strip())
                            except ValueError:
                                pass
                if text_val:
                    self.data.texts.append(TextEntity(
                        position=Point2D(x, y),
                        text=text_val,
                        layer="TEXT",
                    ))
            i += 1

        return self.data

    def _parse_dwg(self) -> DrawingData:
        """解析DWG文件（尝试转换为DXF后解析）"""
        print(f"[信息] DWG文件: {self.filepath}")
        print("[信息] DWG直接解析需要ODA SDK，当前尝试使用ezdxf读取（如果ezdxf支持）")
        try:
            import ezdxf
            doc = ezdxf.readfile(self.filepath)
            # 如果能读取，当作DXF处理
            return self._parse_dxf()
        except Exception as e:
            print(f"[警告] 无法直接解析DWG: {e}")
            print("[提示] 请先将DWG转换为DXF格式，或安装ODA SDK")
            return self.data

    def _parse_pdf(self) -> DrawingData:
        """解析PDF图纸（简化版）"""
        print(f"[信息] PDF图纸解析: {self.filepath}")
        print("[提示] PDF解析需要 pdfplumber + OpenCV，当前为简化模式")
        return self.data

    def _compute_extents(self):
        """计算图纸范围"""
        all_x = []
        all_y = []

        for line in self.data.lines:
            all_x.extend([line.start.x, line.end.x])
            all_y.extend([line.start.y, line.end.y])

        for arc in self.data.arcs:
            all_x.extend([arc.center.x - arc.radius, arc.center.x + arc.radius])
            all_y.extend([arc.center.y - arc.radius, arc.center.y + arc.radius])

        for text in self.data.texts:
            all_x.append(text.position.x)
            all_y.append(text.position.y)

        for block in self.data.blocks:
            all_x.append(block.position.x)
            all_y.append(block.position.y)

        if all_x and all_y:
            self.data.extents = (min(all_x), min(all_y), max(all_x), max(all_y))

    def get_lines_by_layer(self, layer_name: str) -> List[Line2D]:
        """按图层获取线段"""
        return [l for l in self.data.lines if l.layer == layer_name]

    def get_texts_by_layer(self, layer_name: str) -> List[TextEntity]:
        """按图层获取文字"""
        return [t for t in self.data.texts if t.layer == layer_name]

    def get_all_layer_names(self) -> List[str]:
        """获取所有图层名"""
        return list(self.data.layers.keys())

    def summary(self) -> str:
        """输出解析摘要"""
        d = self.data
        return (
            f"图纸: {d.filename}\n"
            f"图层数: {len(d.layers)}\n"
            f"线段数: {len(d.lines)}\n"
            f"圆弧数: {len(d.arcs)}\n"
            f"文字数: {len(d.texts)}\n"
            f"标注数: {len(d.dimensions)}\n"
            f"块参照: {len(d.blocks)}\n"
            f"范围: ({d.extents[0]:.1f}, {d.extents[1]:.1f}) - ({d.extents[2]:.1f}, {d.extents[3]:.1f})"
        )
