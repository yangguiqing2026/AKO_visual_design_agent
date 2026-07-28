"""
AKO 色彩系统 - 品牌色系核心定义
继承自 AKO_visual_design_agent_whitepaper_v2.0
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class AKOColor:
    """AKO色彩定义：RGB + 名称 + 用途"""
    name: str
    rgb: Tuple[int, int, int]
    hex: str
    usage: str

    @property
    def r(self) -> int:
        return self.rgb[0]

    @property
    def g(self) -> int:
        return self.rgb[1]

    @property
    def b(self) -> int:
        return self.rgb[2]

    def to_tuple(self) -> Tuple[int, int, int]:
        return self.rgb


# =============================================
# 品牌主色 (Brand Primary)
# =============================================
CREAM_GOLD = AKOColor(
    name="奶油金",
    rgb=(235, 218, 185),
    hex="#EBDAB9",
    usage="大面积底色、启动画面背景"
)

AMBER_GOLD = AKOColor(
    name="琥珀金",
    rgb=(160, 140, 100),
    hex="#A08C64",
    usage="按钮、高亮、图标主色"
)

MOLTEN_GOLD = AKOColor(
    name="熔金",
    rgb=(185, 155, 95),
    hex="#B99B5F",
    usage="标题、关键词、hover状态"
)

# =============================================
# 功能色 (Functional Colors)
# =============================================
SUCCESS = AKOColor(
    name="成功",
    rgb=(120, 180, 140),
    hex="#78B48C",
    usage="操作成功、在线状态"
)

WARNING = AKOColor(
    name="警告",
    rgb=(220, 180, 100),
    hex="#DCB464",
    usage="需要注意、待确认"
)

ERROR = AKOColor(
    name="错误",
    rgb=(200, 100, 90),
    hex="#C8645A",
    usage="操作失败、离线状态"
)

INFO = AKOColor(
    name="信息",
    rgb=(140, 160, 180),
    hex="#8CA0B4",
    usage="提示信息、链接"
)

# =============================================
# 中性色 (Neutral Scale) - 9级灰度
# =============================================
N900 = AKOColor(name="深棕黑", rgb=(35, 30, 28), hex="#231E1C", usage="主文字、标题、Logo深色版")
N800 = AKOColor(name="炭棕", rgb=(55, 48, 44), hex="#37302C", usage="次级标题")
N700 = AKOColor(name="深灰棕", rgb=(85, 78, 72), hex="#554E48", usage="正文文字")
N600 = AKOColor(name="中灰棕", rgb=(120, 112, 104), hex="#787068", usage="辅助文字、禁用状态")
N500 = AKOColor(name="冷暖灰", rgb=(195, 190, 180), hex="#C3BEB4", usage="边框、分割线、背景")
N400 = AKOColor(name="浅灰", rgb=(210, 205, 195), hex="#D2CDC3", usage="次级背景")
N300 = AKOColor(name="淡灰", rgb=(225, 220, 210), hex="#E1DCD2", usage="卡片背景")
N200 = AKOColor(name="极浅灰", rgb=(240, 235, 225), hex="#F0EBE1", usage="页面背景")
N100 = AKOColor(name="近白", rgb=(250, 248, 244), hex="#FAF8F4", usage="纯白替代色")

# =============================================
# 色彩集合 - 用于质量门禁校验
# =============================================
BRAND_PRIMARY = {
    "cream_gold": CREAM_GOLD,
    "amber_gold": AMBER_GOLD,
    "molten_gold": MOLTEN_GOLD,
}

FUNCTIONAL = {
    "success": SUCCESS,
    "warning": WARNING,
    "error": ERROR,
    "info": INFO,
}

NEUTRAL_SCALE = {
    "N900": N900, "N800": N800, "N700": N700,
    "N600": N600, "N500": N500, "N400": N400,
    "N300": N300, "N200": N200, "N100": N100,
}

# 全部合法色值集合（用于合规检查）
ALL_VALID_COLORS = {}
ALL_VALID_COLORS.update(BRAND_PRIMARY)
ALL_VALID_COLORS.update(FUNCTIONAL)
ALL_VALID_COLORS.update(NEUTRAL_SCALE)

ALL_VALID_RGB_SET = {c.rgb for c in ALL_VALID_COLORS.values()}

# 铁律：禁止纯黑纯白大面积使用
FORBIDDEN_BG_COLORS = {
    (0, 0, 0),       # 纯黑 #000000
    (255, 255, 255),  # 纯白 #FFFFFF
}

# =============================================
# 便捷访问字典
# =============================================
AKO_COLORS = {
    # 品牌主色
    "cream_gold": CREAM_GOLD,
    "amber_gold": AMBER_GOLD,
    "molten_gold": MOLTEN_GOLD,
    # 功能色
    "success": SUCCESS,
    "warning": WARNING,
    "error": ERROR,
    "info": INFO,
    # 中性色
    "N900": N900, "N800": N800, "N700": N700,
    "N600": N600, "N500": N500, "N400": N400,
    "N300": N300, "N200": N200, "N100": N100,
}


def validate_color(rgb: Tuple[int, int, int]) -> bool:
    """检查色值是否在AKO色彩系统内"""
    return rgb in ALL_VALID_RGB_SET


def is_forbidden_background(rgb: Tuple[int, int, int]) -> bool:
    """检查是否为禁止的大面积背景色"""
    return rgb in FORBIDDEN_BG_COLORS


def get_color_by_name(name: str) -> AKOColor:
    """按名称获取颜色"""
    if name in AKO_COLORS:
        return AKO_COLORS[name]
    # 尝试中文名匹配
    for color in AKO_COLORS.values():
        if color.name == name:
            return color
    raise KeyError(f"未知颜色名称: {name}")


def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    """HEX转RGB"""
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """RGB转HEX"""
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
