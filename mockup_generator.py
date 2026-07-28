"""
AKO Mockup Generator - 小样文件生成器
生成5种审批用视觉小样：主界面、图标集、安装向导、暗色模式、配色方案
"""

import os
import math
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont

from ako_colors import (
    CREAM_GOLD, AMBER_GOLD, MOLTEN_GOLD,
    N900, N800, N700, N600, N500, N400, N300, N200, N100,
    SUCCESS, WARNING, ERROR, INFO
)
from perceptor import FunctionalPerceptionReport
from planner import DesignProposal


def _get_font(size: int, bold: bool = False):
    for fname in [("msyhbd.ttc" if bold else "msyh.ttc"), ("arialbd.ttf" if bold else "arial.ttf")]:
        try:
            return ImageFont.truetype(fname, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _draw_text(draw, text, x, y, font, fill):
    draw.text((x, y), text, font=font, fill=fill)


def _draw_text_centered(draw, text, y, width, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) // 2, y), text, font=font, fill=fill)


class MockupGenerator:
    """小样文件生成器"""

    def __init__(self, report: FunctionalPerceptionReport, proposal: DesignProposal):
        self.report = report
        self.proposal = proposal
        self.agent_name = report.agent_name
        self.version = report.version

    def generate_all(self, output_dir: str = "output/mockups") -> dict:
        """生成所有小样"""
        os.makedirs(output_dir, exist_ok=True)
        results = {}

        results["main"] = self.generate_main_mockup(output_dir)
        results["icons"] = self.generate_icons_mockup(output_dir)
        results["palette"] = self.generate_palette_mockup(output_dir)

        return results

    def generate_main_mockup(self, output_dir: str) -> str:
        """生成主界面小样 (1200x800)"""
        w, h = 1200, 800
        img = Image.new("RGB", (w, h), N200.rgb)
        draw = ImageDraw.Draw(img)

        template_id = self.proposal.template_id

        if template_id == "A":
            self._draw_template_a(draw, w, h)
        elif template_id == "B":
            self._draw_template_b(draw, w, h)
        elif template_id == "C":
            self._draw_template_c(draw, w, h)
        else:
            self._draw_template_a(draw, w, h)

        output = os.path.join(output_dir, f"mockup_main_{self.agent_name}_v{self.version}.png")
        img.save(output, "PNG")
        return output

    def _draw_template_a(self, draw, w, h):
        """绘制模板A：计算型/数据密集型"""
        # 标题栏
        draw.rectangle([0, 0, w, 40], fill=N900.rgb)
        font_title = _get_font(14, bold=True)
        _draw_text(draw, f"  [AKO] {self.report.agent_display_name} v{self.version}", 10, 10, font_title, N100.rgb)

        # 左侧输入区 (40%)
        left_w = int(w * 0.4)
        draw.rectangle([0, 40, left_w, h - 28], fill=CREAM_GOLD.rgb)

        font_h2 = _get_font(16, bold=True)
        _draw_text(draw, "输入参数", 60, 60, font_h2, N900.rgb)

        # 模拟输入框
        font_body = _get_font(12)
        labels = ["材料类型", "工程量", "单价(元)", "系数"]
        for i, label in enumerate(labels):
            y = 100 + i * 56
            _draw_text(draw, label, 20, y, font_body, N700.rgb)
            draw.rounded_rectangle([20, y + 20, left_w - 20, y + 48], radius=4,
                                   outline=N500.rgb, width=1, fill=N100.rgb)

        # 计算按钮
        btn_y = 100 + len(labels) * 56 + 10
        draw.rounded_rectangle([20, btn_y, left_w - 20, btn_y + 36], radius=4,
                               fill=AMBER_GOLD.rgb)
        font_btn = _get_font(13, bold=True)
        bbox = draw.textbbox((0, 0), "重新计算", font=font_btn)
        bw = bbox[2] - bbox[0]
        _draw_text(draw, "重新计算", (left_w - bw) // 2, btn_y + 8, font_btn, N900.rgb)

        # 右侧结果区 (60%)
        rx = left_w
        rw = w - left_w
        draw.rectangle([rx, 40, w, h - 28], fill=N100.rgb)

        # 结果区边框
        draw.rectangle([rx + 10, 50, w - 10, 140], outline=AMBER_GOLD.rgb, width=2)
        font_result_label = _get_font(12)
        _draw_text(draw, "计算结果", rx + 20, 58, font_result_label, N600.rgb)

        font_result = _get_font(28, bold=True)
        _draw_text(draw, "128,500.00", rx + 20, 85, font_result, MOLTEN_GOLD.rgb)
        font_unit = _get_font(14)
        _draw_text(draw, "元", rx + 230, 95, font_unit, N700.rgb)

        # 模拟表格
        table_y = 160
        font_th = _get_font(12, bold=True)
        headers = ["序号", "材料名称", "数量", "单价", "小计"]
        col_w = (rw - 40) // len(headers)
        for i, hdr in enumerate(headers):
            hx = rx + 20 + i * col_w
            draw.rectangle([hx, table_y, hx + col_w, table_y + 32], fill=N400.rgb)
            _draw_text(draw, hdr, hx + 8, table_y + 8, font_th, N800)

        # 表格数据行
        font_td = _get_font(11)
        rows = [
            ["1", "C30混凝土", "120 m3", "580", "69,600"],
            ["2", "HRB400钢筋", "8.5 t", "4,200", "35,700"],
            ["3", "模板", "450 m2", "45", "20,250"],
            ["4", "人工费", "1项", "2,950", "2,950"],
        ]
        for ri, row in enumerate(rows):
            ry = table_y + 32 + ri * 40
            bg = N200.rgb if ri % 2 == 0 else N100.rgb
            for ci, cell in enumerate(row):
                cx = rx + 20 + ci * col_w
                draw.rectangle([cx, ry, cx + col_w, ry + 40], fill=bg, outline=N500.rgb)
                _draw_text(draw, cell, cx + 8, ry + 12, font_td, N700.rgb)

        # 操作按钮
        btn_y2 = table_y + 32 + len(rows) * 40 + 20
        draw.rounded_rectangle([rx + 20, btn_y2, rx + 120, btn_y2 + 32], radius=4, fill=AMBER_GOLD.rgb)
        _draw_text(draw, "导出PDF", rx + 35, btn_y2 + 7, _get_font(12, bold=True), N900.rgb)

        draw.rounded_rectangle([rx + 140, btn_y2, rx + 240, btn_y2 + 32], radius=4, fill=N300.rgb)
        _draw_text(draw, "保存历史", rx + 155, btn_y2 + 7, _get_font(12), N700.rgb)

        # 状态栏
        draw.rectangle([0, h - 28, w, h], fill=N500.rgb)
        font_status = _get_font(10)
        _draw_text(draw, f"  当前项目: {self.report.client_short} | 最后计算: 2026-07-28 14:30 | 在线", 5, h - 22, font_status, N700.rgb)

    def _draw_template_b(self, draw, w, h):
        """绘制模板B：仪表盘/监控型"""
        # 标题栏
        draw.rectangle([0, 0, w, 40], fill=N900.rgb)
        font_title = _get_font(14, bold=True)
        _draw_text(draw, f"  [AKO] {self.report.agent_display_name} v{self.version}", 10, 10, font_title, N100.rgb)

        # 指标卡区域
        card_y = 50
        card_h = 100
        card_count = 4
        card_gap = 16
        card_w = (w - 40 - (card_count - 1) * card_gap) // card_count
        card_labels = ["CPU", "内存", "磁盘", "网络"]
        card_values = ["78%", "45%", "62%", "1.2G"]

        for i in range(card_count):
            cx = 20 + i * (card_w + card_gap)
            draw.rounded_rectangle([cx, card_y, cx + card_w, card_y + card_h],
                                   radius=8, fill=N100.rgb, outline=AMBER_GOLD.rgb, width=2)
            font_label = _get_font(11)
            _draw_text(draw, card_labels[i], cx + 15, card_y + 12, font_label, N600.rgb)
            font_val = _get_font(26, bold=True)
            _draw_text(draw, card_values[i], cx + 15, card_y + 38, font_val, MOLTEN_GOLD.rgb)

        # 图表区域 (左60%)
        chart_w = int(w * 0.6)
        chart_y = card_y + card_h + 16
        chart_h = h - chart_y - 40
        draw.rectangle([20, chart_y, 20 + chart_w, chart_y + chart_h], fill=N900.rgb)
        font_chart_title = _get_font(12, bold=True)
        _draw_text(draw, "实时数据趋势", 30, chart_y + 8, font_chart_title, AMBER_GOLD.rgb)

        # 模拟折线
        points = []
        for i in range(20):
            px = 40 + i * (chart_w - 40) // 19
            py = chart_y + chart_h // 2 + int(30 * math.sin(i * 0.5))
            points.append((px, py))
        if len(points) > 1:
            draw.line(points, fill=AMBER_GOLD.rgb, width=2)

        # 网格线
        for i in range(4):
            gy = chart_y + 40 + i * (chart_h - 60) // 3
            draw.line([(40, gy), (chart_w, gy)], fill=N700.rgb, width=1)

        # 告警日志 (右40%)
        log_x = 30 + chart_w
        log_w = w - log_x - 20
        font_log_title = _get_font(12, bold=True)
        _draw_text(draw, "告警日志", log_x, chart_y + 8, font_log_title, N800)

        log_items = [
            (SUCCESS.rgb, "14:30:05 节点A 恢复正常"),
            (WARNING.rgb, "14:28:12 节点C CPU使用率>90%"),
            (ERROR.rgb, "14:25:33 节点B 连接超时"),
            (SUCCESS.rgb, "14:20:00 系统启动完成"),
            (N500.rgb, "14:15:00 监控服务初始化"),
        ]
        font_log = _get_font(10)
        for i, (color, text) in enumerate(log_items):
            ly = chart_y + 30 + i * 32
            draw.ellipse([log_x, ly + 4, log_x + 10, ly + 14], fill=color)
            _draw_text(draw, text, log_x + 16, ly + 2, font_log, N700.rgb)

        # 状态栏
        draw.rectangle([0, h - 28, w, h], fill=N800.rgb)
        font_status = _get_font(10)
        _draw_text(draw, "  监控节点: 128 | 最后刷新: 14:30:05 | 告警: 2", 5, h - 22, font_status, N500.rgb)

    def _draw_template_c(self, draw, w, h):
        """绘制模板C：编辑/空间型"""
        # 标题栏
        draw.rectangle([0, 0, w, 40], fill=N900.rgb)
        font_title = _get_font(14, bold=True)
        _draw_text(draw, f"  [AKO] {self.report.agent_display_name} v{self.version}  [文件] [编辑] [视图]", 10, 10, font_title, N100.rgb)

        # 左侧图层面板 (20%)
        left_w = int(w * 0.2)
        draw.rectangle([0, 40, left_w, h - 28], fill=N300.rgb)
        font_panel = _get_font(12, bold=True)
        _draw_text(draw, " 图层", 10, 50, font_panel, N800)

        layers = ["背景", "墙体", "门窗", "标注", "家具"]
        font_layer = _get_font(11)
        for i, layer in enumerate(layers):
            ly = 80 + i * 32
            bg = AMBER_GOLD.rgb if i == 1 else N300.rgb
            txt_color = N900.rgb if i == 1 else N700.rgb
            draw.rectangle([5, ly, left_w - 5, ly + 28], fill=bg)
            _draw_text(draw, f" {layer}", 10, ly + 6, font_layer, txt_color)

        # 中央画布 (60%)
        canvas_x = left_w
        canvas_w = int(w * 0.6)
        draw.rectangle([canvas_x, 40, canvas_x + canvas_w, h - 28], fill=CREAM_GOLD.rgb)

        # 网格线
        for gx in range(canvas_x, canvas_x + canvas_w, 32):
            draw.line([(gx, 40), (gx, h - 28)], fill=N500.rgb, width=1)
        for gy in range(40, h - 28, 32):
            draw.line([(canvas_x, gy), (canvas_x + canvas_w, gy)], fill=N500.rgb, width=1)

        # 模拟选中元素
        elem_x = canvas_x + canvas_w // 3
        elem_y = 200
        elem_w = 200
        elem_h = 120
        draw.rectangle([elem_x, elem_y, elem_x + elem_w, elem_y + elem_h],
                       outline=AMBER_GOLD.rgb, width=2)
        # 控制点
        hs = 6
        for cx, cy in [(elem_x, elem_y), (elem_x + elem_w, elem_y),
                       (elem_x, elem_y + elem_h), (elem_x + elem_w, elem_y + elem_h)]:
            draw.rectangle([cx - hs, cy - hs, cx + hs, cy + hs], fill=AMBER_GOLD.rgb)

        # 右侧属性面板 (20%)
        right_x = canvas_x + canvas_w
        draw.rectangle([right_x, 40, w, h - 28], fill=N300.rgb)
        _draw_text(draw, " 属性", right_x + 10, 50, font_panel, N800)

        props = [("宽度", "200"), ("高度", "120"), ("角度", "0"), ("X", "400"), ("Y", "200")]
        font_prop = _get_font(11)
        for i, (label, val) in enumerate(props):
            py = 80 + i * 36
            _draw_text(draw, label, right_x + 10, py, font_prop, N600.rgb)
            draw.rounded_rectangle([right_x + 60, py - 2, w - 10, py + 22],
                                   radius=3, fill=N100.rgb, outline=N500.rgb)
            _draw_text(draw, val, right_x + 68, py + 2, font_prop, N700.rgb)

        # 状态栏
        draw.rectangle([0, h - 28, w, h], fill=N500.rgb)
        font_status = _get_font(10)
        _draw_text(draw, "  缩放: 100% | 画布: 1200x800 | 选中: 1个元素", 5, h - 22, font_status, N700.rgb)

    def generate_icons_mockup(self, output_dir: str) -> str:
        """生成图标集小样 (800x400)"""
        w, h = 800, 400
        img = Image.new("RGB", (w, h), N100.rgb)
        draw = ImageDraw.Draw(img)

        font_title = _get_font(16, bold=True)
        _draw_text(draw, f"图标集 - {self.report.agent_display_name}", 20, 15, font_title, N900.rgb)

        # 绘制图标网格
        icons = self.report.icon_requirements
        cols = 4
        icon_size = 48
        cell_w = w // cols
        cell_h = 80

        font_icon = _get_font(10)
        for i, icon_text in enumerate(icons[:12]):
            row = i // cols
            col = i % cols
            cx = col * cell_w + cell_w // 2
            cy = 60 + row * cell_h + cell_h // 2

            # 绘制简化图标占位
            draw.rounded_rectangle([cx - icon_size // 2, cy - icon_size // 2,
                                    cx + icon_size // 2, cy + icon_size // 2],
                                   radius=8, fill=CREAM_GOLD.rgb, outline=AMBER_GOLD.rgb, width=2)
            # 图标名称
            name = icon_text.split(":")[0] if ":" in icon_text else icon_text
            bbox = draw.textbbox((0, 0), name, font=font_icon)
            tw = bbox[2] - bbox[0]
            _draw_text(draw, name, cx - tw // 2, cy + icon_size // 2 + 5, font_icon, N700.rgb)

        output = os.path.join(output_dir, f"mockup_icons_{self.agent_name}_v{self.version}.png")
        img.save(output, "PNG")
        return output

    def generate_palette_mockup(self, output_dir: str) -> str:
        """生成配色方案小样 (400x600)"""
        w, h = 400, 600
        img = Image.new("RGB", (w, h), N100.rgb)
        draw = ImageDraw.Draw(img)

        font_title = _get_font(14, bold=True)
        _draw_text(draw, f"配色方案 - {self.report.agent_display_name}", 15, 10, font_title, N900.rgb)

        # 色板
        colors = [
            ("奶油金", CREAM_GOLD),
            ("琥珀金", AMBER_GOLD),
            ("熔金", MOLTEN_GOLD),
            ("成功", SUCCESS),
            ("警告", WARNING),
            ("错误", ERROR),
            ("信息", INFO),
            ("深棕黑", N900),
            ("炭棕", N800),
            ("深灰棕", N700),
            ("中灰棕", N600),
            ("冷暖灰", N500),
            ("浅灰", N400),
            ("淡灰", N300),
            ("极浅灰", N200),
            ("近白", N100),
        ]

        swatch_size = 40
        cols = 4
        font_swatch = _get_font(9)

        for i, (name, color) in enumerate(colors):
            row = i // cols
            col = i % cols
            sx = 15 + col * (w - 30) // cols
            sy = 45 + row * 65

            draw.rectangle([sx, sy, sx + swatch_size, sy + swatch_size],
                           fill=color.rgb, outline=N500.rgb)
            _draw_text(draw, name, sx, sy + swatch_size + 3, font_swatch, N700.rgb)
            _draw_text(draw, color.hex, sx, sy + swatch_size + 15, font_swatch, N600.rgb)

        output = os.path.join(output_dir, f"mockup_palette_{self.agent_name}_v{self.version}.png")
        img.save(output, "PNG")
        return output
