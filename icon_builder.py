"""
AKO 图标构建器 - 多分辨率 .ico 生成引擎
支持从基础形状 + 内部符号组合生成多分辨率图标
"""

import math
import os
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont

from ako_colors import AKO_COLORS, AMBER_GOLD, CREAM_GOLD, MOLTEN_GOLD, N900, N100


# 标准 .ico 分辨率列表
ICO_STANDARD_SIZES = [16, 24, 32, 48, 64, 128, 256]

# 基础形状枚举
BASE_SHAPES = ["hexagon", "circle", "rounded_square", "shield", "diamond"]


class IconBuilder:
    """AKO图标构建器：从基础形状+内部符号组合生成图标"""

    def __init__(
        self,
        base_shape: str = "hexagon",
        inner_symbol: str = "default",
        primary_color: Tuple = AMBER_GOLD.rgb,
        secondary_color: Tuple = CREAM_GOLD.rgb,
        text_color: Tuple = N900.rgb,
        size: int = 256,
    ):
        self.base_shape = base_shape
        self.inner_symbol = inner_symbol
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.text_color = text_color
        self.size = size

    def _draw_base_shape(self, draw: ImageDraw.Draw, size: int, fill_color: Tuple, outline_color: Tuple):
        """绘制基础形状"""
        margin = int(size * 0.08)
        if self.base_shape == "hexagon":
            self._draw_hexagon(draw, size, margin, fill_color, outline_color)
        elif self.base_shape == "circle":
            draw.ellipse(
                [margin, margin, size - margin, size - margin],
                fill=fill_color, outline=outline_color, width=max(1, size // 64)
            )
        elif self.base_shape == "rounded_square":
            r = int(size * 0.15)
            draw.rounded_rectangle(
                [margin, margin, size - margin, size - margin],
                radius=r, fill=fill_color, outline=outline_color, width=max(1, size // 64)
            )
        elif self.base_shape == "shield":
            self._draw_shield(draw, size, margin, fill_color, outline_color)
        elif self.base_shape == "diamond":
            cx, cy = size // 2, size // 2
            r = size // 2 - margin
            points = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
            draw.polygon(points, fill=fill_color, outline=outline_color)

    def _draw_hexagon(self, draw: ImageDraw.Draw, size: int, margin: int,
                      fill_color: Tuple, outline_color: Tuple):
        """绘制六边形"""
        cx, cy = size // 2, size // 2
        r = size // 2 - margin
        points = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            points.append((x, y))
        draw.polygon(points, fill=fill_color, outline=outline_color)

    def _draw_shield(self, draw: ImageDraw.Draw, size: int, margin: int,
                     fill_color: Tuple, outline_color: Tuple):
        """绘制盾牌形状"""
        w = size - 2 * margin
        points = [
            (margin, margin),
            (margin + w, margin),
            (margin + w, margin + int(w * 0.6)),
            (margin + w // 2, size - margin),
            (margin, margin + int(w * 0.6)),
        ]
        draw.polygon(points, fill=fill_color, outline=outline_color)

    def _draw_inner_symbol(self, draw: ImageDraw.Draw, size: int, color: Tuple):
        """绘制内部符号"""
        cx, cy = size // 2, size // 2
        r = int(size * 0.25)
        lw = max(1, size // 32)

        symbols = {
            "calculator": self._symbol_calculator,
            "ruler": self._symbol_ruler,
            "building": self._symbol_building,
            "gear": self._symbol_gear,
            "play": self._symbol_play,
            "save": self._symbol_save,
            "help": self._symbol_help,
            "exit": self._symbol_exit,
            "install": self._symbol_install,
            "chart": self._symbol_chart,
            "document": self._symbol_document,
            "search": self._symbol_search,
            "home": self._symbol_home,
            "settings": self._symbol_gear,
            "folder": self._symbol_folder,
            "user": self._symbol_user,
            "lock": self._symbol_lock,
            "mail": self._symbol_mail,
            "print": self._symbol_print,
            "default": self._symbol_default,
        }

        func = symbols.get(self.inner_symbol, self._symbol_default)
        func(draw, cx, cy, r, color, lw)

    # ---- 内部符号绘制方法 ----

    def _symbol_calculator(self, draw, cx, cy, r, color, lw):
        s = int(r * 0.7)
        draw.rounded_rectangle([cx-s, cy-s, cx+s, cy+s], radius=s//5, outline=color, width=lw)
        for i in range(3):
            y = cy - s + s//2 + i * s//2
            draw.line([(cx-s+s//3, y), (cx+s-s//3, y)], fill=color, width=max(1, lw//2))

    def _symbol_ruler(self, draw, cx, cy, r, color, lw):
        s = int(r * 0.8)
        draw.rectangle([cx-s, cy-s//3, cx+s, cy+s//3], outline=color, width=lw)
        for i in range(5):
            x = cx - s + i * s // 2
            h = s//3 if i % 2 == 0 else s//5
            draw.line([(x, cy-s//3), (x, cy-s//3+h)], fill=color, width=max(1, lw//2))

    def _symbol_building(self, draw, cx, cy, r, color, lw):
        s = int(r * 0.7)
        draw.rectangle([cx-s//2, cy-s, cx+s//2, cy+s], outline=color, width=lw)
        for row in range(3):
            for col in range(2):
                wx = cx - s//4 + col * s//2
                wy = cy - s + s//3 + row * s//2
                ws = s//6
                draw.rectangle([wx-ws, wy-ws, wx+ws, wy+ws], fill=color)

    def _symbol_gear(self, draw, cx, cy, r, color, lw):
        ir = int(r * 0.35)
        or_ = int(r * 0.65)
        draw.ellipse([cx-ir, cy-ir, cx+ir, cy+ir], outline=color, width=lw)
        for i in range(6):
            angle = math.radians(60 * i)
            x1 = cx + ir * math.cos(angle)
            y1 = cy + ir * math.sin(angle)
            x2 = cx + or_ * math.cos(angle)
            y2 = cy + or_ * math.sin(angle)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=lw)

    def _symbol_play(self, draw, cx, cy, r, color, lw):
        s = int(r * 0.6)
        points = [(cx - s//2, cy - s), (cx - s//2, cy + s), (cx + s, cy)]
        draw.polygon(points, fill=color)

    def _symbol_save(self, draw, cx, cy, r, color, lw):
        s = int(r * 0.65)
        draw.rounded_rectangle([cx-s, cy-s, cx+s, cy+s], radius=s//6, outline=color, width=lw)
        draw.rectangle([cx-s//2, cy-s, cx+s//2, cy-s//3], fill=color)
        draw.rectangle([cx-s//2, cy+s//3, cx+s//2, cy+s], outline=color, width=max(1, lw//2))

    def _symbol_help(self, draw, cx, cy, r, color, lw):
        # 问号
        font_size = int(r * 1.4)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), "?", font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((cx - tw//2, cy - th//2 - bbox[1]), "?", fill=color, font=font)

    def _symbol_exit(self, draw, cx, cy, r, color, lw):
        s = int(r * 0.5)
        # 门框
        draw.rectangle([cx-s, cy-s, cx+s//2, cy+s], outline=color, width=lw)
        # 箭头
        ax = cx + s//2
        draw.line([(ax, cy), (ax + s, cy)], fill=color, width=lw)
        draw.line([(ax + s*2//3, cy - s//3), (ax + s, cy)], fill=color, width=lw)
        draw.line([(ax + s*2//3, cy + s//3), (ax + s, cy)], fill=color, width=lw)

    def _symbol_install(self, draw, cx, cy, r, color, lw):
        s = int(r * 0.6)
        # 向下箭头
        draw.line([(cx, cy - s), (cx, cy + s//2)], fill=color, width=lw)
        draw.line([(cx - s//2, cy), (cx, cy + s//2)], fill=color, width=lw)
        draw.line([(cx + s//2, cy), (cx, cy + s//2)], fill=color, width=lw)
        # 盒子
        draw.line([(cx - s, cy + s//2), (cx - s, cy + s)], fill=color, width=lw)
        draw.line([(cx + s, cy + s//2), (cx + s, cy + s)], fill=color, width=lw)
        draw.line([(cx - s, cy + s), (cx + s, cy + s)], fill=color, width=lw)

    def _symbol_chart(self, draw, cx, cy, r, color, lw):
        s = int(r * 0.6)
        # 柱状图
        bars = [(cx - s, cy + s, cx - s//2, cy - s//2),
                (cx - s//4, cy + s, cx + s//4, cy - s),
                (cx + s//2, cy + s, cx + s, cy)]
        for bar in bars:
            draw.rectangle(bar, fill=color)

    def _symbol_document(self, draw, cx, cy, r, color, lw):
        s = int(r * 0.6)
        fold = s // 3
        points = [(cx-s, cy-s), (cx+s-fold, cy-s), (cx+s, cy-s+fold),
                  (cx+s, cy+s), (cx-s, cy+s)]
        draw.polygon(points, outline=color)
        draw.line([(cx+s-fold, cy-s), (cx+s-fold, cy-s+fold), (cx+s, cy-s+fold)], fill=color, width=max(1, lw//2))
        for i in range(3):
            y = cy - s//3 + i * s//2
            draw.line([(cx-s+s//3, y), (cx+s-s//3, y)], fill=color, width=max(1, lw//2))

    def _symbol_search(self, draw, cx, cy, r, color, lw):
        sr = int(r * 0.4)
        ox, oy = cx - r//6, cy - r//6
        draw.ellipse([ox-sr, oy-sr, ox+sr, oy+sr], outline=color, width=lw)
        hx = ox + int(sr * 0.7)
        hy = oy + int(sr * 0.7)
        draw.line([(hx, hy), (hx + sr, hy + sr)], fill=color, width=lw)

    def _symbol_home(self, draw, cx, cy, r, color, lw):
        s = int(r * 0.65)
        # 屋顶
        draw.polygon([(cx, cy - s), (cx - s, cy), (cx + s, cy)], outline=color)
        # 墙体
        draw.rectangle([cx - s//2, cy, cx + s//2, cy + s//2], outline=color, width=lw)

    def _symbol_folder(self, draw, cx, cy, r, color, lw):
        s = int(r * 0.65)
        tab_h = s // 3
        draw.polygon([
            (cx - s, cy - s + tab_h), (cx - s//3, cy - s + tab_h),
            (cx - s//6, cy - s), (cx + s, cy - s),
            (cx + s, cy + s), (cx - s, cy + s)
        ], outline=color)

    def _symbol_user(self, draw, cx, cy, r, color, lw):
        hr = int(r * 0.25)
        draw.ellipse([cx - hr, cy - r//2 - hr, cx + hr, cy - r//2 + hr], outline=color, width=lw)
        draw.arc([cx - r//2, cy - r//4, cx + r//2, cy + r//2 + r//4], 0, 180, fill=color, width=lw)

    def _symbol_lock(self, draw, cx, cy, r, color, lw):
        s = int(r * 0.5)
        draw.rounded_rectangle([cx-s, cy-s//3, cx+s, cy+s], radius=s//5, outline=color, width=lw)
        draw.arc([cx-s//2, cy-s, cx+s//2, cy], 180, 0, fill=color, width=lw)

    def _symbol_mail(self, draw, cx, cy, r, color, lw):
        s = int(r * 0.65)
        draw.rectangle([cx-s, cy-s//2, cx+s, cy+s//2], outline=color, width=lw)
        draw.line([(cx-s, cy-s//2), (cx, cy+s//6)], fill=color, width=lw)
        draw.line([(cx+s, cy-s//2), (cx, cy+s//6)], fill=color, width=lw)

    def _symbol_print(self, draw, cx, cy, r, color, lw):
        s = int(r * 0.55)
        draw.rectangle([cx-s, cy-s//3, cx+s, cy+s//2], outline=color, width=lw)
        draw.rectangle([cx-s+s//3, cy-s, cx+s-s//3, cy-s//3], outline=color, width=max(1, lw//2))
        draw.rectangle([cx-s+s//3, cy+s//2, cx+s-s//3, cy+s], outline=color, width=max(1, lw//2))

    def _symbol_default(self, draw, cx, cy, r, color, lw):
        """默认符号：AKO字母组合"""
        font_size = int(r * 0.9)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            font = ImageFont.load_default()
        text = "A"
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((cx - tw//2, cy - th//2 - bbox[1]), text, fill=color, font=font)

    def generate(self, size: Optional[int] = None) -> Image.Image:
        """生成指定尺寸的图标"""
        sz = size or self.size
        img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        outline_color = self.text_color
        self._draw_base_shape(draw, sz, self.primary_color, outline_color)
        self._draw_inner_symbol(draw, sz, self.secondary_color)

        return img

    def generate_multi_resolution(
        self,
        sizes: List[int] = None,
        output: str = "output/icon.ico",
    ) -> str:
        """生成多分辨率 .ico 文件"""
        if sizes is None:
            sizes = ICO_STANDARD_SIZES

        images = []
        for s in sizes:
            img = self.generate(s)
            images.append(img)

        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)

        # Pillow ico 保存：最大尺寸256
        ico_images = []
        for img in images:
            if img.size[0] <= 256:
                ico_images.append(img)

        if ico_images:
            ico_images[0].save(
                output,
                format="ICO",
                sizes=[(img.width, img.height) for img in ico_images],
                append_images=ico_images[1:],
            )

        return output

    def generate_png(self, size: int = 256, output: str = "output/icon.png") -> str:
        """生成指定尺寸的 PNG 图标"""
        img = self.generate(size)
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        img.save(output, "PNG")
        return output
