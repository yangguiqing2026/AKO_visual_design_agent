"""
AKO 配色体系 - 多套成熟配色方案
基于主流设计系统（Material Design / Ant Design / Apple HIG）的配色规范
"""

from dataclasses import dataclass
from typing import Tuple, Dict


@dataclass
class ColorScheme:
    """一套完整配色方案"""
    id: str
    name: str
    description: str

    # 品牌主色
    primary: Tuple[int, int, int]       # 主色（按钮、高亮、图标）
    primary_light: Tuple[int, int, int] # 浅主色（大面积底色）
    accent: Tuple[int, int, int]        # 强调色（标题、hover）

    # 中性色
    text_dark: Tuple[int, int, int]     # 主文字
    text_body: Tuple[int, int, int]     # 正文
    text_muted: Tuple[int, int, int]    # 辅助文字
    bg_page: Tuple[int, int, int]       # 页面背景
    bg_card: Tuple[int, int, int]       # 卡片背景
    bg_input: Tuple[int, int, int]      # 输入框背景
    border: Tuple[int, int, int]        # 边框/分割线

    # 功能色
    success: Tuple[int, int, int]
    warning: Tuple[int, int, int]
    error: Tuple[int, int, int]
    info: Tuple[int, int, int]

    def to_dict(self) -> dict:
        """转为配置字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "primary": self.primary,
            "primary_light": self.primary_light,
            "accent": self.accent,
            "text_dark": self.text_dark,
            "text_body": self.text_body,
            "text_muted": self.text_muted,
            "bg_page": self.bg_page,
            "bg_card": self.bg_card,
            "bg_input": self.bg_input,
            "border": self.border,
            "success": self.success,
            "warning": self.warning,
            "error": self.error,
            "info": self.info,
        }


# =============================================
# 配色方案库
# =============================================

# 1. AKO经典金（默认） - 温暖金色系，适合建筑/工程/传统行业
AKO_CLASSIC_GOLD = ColorScheme(
    id="classic_gold",
    name="AKO经典金",
    description="温暖金色系，适合建筑/工程/传统行业",
    primary=(160, 140, 100),       # 琥珀金
    primary_light=(235, 218, 185), # 奶油金
    accent=(185, 155, 95),         # 熔金
    text_dark=(35, 30, 28),        # 深棕黑
    text_body=(85, 78, 72),        # 深灰棕
    text_muted=(120, 112, 104),    # 中灰棕
    bg_page=(240, 235, 225),       # 极浅灰
    bg_card=(250, 248, 244),       # 近白
    bg_input=(250, 248, 244),
    border=(195, 190, 180),        # 冷暖灰
    success=(120, 180, 140),
    warning=(220, 180, 100),
    error=(200, 100, 90),
    info=(140, 160, 180),
)

# 2. 科技蓝 - 专业蓝色系，适合科技/互联网/SaaS
TECH_BLUE = ColorScheme(
    id="tech_blue",
    name="科技蓝",
    description="专业蓝色系，适合科技/互联网/SaaS",
    primary=(24, 144, 255),        # Ant Blue-6
    primary_light=(230, 244, 255), # Blue-1
    accent=(64, 169, 255),         # Blue-5
    text_dark=(38, 38, 38),        # Gray-9
    text_body=(89, 89, 89),        # Gray-7
    text_muted=(140, 140, 140),    # Gray-5
    bg_page=(240, 242, 245),       # Gray-2
    bg_card=(255, 255, 255),       # White
    bg_input=(255, 255, 255),
    border=(217, 217, 217),        # Gray-4
    success=(82, 196, 26),         # Green-6
    warning=(250, 173, 20),        # Gold-6
    error=(255, 77, 79),           # Red-5
    info=(24, 144, 255),           # Blue-6
)

# 3. 商务灰 - 中性灰色系，适合金融/企业办公
BUSINESS_GRAY = ColorScheme(
    id="business_gray",
    name="商务灰",
    description="中性灰色系，适合金融/企业办公",
    primary=(47, 84, 150),         # 深蓝灰
    primary_light=(230, 235, 245), # 浅蓝灰
    accent=(66, 103, 178),         # 中蓝灰
    text_dark=(33, 37, 41),        # Gray-900
    text_body=(73, 80, 87),        # Gray-700
    text_muted=(134, 142, 150),    # Gray-500
    bg_page=(248, 249, 250),       # Gray-100
    bg_card=(255, 255, 255),
    bg_input=(255, 255, 255),
    border=(206, 212, 218),        # Gray-300
    success=(40, 167, 69),
    warning=(255, 193, 7),
    error=(220, 53, 69),
    info=(23, 162, 184),
)

# 4. 翡翠绿 - 自然绿色系，适合医疗/环保/健康
EMERALD_GREEN = ColorScheme(
    id="emerald_green",
    name="翡翠绿",
    description="自然绿色系，适合医疗/环保/健康",
    primary=(16, 185, 129),        # Emerald-500
    primary_light=(236, 253, 245), # Emerald-50
    accent=(52, 211, 153),         # Emerald-400
    text_dark=(31, 41, 55),        # Gray-800
    text_body=(75, 85, 99),        # Gray-600
    text_muted=(156, 163, 175),    # Gray-400
    bg_page=(249, 250, 251),       # Gray-50
    bg_card=(255, 255, 255),
    bg_input=(255, 255, 255),
    border=(209, 213, 219),        # Gray-300
    success=(16, 185, 129),
    warning=(245, 158, 11),
    error=(239, 68, 68),
    info=(59, 130, 246),
)

# 5. 星空紫 - 创意紫色系，适合教育/创意/设计工具
STARRY_PURPLE = ColorScheme(
    id="starry_purple",
    name="星空紫",
    description="创意紫色系，适合教育/创意/设计工具",
    primary=(124, 58, 237),        # Violet-600
    primary_light=(245, 243, 255), # Violet-50
    accent=(139, 92, 246),         # Violet-500
    text_dark=(38, 38, 38),
    text_body=(82, 82, 82),
    text_muted=(140, 140, 140),
    bg_page=(250, 250, 250),
    bg_card=(255, 255, 255),
    bg_input=(255, 255, 255),
    border=(220, 220, 220),
    success=(34, 197, 94),
    warning=(234, 179, 8),
    error=(239, 68, 68),
    info=(59, 130, 246),
)

# 6. 暖橙 - 活力橙色系，适合餐饮/服务/零售
WARM_ORANGE = ColorScheme(
    id="warm_orange",
    name="暖橙",
    description="活力橙色系，适合餐饮/服务/零售",
    primary=(234, 88, 12),         # Orange-600
    primary_light=(255, 247, 237), # Orange-50
    accent=(249, 115, 22),         # Orange-500
    text_dark=(41, 37, 36),        # Stone-800
    text_body=(87, 83, 78),        # Stone-600
    text_muted=(168, 162, 158),    # Stone-400
    bg_page=(250, 250, 249),       # Stone-50
    bg_card=(255, 255, 255),
    bg_input=(255, 255, 255),
    border=(231, 229, 228),        # Stone-200
    success=(22, 163, 74),
    warning=(202, 138, 4),
    error=(220, 38, 38),
    info=(14, 165, 233),
)

# =============================================
# 配色方案集合
# =============================================
COLOR_SCHEMES: Dict[str, ColorScheme] = {
    "classic_gold": AKO_CLASSIC_GOLD,
    "tech_blue": TECH_BLUE,
    "business_gray": BUSINESS_GRAY,
    "emerald_green": EMERALD_GREEN,
    "starry_purple": STARRY_PURPLE,
    "warm_orange": WARM_ORANGE,
}

# 默认配色
DEFAULT_SCHEME = AKO_CLASSIC_GOLD


def get_scheme_by_id(scheme_id: str) -> ColorScheme:
    """按ID获取配色方案"""
    return COLOR_SCHEMES.get(scheme_id, DEFAULT_SCHEME)


def list_schemes() -> list:
    """列出所有配色方案"""
    return list(COLOR_SCHEMES.values())
