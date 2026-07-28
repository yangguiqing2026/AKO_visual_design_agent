"""
AKO Perceptor - 需求感知层（Layer 1）
功能感知分析引擎：解析Agent功能描述 → 识别界面类型 → 提取关键设计约束
"""

import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


# =============================================
# 界面类型识别矩阵（白皮书 3.2.1）
# =============================================
INTERFACE_TYPE_MATRIX = {
    "calculation": {
        "ui_pattern": "form + result_panel",
        "interface_type": "calculation",
        "template": "A",
        "design_focus": [
            "数字突出、结果区视觉权重高",
            "输入校验反馈",
            "等宽数字字体",
        ],
    },
    "data_table": {
        "ui_pattern": "editable_table",
        "interface_type": "data_intensive",
        "template": "A",
        "design_focus": [
            "行高优化（≥40px）",
            "列宽自适应",
            "排序筛选控件",
            "斑马纹",
        ],
    },
    "chart": {
        "ui_pattern": "chart + indicator_cards",
        "interface_type": "dashboard",
        "template": "B",
        "design_focus": [
            "实时刷新",
            "状态色编码",
            "告警动画",
            "响应式布局",
        ],
    },
    "dashboard": {
        "ui_pattern": "indicator_cards + charts",
        "interface_type": "dashboard",
        "template": "B",
        "design_focus": [
            "指标卡突出",
            "趋势箭头",
            "状态灯",
            "深色模式优先",
        ],
    },
    "form": {
        "ui_pattern": "multi_step_form",
        "interface_type": "workflow",
        "template": "A",
        "design_focus": [
            "进度指示",
            "步骤导航",
            "验证状态",
            "前后跳转",
        ],
    },
    "canvas": {
        "ui_pattern": "canvas + toolbar",
        "interface_type": "editor",
        "template": "C",
        "design_focus": [
            "网格线",
            "缩放控件",
            "图层管理",
            "撤销重做",
        ],
    },
    "document": {
        "ui_pattern": "document + sidebar",
        "interface_type": "document",
        "template": "C",
        "design_focus": [
            "富文本工具条",
            "侧边目录",
            "版本对比",
            "批注",
        ],
    },
    "map": {
        "ui_pattern": "map/3d_view",
        "interface_type": "spatial",
        "template": "C",
        "design_focus": [
            "导航控件",
            "比例尺",
            "图层切换",
            "测量工具",
        ],
    },
    "chat": {
        "ui_pattern": "chat + input",
        "interface_type": "dialog",
        "template": "A",
        "design_focus": [
            "消息气泡",
            "输入框",
            "历史滚动",
            "快捷回复",
        ],
    },
    "export": {
        "ui_pattern": "button + progress + save_dialog",
        "interface_type": "calculation",
        "template": "A",
        "design_focus": [
            "进度指示明确",
            "完成反馈",
            "错误重试",
        ],
    },
    "history": {
        "ui_pattern": "list + detail_view",
        "interface_type": "data_intensive",
        "template": "A",
        "design_focus": [
            "列表项清晰",
            "详情区可读",
            "搜索筛选",
            "对比功能",
        ],
    },
}


# =============================================
# 数据密度 → 设计约束映射
# =============================================
DENSITY_RULES = {
    "very_high": {
        "row_height": 40,
        "font_size_body": 13,
        "padding": 8,
        "description": "数据极密集，行高≥40px，支持行内编辑",
    },
    "high": {
        "row_height": 36,
        "font_size_body": 14,
        "padding": 12,
        "description": "数据较密集，行高≥36px，注重数字可读性",
    },
    "medium": {
        "row_height": 32,
        "font_size_body": 14,
        "padding": 16,
        "description": "数据适中，标准间距",
    },
    "low": {
        "row_height": 28,
        "font_size_body": 15,
        "padding": 24,
        "description": "数据稀疏，加大留白，注重呼吸感",
    },
}


# =============================================
# 色彩使用规则生成器
# =============================================
def _generate_color_rules(interface_type: str, data_density: str) -> List[str]:
    """根据界面类型和数据密度生成色彩使用规则"""
    rules = [
        "大面积底色使用奶油金#EBDAB9",
        "按钮/高亮使用琥珀金#A08C64",
        "标题/关键词使用熔金#B99B5F",
        "正文文字使用深灰棕#554E48",
        "边框/分割线使用冷暖灰#C3BEB4",
    ]

    if interface_type in ("calculation", "data_intensive"):
        rules.extend([
            "高亮数字使用熔金#B99B5F",
            "校验错误使用错误红#C8645A",
            "成功计算使用成功绿#78B48C",
        ])
        if data_density in ("high", "very_high"):
            rules.append("表格斑马纹使用极浅灰#F0EBE1")

    if interface_type == "dashboard":
        rules.extend([
            "正常状态使用冷暖灰#C3BEB4",
            "警告状态使用琥珀金#DCB464",
            "错误/告警使用错误红#C8645A",
            "深色模式优先（长时间注视场景）",
        ])

    if interface_type == "editor":
        rules.extend([
            "画布背景使用奶油金#EBDAB9",
            "网格线使用冷暖灰#C3BEB4",
            "选中元素使用琥珀金#A08C64边框",
        ])

    return rules


def _generate_icon_requirements(features: List[dict]) -> List[str]:
    """根据功能列表生成图标需求"""
    icon_map = {
        "calculation": "计算器+六边形",
        "data_table": "网格+编辑笔",
        "export": "PDF文档+向下箭头",
        "history": "时钟+列表",
        "chart": "柱状图+趋势线",
        "dashboard": "仪表盘+指标卡",
        "form": "多步表单+勾选",
        "canvas": "画布+十字光标",
        "document": "文档+编辑笔",
        "chat": "对话框+气泡",
        "settings": "齿轮+调节",
        "save": "软盘（经典语义）",
        "search": "放大镜",
    }

    requirements = []
    for f in features:
        ftype = f.get("type", "")
        fname = f.get("name", "")
        if ftype in icon_map:
            requirements.append(f"{fname}：{icon_map[ftype]}")
        elif "设置" in fname:
            requirements.append(f"{fname}：{icon_map['settings']}")
        elif "保存" in fname:
            requirements.append(f"{fname}：{icon_map['save']}")
        elif "搜索" in fname:
            requirements.append(f"{fname}：{icon_map['search']}")
        else:
            requirements.append(f"{fname}：待确认语义")

    return requirements


# =============================================
# Perceptor 主类
# =============================================

@dataclass
class FunctionalPerceptionReport:
    """功能感知报告"""
    trace_id: str = ""
    agent_name: str = ""
    agent_display_name: str = ""
    version: str = ""
    client_name: str = ""
    client_short: str = ""
    timestamp: str = ""

    # 感知结果
    interface_type: str = ""
    primary_ui_pattern: str = ""
    data_density: str = "medium"
    template_id: str = "A"
    critical_interactions: List[str] = field(default_factory=list)
    visual_priorities: List[str] = field(default_factory=list)
    color_usage_rules: List[str] = field(default_factory=list)
    icon_requirements: List[str] = field(default_factory=list)
    accessibility_notes: List[str] = field(default_factory=list)
    design_focus: List[str] = field(default_factory=list)

    # 用户画像
    user_role: str = ""
    technical_level: str = "intermediate"
    daily_usage_hours: float = 4.0
    primary_device: str = "desktop_1920x1080"

    # 设计意图
    industry_tone: str = ""
    style_variance: str = "conservative"
    lighting_mode: str = "light"
    accent_preference: str = "warm"

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "agent_name": self.agent_name,
            "agent_display_name": self.agent_display_name,
            "version": self.version,
            "client_name": self.client_name,
            "client_short": self.client_short,
            "timestamp": self.timestamp,
            "functional_perception_report": {
                "interface_type": self.interface_type,
                "primary_ui_pattern": self.primary_ui_pattern,
                "data_density": self.data_density,
                "template_id": self.template_id,
                "critical_interactions": self.critical_interactions,
                "visual_priorities": self.visual_priorities,
                "color_usage_rules": self.color_usage_rules,
                "icon_requirements": self.icon_requirements,
                "accessibility_notes": self.accessibility_notes,
                "design_focus": self.design_focus,
            },
            "user_profile": {
                "role": self.user_role,
                "technical_level": self.technical_level,
                "daily_usage_hours": self.daily_usage_hours,
                "primary_device": self.primary_device,
            },
            "design_intent": {
                "industry_tone": self.industry_tone,
                "style_variance": self.style_variance,
                "lighting_mode": self.lighting_mode,
                "accent_preference": self.accent_preference,
            },
        }

    def save_json(self, output: str) -> str:
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        return output


class Perceptor:
    """需求感知层：解析Agent功能 → 输出功能感知报告"""

    def __init__(self):
        self.interface_matrix = INTERFACE_TYPE_MATRIX

    def analyze(self, input_config: dict) -> FunctionalPerceptionReport:
        """执行功能感知分析"""
        report = FunctionalPerceptionReport()

        # 基础信息
        report.trace_id = input_config.get("trace_id", f"AKO-VD-{datetime.now().strftime('%Y%m%d')}-001")
        report.agent_name = input_config.get("agent_name", "unknown")
        report.agent_display_name = input_config.get("agent_display_name", "")
        report.version = input_config.get("version", "1.0.0")
        report.client_name = input_config.get("client_name", "")
        report.client_short = input_config.get("client_short", "")
        report.timestamp = datetime.now().isoformat()

        # 解析功能列表
        features = input_config.get("features", [])
        if isinstance(features, list) and features and isinstance(features[0], str):
            features = [{"name": f, "type": self._infer_type(f)} for f in features]

        # 用户画像
        user_profile = input_config.get("user_profile", {})
        report.user_role = user_profile.get("role", "")
        report.technical_level = user_profile.get("technical_level", "intermediate")
        report.daily_usage_hours = user_profile.get("daily_usage_hours", 4.0)
        report.primary_device = user_profile.get("primary_device", "desktop_1920x1080")

        # 设计意图
        design_intent = input_config.get("design_intent", {})
        report.industry_tone = design_intent.get("industry_tone", "")
        report.style_variance = design_intent.get("style_variance", "conservative")
        report.lighting_mode = design_intent.get("lighting_mode", "light")
        report.accent_preference = design_intent.get("accent_preference", "warm")

        # 核心分析：识别界面类型
        interface_types = []
        templates = set()
        max_density = "low"

        for f in features:
            ftype = f.get("type", "")
            density = f.get("data_density", "medium")

            if ftype in self.interface_matrix:
                info = self.interface_matrix[ftype]
                interface_types.append(info["interface_type"])
                templates.add(info["template"])

                # 更新最大密度
                density_order = {"very_high": 4, "high": 3, "medium": 2, "low": 1}
                if density_order.get(density, 2) > density_order.get(max_density, 2):
                    max_density = density

        # 确定主界面类型
        if interface_types:
            from collections import Counter
            type_counts = Counter(interface_types)
            report.interface_type = " + ".join(type_counts.most_common(2)[i][0]
                                                for i in range(min(2, len(type_counts))))
            report.template_id = type_counts.most_common(1)[0][0] if templates else "A"
            # 从模板映射确定主UI模式
            primary_type = type_counts.most_common(1)[0][0]
            for ftype, info in self.interface_matrix.items():
                if info["template"] == report.template_id:
                    report.primary_ui_pattern = info["ui_pattern"]
                    report.design_focus = info["design_focus"]
                    break
        else:
            report.interface_type = "calculation"
            report.template_id = "A"
            report.primary_ui_pattern = "form + result_panel"

        report.data_density = max_density

        # 提取关键交互
        report.critical_interactions = self._extract_interactions(features)

        # 生成视觉优先级
        report.visual_priorities = self._generate_visual_priorities(report.interface_type, max_density)

        # 生成色彩使用规则
        report.color_usage_rules = _generate_color_rules(report.interface_type, max_density)

        # 生成图标需求
        report.icon_requirements = _generate_icon_requirements(features)

        # 生成可访问性备注
        report.accessibility_notes = self._generate_accessibility_notes(report.interface_type, max_density)

        return report

    def _infer_type(self, feature_name: str) -> str:
        """从功能名称推断类型"""
        name = feature_name.lower()
        if any(kw in name for kw in ["计算", "报价", "统计"]):
            return "calculation"
        if any(kw in name for kw in ["清单", "列表", "表格", "记录"]):
            return "data_table"
        if any(kw in name for kw in ["导出", "打印"]):
            return "export"
        if any(kw in name for kw in ["历史", "记录"]):
            return "history"
        if any(kw in name for kw in ["监控", "仪表", "状态"]):
            return "dashboard"
        if any(kw in name for kw in ["图表", "分析"]):
            return "chart"
        if any(kw in name for kw in ["画布", "编辑", "设计"]):
            return "canvas"
        if any(kw in name for kw in ["文档", "写作", "编辑"]):
            return "document"
        if any(kw in name for kw in ["对话", "聊天"]):
            return "chat"
        return "calculation"

    def _extract_interactions(self, features: List[dict]) -> List[str]:
        """提取关键交互"""
        interactions = []
        interaction_map = {
            "calculation": "数字输入即时校验",
            "data_table": "表格行内编辑",
            "export": "导出进度反馈",
            "history": "选择→查看→对比",
            "dashboard": "实时数据刷新",
            "chart": "图表交互筛选",
            "form": "多步表单导航",
            "canvas": "拖拽+缩放+选中",
            "document": "富文本编辑+目录跳转",
            "chat": "消息发送+历史滚动",
        }
        for f in features:
            ftype = f.get("type", "")
            if ftype in interaction_map:
                interactions.append(interaction_map[ftype])
            elif "interaction" in f:
                interactions.append(f["interaction"])
        return interactions

    def _generate_visual_priorities(self, interface_type: str, density: str) -> List[str]:
        """生成视觉优先级"""
        priorities = []
        if "calculation" in interface_type or "data" in interface_type:
            priorities.extend([
                "数字可读性 > 装饰性",
                "结果区与输入区视觉分离",
                "表格行高 >= 40px（容纳编辑控件）" if density in ("high", "very_high") else "表格行高 >= 32px",
            ])
        if "dashboard" in interface_type:
            priorities.extend([
                "状态色编码一致性",
                "告警信息视觉优先级最高",
                "指标卡数值大字体突出",
            ])
        if "editor" in interface_type:
            priorities.extend([
                "画布区域最大化",
                "工具栏不抢占注意力",
                "选中元素高亮明确",
            ])
        if not priorities:
            priorities = ["信息层级清晰", "操作路径简洁", "品牌一致性"]
        return priorities

    def _generate_accessibility_notes(self, interface_type: str, density: str) -> List[str]:
        """生成可访问性备注"""
        notes = []
        if "calculation" in interface_type or "data" in interface_type:
            notes.append("数字字体使用等宽字体（如Consolas）")
            notes.append("表格需要支持键盘导航")
        if density in ("high", "very_high"):
            notes.append("高密度数据场景需要支持缩放")
        notes.append("高对比度模式适配")
        return notes
