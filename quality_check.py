"""
AKO 质量门禁 - 三Agent统一质量检查
覆盖视觉设计、图纸识别、建筑性能分析的质量检查
"""

import os
import json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from PIL import Image

from ako_colors import ALL_VALID_RGB_SET, FORBIDDEN_BG_COLORS


@dataclass
class CheckItem:
    """检查项"""
    check_id: str
    agent: str          # visual, drawing, analysis
    category: str       # 检查类别
    name: str           # 检查项名称
    standard: str       # 标准
    passed: bool = False
    actual_value: str = ""
    message: str = ""
    severity: str = "info"  # info, warning, critical, blocker

    def to_dict(self) -> dict:
        return {
            "check_id": self.check_id,
            "agent": self.agent,
            "category": self.category,
            "name": self.name,
            "standard": self.standard,
            "passed": self.passed,
            "actual_value": self.actual_value,
            "message": self.message,
            "severity": self.severity,
        }


@dataclass
class QualityReport:
    """质量报告"""
    project_name: str = ""
    checks: List[CheckItem] = field(default_factory=list)
    total: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    blockers: int = 0
    overall_pass: bool = True

    def to_dict(self) -> dict:
        return {
            "project_name": self.project_name,
            "summary": {
                "total": self.total,
                "passed": self.passed,
                "failed": self.failed,
                "warnings": self.warnings,
                "blockers": self.blockers,
                "overall_pass": self.overall_pass,
            },
            "checks": [c.to_dict() for c in self.checks],
        }

    def save_json(self, output: str):
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        return output


class QualityGate:
    """质量门禁"""

    def __init__(self, project_name: str = ""):
        self.project_name = project_name
        self.report = QualityReport(project_name=project_name)
        self._check_idx = 0

    def _add_check(self, agent: str, category: str, name: str, standard: str,
                   passed: bool, actual: str = "", message: str = "", severity: str = "info"):
        item = CheckItem(
            check_id=f"qc_{self._check_idx:03d}",
            agent=agent, category=category, name=name,
            standard=standard, passed=passed,
            actual_value=actual, message=message, severity=severity,
        )
        self.report.checks.append(item)
        self._check_idx += 1

        if passed:
            self.report.passed += 1
        else:
            self.report.failed += 1
            if severity == "blocker":
                self.report.blockers += 1
                self.report.overall_pass = False
            elif severity == "warning":
                self.report.warnings += 1

        self.report.total += 1

    # =============================================
    # 视觉设计Agent检查
    # =============================================

    def check_ico_file(self, filepath: str):
        """检查.ico文件"""
        if not os.path.exists(filepath):
            self._add_check("visual", "icon", "文件存在性", "文件必须存在",
                            False, filepath, f"文件不存在: {filepath}", "blocker")
            return

        file_size = os.path.getsize(filepath)
        self._add_check("visual", "icon", "文件大小", ".ico ≤ 500KB",
                        file_size <= 500 * 1024,
                        f"{file_size / 1024:.0f}KB",
                        "文件大小合规" if file_size <= 500 * 1024 else "文件过大")

        try:
            img = Image.open(filepath)
            self._add_check("visual", "icon", "文件可读性", "ICO文件可正常打开",
                            True, f"{img.size[0]}x{img.size[1]}", "文件可正常打开")
        except Exception as e:
            self._add_check("visual", "icon", "文件可读性", "ICO文件可正常打开",
                            False, str(e), "文件无法打开", "blocker")

    def check_png_file(self, filepath: str):
        """检查.png文件"""
        if not os.path.exists(filepath):
            self._add_check("visual", "image", "文件存在性", "文件必须存在",
                            False, filepath, f"文件不存在: {filepath}", "blocker")
            return

        file_size = os.path.getsize(filepath)
        self._add_check("visual", "image", "文件大小", ".png ≤ 300KB",
                        file_size <= 300 * 1024,
                        f"{file_size / 1024:.0f}KB")

    def check_bmp_file(self, filepath: str):
        """检查.bmp文件"""
        if not os.path.exists(filepath):
            self._add_check("visual", "image", "文件存在性", "文件必须存在",
                            False, filepath, f"文件不存在: {filepath}", "blocker")
            return

        file_size = os.path.getsize(filepath)
        self._add_check("visual", "image", "文件大小", ".bmp ≤ 200KB",
                        file_size <= 200 * 1024,
                        f"{file_size / 1024:.0f}KB")

    def check_image_colors(self, filepath: str, sample_count: int = 100):
        """检查图片色值是否在AKO色彩系统内"""
        if not os.path.exists(filepath):
            return

        try:
            img = Image.open(filepath).convert("RGB")
            w, h = img.size
            step_x = max(1, w // 10)
            step_y = max(1, h // 10)

            forbidden_count = 0
            total_sampled = 0

            for x in range(0, w, step_x):
                for y in range(0, h, step_y):
                    pixel = img.getpixel((x, y))[:3]
                    total_sampled += 1
                    if pixel in FORBIDDEN_BG_COLORS:
                        forbidden_count += 1

            forbidden_ratio = forbidden_count / total_sampled if total_sampled > 0 else 0
            self._add_check("visual", "color", "禁止色检查", "禁止纯黑/纯白大面积使用",
                            forbidden_ratio < 0.05,
                            f"禁止色占比: {forbidden_ratio:.1%}",
                            "未使用禁止色" if forbidden_ratio < 0.05 else "检测到禁止色大面积使用",
                            "warning" if forbidden_ratio >= 0.05 else "info")
        except Exception:
            pass

    def check_file_naming(self, filepath: str, expected_prefix: str = "AKO_"):
        """检查文件命名规范"""
        filename = os.path.basename(filepath)
        name_ok = filename.startswith(expected_prefix) or filename.startswith(("wizard_", "splash_", "icon_", "theme_", "ui_guide_"))
        self._add_check("visual", "naming", "文件命名", f"必须符合AKO命名规范",
                        name_ok, filename,
                        "命名合规" if name_ok else f"命名不符合规范（应以{expected_prefix}开头）",
                        "warning")

    # =============================================
    # 图纸识别Agent检查
    # =============================================

    def check_recognition_coverage(self, recognition_result: dict):
        """检查识别覆盖率"""
        summary = recognition_result.get("summary", {})
        total_elements = (
            summary.get("wall_count", 0) +
            summary.get("door_count", 0) +
            summary.get("window_count", 0) +
            summary.get("room_count", 0)
        )

        self._add_check("drawing", "recognition", "识别元素数量", "至少识别出10个元素",
                        total_elements >= 10,
                        f"识别到 {total_elements} 个元素",
                        "识别数量充足" if total_elements >= 10 else "识别元素过少，请检查图纸质量",
                        "warning")

    def check_bim_geometry(self, bim_model: dict):
        """检查BIM模型几何闭合"""
        summary = bim_model.get("summary", {})
        total_elements = summary.get("total_elements", 0)

        self._add_check("drawing", "bim", "模型完整性", "BIM模型必须包含构件",
                        total_elements > 0,
                        f"构件数: {total_elements}",
                        "模型包含构件" if total_elements > 0 else "模型为空",
                        "blocker")

    def check_area_accuracy(self, rooms: list, expected_total: float = 0):
        """检查面积精度"""
        if not rooms or expected_total <= 0:
            return

        total_area = sum(r.get("area", 0) for r in rooms)
        error = abs(total_area - expected_total) / expected_total if expected_total > 0 else 0

        self._add_check("drawing", "area", "面积误差", "面积误差≤2%",
                        error <= 0.02,
                        f"误差: {error:.1%}",
                        "面积误差在允许范围内" if error <= 0.02 else "面积误差超标",
                        "warning")

    # =============================================
    # 建筑性能分析Agent检查
    # =============================================

    def check_energy_convergence(self, energy_result: dict):
        """检查能耗模拟收敛性"""
        total = energy_result.get("total_energy", 0)
        self._add_check("analysis", "energy", "模拟收敛性", "能耗值在合理范围内",
                        10 < total < 500,
                        f"年能耗: {total:.1f} kWh/m².a",
                        "能耗值合理" if 10 < total < 500 else "能耗值异常，请检查输入参数",
                        "warning")

    def check_weather_data(self, location: str):
        """检查气象数据匹配"""
        valid_cities = ["北京", "上海", "广州", "深圳", "贵阳", "成都", "武汉",
                        "杭州", "南京", "重庆", "西安", "长沙", "郑州", "天津"]
        matched = any(city in location for city in valid_cities)
        self._add_check("analysis", "weather", "气象数据", "项目所在地必须有对应气象数据",
                        matched, location,
                        "气象数据匹配成功" if matched else f"未找到'{location}'的气象数据，请确认城市名",
                        "warning")

    def check_compliance_standard(self, standard: str):
        """检查审查标准版本"""
        valid_standards = ["GB/T_50378_2019", "GB_50189_2015", "GB_50176_2016",
                           "GB_50033_2013", "GB_50118_2010"]
        valid = standard in valid_standards
        self._add_check("analysis", "compliance", "标准版本", "必须指定有效标准版本",
                        valid, standard,
                        "标准版本有效" if valid else f"未知标准: {standard}",
                        "warning")

    def check_result_reasonability(self, energy_per_area: float, building_type: str = "office"):
        """检查结果合理性"""
        limits = {"office": (30, 200), "residential": (15, 100), "commercial": (50, 300), "education": (25, 150)}
        low, high = limits.get(building_type, (20, 250))
        reasonable = low <= energy_per_area <= high
        self._add_check("analysis", "result", "结果合理性", "能耗指标在同类建筑±30%范围内",
                        reasonable,
                        f"{energy_per_area:.1f} kWh/m².a",
                        "结果合理" if reasonable else "结果异常，请人工复核",
                        "warning")

    # =============================================
    # 汇总
    # =============================================

    def generate_summary(self) -> str:
        """生成质量检查摘要"""
        r = self.report
        status = "通过" if r.overall_pass else "未通过"
        lines = [
            f"=== 质量检查报告: {self.project_name} ===",
            f"状态: {status}",
            f"检查总数: {r.total}",
            f"  通过: {r.passed}",
            f"  未通过: {r.failed}",
            f"  阻断项: {r.blockers}",
            f"",
        ]

        if r.failed > 0:
            lines.append("--- 未通过项 ---")
            for c in r.checks:
                if not c.passed:
                    mark = "!!" if c.severity == "blocker" else "!"
                    lines.append(f"  [{mark}] [{c.agent}] {c.name}: {c.message}")

        return "\n".join(lines)

    def final_report(self) -> QualityReport:
        """返回最终报告"""
        return self.report
