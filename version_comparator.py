"""
AKO 图纸版本比对器
检测两版图纸之间的差异，输出变更清单和可视化标注
"""

import os
import json
import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from ako_drawing_kit import DrawingData, Line2D, Point2D, TextEntity
from element_recognizer import RecognitionResult


@dataclass
class ChangeItem:
    """变更项"""
    change_id: str
    change_type: str  # added, deleted, modified
    element_type: str  # wall, door, window, room, dimension, text, layer
    description: str = ""
    old_value: dict = field(default_factory=dict)
    new_value: dict = field(default_factory=dict)
    position: dict = field(default_factory=dict)
    severity: str = "info"  # info, warning, critical

    def to_dict(self) -> dict:
        return {
            "change_id": self.change_id,
            "change_type": self.change_type,
            "element_type": self.element_type,
            "description": self.description,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "position": self.position,
            "severity": self.severity,
        }


@dataclass
class ComparisonResult:
    """比对结果"""
    old_file: str = ""
    new_file: str = ""
    changes: List[ChangeItem] = field(default_factory=list)
    summary: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "old_file": self.old_file,
            "new_file": self.new_file,
            "changes": [c.to_dict() for c in self.changes],
            "summary": self.summary,
        }

    def save_json(self, output: str):
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        return output


class VersionComparator:
    """图纸版本比对器"""

    def __init__(self, tolerance: float = 5.0):
        """
        Args:
            tolerance: 几何比对容差（mm）
        """
        self.tolerance = tolerance

    def compare(self, old_drawing: DrawingData, new_drawing: DrawingData) -> ComparisonResult:
        """比对两版图纸"""
        result = ComparisonResult(
            old_file=old_drawing.filename,
            new_file=new_drawing.filename,
        )

        change_idx = 0

        # 1. 图层变更
        layer_changes = self._compare_layers(old_drawing, new_drawing)
        for c in layer_changes:
            c.change_id = f"chg_{change_idx:03d}"
            result.changes.append(c)
            change_idx += 1

        # 2. 线段变更（墙体等）
        line_changes = self._compare_lines(old_drawing, new_drawing)
        for c in line_changes:
            c.change_id = f"chg_{change_idx:03d}"
            result.changes.append(c)
            change_idx += 1

        # 3. 文字变更
        text_changes = self._compare_texts(old_drawing, new_drawing)
        for c in text_changes:
            c.change_id = f"chg_{change_idx:03d}"
            result.changes.append(c)
            change_idx += 1

        # 4. 块参照变更
        block_changes = self._compare_blocks(old_drawing, new_drawing)
        for c in block_changes:
            c.change_id = f"chg_{change_idx:03d}"
            result.changes.append(c)
            change_idx += 1

        # 汇总
        added = sum(1 for c in result.changes if c.change_type == "added")
        deleted = sum(1 for c in result.changes if c.change_type == "deleted")
        modified = sum(1 for c in result.changes if c.change_type == "modified")
        result.summary = {
            "total_changes": len(result.changes),
            "added": added,
            "deleted": deleted,
            "modified": modified,
            "critical": sum(1 for c in result.changes if c.severity == "critical"),
            "warning": sum(1 for c in result.changes if c.severity == "warning"),
            "info": sum(1 for c in result.changes if c.severity == "info"),
        }

        return result

    def compare_recognition_results(
        self, old_result: RecognitionResult, new_result: RecognitionResult
    ) -> ComparisonResult:
        """比对两版识别结果"""
        result = ComparisonResult()
        change_idx = 0

        # 墙体变更
        wall_changes = self._compare_walls(old_result.walls, new_result.walls)
        for c in wall_changes:
            c.change_id = f"chg_{change_idx:03d}"
            c.element_type = "wall"
            result.changes.append(c)
            change_idx += 1

        # 门变更
        door_changes = self._compare_doors(old_result.doors, new_result.doors)
        for c in door_changes:
            c.change_id = f"chg_{change_idx:03d}"
            c.element_type = "door"
            result.changes.append(c)
            change_idx += 1

        # 房间面积变更
        room_changes = self._compare_rooms(old_result.rooms, new_result.rooms)
        for c in room_changes:
            c.change_id = f"chg_{change_idx:03d}"
            c.element_type = "room"
            result.changes.append(c)
            change_idx += 1

        # 汇总
        added = sum(1 for c in result.changes if c.change_type == "added")
        deleted = sum(1 for c in result.changes if c.change_type == "deleted")
        modified = sum(1 for c in result.changes if c.change_type == "modified")
        result.summary = {
            "total_changes": len(result.changes),
            "added": added,
            "deleted": deleted,
            "modified": modified,
        }

        return result

    def _compare_layers(self, old: DrawingData, new: DrawingData) -> List[ChangeItem]:
        """比对图层"""
        changes = []
        old_layers = set(old.layers.keys())
        new_layers = set(new.layers.keys())

        for layer in new_layers - old_layers:
            changes.append(ChangeItem(
                change_id="",
                change_type="added",
                element_type="layer",
                description=f"新增图层: {layer}",
                new_value={"layer": layer},
                severity="info",
            ))

        for layer in old_layers - new_layers:
            changes.append(ChangeItem(
                change_id="",
                change_type="deleted",
                element_type="layer",
                description=f"删除图层: {layer}",
                old_value={"layer": layer},
                severity="warning",
            ))

        return changes

    def _compare_lines(self, old: DrawingData, new: DrawingData) -> List[ChangeItem]:
        """比对线段"""
        changes = []

        old_lines = {(round(l.start.x, 1), round(l.start.y, 1),
                       round(l.end.x, 1), round(l.end.y, 1)): l for l in old.lines}
        new_lines = {(round(l.start.x, 1), round(l.start.y, 1),
                       round(l.end.x, 1), round(l.end.y, 1)): l for l in new.lines}

        old_keys = set(old_lines.keys())
        new_keys = set(new_lines.keys())

        # 新增线段
        for key in new_keys - old_keys:
            line = new_lines[key]
            changes.append(ChangeItem(
                change_id="",
                change_type="added",
                element_type="line",
                description=f"新增线段 (图层:{line.layer}, 长度:{line.length:.0f}mm)",
                new_value={"start": {"x": line.start.x, "y": line.start.y},
                           "end": {"x": line.end.x, "y": line.end.y},
                           "layer": line.layer},
                position={"x": line.midpoint.x, "y": line.midpoint.y},
                severity="info",
            ))

        # 删除线段
        for key in old_keys - new_keys:
            line = old_lines[key]
            changes.append(ChangeItem(
                change_id="",
                change_type="deleted",
                element_type="line",
                description=f"删除线段 (图层:{line.layer}, 长度:{line.length:.0f}mm)",
                old_value={"start": {"x": line.start.x, "y": line.start.y},
                           "end": {"x": line.end.x, "y": line.end.y},
                           "layer": line.layer},
                position={"x": line.midpoint.x, "y": line.midpoint.y},
                severity="info",
            ))

        return changes

    def _compare_texts(self, old: DrawingData, new: DrawingData) -> List[ChangeItem]:
        """比对文字"""
        changes = []

        old_texts = {(round(t.position.x, 0), round(t.position.y, 0)): t for t in old.texts}
        new_texts = {(round(t.position.x, 0), round(t.position.y, 0)): t for t in new.texts}

        old_keys = set(old_texts.keys())
        new_keys = set(new_texts.keys())

        # 新增文字
        for key in new_keys - old_keys:
            text = new_texts[key]
            changes.append(ChangeItem(
                change_id="",
                change_type="added",
                element_type="text",
                description=f"新增文字: '{text.text}'",
                new_value={"text": text.text, "layer": text.layer},
                position={"x": text.position.x, "y": text.position.y},
                severity="info",
            ))

        # 删除文字
        for key in old_keys - new_keys:
            text = old_texts[key]
            changes.append(ChangeItem(
                change_id="",
                change_type="deleted",
                element_type="text",
                description=f"删除文字: '{text.text}'",
                old_value={"text": text.text, "layer": text.layer},
                position={"x": text.position.x, "y": text.position.y},
                severity="info",
            ))

        # 修改文字（同位置不同内容）
        for key in old_keys & new_keys:
            old_t = old_texts[key]
            new_t = new_texts[key]
            if old_t.text != new_t.text:
                changes.append(ChangeItem(
                    change_id="",
                    change_type="modified",
                    element_type="text",
                    description=f"文字修改: '{old_t.text}' → '{new_t.text}'",
                    old_value={"text": old_t.text},
                    new_value={"text": new_t.text},
                    position={"x": old_t.position.x, "y": old_t.position.y},
                    severity="warning",
                ))

        return changes

    def _compare_blocks(self, old: DrawingData, new: DrawingData) -> List[ChangeItem]:
        """比对块参照"""
        changes = []

        old_blocks = {(b.name, round(b.position.x, 0), round(b.position.y, 0)): b for b in old.blocks}
        new_blocks = {(b.name, round(b.position.x, 0), round(b.position.y, 0)): b for b in new.blocks}

        old_keys = set(old_blocks.keys())
        new_keys = set(new_blocks.keys())

        for key in new_keys - old_keys:
            block = new_blocks[key]
            changes.append(ChangeItem(
                change_id="",
                change_type="added",
                element_type="block",
                description=f"新增块参照: {block.name}",
                new_value={"name": block.name, "layer": block.layer},
                position={"x": block.position.x, "y": block.position.y},
                severity="info",
            ))

        for key in old_keys - new_keys:
            block = old_blocks[key]
            changes.append(ChangeItem(
                change_id="",
                change_type="deleted",
                element_type="block",
                description=f"删除块参照: {block.name}",
                old_value={"name": block.name, "layer": block.layer},
                position={"x": block.position.x, "y": block.position.y},
                severity="info",
            ))

        return changes

    def _compare_walls(self, old_walls, new_walls) -> List[ChangeItem]:
        """比对墙体"""
        changes = []
        old_ids = {w.wall_id for w in old_walls}
        new_ids = {w.wall_id for w in new_walls}

        for wid in new_ids - old_ids:
            w = next(w for w in new_walls if w.wall_id == wid)
            changes.append(ChangeItem(
                change_id="", change_type="added", element_type="wall",
                description=f"新增墙体 {wid} (长度:{w.length:.0f}mm)",
                new_value=w.to_dict(), severity="critical",
            ))

        for wid in old_ids - new_ids:
            w = next(w for w in old_walls if w.wall_id == wid)
            changes.append(ChangeItem(
                change_id="", change_type="deleted", element_type="wall",
                description=f"删除墙体 {wid} (长度:{w.length:.0f}mm)",
                old_value=w.to_dict(), severity="critical",
            ))

        return changes

    def _compare_doors(self, old_doors, new_doors) -> List[ChangeItem]:
        """比对门"""
        changes = []
        old_ids = {d.door_id for d in old_doors}
        new_ids = {d.door_id for d in new_doors}

        for did in new_ids - old_ids:
            changes.append(ChangeItem(
                change_id="", change_type="added", element_type="door",
                description=f"新增门 {did}", severity="warning",
            ))

        for did in old_ids - new_ids:
            changes.append(ChangeItem(
                change_id="", change_type="deleted", element_type="door",
                description=f"删除门 {did}", severity="warning",
            ))

        return changes

    def _compare_rooms(self, old_rooms, new_rooms) -> List[ChangeItem]:
        """比对房间"""
        changes = []
        old_names = {r.name for r in old_rooms if r.name}
        new_names = {r.name for r in new_rooms if r.name}

        for name in new_names - old_names:
            r = next(r for r in new_rooms if r.name == name)
            changes.append(ChangeItem(
                change_id="", change_type="added", element_type="room",
                description=f"新增房间: {name} (面积:{r.area:.1f}m²)",
                new_value=r.to_dict(), severity="critical",
            ))

        for name in old_names - new_names:
            r = next(r for r in old_rooms if r.name == name)
            changes.append(ChangeItem(
                change_id="", change_type="deleted", element_type="room",
                description=f"删除房间: {name} (面积:{r.area:.1f}m²)",
                old_value=r.to_dict(), severity="critical",
            ))

        # 面积变化
        for name in old_names & new_names:
            old_r = next(r for r in old_rooms if r.name == name)
            new_r = next(r for r in new_rooms if r.name == name)
            if abs(old_r.area - new_r.area) > 0.5:
                diff = new_r.area - old_r.area
                changes.append(ChangeItem(
                    change_id="", change_type="modified", element_type="room",
                    description=f"房间面积变化: {name} ({old_r.area:.1f}→{new_r.area:.1f}m², {'+' if diff > 0 else ''}{diff:.1f}m²)",
                    old_value=old_r.to_dict(), new_value=new_r.to_dict(),
                    severity="warning",
                ))

        return changes

    def generate_diff_summary(self, result: ComparisonResult) -> str:
        """生成变更摘要文本"""
        s = result.summary
        lines = [
            f"=== 图纸版本比对报告 ===",
            f"旧版: {result.old_file}",
            f"新版: {result.new_file}",
            f"",
            f"变更总数: {s.get('total_changes', 0)}",
            f"  新增: {s.get('added', 0)}",
            f"  删除: {s.get('deleted', 0)}",
            f"  修改: {s.get('modified', 0)}",
            f"",
            f"严重程度:",
            f"  严重: {s.get('critical', 0)}",
            f"  警告: {s.get('warning', 0)}",
            f"  信息: {s.get('info', 0)}",
            f"",
            f"--- 变更明细 ---",
        ]

        for c in result.changes:
            severity_mark = {"critical": "!!", "warning": "!", "info": " "}.get(c.severity, " ")
            type_mark = {"added": "+", "deleted": "-", "modified": "~"}.get(c.change_type, "?")
            lines.append(f"  [{severity_mark}][{type_mark}] {c.description}")

        return "\n".join(lines)

