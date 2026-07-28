"""
AKO 向导图生成器 - 3套模板
模板: standard（标准）、modern（现代）、minimal（极简）
"""

import os
import math
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont

from ako_colors import (
    AKO_COLORS, CREAM_GOLD, AMBER_GOLD, MOLTEN_GOLD,
    N900, N800, N700, N600, N500, N400, N300, N200, N100
)


# =============================================
# 模板定义
# =============================================
TEMPLATES = {
    "standard": {
        "name": "标准模板",
        "bg_color": CREAM_GOLD.rgb,
        "accent_color": AMBER_GOLD.rgb,
        "text_color": N900.rgb,
        "border_color": N500.rgb,
    },
    "modern": {
        "name": "现代模板",
        "bg_color": N200.rgb,
        "accent_color": MOLTEN_GOLD.rgb,
        "text_color": N800.rgb,
        "border_color": N400.rgb,
    },
    "minimal": {
        "name": "极简模板",
        "bg_color": N100.rgb,
        "accent_color": AMBER_GOLD.rgb,
        "text_color": N700.rgb,
        "border_color": N300.rgb,
    },
}


def _get_font(size: int, bold: bool = False):
    """获取字体"""
    weight = "bold" if bold else "regular"
    font_candidates = [
        ("msyhbd.ttc" if bold else "msyh.ttc", "Microsoft YaHei"),
        ("arialbd.ttf" if bold else "arial.ttf", "Arial"),
    ]
    for fname, fallback in font_candidates:
        try:
            return ImageFont.truetype(fname, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _draw_text_centered(draw: ImageDraw.Draw, text: str, y: int, width: int,
                        font: ImageFont.FreeTypeFont, fill: Tuple):
    """居中绘制文字"""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (width - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)


def _draw_text_in_region(draw: ImageDraw.Draw, text: str, x_offset: int, y: int,
                         region_width: int, font: ImageFont.FreeTypeFont, fill: Tuple):
    """在指定区域内居中绘制文字"""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = x_offset + (region_width - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)


def _draw_brand_mark(draw: ImageDraw.Draw, x: int, y: int, size: int, color: Tuple):
    """绘制AKO品牌标记（简化三角A）"""
    # 三角形
    points = [
        (x + size // 2, y),
        (x, y + size),
        (x + size, y + size),
    ]
    draw.polygon(points, fill=color)
    # 内部小三角（镂空效果）
    inner_size = size // 3
    inner_points = [
        (x + size // 2, y + inner_size),
        (x + size // 2 - inner_size // 2, y + size - inner_size // 3),
        (x + size // 2 + inner_size // 2, y + size - inner_size // 3),
    ]
    draw.polygon(inner_points, fill=N100.rgb + (200,))


class WizardGenerator:
    """向导图生成器"""

    def __init__(
        self,
        template: str = "standard",
        agent_name: str = "AKO智能体",
        client_name: str = "客户名称",
        version: str = "1.0.0",
        accent_color: Optional[Tuple] = None,
    ):
        self.template = template
        self.config = TEMPLATES.get(template, TEMPLATES["standard"])
        self.agent_name = agent_name
        self.client_name = client_name
        self.version = version
        if accent_color:
            self.config = {**self.config, "accent_color": accent_color}

    def generate_left_panel(self, output: str = "output/wizard_left.bmp") -> str:
        """生成安装向导左侧面板 (164×314px)"""
        w, h = 164, 314
        img = Image.new("RGB", (w, h), self.config["bg_color"])
        draw = ImageDraw.Draw(img)

        # 顶部品牌标记
        _draw_brand_mark(draw, w // 2 - 20, 20, 40, self.config["accent_color"])

        # 分隔线
        line_y = 75
        draw.line([(20, line_y), (w - 20, line_y)], fill=self.config["border_color"], width=1)

        # 产品名称
        font_title = _get_font(14, bold=True)
        _draw_text_centered(draw, self.agent_name, 90, w, font_title, self.config["text_color"])

        # 客户名称
        font_body = _get_font(11)
        _draw_text_centered(draw, self.client_name, 115, w, font_body, self.config["text_color"])

        # 版本号
        font_caption = _get_font(9)
        _draw_text_centered(draw, f"v{self.version}", 140, w, font_caption, self.config["accent_color"])

        # 底部装饰条
        bar_h = 4
        draw.rectangle([0, h - bar_h, w, h], fill=self.config["accent_color"])

        # 底部品牌文字
        font_brand = _get_font(8)
        _draw_text_centered(draw, "AKO_studio", h - 25, w, font_brand, self.config["border_color"])

        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        img.save(output, "BMP")
        return output

    def generate_welcome_page(self, output: str = "output/wizard_welcome.bmp") -> str:
        """生成安装向导欢迎页大图 (500×300px)"""
        w, h = 500, 300
        img = Image.new("RGB", (w, h), self.config["bg_color"])
        draw = ImageDraw.Draw(img)

        # 左侧装饰区域
        left_w = 160
        draw.rectangle([0, 0, left_w, h], fill=self.config["accent_color"])

        # 左侧品牌标记
        _draw_brand_mark(draw, left_w // 2 - 30, 40, 60,
                         self.config["bg_color"])

        # 左侧文字
        font_side = _get_font(12, bold=True)
        _draw_text_centered(draw, "AKO", 120, left_w, font_side, self.config["bg_color"])
        font_side_sm = _get_font(9)
        _draw_text_centered(draw, "studio", 140, left_w, font_side_sm, self.config["bg_color"])

        # 右侧内容区
        rx = left_w + 30
        rw = w - rx - 30

        # 欢迎标题
        font_h1 = _get_font(22, bold=True)
        _draw_text_in_region(draw, f"欢迎使用", rx, 50, rw, font_h1, self.config["text_color"])

        # 产品名称
        font_h2 = _get_font(18, bold=True)
        _draw_text_in_region(draw, self.agent_name, rx, 85, rw, font_h2, self.config["accent_color"])

        # 分隔线
        sep_y = 120
        draw.line([(rx, sep_y), (rx + rw, sep_y)], fill=self.config["border_color"], width=1)

        # 客户信息
        font_body = _get_font(13)
        _draw_text_in_region(draw, f"业主：{self.client_name}", rx, 135, rw, font_body, self.config["text_color"])

        # 版本信息
        font_caption = _get_font(11)
        _draw_text_in_region(draw, f"版本 {self.version}", rx, 160, rw, font_caption, self.config["accent_color"])

        # 提示文字
        font_hint = _get_font(10)
        _draw_text_in_region(draw, '点击「下一步」继续安装', rx, 200, rw, font_hint, self.config["border_color"])

        # 底部品牌条
        draw.rectangle([0, h - 3, w, h], fill=self.config["accent_color"])

        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        img.save(output, "BMP")
        return output

    def generate_both(self, output_dir: str = "output") -> dict:
        """同时生成左侧面板和欢迎页"""
        os.makedirs(output_dir, exist_ok=True)
        left = self.generate_left_panel(os.path.join(output_dir, f"wizard_left_{self.agent_name}_{self.client_name}.bmp"))
        welcome = self.generate_welcome_page(os.path.join(output_dir, f"wizard_welcome_{self.agent_name}_{self.client_name}.bmp"))
        return {"left_panel": left, "welcome_page": welcome}
