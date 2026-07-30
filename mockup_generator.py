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
from color_schemes import ColorScheme, DEFAULT_SCHEME
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

    def __init__(self, report: FunctionalPerceptionReport, proposal: DesignProposal,
                 scheme: ColorScheme = None):
        self.report = report
        self.proposal = proposal
        self.agent_name = report.agent_name
        self.version = report.version
        self.scheme = scheme or DEFAULT_SCHEME

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
        s = self.scheme
        # 标题栏
        draw.rectangle([0, 0, w, 40], fill=s.text_dark)
        font_title = _get_font(14, bold=True)
        _draw_text(draw, f"  [AKO] {self.report.agent_display_name} v{self.version}", 10, 10, font_title, s.bg_card)

        # 左侧输入区 (40%)
        left_w = int(w * 0.4)
        draw.rectangle([0, 40, left_w, h - 28], fill=s.primary_light)

        font_h2 = _get_font(16, bold=True)
        _draw_text(draw, "输入参数", 60, 60, font_h2, s.text_dark)

        # 模拟输入框
        font_body = _get_font(12)
        labels = ["材料类型", "工程量", "单价(元)", "系数"]
        for i, label in enumerate(labels):
            y = 100 + i * 56
            _draw_text(draw, label, 20, y, font_body, s.text_body)
            draw.rounded_rectangle([20, y + 20, left_w - 20, y + 48], radius=4,
                                   outline=s.border, width=1, fill=s.bg_input)

        # 计算按钮
        btn_y = 100 + len(labels) * 56 + 10
        draw.rounded_rectangle([20, btn_y, left_w - 20, btn_y + 36], radius=4,
                               fill=s.primary)
        font_btn = _get_font(13, bold=True)
        bbox = draw.textbbox((0, 0), "重新计算", font=font_btn)
        bw = bbox[2] - bbox[0]
        _draw_text(draw, "重新计算", (left_w - bw) // 2, btn_y + 8, font_btn, s.bg_card)

        # 右侧结果区 (60%)
        rx = left_w
        rw = w - left_w
        draw.rectangle([rx, 40, w, h - 28], fill=s.bg_card)

        # 结果区边框
        draw.rectangle([rx + 10, 50, w - 10, 140], outline=s.primary, width=2)
        font_result_label = _get_font(12)
        _draw_text(draw, "计算结果", rx + 20, 58, font_result_label, s.text_muted)

        font_result = _get_font(28, bold=True)
        _draw_text(draw, "128,500.00", rx + 20, 85, font_result, s.accent)
        font_unit = _get_font(14)
        _draw_text(draw, "元", rx + 230, 95, font_unit, s.text_body)

        # 模拟表格
        table_y = 160
        font_th = _get_font(12, bold=True)
        headers = ["序号", "材料名称", "数量", "单价", "小计"]
        col_w = (rw - 40) // len(headers)
        for i, hdr in enumerate(headers):
            hx = rx + 20 + i * col_w
            draw.rectangle([hx, table_y, hx + col_w, table_y + 32], fill=s.border)
            _draw_text(draw, hdr, hx + 8, table_y + 8, font_th, s.text_dark)

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
            bg = s.bg_page if ri % 2 == 0 else s.bg_card
            for ci, cell in enumerate(row):
                cx = rx + 20 + ci * col_w
                draw.rectangle([cx, ry, cx + col_w, ry + 40], fill=bg, outline=s.border)
                _draw_text(draw, cell, cx + 8, ry + 12, font_td, s.text_body)

        # 操作按钮
        btn_y2 = table_y + 32 + len(rows) * 40 + 20
        draw.rounded_rectangle([rx + 20, btn_y2, rx + 120, btn_y2 + 32], radius=4, fill=s.primary)
        _draw_text(draw, "导出PDF", rx + 35, btn_y2 + 7, _get_font(12, bold=True), s.bg_card)

        draw.rounded_rectangle([rx + 140, btn_y2, rx + 240, btn_y2 + 32], radius=4, fill=s.bg_card)
        _draw_text(draw, "保存历史", rx + 155, btn_y2 + 7, _get_font(12), s.text_body)

        # 状态栏
        draw.rectangle([0, h - 28, w, h], fill=s.border)
        font_status = _get_font(10)
        _draw_text(draw, f"  当前项目: {self.report.client_short} | 最后计算: 2026-07-28 14:30 | 在线", 5, h - 22, font_status, s.text_body)

    def _draw_template_b(self, draw, w, h):
        """绘制模板B：仪表盘/监控型"""
        s = self.scheme
        # 标题栏
        draw.rectangle([0, 0, w, 40], fill=s.text_dark)
        font_title = _get_font(14, bold=True)
        _draw_text(draw, f"  [AKO] {self.report.agent_display_name} v{self.version}", 10, 10, font_title, s.bg_card)

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
                                   radius=8, fill=s.bg_card, outline=s.primary, width=2)
            font_label = _get_font(11)
            _draw_text(draw, card_labels[i], cx + 15, card_y + 12, font_label, s.text_muted)
            font_val = _get_font(26, bold=True)
            _draw_text(draw, card_values[i], cx + 15, card_y + 38, font_val, s.accent)

        # 图表区域 (左60%)
        chart_w = int(w * 0.6)
        chart_y = card_y + card_h + 16
        chart_h = h - chart_y - 40
        draw.rectangle([20, chart_y, 20 + chart_w, chart_y + chart_h], fill=s.text_dark)
        font_chart_title = _get_font(12, bold=True)
        _draw_text(draw, "实时数据趋势", 30, chart_y + 8, font_chart_title, s.primary)

        # 模拟折线
        points = []
        for i in range(20):
            px = 40 + i * (chart_w - 40) // 19
            py = chart_y + chart_h // 2 + int(30 * math.sin(i * 0.5))
            points.append((px, py))
        if len(points) > 1:
            draw.line(points, fill=s.primary, width=2)

        # 网格线
        for i in range(4):
            gy = chart_y + 40 + i * (chart_h - 60) // 3
            draw.line([(40, gy), (chart_w, gy)], fill=s.text_body, width=1)

        # 告警日志 (右40%)
        log_x = 30 + chart_w
        log_w = w - log_x - 20
        font_log_title = _get_font(12, bold=True)
        _draw_text(draw, "告警日志", log_x, chart_y + 8, font_log_title, s.text_dark)

        log_items = [
            (s.success, "14:30:05 节点A 恢复正常"),
            (s.warning, "14:28:12 节点C CPU使用率>90%"),
            (s.error, "14:25:33 节点B 连接超时"),
            (s.success, "14:20:00 系统启动完成"),
            (s.border, "14:15:00 监控服务初始化"),
        ]
        font_log = _get_font(10)
        for i, (color, text) in enumerate(log_items):
            ly = chart_y + 30 + i * 32
            draw.ellipse([log_x, ly + 4, log_x + 10, ly + 14], fill=color)
            _draw_text(draw, text, log_x + 16, ly + 2, font_log, s.text_body)

        # 状态栏
        draw.rectangle([0, h - 28, w, h], fill=s.text_dark)
        font_status = _get_font(10)
        _draw_text(draw, "  监控节点: 128 | 最后刷新: 14:30:05 | 告警: 2", 5, h - 22, font_status, s.border)

    def _draw_template_c(self, draw, w, h):
        """绘制模板C：编辑/空间型"""
        s = self.scheme
        # 标题栏
        draw.rectangle([0, 0, w, 40], fill=s.text_dark)
        font_title = _get_font(14, bold=True)
        _draw_text(draw, f"  [AKO] {self.report.agent_display_name} v{self.version}  [文件] [编辑] [视图]", 10, 10, font_title, s.bg_card)

        # 左侧图层面板 (20%)
        left_w = int(w * 0.2)
        draw.rectangle([0, 40, left_w, h - 28], fill=s.bg_card)
        font_panel = _get_font(12, bold=True)
        _draw_text(draw, " 图层", 10, 50, font_panel, s.text_dark)

        layers = ["背景", "墙体", "门窗", "标注", "家具"]
        font_layer = _get_font(11)
        for i, layer in enumerate(layers):
            ly = 80 + i * 32
            bg = s.primary if i == 1 else s.bg_card
            txt_color = s.bg_card if i == 1 else s.text_body
            draw.rectangle([5, ly, left_w - 5, ly + 28], fill=bg)
            _draw_text(draw, f" {layer}", 10, ly + 6, font_layer, txt_color)

        # 中央画布 (60%)
        canvas_x = left_w
        canvas_w = int(w * 0.6)
        draw.rectangle([canvas_x, 40, canvas_x + canvas_w, h - 28], fill=s.primary_light)

        # 网格线
        for gx in range(canvas_x, canvas_x + canvas_w, 32):
            draw.line([(gx, 40), (gx, h - 28)], fill=s.border, width=1)
        for gy in range(40, h - 28, 32):
            draw.line([(canvas_x, gy), (canvas_x + canvas_w, gy)], fill=s.border, width=1)

        # 模拟选中元素
        elem_x = canvas_x + canvas_w // 3
        elem_y = 200
        elem_w = 200
        elem_h = 120
        draw.rectangle([elem_x, elem_y, elem_x + elem_w, elem_y + elem_h],
                       outline=s.primary, width=2)
        # 控制点
        hs = 6
        for cx, cy in [(elem_x, elem_y), (elem_x + elem_w, elem_y),
                       (elem_x, elem_y + elem_h), (elem_x + elem_w, elem_y + elem_h)]:
            draw.rectangle([cx - hs, cy - hs, cx + hs, cy + hs], fill=s.primary)

        # 右侧属性面板 (20%)
        right_x = canvas_x + canvas_w
        draw.rectangle([right_x, 40, w, h - 28], fill=s.bg_card)
        _draw_text(draw, " 属性", right_x + 10, 50, font_panel, s.text_dark)

        props = [("宽度", "200"), ("高度", "120"), ("角度", "0"), ("X", "400"), ("Y", "200")]
        font_prop = _get_font(11)
        for i, (label, val) in enumerate(props):
            py = 80 + i * 36
            _draw_text(draw, label, right_x + 10, py, font_prop, s.text_muted)
            draw.rounded_rectangle([right_x + 60, py - 2, w - 10, py + 22],
                                   radius=3, fill=s.bg_input, outline=s.border)
            _draw_text(draw, val, right_x + 68, py + 2, font_prop, s.text_body)

        # 状态栏
        draw.rectangle([0, h - 28, w, h], fill=s.border)
        font_status = _get_font(10)
        _draw_text(draw, "  缩放: 100% | 画布: 1200x800 | 选中: 1个元素", 5, h - 22, font_status, s.text_body)

    def generate_icons_mockup(self, output_dir: str) -> str:
        """生成图标集小样 (800x400)"""
        s = self.scheme
        w, h = 800, 400
        img = Image.new("RGB", (w, h), s.bg_card)
        draw = ImageDraw.Draw(img)

        font_title = _get_font(16, bold=True)
        _draw_text(draw, f"图标集 - {self.report.agent_display_name}", 20, 15, font_title, s.text_dark)

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
                                   radius=8, fill=s.primary_light, outline=s.primary, width=2)
            # 图标名称
            name = icon_text.split(":")[0] if ":" in icon_text else icon_text
            bbox = draw.textbbox((0, 0), name, font=font_icon)
            tw = bbox[2] - bbox[0]
            _draw_text(draw, name, cx - tw // 2, cy + icon_size // 2 + 5, font_icon, s.text_body)

        output = os.path.join(output_dir, f"mockup_icons_{self.agent_name}_v{self.version}.png")
        img.save(output, "PNG")
        return output

    def generate_palette_mockup(self, output_dir: str) -> str:
        """生成配色方案小样 (400x600) - 显示当前选中色系的色板"""
        s = self.scheme
        w, h = 400, 600
        img = Image.new("RGB", (w, h), s.bg_card)
        draw = ImageDraw.Draw(img)

        font_title = _get_font(14, bold=True)
        _draw_text(draw, f"配色方案: {s.name} - {self.report.agent_display_name}", 15, 10, font_title, s.text_dark)

        # 从当前色系提取色板
        from ako_colors import rgb_to_hex
        colors = [
            ("主色", s.primary),
            ("浅主色", s.primary_light),
            ("强调色", s.accent),
            ("成功", s.success),
            ("警告", s.warning),
            ("错误", s.error),
            ("信息", s.info),
            ("主文字", s.text_dark),
            ("正文", s.text_body),
            ("辅助", s.text_muted),
            ("页面背景", s.bg_page),
            ("卡片背景", s.bg_card),
            ("输入框", s.bg_input),
            ("边框", s.border),
        ]

        swatch_size = 40
        cols = 4
        font_swatch = _get_font(9)

        for i, (name, rgb_tuple) in enumerate(colors):
            row = i // cols
            col = i % cols
            sx = 15 + col * (w - 30) // cols
            sy = 45 + row * 65

            draw.rectangle([sx, sy, sx + swatch_size, sy + swatch_size],
                           fill=rgb_tuple, outline=s.border)
            _draw_text(draw, name, sx, sy + swatch_size + 3, font_swatch, s.text_body)
            _draw_text(draw, rgb_to_hex(rgb_tuple), sx, sy + swatch_size + 15, font_swatch, s.text_muted)

        output = os.path.join(output_dir, f"mockup_palette_{self.agent_name}_v{self.version}.png")
        img.save(output, "PNG")
        return output
