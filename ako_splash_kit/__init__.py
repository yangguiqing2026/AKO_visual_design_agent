"""
AKO Splash Screen 生成器 - 2套模板
模板: classic（经典）、modern（现代）
"""

import os
import math
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont

from ako_colors import (
    CREAM_GOLD, AMBER_GOLD, MOLTEN_GOLD,
    N900, N800, N700, N600, N500, N300, N200, N100
)


SPLASH_TEMPLATES = {
    "classic": {
        "name": "经典模板",
        "bg_color": CREAM_GOLD.rgb,
        "accent_color": AMBER_GOLD.rgb,
        "title_color": N900.rgb,
        "subtitle_color": N700.rgb,
        "brand_color": MOLTEN_GOLD.rgb,
    },
    "modern": {
        "name": "现代模板",
        "bg_color": N200.rgb,
        "accent_color": MOLTEN_GOLD.rgb,
        "title_color": N800,
        "subtitle_color": N600,
        "brand_color": AMBER_GOLD.rgb,
    },
}


def _get_font(size: int, bold: bool = False):
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


def _draw_text_centered(draw, text, y, width, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (width - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)


def _draw_ako_logo(draw, cx, cy, size, color):
    """绘制AKO品牌Logo（简化版：三角A + KO文字）"""
    # 三角形 A
    tri_h = int(size * 0.6)
    tri_w = int(size * 0.5)
    points = [
        (cx - tri_w, cy + tri_h // 2),
        (cx, cy - tri_h // 2),
        (cx + tri_w, cy + tri_h // 2),
    ]
    draw.polygon(points, fill=color)

    # 内部镂空小三角
    inner_h = int(tri_h * 0.35)
    inner_w = int(tri_w * 0.35)
    inner_points = [
        (cx - inner_w, cy + inner_h // 2 - 2),
        (cx, cy - inner_h // 2 + 5),
        (cx + inner_w, cy + inner_h // 2 - 2),
    ]
    bg = draw._image.getpixel((cx, cy))
    draw.polygon(inner_points, fill=bg)


class SplashGenerator:
    """Splash Screen 生成器"""

    def __init__(
        self,
        template: str = "classic",
        agent_name: str = "AKO智能体",
        client_name: str = "客户名称",
        version: str = "1.0.0",
        accent_color: Optional[Tuple] = None,
    ):
        self.template = template
        self.config = SPLASH_TEMPLATES.get(template, SPLASH_TEMPLATES["classic"])
        self.agent_name = agent_name
        self.client_name = client_name
        self.version = version
        if accent_color:
            self.config = {**self.config, "accent_color": accent_color}

    def generate(self, output: str = "output/splash.png") -> str:
        """生成 Splash Screen (600×400px)"""
        w, h = 600, 400
        img = Image.new("RGB", (w, h), self.config["bg_color"])
        draw = ImageDraw.Draw(img)

        # 顶部装饰条
        bar_h = 4
        draw.rectangle([0, 0, w, bar_h], fill=self.config["accent_color"])

        # 品牌Logo区域
        logo_y = 50
        _draw_ako_logo(draw, w // 2, logo_y + 40, 60, self.config["brand_color"])

        # 品牌名
        font_brand = _get_font(14, bold=True)
        _draw_text_centered(draw, "AKO_studio", logo_y + 80, w, font_brand, self.config["brand_color"])

        # 分隔线
        sep_y = 160
        line_half = 80
        draw.line(
            [(w // 2 - line_half, sep_y), (w // 2 + line_half, sep_y)],
            fill=self.config["accent_color"], width=1
        )

        # 产品名称（大标题）
        font_title = _get_font(28, bold=True)
        _draw_text_centered(draw, self.agent_name, 180, w, font_title, self.config["title_color"])

        # 客户名称
        font_subtitle = _get_font(16)
        _draw_text_centered(draw, self.client_name, 225, w, font_subtitle, self.config["subtitle_color"])

        # 版本号
        font_ver = _get_font(12)
        _draw_text_centered(draw, f"Version {self.version}", 260, w, font_ver, self.config["accent_color"])

        # 底部加载区域提示
        font_loading = _get_font(10)
        _draw_text_centered(draw, "正在加载...", 340, w, font_loading, self.config["subtitle_color"])

        # 底部品牌条
        draw.rectangle([0, h - bar_h, w, h], fill=self.config["accent_color"])

        # 底部版权
        font_copy = _get_font(8)
        _draw_text_centered(draw, "© AKO_studio 2026", h - 22, w, font_copy, self.config["subtitle_color"])

        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        img.save(output, "PNG")
        return output

    def generate_both_templates(self, output_dir: str = "output") -> dict:
        """为两个模板各生成一张"""
        os.makedirs(output_dir, exist_ok=True)
        results = {}
        for tpl_name in SPLASH_TEMPLATES:
            self.template = tpl_name
            self.config = SPLASH_TEMPLATES[tpl_name]
            out_path = os.path.join(output_dir, f"splash_{tpl_name}_{self.agent_name}_v{self.version}.png")
            self.generate(out_path)
            results[tpl_name] = out_path
        return results
