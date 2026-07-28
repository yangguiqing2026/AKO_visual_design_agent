"""
AKO Producer - 生产层（Layer 4）
审批通过后，按设计方案精确生产视觉资产
"""

import os
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

from ako_colors import (
    CREAM_GOLD, AMBER_GOLD, MOLTEN_GOLD,
    N900, N800, N700, N600, N500, N400, N300, N200, N100,
    SUCCESS, WARNING, ERROR, INFO
)
from perceptor import FunctionalPerceptionReport
from planner import DesignProposal
from reviewer import ApprovalRecord, APPROVED


def _get_font(size: int, bold: bool = False):
    for fname in [("msyhbd.ttc" if bold else "msyh.ttc"), ("arialbd.ttf" if bold else "arial.ttf")]:
        try:
            return ImageFont.truetype(fname, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _draw_text_centered(draw, text, y, width, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) // 2, y), text, font=font, fill=fill)


@dataclass
class ProductionResult:
    """生产结果"""
    trace_id: str = ""
    agent_name: str = ""
    version: str = ""
    produced_at: str = ""
    status: str = ""
    assets: List[dict] = field(default_factory=list)
    compliance_score: int = 0
    design_decisions: List[str] = field(default_factory=list)
    output_dir: str = ""

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "agent_name": self.agent_name,
            "version": self.version,
            "produced_at": self.produced_at,
            "status": self.status,
            "assets": self.assets,
            "compliance_score": self.compliance_score,
            "design_decisions": self.design_decisions,
            "output_dir": self.output_dir,
        }

    def save_json(self, output: str) -> str:
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        return output


class Producer:
    """生产层：审批通过后执行精确生产"""

    def __init__(self):
        pass

    def produce(self, proposal: DesignProposal, report: FunctionalPerceptionReport,
                approval: ApprovalRecord, output_dir: str = "output/production") -> ProductionResult:
        """执行生产"""
        result = ProductionResult()
        result.trace_id = proposal.trace_id
        result.agent_name = proposal.agent_name
        result.version = proposal.version
        result.produced_at = datetime.now().isoformat()
        result.output_dir = output_dir

        # 铁律：必须有APPROVED审批
        if approval.status != APPROVED:
            result.status = "REJECTED"
            result.design_decisions.append("审批未通过，拒绝生产")
            return result

        os.makedirs(output_dir, exist_ok=True)

        # Step 1: 图标生产
        icon_assets = self._produce_icons(proposal, report, output_dir)
        result.assets.extend(icon_assets)
        result.design_decisions.append(f"图标生产完成: {len(icon_assets)}个文件")

        # Step 2: 主题配色生产
        theme_assets = self._produce_theme(proposal, output_dir)
        result.assets.extend(theme_assets)
        result.design_decisions.append(f"主题配色生产完成: {len(theme_assets)}个文件")

        # Step 3: 向导图生产
        wizard_assets = self._produce_wizard(proposal, report, output_dir)
        result.assets.extend(wizard_assets)
        result.design_decisions.append(f"向导图生产完成: {len(wizard_assets)}个文件")

        # Step 4: Splash Screen 生产
        splash_assets = self._produce_splash(proposal, report, output_dir)
        result.assets.extend(splash_assets)
        result.design_decisions.append(f"Splash Screen生产完成: {len(splash_assets)}个文件")

        # Step 5: 设计决策日志
        log_path = self._produce_design_log(proposal, result, output_dir)
        result.assets.append({"type": "design_log", "path": log_path})

        # Step 6: 审批记录
        approval_path = self._produce_approval_record(approval, output_dir)
        result.assets.append({"type": "approval_record", "path": approval_path})

        result.status = "SUCCESS"
        result.compliance_score = approval.compliance_score

        return result

    def _produce_icons(self, proposal: DesignProposal, report: FunctionalPerceptionReport,
                       output_dir: str) -> List[dict]:
        """生产图标资产"""
        assets = []
        icon_dir = os.path.join(output_dir, "icons")
        os.makedirs(icon_dir, exist_ok=True)

        # 主图标 (多分辨率 .ico)
        main_icon = self._generate_main_icon(report, icon_dir)
        assets.append({"type": "main_icon", "path": main_icon, "format": "ico", "sizes": "16-256px"})

        # 任务栏图标
        taskbar_icon = self._generate_taskbar_icon(report, icon_dir)
        assets.append({"type": "taskbar_icon", "path": taskbar_icon, "format": "ico", "sizes": "16-48px"})

        # 功能图标集
        func_icons = self._generate_functional_icons(proposal, report, icon_dir)
        for fi in func_icons:
            assets.append(fi)

        return assets

    def _generate_main_icon(self, report: FunctionalPerceptionReport, icon_dir: str) -> str:
        """生成主图标 (256x256 多分辨率)"""
        size = 256
        img = Image.new("RGBA", (size, size), N100.rgb + (255,))
        draw = ImageDraw.Draw(img)

        # 六边形底色
        cx, cy = size // 2, size // 2
        r = size // 2 - 8
        points = []
        for i in range(6):
            angle = 60 * i - 30
            px = cx + r * 0.866 * (1 if i % 2 == 0 else -1) * (1 if i < 3 else -1)
            py = cy + r * 0.5 * (1 if i % 3 < 2 else -1)
            points.append((cx + int(r * 0.866 * (1 if (i % 3 == 0) else (-1 if i % 3 == 2 else 0))),
                           cy + int(r * 0.5 * (1 if i < 3 else -1))))

        # 简化：绘制圆形底色
        draw.ellipse([8, 8, size - 8, size - 8], fill=AMBER_GOLD.rgb)
        draw.ellipse([16, 16, size - 16, size - 16], fill=CREAM_GOLD.rgb)

        # 中心符号
        font = _get_font(80, bold=True)
        text = report.agent_display_name[0] if report.agent_display_name else "A"
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((cx - tw // 2, cy - th // 2 - 5), text, font=font, fill=MOLTEN_GOLD.rgb)

        # 保存多分辨率
        path = os.path.join(icon_dir, f"AKO_{report.agent_name}_icon_v{report.version}.ico")
        img.save(path, "ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        return path

    def _generate_taskbar_icon(self, report: FunctionalPerceptionReport, icon_dir: str) -> str:
        """生成任务栏图标 (48x48)"""
        size = 48
        img = Image.new("RGBA", (size, size), N100.rgb + (255,))
        draw = ImageDraw.Draw(img)

        draw.rounded_rectangle([2, 2, size - 2, size - 2], radius=8, fill=AMBER_GOLD.rgb)
        draw.rounded_rectangle([4, 4, size - 4, size - 4], radius=6, fill=CREAM_GOLD.rgb)

        font = _get_font(18, bold=True)
        text = report.agent_display_name[0] if report.agent_display_name else "A"
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((size // 2 - tw // 2, size // 2 - th // 2 - 2), text, font=font, fill=MOLTEN_GOLD.rgb)

        path = os.path.join(icon_dir, f"AKO_{report.agent_name}_taskbar_v{report.version}.ico")
        img.save(path, "ICO", sizes=[(16, 16), (32, 32), (48, 48)])
        return path

    def _generate_functional_icons(self, proposal: DesignProposal, report: FunctionalPerceptionReport,
                                   icon_dir: str) -> List[dict]:
        """生成功能图标集"""
        assets = []
        size = 24

        for i, icon_req in enumerate(proposal.icon_plan):
            img = Image.new("RGBA", (size, size), N100.rgb + (255,))
            draw = ImageDraw.Draw(img)

            # 基础圆形背景
            draw.ellipse([1, 1, size - 1, size - 1], outline=AMBER_GOLD.rgb, width=2)

            # 简化符号
            font = _get_font(10, bold=True)
            symbol = chr(0x2460 + i) if i < 10 else str(i + 1)
            bbox = draw.textbbox((0, 0), symbol, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((size // 2 - tw // 2, size // 2 - th // 2), symbol, font=font, fill=AMBER_GOLD.rgb)

            name = icon_req.split(":")[0].strip() if ":" in icon_req else f"func_{i}"
            path = os.path.join(icon_dir, f"icon_{name}_{report.agent_name}.png")
            img.save(path, "PNG")
            assets.append({"type": "functional_icon", "name": name, "path": path, "size": f"{size}x{size}"})

        return assets

    def _produce_theme(self, proposal: DesignProposal, output_dir: str) -> List[dict]:
        """生产主题配色方案"""
        assets = []
        theme_path = os.path.join(output_dir, f"theme_{proposal.agent_name}_v{proposal.version}.json")

        theme_data = {
            "name": f"{proposal.agent_name}_theme",
            "version": proposal.version,
            "template_id": proposal.template_id,
            "colors": {},
            "components": {},
        }

        # 从设计方案提取色彩
        for category, colors in proposal.color_scheme.items():
            theme_data["colors"][category] = {}
            if isinstance(colors, dict):
                for name, info in colors.items():
                    if isinstance(info, dict):
                        theme_data["colors"][category][name] = info.get("hex", "")
                    else:
                        theme_data["colors"][category][name] = str(info)

        # 组件样式
        for comp_name, comp_style in proposal.components.items():
            theme_data["components"][comp_name] = {}
            if isinstance(comp_style, dict):
                for prop, val in comp_style.items():
                    if isinstance(val, tuple):
                        theme_data["components"][comp_name][prop] = f"rgb{val}"
                    else:
                        theme_data["components"][comp_name][prop] = val

        os.makedirs(os.path.dirname(theme_path) if os.path.dirname(theme_path) else ".", exist_ok=True)
        with open(theme_path, "w", encoding="utf-8") as f:
            json.dump(theme_data, f, ensure_ascii=False, indent=2)

        assets.append({"type": "theme", "path": theme_path, "format": "json"})
        return assets

    def _produce_wizard(self, proposal: DesignProposal, report: FunctionalPerceptionReport,
                        output_dir: str) -> List[dict]:
        """生产安装向导图"""
        assets = []
        wizard_dir = os.path.join(output_dir, "wizard")
        os.makedirs(wizard_dir, exist_ok=True)

        # 左面板 (164x314)
        left_img = Image.new("RGB", (164, 314), CREAM_GOLD.rgb)
        draw = ImageDraw.Draw(left_img)

        font_brand = _get_font(20, bold=True)
        _draw_text_centered(draw, "AKO", 30, 164, font_brand, MOLTEN_GOLD.rgb)

        font_name = _get_font(14, bold=True)
        _draw_text_centered(draw, report.agent_display_name, 65, 164, font_name, N800.rgb)

        font_ver = _get_font(11)
        _draw_text_centered(draw, f"v{report.version}", 90, 164, font_ver, N600.rgb)

        # 装饰线
        draw.line([(20, 120), (144, 120)], fill=AMBER_GOLD.rgb, width=2)

        font_client = _get_font(11)
        if report.client_short:
            _draw_text_centered(draw, report.client_short, 140, 164, font_client, N700.rgb)

        left_path = os.path.join(wizard_dir, f"wizard_left_{report.agent_name}_{report.client_short}.bmp")
        left_img.save(left_path, "BMP")
        assets.append({"type": "wizard_left", "path": left_path, "size": "164x314", "format": "bmp"})

        # 欢迎页大图 (500x300)
        welcome_img = Image.new("RGB", (500, 300), N900.rgb)
        draw_w = ImageDraw.Draw(welcome_img)

        # 顶部金色装饰条
        draw_w.rectangle([0, 0, 500, 6], fill=AMBER_GOLD.rgb)

        font_welcome_title = _get_font(28, bold=True)
        _draw_text_centered(draw_w, report.agent_display_name, 50, 500, font_welcome_title, CREAM_GOLD.rgb)

        font_welcome_sub = _get_font(14)
        _draw_text_centered(draw_w, f"v{report.version}", 95, 500, font_welcome_sub, AMBER_GOLD.rgb)

        draw_w.line([(50, 130), (450, 130)], fill=AMBER_GOLD.rgb, width=1)

        if report.client_name:
            font_client_w = _get_font(12)
            _draw_text_centered(draw_w, report.client_name, 150, 500, font_client_w, N500.rgb)

        # 底部提示
        font_hint = _get_font(11)
        _draw_text_centered(draw_w, '点击「下一步」继续安装', 260, 500, font_hint, N600.rgb)

        welcome_path = os.path.join(wizard_dir, f"wizard_welcome_{report.agent_name}_{report.client_short}.bmp")
        welcome_img.save(welcome_path, "BMP")
        assets.append({"type": "wizard_welcome", "path": welcome_path, "size": "500x300", "format": "bmp"})

        return assets

    def _produce_splash(self, proposal: DesignProposal, report: FunctionalPerceptionReport,
                        output_dir: str) -> List[dict]:
        """生产 Splash Screen"""
        assets = []
        splash_dir = os.path.join(output_dir, "splash")
        os.makedirs(splash_dir, exist_ok=True)

        w, h = 600, 400
        img = Image.new("RGB", (w, h), N900.rgb)
        draw = ImageDraw.Draw(img)

        # 顶部金色装饰条
        draw.rectangle([0, 0, w, 4], fill=AMBER_GOLD.rgb)

        # 中央大标题
        font_title = _get_font(32, bold=True)
        _draw_text_centered(draw, report.agent_display_name, 80, w, font_title, CREAM_GOLD.rgb)

        # 版本号
        font_ver = _get_font(16)
        _draw_text_centered(draw, f"Version {report.version}", 130, w, font_ver, AMBER_GOLD.rgb)

        # 分隔线
        draw.line([(100, 170), (500, 170)], fill=AMBER_GOLD.rgb, width=1)

        # 客户信息
        if report.client_name:
            font_client = _get_font(13)
            _draw_text_centered(draw, report.client_name, 190, w, font_client, N500.rgb)

        # 品牌标识
        font_brand = _get_font(11)
        _draw_text_centered(draw, "Powered by AKO", 350, w, font_brand, N600.rgb)

        # 底部装饰条
        draw.rectangle([0, h - 4, w, h], fill=AMBER_GOLD.rgb)

        splash_path = os.path.join(splash_dir, f"splash_{report.agent_name}_{report.client_short}_v{report.version}.png")
        img.save(splash_path, "PNG")
        assets.append({"type": "splash", "path": splash_path, "size": "600x400", "format": "png"})

        return assets

    def _produce_design_log(self, proposal: DesignProposal, result: ProductionResult,
                            output_dir: str) -> str:
        """生成设计决策日志"""
        log_path = os.path.join(output_dir, f"design_decisions_log_{proposal.trace_id}.md")

        lines = [
            f"# 设计决策日志",
            f"",
            f"> Trace ID: {proposal.trace_id}",
            f"> Agent: {proposal.agent_name} v{proposal.version}",
            f"> 生产时间: {result.produced_at}",
            f"",
            f"## 设计决策记录",
            f"",
        ]

        for i, decision in enumerate(result.design_decisions, 1):
            lines.append(f"{i}. {decision}")

        lines.extend([
            f"",
            f"## 模板选择",
            f"",
            f"- 模板ID: {proposal.template_id}",
            f"- 界面类型: {proposal.interface_type}",
            f"",
            f"## 资产清单",
            f"",
        ])

        for asset in result.assets:
            lines.append(f"- [{asset.get('type', '?')}] {asset.get('path', '')}")

        os.makedirs(os.path.dirname(log_path) if os.path.dirname(log_path) else ".", exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return log_path

    def _produce_approval_record(self, approval: ApprovalRecord, output_dir: str) -> str:
        """保存审批记录到生产目录"""
        record_path = os.path.join(output_dir, f"approval_record_{approval.trace_id}.md")
        approval.save_markdown(record_path)
        return record_path
