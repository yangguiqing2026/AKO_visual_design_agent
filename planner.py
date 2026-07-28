"""
AKO Planner - 方案规划层（Layer 2）
基于功能感知报告，生成视觉设计方案草案 + 小样文件
"""

import os
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

from ako_colors import (
    AKO_COLORS, CREAM_GOLD, AMBER_GOLD, MOLTEN_GOLD,
    N900, N800, N700, N600, N500, N400, N300, N200, N100,
    SUCCESS, WARNING, ERROR, INFO
)
from perceptor import FunctionalPerceptionReport


# =============================================
# 设计方案数据模型
# =============================================

@dataclass
class DesignProposal:
    """设计方案草案"""
    trace_id: str = ""
    agent_name: str = ""
    version: str = ""
    template_id: str = "A"
    created_at: str = ""

    # 设计概述
    overview: str = ""
    interface_type: str = ""
    layout_description: str = ""

    # 色彩方案
    color_scheme: dict = field(default_factory=dict)

    # 布局规范
    layout: dict = field(default_factory=dict)

    # 组件规范
    components: dict = field(default_factory=dict)

    # 图标方案
    icon_plan: list = field(default_factory=list)

    # 动效规范
    animation_rules: list = field(default_factory=list)

    # 小样文件路径
    mockup_files: dict = field(default_factory=dict)

    # 审批检查表
    checklist: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "agent_name": self.agent_name,
            "version": self.version,
            "template_id": self.template_id,
            "created_at": self.created_at,
            "overview": self.overview,
            "interface_type": self.interface_type,
            "layout_description": self.layout_description,
            "color_scheme": self.color_scheme,
            "layout": self.layout,
            "components": self.components,
            "icon_plan": self.icon_plan,
            "animation_rules": self.animation_rules,
            "mockup_files": self.mockup_files,
            "checklist": self.checklist,
        }

    def save_json(self, output: str) -> str:
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        return output

    def save_markdown(self, output: str) -> str:
        """保存为Markdown格式的设计方案"""
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        lines = [
            f"# 视觉设计方案草案",
            f"",
            f"> Trace ID: {self.trace_id}",
            f"> Agent: {self.agent_name} v{self.version}",
            f"> 模板: {self.template_id}",
            f"> 创建时间: {self.created_at}",
            f"",
            f"## 1. 设计概述",
            f"",
            self.overview,
            f"",
            f"**界面类型**: {self.interface_type}",
            f"",
            f"## 2. 界面架构",
            f"",
            self.layout_description,
            f"",
            f"## 3. 色彩方案",
            f"",
        ]

        for category, colors in self.color_scheme.items():
            lines.append(f"### {category}")
            lines.append("")
            if isinstance(colors, dict):
                for name, info in colors.items():
                    if isinstance(info, dict):
                        lines.append(f"- **{name}**: {info.get('hex', '')} — {info.get('usage', '')}")
                    else:
                        lines.append(f"- **{name}**: {info}")
            lines.append("")

        lines.extend([
            f"## 4. 布局规范",
            f"",
            f"```json",
            json.dumps(self.layout, ensure_ascii=False, indent=2),
            f"```",
            f"",
            f"## 5. 图标设计方案",
            f"",
        ])
        for icon in self.icon_plan:
            lines.append(f"- {icon}")
        lines.append("")

        lines.extend([
            f"## 6. 动效规范",
            f"",
        ])
        for rule in self.animation_rules:
            lines.append(f"- {rule}")
        lines.append("")

        lines.extend([
            f"## 7. 审批检查表",
            f"",
        ])
        for item in self.checklist:
            lines.append(f"- [ ] {item}")

        with open(output, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return output


# =============================================
# 界面模板定义
# =============================================

TEMPLATE_A = {
    "name": "计算型/数据密集型",
    "layout": {
        "type": "left_right_split",
        "left_ratio": 0.4,
        "right_ratio": 0.6,
        "title_bar": {"height": 40, "bg": N900.rgb, "text": N100.rgb},
        "status_bar": {"height": 28, "bg": N500.rgb, "text": N700.rgb},
        "left_panel": {"bg": CREAM_GOLD.rgb, "padding": 16},
        "right_panel": {"bg": N100.rgb, "border": AMBER_GOLD.rgb, "padding": 16},
    },
    "components": {
        "input_field": {"height": 32, "border": N500.rgb, "focus_border": AMBER_GOLD.rgb, "radius": 4},
        "button_primary": {"height": 36, "bg": AMBER_GOLD.rgb, "text": N900.rgb, "radius": 4},
        "button_secondary": {"height": 36, "bg": N300.rgb, "text": N700.rgb, "radius": 4},
        "table": {"row_height": 40, "header_bg": N400.rgb, "zebra_bg": N200.rgb, "border": N500.rgb},
        "result_display": {"font_size": 32, "font_weight": "bold", "color": MOLTEN_GOLD.rgb, "font_family": "Consolas"},
    },
}

TEMPLATE_B = {
    "name": "仪表盘/监控型",
    "layout": {
        "type": "top_cards + bottom_split",
        "card_area": {"height": 120, "bg": N200.rgb, "card_count": 4, "card_bg": N100.rgb, "card_border": AMBER_GOLD.rgb},
        "bottom_split": {"left_ratio": 0.6, "right_ratio": 0.4},
        "title_bar": {"height": 40, "bg": N900.rgb, "text": N100.rgb},
        "status_bar": {"height": 28, "bg": N800.rgb, "text": N500.rgb},
        "chart_bg": N900.rgb,
        "chart_line": AMBER_GOLD.rgb,
        "chart_grid": N500.rgb,
    },
    "components": {
        "indicator_card": {"height": 100, "bg": N100.rgb, "border": AMBER_GOLD.rgb, "value_font_size": 28, "label_font_size": 12},
        "alert_item": {"height": 32, "dot_colors": {"normal": N500.rgb, "warning": WARNING.rgb, "error": ERROR.rgb}},
        "log_list": {"row_height": 28, "bg": N200.rgb, "text": N700.rgb},
    },
}

TEMPLATE_C = {
    "name": "编辑/空间型",
    "layout": {
        "type": "three_column",
        "left_ratio": 0.2,
        "center_ratio": 0.6,
        "right_ratio": 0.2,
        "title_bar": {"height": 40, "bg": N900.rgb, "text": N100.rgb},
        "status_bar": {"height": 28, "bg": N500.rgb, "text": N700.rgb},
        "left_panel": {"bg": N300.rgb, "title": "图层/目录"},
        "center_canvas": {"bg": CREAM_GOLD.rgb, "grid_color": N500.rgb, "grid_spacing": 8},
        "right_panel": {"bg": N300.rgb, "title": "属性"},
    },
    "components": {
        "layer_item": {"height": 32, "selected_bg": AMBER_GOLD.rgb, "text": N700.rgb},
        "canvas_selection": {"border": AMBER_GOLD.rgb, "border_width": 2, "handle_size": 8},
        "property_field": {"height": 28, "label_width": 80, "input_bg": N100.rgb},
    },
}

TEMPLATES = {"A": TEMPLATE_A, "B": TEMPLATE_B, "C": TEMPLATE_C}


# =============================================
# Planner 主类
# =============================================

class Planner:
    """方案规划层：基于功能感知报告生成设计方案"""

    def __init__(self):
        self.templates = TEMPLATES

    def create_proposal(self, report: FunctionalPerceptionReport) -> DesignProposal:
        """生成设计方案草案"""
        proposal = DesignProposal()
        proposal.trace_id = report.trace_id
        proposal.agent_name = report.agent_name
        proposal.version = report.version
        proposal.template_id = report.template_id
        proposal.created_at = datetime.now().isoformat()
        proposal.interface_type = report.interface_type

        # 1. 设计概述
        template = self.templates.get(report.template_id, TEMPLATE_A)
        proposal.overview = self._generate_overview(report, template)

        # 2. 布局描述
        proposal.layout_description = self._generate_layout_description(report, template)

        # 3. 色彩方案
        proposal.color_scheme = self._generate_color_scheme(report)

        # 4. 布局规范
        proposal.layout = template["layout"]

        # 5. 组件规范
        proposal.components = template.get("components", {})

        # 6. 图标方案
        proposal.icon_plan = report.icon_requirements

        # 7. 动效规范
        proposal.animation_rules = self._generate_animation_rules(report)

        # 8. 审批检查表
        proposal.checklist = self._generate_checklist(report)

        return proposal

    def _generate_overview(self, report: FunctionalPerceptionReport, template: dict) -> str:
        """生成设计概述"""
        return (
            f"本方案为 **{report.agent_display_name}** (v{report.version}) 设计视觉界面。"
            f"\n\n"
            f"基于功能感知分析，该Agent的核心界面类型为 **{report.interface_type}**，"
            f"数据密度为 **{report.data_density}**，"
            f"匹配设计模板 **{template['name']}**（模板{report.template_id}）。"
            f"\n\n"
            f"设计重点：{'；'.join(report.design_focus[:3])}。"
            f"\n\n"
            f"目标用户为 **{report.user_role}**，"
            f"日均使用 **{report.daily_usage_hours}小时**，"
            f"主要设备为 **{report.primary_device}**。"
        )

    def _generate_layout_description(self, report: FunctionalPerceptionReport, template: dict) -> str:
        """生成布局描述"""
        layout_type = template["layout"].get("type", "")

        if layout_type == "left_right_split":
            left_pct = int(template["layout"]["left_ratio"] * 100)
            right_pct = int(template["layout"]["right_ratio"] * 100)
            return (
                f"**左右分栏布局**：\n\n"
                f"- 标题栏：深棕黑{N900.hex}背景，近白{N100.hex}文字，高度40px\n"
                f"- 左侧输入区（{left_pct}%）：奶油金{CREAM_GOLD.hex}底色，放置输入参数表单\n"
                f"- 右侧结果区（{right_pct}%）：近白{N100.hex}底色，琥珀金{AMBER_GOLD.hex}高亮边框\n"
                f"- 结果数字：熔金{MOLTEN_GOLD.hex}，32px Bold，等宽字体\n"
                f"- 状态栏：冷暖灰{N500.hex}背景，高度28px"
            )
        elif "cards" in layout_type:
            return (
                f"**顶部指标卡 + 底部双栏布局**：\n\n"
                f"- 标题栏：深棕黑背景，高度40px\n"
                f"- 顶部指标卡区域：4个指标卡并排，琥珀金边框\n"
                f"- 底部左侧（60%）：实时图表区，深棕黑背景+琥珀金线条\n"
                f"- 底部右侧（40%）：告警日志列表，状态色编码\n"
                f"- 状态栏：深棕黑背景，冷暖灰文字"
            )
        elif "three" in layout_type:
            return (
                f"**三栏布局**：\n\n"
                f"- 标题栏：深棕黑背景，高度40px\n"
                f"- 左侧面板（20%）：图层/目录面板，淡灰底色\n"
                f"- 中央画布（60%）：奶油金底色+冷暖灰网格线\n"
                f"- 右侧面板（20%）：属性面板，淡灰底色\n"
                f"- 选中元素：琥珀金2px边框 + 4角控制点\n"
                f"- 状态栏：冷暖灰背景"
            )
        return "标准布局"

    def _generate_color_scheme(self, report: FunctionalPerceptionReport) -> dict:
        """生成色彩方案"""
        scheme = {
            "品牌主色": {
                "奶油金": {"hex": CREAM_GOLD.hex, "rgb": list(CREAM_GOLD.rgb), "usage": "大面积底色"},
                "琥珀金": {"hex": AMBER_GOLD.hex, "rgb": list(AMBER_GOLD.rgb), "usage": "按钮/高亮/边框"},
                "熔金": {"hex": MOLTEN_GOLD.hex, "rgb": list(MOLTEN_GOLD.rgb), "usage": "标题/关键数字"},
            },
            "功能色": {
                "成功": {"hex": SUCCESS.hex, "usage": "操作成功/在线"},
                "警告": {"hex": WARNING.hex, "usage": "需要注意/待确认"},
                "错误": {"hex": ERROR.hex, "usage": "操作失败/告警"},
                "信息": {"hex": INFO.hex, "usage": "提示信息/链接"},
            },
            "中性色": {
                "深棕黑": {"hex": N900.hex, "usage": "标题栏/主文字"},
                "冷暖灰": {"hex": N500.hex, "usage": "边框/分割线"},
                "极浅灰": {"hex": N200.hex, "usage": "页面背景/斑马纹"},
                "近白": {"hex": N100.hex, "usage": "纯白替代"},
            },
        }

        # 根据界面类型添加特殊色彩规则
        if "dashboard" in report.interface_type:
            scheme["监控专用色"] = {
                "图表背景": {"hex": N900.hex, "usage": "折线图/面积图底色"},
                "图表线条": {"hex": AMBER_GOLD.hex, "usage": "数据线/趋势线"},
                "正常状态": {"hex": N500.hex, "usage": "状态灯-正常"},
                "告警脉冲": {"hex": WARNING.hex, "usage": "告警闪烁"},
            }

        if "editor" in report.interface_type:
            scheme["编辑专用色"] = {
                "画布底色": {"hex": CREAM_GOLD.hex, "usage": "编辑画布背景"},
                "网格线": {"hex": N500.hex, "usage": "参考网格"},
                "选中边框": {"hex": AMBER_GOLD.hex, "usage": "选中元素边框"},
            }

        return scheme

    def _generate_animation_rules(self, report: FunctionalPerceptionReport) -> list:
        """生成动效规范"""
        rules = [
            "按钮Hover: 200ms ease-out，颜色/阴影变化",
            "窗口打开: 300ms cubic-bezier(0.4,0,0.2,1)，缩放+淡入",
            "页面切换: 250ms ease-in-out，滑动过渡",
            "Splash Screen: 3000ms ease-in-out",
        ]

        if "calculation" in report.interface_type:
            rules.append("计算成功: 1000ms pulse（结果区琥珀金边框脉冲）")
            rules.append("校验错误: 300ms shake（输入框左右抖动）")

        if "dashboard" in report.interface_type:
            rules.append("告警脉冲: 2000ms 周期，琥珀金/红色交替")
            rules.append("数据刷新: 500ms fade（新数据淡入替换）")

        if "editor" in report.interface_type:
            rules.append("拖拽状态: 元素半透明+阴影跟随")
            rules.append("选中切换: 150ms ease（边框平滑过渡）")

        return rules

    def _generate_checklist(self, report: FunctionalPerceptionReport) -> list:
        """生成审批检查表"""
        return [
            f"功能匹配度：界面布局是否匹配{report.agent_display_name}核心功能？",
            f"品牌一致性：是否体现AKO暖金黄昏调？奶油金是否被正确使用？",
            f"用户体验：{report.user_role}首次使用是否能直觉理解？",
            f"数据密度：{report.data_density}密度下的行高/字号是否合理？",
            f"图标语义：每个图标是否准确传达功能含义？",
            f"色彩合规：所有色值是否在AKO色彩系统内？",
            f"暗色模式：是否需要暗色适配？（当前模式：{report.lighting_mode}）",
            f"业主定制：{report.client_short}的定制化需求是否体现？",
        ]
