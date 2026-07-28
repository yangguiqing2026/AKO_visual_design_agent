"""
AKO BIM 模型构建器
从识别结果构建BIM模型，导出IFC/JSON/glTF格式
"""

import os
import json
import math
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from datetime import datetime

from ako_drawing_kit import Point2D
from element_recognizer import (
    RecognitionResult, Wall, Door, Window, Room,
    Staircase, Column, AxisLine
)


@dataclass
class BIMElement:
    """BIM构件基类"""
    element_id: str
    element_type: str
    sub_type: str = ""
    geometry: dict = field(default_factory=dict)
    material: str = ""
    floor: int = 1
    position: dict = field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    properties: dict = field(default_factory=dict)
    confidence: float = 0.0


@dataclass
class BIMFloor:
    """楼层"""
    floor_id: int
    name: str = ""
    elevation: float = 0.0  # 标高（mm）
    height: float = 3000.0  # 层高（mm）
    elements: List[BIMElement] = field(default_factory=list)


@dataclass
class BIMModel:
    """BIM模型"""
    project_name: str = ""
    version: str = "1.0.0"
    created_at: str = ""
    floors: List[BIMFloor] = field(default_factory=list)
    total_elements: int = 0
    total_area: float = 0.0  # m²

    def to_dict(self) -> dict:
        return {
            "project_name": self.project_name,
            "version": self.version,
            "created_at": self.created_at,
            "floors": [
                {
                    "floor_id": f.floor_id,
                    "name": f.name,
                    "elevation": f.elevation,
                    "height": f.height,
                    "element_count": len(f.elements),
                    "elements": [
                        {
                            "element_id": e.element_id,
                            "element_type": e.element_type,
                            "sub_type": e.sub_type,
                            "geometry": e.geometry,
                            "material": e.material,
                            "position": e.position,
                            "properties": e.properties,
                            "confidence": e.confidence,
                        }
                        for e in f.elements
                    ]
                }
                for f in self.floors
            ],
            "summary": {
                "total_floors": len(self.floors),
                "total_elements": self.total_elements,
                "total_area": round(self.total_area, 2),
            }
        }

    def save_json(self, output: str):
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        return output


class BIMBuilder:
    """BIM模型构建器"""

    def __init__(
        self,
        project_name: str = "AKO_Project",
        version: str = "1.0.0",
        floor_count: int = 1,
        floor_height: float = 3000.0,
    ):
        self.project_name = project_name
        self.version = version
        self.floor_count = floor_count
        self.floor_height = floor_height
        self.model = BIMModel(
            project_name=project_name,
            version=version,
            created_at=datetime.now().isoformat(),
        )
        self._init_floors()

    def _init_floors(self):
        """初始化楼层"""
        for i in range(self.floor_count):
            floor = BIMFloor(
                floor_id=i + 1,
                name=f"{i + 1}F",
                elevation=i * self.floor_height,
                height=self.floor_height,
            )
            self.model.floors.append(floor)

    def add_elements_from_recognition(self, result: RecognitionResult, floor: int = 1):
        """从识别结果添加元素"""
        if floor < 1 or floor > len(self.model.floors):
            floor = 1

        bim_floor = self.model.floors[floor - 1]

        # 添加墙体
        for wall in result.walls:
            elem = self._wall_to_bim(wall, floor)
            bim_floor.elements.append(elem)

        # 添加门
        for door in result.doors:
            elem = self._door_to_bim(door, floor)
            bim_floor.elements.append(elem)

        # 添加窗
        for window in result.windows:
            elem = self._window_to_bim(window, floor)
            bim_floor.elements.append(elem)

        # 添加柱子
        for col in result.columns:
            elem = self._column_to_bim(col, floor)
            bim_floor.elements.append(elem)

        # 添加楼梯
        for stair in result.staircases:
            elem = self._stair_to_bim(stair, floor)
            bim_floor.elements.append(elem)

        # 更新统计
        self.model.total_elements = sum(len(f.elements) for f in self.model.floors)
        self.model.total_area = sum(r.area for r in result.rooms)

    def _wall_to_bim(self, wall: Wall, floor: int) -> BIMElement:
        """墙体转BIM构件"""
        return BIMElement(
            element_id=wall.wall_id,
            element_type="wall",
            sub_type=wall.wall_type,
            geometry={
                "shape": "extrusion",
                "start": {"x": wall.start.x, "y": wall.start.y},
                "end": {"x": wall.end.x, "y": wall.end.y},
                "thickness": wall.thickness,
                "height": wall.height,
                "length": round(wall.length, 1),
            },
            material=wall.material,
            floor=floor,
            position={
                "x": (wall.start.x + wall.end.x) / 2,
                "y": (wall.start.y + wall.end.y) / 2,
                "z": (floor - 1) * self.floor_height,
            },
            properties={
                "fire_rating": "R120" if wall.wall_type == "bearing" else "R60",
            },
            confidence=wall.confidence,
        )

    def _door_to_bim(self, door: Door, floor: int) -> BIMElement:
        """门转BIM构件"""
        return BIMElement(
            element_id=door.door_id,
            element_type="door",
            sub_type=door.door_type,
            geometry={
                "width": door.width,
                "height": 2100,
                "open_direction": door.open_direction,
            },
            material="wood",
            floor=floor,
            position={"x": door.position.x, "y": door.position.y, "z": (floor - 1) * self.floor_height},
            confidence=door.confidence,
        )

    def _window_to_bim(self, window: Window, floor: int) -> BIMElement:
        """窗转BIM构件"""
        return BIMElement(
            element_id=window.window_id,
            element_type="window",
            sub_type=window.window_type,
            geometry={
                "width": window.width,
                "height": window.height,
                "sill_height": window.sill_height,
            },
            material="aluminum_glass",
            floor=floor,
            position={"x": window.position.x, "y": window.position.y, "z": (floor - 1) * self.floor_height},
            confidence=window.confidence,
        )

    def _column_to_bim(self, col: Column, floor: int) -> BIMElement:
        """柱转BIM构件"""
        return BIMElement(
            element_id=col.column_id,
            element_type="column",
            sub_type=col.column_type,
            geometry={
                "width": col.width,
                "depth": col.height,
                "height": self.floor_height,
            },
            material="reinforced_concrete",
            floor=floor,
            position={"x": col.position.x, "y": col.position.y, "z": (floor - 1) * self.floor_height},
            confidence=col.confidence,
        )

    def _stair_to_bim(self, stair: Staircase, floor: int) -> BIMElement:
        """楼梯转BIM构件"""
        return BIMElement(
            element_id=stair.stair_id,
            element_type="staircase",
            sub_type=stair.stair_type,
            geometry={
                "step_count": stair.step_count,
                "step_width": stair.step_width,
                "step_height": stair.step_height,
                "total_height": stair.step_count * stair.step_height,
            },
            material="concrete",
            floor=floor,
            position={"x": stair.position.x, "y": stair.position.y, "z": (floor - 1) * self.floor_height},
            confidence=stair.confidence,
        )

    def build(self) -> BIMModel:
        """构建完成，返回模型"""
        return self.model

    def export_json(self, output: str = "output/bim_model.json") -> str:
        """导出为JSON"""
        return self.model.save_json(output)

    def export_ifc(self, output: str = "output/bim_model.ifc") -> str:
        """导出为IFC格式"""
        try:
            import ifcopenshell
            return self._export_ifc_native(output)
        except ImportError:
            print("[警告] IfcOpenShell 未安装，使用简化IFC导出")
            return self._export_ifc_simplified(output)

    def _export_ifc_native(self, output: str) -> str:
        """使用IfcOpenShell导出IFC"""
        import ifcopenshell
        from ifcopenshell.guid import expand

        f = ifcopenshell.file(schema="IFC2X3")

        # 创建项目
        project = f.createIfcProject(
            expand(str(uuid.uuid4())),
            Name=self.project_name,
        )

        # 创建站点
        site = f.createIfcSite(
            expand(str(uuid.uuid4())),
            Name=f"{self.project_name}_Site",
        )

        # 创建楼层
        for bim_floor in self.model.floors:
            building_storey = f.createIfcBuildingStorey(
                expand(str(uuid.uuid4())),
                Name=bim_floor.name,
                ElevationWithFlooring=bim_floor.elevation / 1000.0,
            )

            for elem in bim_floor.elements:
                if elem.element_type == "wall":
                    self._create_ifc_wall(f, elem)
                elif elem.element_type == "door":
                    self._create_ifc_door(f, elem)
                elif elem.element_type == "window":
                    self._create_ifc_window(f, elem)

        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        f.write(output)
        return output

    def _create_ifc_wall(self, f, elem: BIMElement):
        """创建IFC墙体"""
        from ifcopenshell.guid import expand
        geom = elem.geometry

        length = geom.get("length", 1000) / 1000.0
        thickness = geom.get("thickness", 240) / 1000.0
        height = geom.get("height", 2800) / 1000.0

        wall = f.createIfcWallStandardCase(
            expand(str(uuid.uuid4())),
            Name=elem.element_id,
        )
        return wall

    def _create_ifc_door(self, f, elem: BIMElement):
        """创建IFC门"""
        from ifcopenshell.guid import expand
        door = f.createIfcDoor(
            expand(str(uuid.uuid4())),
            Name=elem.element_id,
            OverallHeight=2.1,
            OverallWidth=elem.geometry.get("width", 900) / 1000.0,
        )
        return door

    def _create_ifc_window(self, f, elem: BIMElement):
        """创建IFC窗"""
        from ifcopenshell.guid import expand
        window = f.createIfcWindow(
            expand(str(uuid.uuid4())),
            Name=elem.element_id,
            OverallHeight=elem.geometry.get("height", 1500) / 1000.0,
            OverallWidth=elem.geometry.get("width", 1200) / 1000.0,
        )
        return window

    def _export_ifc_simplified(self, output: str) -> str:
        """简化IFC导出（纯文本格式）"""
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)

        lines = []
        lines.append("ISO-10303-21;")
        lines.append("HEADER;")
        lines.append(f"FILE_DESCRIPTION(('AKO BIM Model - {self.project_name}'));")
        lines.append(f"FILE_NAME('{os.path.basename(output)}','{datetime.now().isoformat()}',('AKO_studio'),('AKO_studio'),'','','');")
        lines.append("FILE_SCHEMA(('IFC2X3'));")
        lines.append("ENDSEC;")
        lines.append("DATA;")

        elem_id = 1
        for floor in self.model.floors:
            lines.append(f"#{elem_id}=IFCBUILDINGSTOREY('{floor.name}','',{floor.elevation / 1000.0});")
            elem_id += 1

            for elem in floor.elements:
                if elem.element_type == "wall":
                    lines.append(f"#{elem_id}=IFCWALL('{elem.element_id}','{elem.sub_type}',{elem.geometry.get('thickness', 240) / 1000.0},{elem.geometry.get('height', 2800) / 1000.0});")
                elif elem.element_type == "door":
                    lines.append(f"#{elem_id}=IFCDOOR('{elem.element_id}','{elem.sub_type}',{elem.geometry.get('width', 900) / 1000.0},2.1);")
                elif elem.element_type == "window":
                    lines.append(f"#{elem_id}=IFCWINDOW('{elem.element_id}','{elem.sub_type}',{elem.geometry.get('width', 1200) / 1000.0},{elem.geometry.get('height', 1500) / 1000.0});")
                elem_id += 1

        lines.append("ENDSEC;")
        lines.append("END-ISO-10303-21;")

        with open(output, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return output

    def summary(self) -> str:
        """输出模型摘要"""
        m = self.model
        return (
            f"BIM模型: {m.project_name} v{m.version}\n"
            f"楼层数: {len(m.floors)}\n"
            f"构件总数: {m.total_elements}\n"
            f"总面积: {m.total_area:.1f} m²\n"
            + "\n".join(f"  {f.name}: {len(f.elements)} 个构件" for f in m.floors)
        )
