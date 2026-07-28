"""
AKO 建筑性能分析引擎
提供能耗模拟、采光分析、碳排放计算、绿建合规审查
"""

import os
import json
import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from datetime import datetime


# =============================================
# 碳排放因子库
# =============================================
CARBON_FACTORS = {
    "concrete_C30": {"factor": 290, "unit": "kgCO2e/m3", "name": "混凝土C30"},
    "steel_HRB400": {"factor": 2.35, "unit": "kgCO2e/kg", "name": "钢筋HRB400"},
    "brick": {"factor": 180, "unit": "kgCO2e/m3", "name": "烧结普通砖"},
    "aluminum": {"factor": 12.8, "unit": "kgCO2e/kg", "name": "铝合金型材"},
    "glass": {"factor": 1.25, "unit": "kgCO2e/kg", "name": "平板玻璃"},
    "electricity_east": {"factor": 0.7035, "unit": "kgCO2e/kWh", "name": "电力(华东电网)"},
    "electricity_south": {"factor": 0.5810, "unit": "kgCO2e/kWh", "name": "电力(南方电网)"},
    "natural_gas": {"factor": 2.162, "unit": "kgCO2e/m3", "name": "天然气"},
}

# =============================================
# 能耗限额标准
# =============================================
ENERGY_LIMITS = {
    "office": {"constraint": 80, "guide": 60, "unit": "kWh/m2.a", "name": "办公建筑"},
    "residential": {"constraint": 45, "guide": 30, "unit": "kWh/m2.a", "name": "居住建筑"},
    "commercial": {"constraint": 120, "guide": 90, "unit": "kWh/m2.a", "name": "商业建筑"},
    "education": {"constraint": 70, "guide": 50, "unit": "kWh/m2.a", "name": "教育建筑"},
}

# =============================================
# 采光标准 (GB 50033-2013)
# =============================================
DAYLIGHT_STANDARDS = {
    "bedroom": {"df_min": 2.0, "grade": "III", "window_ratio": 1/7, "name": "卧室/起居室"},
    "kitchen": {"df_min": 1.0, "grade": "IV", "window_ratio": 1/10, "name": "厨房"},
    "office": {"df_min": 3.0, "grade": "III", "window_ratio": 1/5, "name": "办公室"},
    "classroom": {"df_min": 3.0, "grade": "III", "window_ratio": 1/5, "name": "教室"},
    "drawing_room": {"df_min": 4.0, "grade": "II", "window_ratio": 1/4, "name": "绘图室"},
}

# =============================================
# 风环境评价标准
# =============================================
WIND_STANDARDS = {
    "pedestrian_winter_max": 5.0,   # m/s
    "pedestrian_transition_max": 3.0,
    "indoor_co2_max": 1000,         # ppm
    "ventilation_residential": 1.0,  # 次/h
    "ventilation_office": 2.0,
}


# =============================================
# 数据模型
# =============================================

@dataclass
class BuildingInfo:
    """建筑基本信息"""
    project_name: str = ""
    location: str = "贵阳"
    building_type: str = "office"
    total_area: float = 0.0        # m²
    floor_count: int = 1
    floor_height: float = 3.0      # m
    window_ratio: float = 0.3      # 窗墙比
    orientation: str = "south"     # 朝向
    body_coefficient: float = 0.0  # 体型系数


@dataclass
class EnergyResult:
    """能耗模拟结果"""
    total_energy: float = 0.0      # kWh/m²·a
    cooling_load_peak: float = 0.0 # W/m²
    heating_load_peak: float = 0.0 # W/m²
    monthly_energy: List[float] = field(default_factory=list)
    energy_breakdown: Dict[str, float] = field(default_factory=dict)
    rating: str = ""
    standard: str = ""

    def to_dict(self) -> dict:
        return {
            "total_energy": round(self.total_energy, 1),
            "cooling_load_peak": round(self.cooling_load_peak, 1),
            "heating_load_peak": round(self.heating_load_peak, 1),
            "monthly_energy": [round(e, 1) for e in self.monthly_energy],
            "energy_breakdown": {k: round(v, 1) for k, v in self.energy_breakdown.items()},
            "rating": self.rating,
            "standard": self.standard,
        }


@dataclass
class DaylightResult:
    """采光分析结果"""
    average_df: float = 0.0        # 平均采光系数 %
    min_df: float = 0.0
    max_df: float = 0.0
    uniformity: float = 0.0        # 均匀度
    window_ratio_actual: float = 0.0
    compliance_rate: float = 0.0   # 达标率 %
    rooms: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "average_df": round(self.average_df, 2),
            "min_df": round(self.min_df, 2),
            "max_df": round(self.max_df, 2),
            "uniformity": round(self.uniformity, 2),
            "window_ratio_actual": round(self.window_ratio_actual, 3),
            "compliance_rate": round(self.compliance_rate, 1),
            "rooms": self.rooms,
        }


@dataclass
class CarbonResult:
    """碳排放计算结果"""
    total_carbon: float = 0.0      # kgCO2e
    per_area: float = 0.0          # kgCO2e/m²·a
    breakdown: Dict[str, float] = field(default_factory=dict)
    lifecycle_stages: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "total_carbon": round(self.total_carbon, 0),
            "per_area": round(self.per_area, 1),
            "breakdown": {k: round(v, 0) for k, v in self.breakdown.items()},
            "lifecycle_stages": {k: round(v, 0) for k, v in self.lifecycle_stages.items()},
        }


@dataclass
class ComplianceResult:
    """合规审查结果"""
    standard: str = ""
    star_rating: int = 0
    total_score: float = 0.0
    items: List[dict] = field(default_factory=list)
    non_compliant: List[dict] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "standard": self.standard,
            "star_rating": self.star_rating,
            "total_score": round(self.total_score, 1),
            "items": self.items,
            "non_compliant": self.non_compliant,
            "suggestions": self.suggestions,
        }


@dataclass
class AnalysisReport:
    """综合分析报告"""
    building: dict = field(default_factory=dict)
    energy: dict = field(default_factory=dict)
    daylight: dict = field(default_factory=dict)
    carbon: dict = field(default_factory=dict)
    compliance: dict = field(default_factory=dict)
    optimizations: List[str] = field(default_factory=list)
    generated_at: str = ""

    def save_json(self, output: str):
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            json.dump(self.__dict__, f, ensure_ascii=False, indent=2)
        return output


# =============================================
# 性能分析引擎
# =============================================

class PerformanceAnalyzer:
    """建筑性能分析器"""

    def __init__(self, building: Optional[BuildingInfo] = None):
        self.building = building or BuildingInfo()

    def run_energy_simulation(self) -> EnergyResult:
        """运行能耗模拟（简化模型）"""
        b = self.building
        result = EnergyResult()

        # 简化能耗估算模型
        base_energy = self._base_energy(b.building_type)

        # 窗墙比修正
        wr_factor = 1.0 + (b.window_ratio - 0.3) * 0.5

        # 朝向修正
        orientation_factor = {"south": 0.95, "north": 1.1, "east": 1.05, "west": 1.08}.get(b.orientation, 1.0)

        # 体型系数修正
        body_factor = 1.0 + max(0, b.body_coefficient - 0.3) * 0.3

        result.total_energy = base_energy * wr_factor * orientation_factor * body_factor

        # 负荷峰值估算
        result.cooling_load_peak = self._estimate_cooling_peak(b)
        result.heating_load_peak = self._estimate_heating_peak(b)

        # 月度分布（简化）
        result.monthly_energy = self._monthly_distribution(result.total_energy, b.location)

        # 能耗分项
        result.energy_breakdown = {
            "hvac": result.total_energy * 0.45,
            "lighting": result.total_energy * 0.25,
            "equipment": result.total_energy * 0.20,
            "hot_water": result.total_energy * 0.10,
        }

        # 对标评级
        standard = ENERGY_LIMITS.get(b.building_type, ENERGY_LIMITS["office"])
        result.standard = standard["name"]
        if result.total_energy <= standard["guide"]:
            result.rating = "优秀（低于引导值）"
        elif result.total_energy <= standard["constraint"]:
            result.rating = "达标（低于约束值）"
        else:
            result.rating = "不达标（超过约束值）"

        return result

    def run_daylight_analysis(self) -> DaylightResult:
        """运行采光分析（简化模型）"""
        b = self.building
        result = DaylightResult()

        # 简化采光系数估算
        result.average_df = b.window_ratio * 12.0  # 简化公式
        result.min_df = result.average_df * 0.4
        result.max_df = result.average_df * 1.8
        result.uniformity = result.min_df / result.average_df if result.average_df > 0 else 0
        result.window_ratio_actual = b.window_ratio

        # 各房间采光评估
        for room_type, std in DAYLIGHT_STANDARDS.items():
            room_df = result.average_df * (0.8 + hash(room_type) % 40 / 100)
            compliant = room_df >= std["df_min"]
            result.rooms.append({
                "room_type": std["name"],
                "estimated_df": round(room_df, 2),
                "standard_df": std["df_min"],
                "compliant": compliant,
            })

        compliant_count = sum(1 for r in result.rooms if r["compliant"])
        result.compliance_rate = (compliant_count / len(result.rooms) * 100) if result.rooms else 0

        return result

    def run_carbon_calculation(self) -> CarbonResult:
        """运行碳排放计算"""
        b = self.building
        result = CarbonResult()

        # 运行能耗碳排放
        energy = self.run_energy_simulation()
        electricity_factor = CARBON_FACTORS["electricity_east"]["factor"]
        annual_energy = energy.total_energy * b.total_area  # kWh/a
        operational_carbon = annual_energy * electricity_factor

        # 建材碳排放（简化估算）
        material_carbon = b.total_area * 350  # kgCO2e/m²（经验值）

        # 施工阶段
        construction_carbon = b.total_area * 30

        # 全生命周期（50年）
        lifecycle = 50
        total_operational = operational_carbon * lifecycle
        result.total_carbon = material_carbon + construction_carbon + total_operational
        result.per_area = result.total_carbon / b.total_area if b.total_area > 0 else 0

        result.breakdown = {
            "material": material_carbon,
            "construction": construction_carbon,
            "operational_50y": total_operational,
        }

        result.lifecycle_stages = {
            "A1-A3_建材生产": material_carbon,
            "A4-A5_施工建造": construction_carbon,
            "B1-B7_运行能耗": total_operational,
        }

        return result

    def run_compliance_check(self, standard: str = "GB/T_50378_2019") -> ComplianceResult:
        """运行合规审查"""
        result = ComplianceResult(standard=standard)

        energy = self.run_energy_simulation()
        daylight = self.run_daylight_analysis()

        # 评分项
        items = []

        # 1. 能耗达标
        std = ENERGY_LIMITS.get(self.building.building_type, ENERGY_LIMITS["office"])
        energy_pass = energy.total_energy <= std["constraint"]
        items.append({
            "category": "节能",
            "item": "年能耗低于约束值",
            "value": f"{energy.total_energy:.1f} kWh/m².a",
            "limit": f"≤ {std['constraint']} kWh/m².a",
            "pass": energy_pass,
            "score": 10 if energy_pass else 0,
        })

        # 2. 采光达标
        daylight_pass = daylight.compliance_rate >= 80
        items.append({
            "category": "采光",
            "item": "房间采光达标率",
            "value": f"{daylight.compliance_rate:.0f}%",
            "limit": "≥ 80%",
            "pass": daylight_pass,
            "score": 10 if daylight_pass else 0,
        })

        # 3. 窗墙比
        wr_pass = self.building.window_ratio <= 0.7
        items.append({
            "category": "围护结构",
            "item": "窗墙比",
            "value": f"{self.building.window_ratio:.2f}",
            "limit": "≤ 0.70",
            "pass": wr_pass,
            "score": 8 if wr_pass else 0,
        })

        result.items = items
        result.total_score = sum(i["score"] for i in items)

        # 不达标项
        result.non_compliant = [i for i in items if not i["pass"]]

        # 星级评估
        if result.total_score >= 80:
            result.star_rating = 3
        elif result.total_score >= 60:
            result.star_rating = 2
        elif result.total_score >= 40:
            result.star_rating = 1
        else:
            result.star_rating = 0

        # 优化建议
        result.suggestions = self._generate_suggestions(energy, daylight)

        return result

    def generate_full_report(self) -> AnalysisReport:
        """生成完整分析报告"""
        energy = self.run_energy_simulation()
        daylight = self.run_daylight_analysis()
        carbon = self.run_carbon_calculation()
        compliance = self.run_compliance_check()

        report = AnalysisReport(
            building={
                "project_name": self.building.project_name,
                "location": self.building.location,
                "building_type": self.building.building_type,
                "total_area": self.building.total_area,
                "floor_count": self.building.floor_count,
                "window_ratio": self.building.window_ratio,
                "orientation": self.building.orientation,
            },
            energy=energy.to_dict(),
            daylight=daylight.to_dict(),
            carbon=carbon.to_dict(),
            compliance=compliance.to_dict(),
            optimizations=compliance.suggestions,
            generated_at=datetime.now().isoformat(),
        )

        return report

    # ---- 内部辅助方法 ----

    def _base_energy(self, building_type: str) -> float:
        """基础能耗（kWh/m²·a）"""
        base = {"office": 75, "residential": 38, "commercial": 100, "education": 60}
        return base.get(building_type, 70)

    def _estimate_cooling_peak(self, b: BuildingInfo) -> float:
        """估算冷负荷峰值 W/m²"""
        base = {"office": 50, "residential": 35, "commercial": 65, "education": 45}
        return base.get(b.building_type, 50) * (1 + b.window_ratio * 0.3)

    def _estimate_heating_peak(self, b: BuildingInfo) -> float:
        """估算热负荷峰值 W/m²"""
        base = {"office": 40, "residential": 30, "commercial": 50, "education": 35}
        return base.get(b.building_type, 40) * (1 + (1 - b.window_ratio) * 0.2)

    def _monthly_distribution(self, total: float, location: str) -> List[float]:
        """月度能耗分布（简化）"""
        # 各月权重（冬高夏高，春秋低）
        weights = [0.12, 0.10, 0.08, 0.06, 0.05, 0.08,
                   0.12, 0.12, 0.07, 0.06, 0.07, 0.10]
        total_w = sum(weights)
        return [total * w / total_w for w in weights]

    def _generate_suggestions(self, energy: EnergyResult, daylight: DaylightResult) -> List[str]:
        """生成优化建议"""
        suggestions = []

        if energy.total_energy > ENERGY_LIMITS.get(self.building.building_type, {}).get("guide", 60):
            suggestions.append("建议增加外墙保温层厚度，降低传热系数")
            suggestions.append("建议采用高性能Low-E玻璃，降低窗体热损失")

        if self.building.window_ratio > 0.5:
            suggestions.append("窗墙比偏高，建议增设外遮阳设施")
        elif self.building.window_ratio < 0.2:
            suggestions.append("窗墙比偏低，采光可能不足，建议增大开窗面积")

        if daylight.compliance_rate < 80:
            suggestions.append("部分房间采光不达标，建议调整窗型或增加采光面积")

        if daylight.uniformity < 0.3:
            suggestions.append("采光均匀度不足，建议优化窗户分布")

        if not suggestions:
            suggestions.append("各项指标良好，建议维持当前设计方案")

        return suggestions
