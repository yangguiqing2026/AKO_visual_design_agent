"""
AKO Icon Builder — 图标生成器
作者: AKO_studio
版本: 1.0.0
"""

import os
from PIL import Image, ImageDraw


# 标准ICO尺寸列表
ICO_STANDARD_SIZES = [16, 24, 32, 48, 64, 128, 256]


class IconBuilder:
    """AKO 图标构建器"""

    def __init__(self, base_shape: str = "hexagon", inner_symbol: str = "ako",
                 primary_color: tuple = (235, 218, 185), secondary_color: tuple = (163, 140, 100),
                 size: int = 256):
        self.base_shape = base_shape
        self.inner_symbol = inner_symbol
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.size = size

    def _draw_hexagon(self, draw, size, color):
        """绘制六边形"""
        import math
        cx, cy = size / 2, size / 2
        r = size * 0.45
        points = []
        for i in range(6):
            angle = math.pi / 6 + i * math.pi / 3
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            points.append((x, y))
        draw.polygon(points, fill=color)

    def _draw_symbol(self, draw, size):
        """绘制中心符号"""
        cx, cy = size / 2, size / 2
        # 简化的 AKO 文字标记
        bar_w = size * 0.08
        bar_h = size * 0.3

        # A 字母简笔画
        draw.rectangle([cx - bar_w * 2, cy + bar_h * 0.1, cx - bar_w, cy - bar_h * 0.9], fill=self.secondary_color)
        draw.rectangle([cx + bar_w, cy + bar_h * 0.1, cx + bar_w * 2, cy - bar_h * 0.9], fill=self.secondary_color)
        draw.rectangle([cx - bar_w * 2, cy - bar_h * 0.2, cx + bar_w * 2, cy - bar_h * 0.5], fill=self.secondary_color)

    def _generate_image(self, size: int) -> Image.Image:
        """生成单尺寸图标"""
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        if self.base_shape == "hexagon":
            self._draw_hexagon(draw, size, self.primary_color)
            self._draw_symbol(draw, size)

        return img

    def generate_multi_resolution(self, sizes: list = None, output: str = "AKO_icon.ico") -> str:
        """生成多分辨率ICO文件"""
        if sizes is None:
            sizes = ICO_STANDARD_SIZES

        images = []
        for s in sizes:
            img = self._generate_image(s)
            images.append(img)

        # 保存为ICO
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        images[0].save(output, format="ICO", sizes=[(s, s) for s in sizes], append_images=images[1:])

        return os.path.abspath(output)

    def generate_png(self, output: str = "AKO_icon.png", size: int = None) -> str:
        """生成单张PNG图标"""
        if size is None:
            size = self.size
        img = self._generate_image(size)
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        img.save(output, format="PNG")
        return os.path.abspath(output)