"""
AKO 图标语义库 - 基础20个图标定义
每个图标包含：名称、语义描述、推荐基础形状、内部符号
"""

from dataclasses import dataclass
from typing import Tuple, Optional
from ako_colors import AMBER_GOLD, CREAM_GOLD, MOLTEN_GOLD, N900


@dataclass(frozen=True)
class IconDefinition:
    """图标定义"""
    name: str           # 英文标识
    display_name: str   # 中文显示名
    semantic: str       # 语义描述
    base_shape: str     # 推荐基础形状
    inner_symbol: str   # 内部符号
    primary_color: Tuple = AMBER_GOLD.rgb
    secondary_color: Tuple = CREAM_GOLD.rgb


# =============================================
# 基础20个图标定义
# =============================================
ICON_LIBRARY = {
    # --- 通用操作 (6个) ---
    "install": IconDefinition(
        name="install",
        display_name="安装",
        semantic="向下箭头+盒子，暗示'放入'",
        base_shape="hexagon",
        inner_symbol="install",
    ),
    "launch": IconDefinition(
        name="launch",
        display_name="启动",
        semantic="播放三角形，暗示'开始运行'",
        base_shape="circle",
        inner_symbol="play",
    ),
    "settings": IconDefinition(
        name="settings",
        display_name="设置",
        semantic="齿轮，暗示'可调节'",
        base_shape="circle",
        inner_symbol="gear",
    ),
    "help": IconDefinition(
        name="help",
        display_name="帮助",
        semantic="问号+对话框，暗示'有疑问找我'",
        base_shape="circle",
        inner_symbol="help",
    ),
    "exit": IconDefinition(
        name="exit",
        display_name="退出",
        semantic="门+向外箭头，暗示'离开'而非'关闭'",
        base_shape="rounded_square",
        inner_symbol="exit",
    ),
    "save": IconDefinition(
        name="save",
        display_name="保存",
        semantic="软盘（经典语义），老用户秒懂",
        base_shape="rounded_square",
        inner_symbol="save",
    ),

    # --- 建筑专业 (6个) ---
    "building": IconDefinition(
        name="building",
        display_name="建筑",
        semantic="建筑物，暗示'建筑项目'",
        base_shape="hexagon",
        inner_symbol="building",
    ),
    "ruler": IconDefinition(
        name="ruler",
        display_name="测量",
        semantic="尺子，暗示'精确测量'",
        base_shape="hexagon",
        inner_symbol="ruler",
    ),
    "calculator": IconDefinition(
        name="calculator",
        display_name="计算",
        semantic="计算器，暗示'数值计算'",
        base_shape="rounded_square",
        inner_symbol="calculator",
    ),
    "chart": IconDefinition(
        name="chart",
        display_name="图表",
        semantic="柱状图，暗示'数据分析'",
        base_shape="rounded_square",
        inner_symbol="chart",
    ),
    "document": IconDefinition(
        name="document",
        display_name="文档",
        semantic="文档，暗示'报告/文件'",
        base_shape="rounded_square",
        inner_symbol="document",
    ),
    "search": IconDefinition(
        name="search",
        display_name="搜索",
        semantic="放大镜，暗示'查找/检索'",
        base_shape="circle",
        inner_symbol="search",
    ),

    # --- 系统功能 (4个) ---
    "home": IconDefinition(
        name="home",
        display_name="主页",
        semantic="房屋，暗示'回到起点'",
        base_shape="circle",
        inner_symbol="home",
    ),
    "folder": IconDefinition(
        name="folder",
        display_name="文件夹",
        semantic="文件夹，暗示'项目管理'",
        base_shape="rounded_square",
        inner_symbol="folder",
    ),
    "user": IconDefinition(
        name="user",
        display_name="用户",
        semantic="人像，暗示'账户/权限'",
        base_shape="circle",
        inner_symbol="user",
    ),
    "lock": IconDefinition(
        name="lock",
        display_name="安全",
        semantic="锁，暗示'安全/加密'",
        base_shape="shield",
        inner_symbol="lock",
    ),

    # --- 通信与输出 (4个) ---
    "mail": IconDefinition(
        name="mail",
        display_name="邮件",
        semantic="信封，暗示'通知/通信'",
        base_shape="rounded_square",
        inner_symbol="mail",
    ),
    "print": IconDefinition(
        name="print",
        display_name="打印",
        semantic="打印机，暗示'输出/打印'",
        base_shape="rounded_square",
        inner_symbol="print",
    ),
    "default": IconDefinition(
        name="default",
        display_name="默认",
        semantic="AKO品牌标识",
        base_shape="hexagon",
        inner_symbol="default",
    ),
    "ako_brand": IconDefinition(
        name="ako_brand",
        display_name="AKO品牌",
        semantic="AKO品牌主图标",
        base_shape="hexagon",
        inner_symbol="default",
        primary_color=AMBER_GOLD.rgb,
        secondary_color=MOLTEN_GOLD.rgb,
    ),
}


def get_icon_definition(name: str) -> IconDefinition:
    """按名称获取图标定义"""
    if name in ICON_LIBRARY:
        return ICON_LIBRARY[name]
    raise KeyError(f"未知图标: {name}，可用图标: {list(ICON_LIBRARY.keys())}")


def list_icons() -> list:
    """列出所有可用图标"""
    return list(ICON_LIBRARY.values())


def get_icon_by_semantic(semantic_keyword: str) -> Optional[IconDefinition]:
    """按语义关键词查找图标"""
    for icon in ICON_LIBRARY.values():
        if semantic_keyword in icon.semantic or semantic_keyword in icon.display_name:
            return icon
    return None
