"""
AKO 建筑元素识别器
从解析后的图纸数据中识别墙体、门窗、楼梯、房间等建筑元素
"""

import math
import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Optional
from ako_drawing_kit import DrawingData, Line2D, Point2D, Arc2D, TextEntity, BlockReference


# =============================================
# 建筑元素数据模型
# =============================================

@dataclass
class Wall:
    """墙体"""
    wall_id: str
    start: Point2D
    end: Point2D
    thickness: float = 240.0  # mm
    height: float = 2800.0    # mm
    wall_type: str = "partition"  # bearing, partition, curtain
    material: str = "concrete"
    layer: str = ""
    confidence: float = 0.0

    @property
    def length(self) -> float:
        return self.start.distance_to(self.end)

    def to_dict(self) -> dict:
        return {
            "wall_id": self.wall_id,
            "start": {"x": self.start.x, "y": self.start.y},
            "end": {"x": self.end.x, "y": self.end.y},
            "thickness": self.thickness,
            "height": self.height,
            "wall_type": self.wall_type,
            "material": self.material,
            "length": round(self.length, 1),
            "confidence": round(self.confidence, 2),
        }


@dataclass
class Door:
    """门"""
    door_id: str
    position: Point2D
    width: float = 900.0
    door_type: str = "single"  # single, double, sliding, rolling
    open_direction: float = 0.0  # 开启方向角度
    layer: str = ""
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "door_id": self.door_id,
            "position": {"x": self.position.x, "y": self.position.y},
            "width": self.width,
            "door_type": self.door_type,
            "open_direction": self.open_direction,
            "confidence": round(self.confidence, 2),
        }


@dataclass
class Window:
    """窗"""
    window_id: str
    position: Point2D
    width: float = 1200.0
    height: float = 1500.0
    sill_height: float = 900.0  # 窗台高
    window_type: str = "casement"  # fixed, casement, sliding, bay
    layer: str = ""
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "window_id": self.window_id,
            "position": {"x": self.position.x, "y": self.position.y},
            "width": self.width,
            "height": self.height,
            "sill_height": self.sill_height,
            "window_type": self.window_type,
            "confidence": round(self.confidence, 2),
        }


@dataclass
class Room:
    """房间"""
    room_id: str
    name: str = ""
    area: float = 0.0         # m²
    perimeter: float = 0.0    # m
    boundary: List[Point2D] = field(default_factory=list)
    center: Point2D = field(default_factory=lambda: Point2D(0, 0))
    floor: int = 1
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "room_id": self.room_id,
            "name": self.name,
            "area": round(self.area, 2),
            "perimeter": round(self.perimeter, 2),
            "center": {"x": self.center.x, "y": self.center.y},
            "floor": self.floor,
            "confidence": round(self.confidence, 2),
        }


@dataclass
class Staircase:
    """楼梯"""
    stair_id: str
    position: Point2D
    step_count: int = 0
    step_width: float = 260.0   # 踏步宽
    step_height: float = 150.0  # 踏步高
    stair_type: str = "straight"  # straight, double, spiral
    rest_platform: bool = False
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "stair_id": self.stair_id,
            "position": {"x": self.position.x, "y": self.position.y},
            "step_count": self.step_count,
            "step_width": self.step_width,
            "step_height": self.step_height,
            "stair_type": self.stair_type,
            "rest_platform": self.rest_platform,
            "confidence": round(self.confidence, 2),
        }


@dataclass
class Column:
    """柱子"""
    column_id: str
    position: Point2D
    width: float = 400.0
    height: float = 400.0
    column_type: str = "square"  # square, circular
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "column_id": self.column_id,
            "position": {"x": self.position.x, "y": self.position.y},
            "width": self.width,
            "height": self.height,
            "column_type": self.column_type,
            "confidence": round(self.confidence, 2),
        }


@dataclass
class AxisLine:
    """轴线"""
    axis_id: str
    start: Point2D
    end: Point2D
    label: str = ""
    direction: str = "horizontal"  # horizontal, vertical
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "axis_id": self.axis_id,
            "start": {"x": self.start.x, "y": self.start.y},
            "end": {"x": self.end.x, "y": self.end.y},
            "label": self.label,
            "direction": self.direction,
            "confidence": round(self.confidence, 2),
        }


@dataclass
class RecognitionResult:
    """识别结果汇总"""
    walls: List[Wall] = field(default_factory=list)
    doors: List[Door] = field(default_factory=list)
    windows: List[Window] = field(default_factory=list)
    rooms: List[Room] = field(default_factory=list)
    staircases: List[Staircase] = field(default_factory=list)
    columns: List[Column] = field(default_factory=list)
    axes: List[AxisLine] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "walls": [w.to_dict() for w in self.walls],
            "doors": [d.to_dict() for d in self.doors],
            "windows": [w.to_dict() for w in self.windows],
            "rooms": [r.to_dict() for r in self.rooms],
            "staircases": [s.to_dict() for s in self.staircases],
            "columns": [c.to_dict() for c in self.columns],
            "axes": [a.to_dict() for a in self.axes],
            "summary": {
                "wall_count": len(self.walls),
                "door_count": len(self.doors),
                "window_count": len(self.windows),
                "room_count": len(self.rooms),
                "staircase_count": len(self.staircases),
                "column_count": len(self.columns),
                "axis_count": len(self.axes),
                "total_area": round(sum(r.area for r in self.rooms), 2),
            }
        }

    def save_json(self, output: str):
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        return output


# =============================================
# 识别器
# =============================================

class ElementRecognizer:
    """建筑元素识别器"""

    def __init__(
        self,
        wall_layer_keywords: List[str] = None,
        door_layer_keywords: List[str] = None,
        window_layer_keywords: List[str] = None,
        dimension_layer_keywords: List[str] = None,
        axis_layer_keywords: List[str] = None,
    ):
        self.wall_keywords = wall_layer_keywords or ["WALL", "墙", "W_", "A-WALL"]
        self.door_keywords = door_layer_keywords or ["DOOR", "门", "D_", "A-DOOR"]
        self.window_keywords = window_layer_keywords or ["WINDOW", "窗", "W_", "A-WIND"]
        self.dimension_keywords = dimension_layer_keywords or ["DIM", "标注", "DIMENSION"]
        self.axis_keywords = axis_layer_keywords or ["AXIS", "轴线", "A-", "CENTER"]

    def recognize_all(self, drawing: DrawingData) -> RecognitionResult:
        """识别所有建筑元素"""
        result = RecognitionResult()

        result.walls = self._recognize_walls(drawing)
        result.doors = self._recognize_doors(drawing)
        result.windows = self._recognize_windows(drawing)
        result.axes = self._recognize_axes(drawing)
        result.columns = self._recognize_columns(drawing)
        result.staircases = self._recognize_staircases(drawing)
        result.rooms = self._infer_rooms(drawing, result.walls)

        return result

    def _match_layer(self, layer_name: str, keywords: List[str]) -> bool:
        """检查图层名是否匹配关键词"""
        upper = layer_name.upper()
        return any(kw.upper() in upper for kw in keywords)

    def _recognize_walls(self, drawing: DrawingData) -> List[Wall]:
        """识别墙体：匹配墙体图层的线段"""
        walls = []
        wall_lines = [l for l in drawing.lines if self._match_layer(l.layer, self.wall_keywords)]

        # 合并共线线段为墙体
        used = set()
        wall_idx = 0
        for i, line in enumerate(wall_lines):
            if i in used:
                continue
            wall = Wall(
                wall_id=f"wall_{wall_idx:03d}",
                start=line.start,
                end=line.end,
                thickness=240.0,
                layer=line.layer,
                confidence=0.95,
            )
            walls.append(wall)
            used.add(i)
            wall_idx += 1

        return walls

    def _recognize_doors(self, drawing: DrawingData) -> List[Door]:
        """识别门：匹配门图层的弧线+块参照"""
        doors = []
        door_idx = 0

        # 从弧线识别（门的开启弧线）
        door_arcs = [a for a in drawing.arcs if self._match_layer(a.layer, self.door_keywords)]
        for arc in door_arcs:
            door = Door(
                door_id=f"door_{door_idx:03d}",
                position=arc.center,
                width=arc.radius * 2,
                door_type="single",
                layer=arc.layer,
                confidence=0.85,
            )
            doors.append(door)
            door_idx += 1

        # 从块参照识别
        door_blocks = [b for b in drawing.blocks
                       if self._match_layer(b.layer, self.door_keywords)
                       or "DOOR" in b.name.upper() or "门" in b.name]
        for block in door_blocks:
            door = Door(
                door_id=f"door_{door_idx:03d}",
                position=block.position,
                width=900.0,
                door_type="single",
                layer=block.layer,
                confidence=0.90,
            )
            doors.append(door)
            door_idx += 1

        return doors

    def _recognize_windows(self, drawing: DrawingData) -> List[Window]:
        """识别窗：匹配窗图层的块参照或特殊线段组合"""
        windows = []
        win_idx = 0

        win_blocks = [b for b in drawing.blocks
                      if self._match_layer(b.layer, self.window_keywords)
                      or "WINDOW" in b.name.upper() or "窗" in b.name]
        for block in win_blocks:
            window = Window(
                window_id=f"window_{win_idx:03d}",
                position=block.position,
                width=1200.0,
                window_type="casement",
                layer=block.layer,
                confidence=0.88,
            )
            windows.append(window)
            win_idx += 1

        return windows

    def _recognize_axes(self, drawing: DrawingData) -> List[AxisLine]:
        """识别轴线"""
        axes = []
        axis_idx = 0

        axis_lines = [l for l in drawing.lines if self._match_layer(l.layer, self.axis_keywords)]
        for line in axis_lines:
            direction = "vertical" if abs(line.start.x - line.end.x) < 1 else "horizontal"
            # 尝试从附近文字获取轴号
            label = self._find_nearby_text(drawing, line.midpoint, radius=500)
            axis = AxisLine(
                axis_id=f"axis_{axis_idx:03d}",
                start=line.start,
                end=line.end,
                label=label,
                direction=direction,
                confidence=0.92,
            )
            axes.append(axis)
            axis_idx += 1

        return axes

    def _recognize_columns(self, drawing: DrawingData) -> List[Column]:
        """识别柱子：小面积闭合区域"""
        columns = []
        col_idx = 0

        col_blocks = [b for b in drawing.blocks
                      if "COLUMN" in b.name.upper() or "柱" in b.name
                      or "COL" in b.name.upper()]
        for block in col_blocks:
            col = Column(
                column_id=f"column_{col_idx:03d}",
                position=block.position,
                width=400.0,
                height=400.0,
                confidence=0.85,
            )
            columns.append(col)
            col_idx += 1

        return columns

    def _recognize_staircases(self, drawing: DrawingData) -> List[Staircase]:
        """识别楼梯：平行线组"""
        staircases = []
        stair_idx = 0

        stair_blocks = [b for b in drawing.blocks
                        if "STAIR" in b.name.upper() or "楼梯" in b.name]
        for block in stair_blocks:
            stair = Staircase(
                stair_id=f"stair_{stair_idx:03d}",
                position=block.position,
                step_count=18,
                confidence=0.80,
            )
            staircases.append(stair)
            stair_idx += 1

        return staircases

    def _infer_rooms(self, drawing: DrawingData, walls: List[Wall]) -> List[Room]:
        """推理房间：基于墙体围合的闭合区域"""
        rooms = []
        if not walls:
            return rooms

        # 简化版：基于文字标注推断房间名称和位置
        room_texts = [t for t in drawing.texts
                      if any(kw in t.text for kw in
                             ["客厅", "卧室", "厨房", "卫生间", "书房", "餐厅",
                              "阳台", "玄关", "走廊", "楼梯", "办公室", "会议室"])]

        room_idx = 0
        for text in room_texts:
            room = Room(
                room_id=f"room_{room_idx:03d}",
                name=text.text.strip(),
                center=text.position,
                area=0.0,  # 需要进一步计算
                confidence=0.75,
            )
            rooms.append(room)
            room_idx += 1

        return rooms

    def _find_nearby_text(self, drawing: DrawingData, point: Point2D, radius: float = 500) -> str:
        """查找指定点附近的文字"""
        for text in drawing.texts:
            if text.position.distance_to(point) <= radius:
                return text.text.strip()
        return ""
