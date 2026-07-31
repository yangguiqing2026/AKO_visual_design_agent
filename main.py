"""
AKO_visual_design_agent v1.2 - 主入口
功能感知型四层架构：Perceptor -> Planner -> Reviewer -> Producer
"""

import os
import sys
import json
import click
from datetime import datetime

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ako_colors import AKO_COLORS, AMBER_GOLD, CREAM_GOLD, MOLTEN_GOLD
from color_schemes import COLOR_SCHEMES, DEFAULT_SCHEME, ColorScheme, list_schemes
from icon_builder import IconBuilder, ICO_STANDARD_SIZES
from ako_icon_kit import ICON_LIBRARY, get_icon_definition, list_icons
from ako_wizard_kit import WizardGenerator, TEMPLATES
from ako_splash_kit import SplashGenerator, SPLASH_TEMPLATES
from ako_drawing_kit import DrawingParser


def _select_color_scheme(interactive: bool = True, preset_id: str = None) -> ColorScheme:
    """色系选择：交互式/预设/默认"""
    # 如果指定了预设ID，直接返回
    if preset_id and preset_id in COLOR_SCHEMES:
        return COLOR_SCHEMES[preset_id]

    schemes = list_schemes()

    if not interactive:
        return DEFAULT_SCHEME

    # 交互式选择
    print(f"\n{'='*50}")
    print(f"  配色方案选择")
    print(f"{'='*50}")
    print(f"  请选择配色方案（输入编号回车确认）:\n")

    for i, scheme in enumerate(schemes, 1):
        # 显示色系名称和描述
        print(f"    {i}. {scheme.name} - {scheme.description}")
        # 显示主色预览（用ANSI色块近似）
        p = scheme.primary
        pl = scheme.primary_light
        print(f"       主色: RGB{p}  浅底: RGB{pl}")

    print(f"\n  默认: 1 ({DEFAULT_SCHEME.name})")

    while True:
        choice = input("\n  请选择配色方案编号: ").strip()
        if not choice:
            print(f"  已选择默认: {DEFAULT_SCHEME.name}")
            return DEFAULT_SCHEME
        if choice.isdigit() and 1 <= int(choice) <= len(schemes):
            selected = schemes[int(choice) - 1]
            print(f"  已选择: {selected.name}")
            return selected
        # 尝试按ID匹配
        if choice in COLOR_SCHEMES:
            selected = COLOR_SCHEMES[choice]
            print(f"  已选择: {selected.name}")
            return selected
        print("  无效选择，请重新输入")
from element_recognizer import ElementRecognizer
from annotation_ocr import AnnotationOCR
from ako_bim_kit import BIMBuilder
from version_comparator import VersionComparator
from ako_analysis_kit import PerformanceAnalyzer, BuildingInfo
from quality_check import QualityGate

# v1.2 四层架构
from perceptor import Perceptor, FunctionalPerceptionReport
from planner import Planner, DesignProposal
from reviewer import Reviewer, ApprovalRecord, APPROVED, REVISION_REQUIRED, REJECTED
from producer import Producer, ProductionResult
from mockup_generator import MockupGenerator


# =============================================
# v1.2 功能感知型视觉设计Agent工作流（四层架构）
# =============================================

def run_functional_design_agent(config: dict, output_dir: str = "output",
                                 interactive: bool = True):
    """
    功能感知型四层架构工作流
    Perceptor -> Planner -> Reviewer -> Producer
    interactive: 是否启用小样确认交互（False=直接输出成品）
    """
    print("\n" + "=" * 60)
    print("  AKO 功能感知型视觉设计Agent v1.2 - 四层架构工作流")
    print("=" * 60)

    agent_name = config.get("agent_name", "AKO_Agent")
    version = config.get("version", "1.0.0")
    trace_id = config.get("trace_id", f"AKO-VD-{datetime.now().strftime('%Y%m%d')}-001")
    config["trace_id"] = trace_id

    # 输出文件夹与项目名称（agent_name）保持一致
    agent_dir = os.path.join(output_dir, agent_name)
    os.makedirs(agent_dir, exist_ok=True)

    # ============================
    # Layer 1: Perceptor（需求感知层）
    # ============================
    print(f"\n{'='*50}")
    print(f"  Layer 1: Perceptor - 需求感知分析")
    print(f"{'='*50}")

    perceptor = Perceptor()
    report = perceptor.analyze(config)

    # 保存感知报告
    report_path = os.path.join(agent_dir, f"functional_perception_report_{trace_id}.json")
    report.save_json(report_path)

    print(f"  Trace ID: {report.trace_id}")
    print(f"  Agent: {report.agent_display_name} v{report.version}")
    print(f"  界面类型: {report.interface_type}")
    print(f"  数据密度: {report.data_density}")
    print(f"  匹配模板: {report.template_id}")
    print(f"  设计重点: {'; '.join(report.design_focus[:3])}")
    print(f"  关键交互: {'; '.join(report.critical_interactions[:3])}")
    print(f"  图标需求: {len(report.icon_requirements)}个")
    print(f"  感知报告: {report_path}")

    # ============================
    # Layer 2: Planner（方案规划层）
    # ============================
    print(f"\n{'='*50}")
    print(f"  Layer 2: Planner - 设计方案规划")
    print(f"{'='*50}")

    planner = Planner()
    proposal = planner.create_proposal(report)

    # 保存设计方案
    proposal_json = os.path.join(agent_dir, f"design_proposal_v1.0_{trace_id}.json")
    proposal.save_json(proposal_json)
    proposal_md = os.path.join(agent_dir, f"design_proposal_v1.0_{trace_id}.md")
    proposal.save_markdown(proposal_md)

    print(f"  模板: {proposal.template_id}")
    print(f"  界面类型: {proposal.interface_type}")
    print(f"  色彩方案: {len(proposal.color_scheme)}类")
    print(f"  图标方案: {len(proposal.icon_plan)}个")
    print(f"  动效规范: {len(proposal.animation_rules)}条")
    print(f"  审批检查表: {len(proposal.checklist)}项")
    print(f"  设计方案(JSON): {proposal_json}")
    print(f"  设计方案(MD): {proposal_md}")

    # ============================
    # 色系选择（交互式/配置预设）
    # ============================
    preset_scheme_id = config.get("color_scheme_id")
    selected_scheme = _select_color_scheme(
        interactive=interactive,
        preset_id=preset_scheme_id
    )
    config["color_scheme_id"] = selected_scheme.id
    print(f"  配色方案: {selected_scheme.name} ({selected_scheme.id})")

    # 生成小样文件（使用选中色系）
    print(f"\n  生成视觉小样...")
    mockup_gen = MockupGenerator(report, proposal, scheme=selected_scheme)
    mockup_dir = os.path.join(agent_dir, "mockups")
    mockup_results = mockup_gen.generate_all(mockup_dir)
    for mtype, mpath in mockup_results.items():
        print(f"  小样[{mtype}]: {mpath}")
        proposal.mockup_files[mtype] = mpath

    # ============================
    # 小样确认交互
    # ============================
    if interactive:
        print(f"\n{'='*50}")
        print(f"  小样预览确认")
        print(f"{'='*50}")
        print(f"  小样已生成，请查看:")
        for mtype, mpath in mockup_results.items():
            abs_path = os.path.abspath(mpath)
            print(f"    [{mtype}] {abs_path}")
        print(f"\n  提示: 可打开上述文件预览效果")
        while True:
            confirm = input("\n  确认小样，继续生成成品？(y/n): ").strip().lower()
            if confirm in ("y", "yes", ""):
                print("  已确认，继续生产流程...")
                break
            elif confirm in ("n", "no"):
                print("  已取消。可修改配置后重新运行。")
                print(f"  小样保留在: {os.path.abspath(mockup_dir)}")
                return None
            else:
                print("  请输入 y 或 n")

    # ============================
    # Layer 3: Reviewer（审批层）
    # ============================
    print(f"\n{'='*50}")
    print(f"  Layer 3: Reviewer - 审批")
    print(f"{'='*50}")

    reviewer = Reviewer()

    # 自动预检
    pre_check = reviewer.pre_check(proposal, report)
    print(f"  自动预检:")
    print(f"    色彩合规: {'PASS' if pre_check.color_compliance else 'FAIL'}")
    print(f"    命名规范: {'PASS' if pre_check.naming_compliance else 'FAIL'}")
    print(f"    文件完整: {'PASS' if pre_check.file_completeness else 'FAIL'}")
    if pre_check.details:
        for d in pre_check.details:
            print(f"    ! {d}")

    # 自动审批
    approval = reviewer.auto_approve(proposal, report)

    # 保存审批记录
    approval_json = os.path.join(agent_dir, f"approval_record_{trace_id}.json")
    approval.save_json(approval_json)
    approval_md = os.path.join(agent_dir, f"approval_record_{trace_id}.md")
    approval.save_markdown(approval_md)

    print(f"\n  审批结果: {approval.status}")
    print(f"  合规评分: {approval.compliance_score}/100")
    print(f"  审批记录: {approval_json}")

    # 打印审批摘要
    print(f"\n{reviewer.generate_approval_summary(approval)}")

    # ============================
    # Layer 4: Producer（生产层）
    # ============================
    if approval.status == APPROVED:
        print(f"\n{'='*50}")
        print(f"  Layer 4: Producer - 生产")
        print(f"{'='*50}")

        production_dir = os.path.join(agent_dir, "production")
        producer = Producer()
        result = producer.produce(proposal, report, approval, production_dir)

        print(f"  生产状态: {result.status}")
        print(f"  合规评分: {result.compliance_score}/100")

        for asset in result.assets:
            atype = asset.get("type", "?")
            apath = asset.get("path", "")
            print(f"  [{atype}] {apath}")

        for decision in result.design_decisions:
            print(f"  >> {decision}")

        # 保存生产结果
        result_json = os.path.join(agent_dir, f"production_result_{trace_id}.json")
        result.save_json(result_json)

        # 质量检查
        print(f"\n  质量检查...")
        qg = QualityGate(project_name=agent_name)
        for asset in result.assets:
            apath = asset.get("path", "")
            if apath.endswith(".ico"):
                qg.check_ico_file(apath)
            elif apath.endswith(".png"):
                qg.check_png_file(apath)
                qg.check_image_colors(apath)
            elif apath.endswith(".bmp"):
                qg.check_bmp_file(apath)
                qg.check_image_colors(apath)

        print(f"\n{qg.generate_summary()}")

        print(f"\n  生产完成！输出目录: {production_dir}")
        return production_dir
    else:
        print(f"\n  审批未通过，Producer拒绝生产。")
        print(f"  请根据审批意见修改设计方案后重新提交。")
        return None


# =============================================
# 图纸识别与翻模Agent工作流（保留）
# =============================================

def run_drawing_recognition_agent(drawing_file: str, output_dir: str = "output",
                                   project_name: str = "project", floor_count: int = 1):
    """图纸识别与翻模Agent工作流"""
    print("\n" + "=" * 60)
    print("  AKO 图纸识别与翻模Agent - 开始工作")
    print("=" * 60)

    bim_dir = os.path.join(output_dir, "bim_output", project_name)
    os.makedirs(bim_dir, exist_ok=True)

    print(f"\n[Step 1] 解析图纸: {drawing_file}")
    parser = DrawingParser(drawing_file)
    drawing_data = parser.parse()
    print(parser.summary())

    parse_json = os.path.join(bim_dir, f"parsed_{project_name}.json")
    drawing_data.save_json(parse_json)
    print(f"  解析结果: {parse_json}")

    print(f"\n[Step 2] 识别建筑元素...")
    recognizer = ElementRecognizer()
    recognition = recognizer.recognize_all(drawing_data)
    rec_json = os.path.join(bim_dir, f"recognition_{project_name}.json")
    recognition.save_json(rec_json)
    print(f"  墙体: {len(recognition.walls)} | 门: {len(recognition.doors)} | 窗: {len(recognition.windows)}")
    print(f"  房间: {len(recognition.rooms)} | 轴线: {len(recognition.axes)}")

    print(f"\n[Step 3] 标注OCR识别...")
    ocr = AnnotationOCR()
    ocr_result = ocr.recognize(drawing_data)
    ocr_json = os.path.join(bim_dir, f"ocr_{project_name}.json")
    ocr_result.save_json(ocr_json)
    print(f"  标注: {len(ocr_result.dimensions)} | 标高: {len(ocr_result.elevations)} | 注释: {len(ocr_result.annotations)}")

    print(f"\n[Step 4] 构建BIM模型...")
    bim = BIMBuilder(project_name=project_name, floor_count=floor_count)
    bim.add_elements_from_recognition(recognition, floor=1)
    model = bim.build()

    bim_json = os.path.join(bim_dir, f"bim_{project_name}.json")
    bim.export_json(bim_json)
    print(f"  BIM(JSON): {bim_json}")

    ifc_path = os.path.join(bim_dir, f"bim_{project_name}.ifc")
    bim.export_ifc(ifc_path)
    print(f"  BIM(IFC): {ifc_path}")

    print(f"\n[Step 5] 质量检查...")
    qg = QualityGate(project_name=project_name)
    qg.check_recognition_coverage(recognition.to_dict())
    qg.check_bim_geometry(model.to_dict())
    print(f"\n{qg.generate_summary()}")

    print(f"\n图纸识别与翻模Agent工作完成！输出目录: {bim_dir}")
    return bim_dir


# =============================================
# 建筑性能分析Agent工作流（保留）
# =============================================

def run_performance_analysis_agent(config: dict, output_dir: str = "output"):
    """建筑性能分析Agent工作流"""
    print("\n" + "=" * 60)
    print("  AKO 建筑性能分析Agent - 开始工作")
    print("=" * 60)

    project_name = config.get("project_name", "project")
    analysis_dir = os.path.join(output_dir, "analysis_output", project_name)
    os.makedirs(analysis_dir, exist_ok=True)

    building = BuildingInfo(
        project_name=config.get("project_name", "项目"),
        location=config.get("location", "贵阳"),
        building_type=config.get("building_type", "office"),
        total_area=config.get("total_area", 1000),
        floor_count=config.get("floor_count", 1),
        floor_height=config.get("floor_height", 3.0),
        window_ratio=config.get("window_ratio", 0.3),
        orientation=config.get("orientation", "south"),
        body_coefficient=config.get("body_coefficient", 0.25),
    )

    analyzer = PerformanceAnalyzer(building)

    print(f"\n[Step 1] 能耗模拟...")
    energy = analyzer.run_energy_simulation()
    print(f"  年能耗: {energy.total_energy:.1f} kWh/m2.a | 评级: {energy.rating}")
    energy_json = os.path.join(analysis_dir, f"energy_{project_name}.json")
    with open(energy_json, "w", encoding="utf-8") as f:
        json.dump(energy.to_dict(), f, ensure_ascii=False, indent=2)

    print(f"\n[Step 2] 采光分析...")
    daylight = analyzer.run_daylight_analysis()
    print(f"  平均采光系数: {daylight.average_df:.2f}% | 达标率: {daylight.compliance_rate:.0f}%")
    daylight_json = os.path.join(analysis_dir, f"daylight_{project_name}.json")
    with open(daylight_json, "w", encoding="utf-8") as f:
        json.dump(daylight.to_dict(), f, ensure_ascii=False, indent=2)

    print(f"\n[Step 3] 碳排放计算...")
    carbon = analyzer.run_carbon_calculation()
    print(f"  全生命周期碳排放: {carbon.total_carbon:.0f} kgCO2e")
    carbon_json = os.path.join(analysis_dir, f"carbon_{project_name}.json")
    with open(carbon_json, "w", encoding="utf-8") as f:
        json.dump(carbon.to_dict(), f, ensure_ascii=False, indent=2)

    print(f"\n[Step 4] 绿建合规审查...")
    compliance = analyzer.run_compliance_check()
    print(f"  绿建星级: {'*' * compliance.star_rating}{'.' * (3 - compliance.star_rating)}")
    compliance_json = os.path.join(analysis_dir, f"compliance_{project_name}.json")
    with open(compliance_json, "w", encoding="utf-8") as f:
        json.dump(compliance.to_dict(), f, ensure_ascii=False, indent=2)

    print(f"\n[Step 5] 生成综合报告...")
    report = analyzer.generate_full_report()
    report_path = os.path.join(analysis_dir, f"summary_{project_name}.json")
    report.save_json(report_path)
    print(f"  综合报告: {report_path}")

    print(f"\n[Step 6] 质量检查...")
    qg = QualityGate(project_name=project_name)
    qg.check_weather_data(building.location)
    qg.check_energy_convergence(energy.to_dict())
    qg.check_result_reasonability(energy.total_energy, building.building_type)
    print(f"\n{qg.generate_summary()}")

    print(f"\n建筑性能分析Agent工作完成！输出目录: {analysis_dir}")
    return analysis_dir


# =============================================
# CLI入口
# =============================================

@click.group()
def cli():
    """AKO_visual_design_agent v1.2 - 功能感知型视觉设计Agent"""
    pass


@cli.command()
@click.option("--config", "-c", default=None, help="配置文件路径(JSON)")
@click.option("--output", "-o", default=None, help="输出目录(默认从配置读取或output)")
@click.option("--yes", "-y", is_flag=True, help="跳过小样确认，直接输出成品")
def functional(config, output, yes):
    """运行功能感知型视觉设计Agent（v1.2四层架构）"""
    if config:
        with open(config, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = {
            "agent_name": "quote_agent",
            "agent_display_name": "报价智能体",
            "version": "2.1.0",
            "client_name": "中黔顺安建设有限公司",
            "client_short": "中黔顺安",
            "features": [
                {"name": "报价计算", "type": "calculation", "ui_pattern": "form + result_panel",
                 "data_density": "high", "interaction": "input -> calculate -> display"},
                {"name": "材料清单", "type": "data_table", "ui_pattern": "editable_table",
                 "data_density": "very_high", "interaction": "crud_operations"},
                {"name": "PDF导出", "type": "export", "ui_pattern": "button + progress + save_dialog",
                 "data_density": "low", "interaction": "trigger -> process -> complete"},
                {"name": "历史记录", "type": "history", "ui_pattern": "list + detail_view",
                 "data_density": "medium", "interaction": "select -> view -> compare"},
            ],
            "interaction_scenarios": ["首次启动引导", "日常高频操作", "数据批量处理", "结果导出分享"],
            "user_profile": {"role": "造价工程师", "technical_level": "intermediate",
                             "daily_usage_hours": 4, "primary_device": "desktop_1920x1080"},
            "design_intent": {"industry_tone": "construction", "style_variance": "conservative",
                              "lighting_mode": "light", "accent_preference": "warm"},
        }
    out = output or cfg.get("output_dir", "output")
    run_functional_design_agent(cfg, out, interactive=not yes)


@cli.command()
@click.option("--config", "-c", default=None, help="配置文件路径(JSON)")
@click.option("--output", "-o", default=None, help="输出目录(默认从配置读取或output)")
@click.option("--yes", "-y", is_flag=True, help="跳过小样确认，直接输出成品")
def visual(config, output, yes):
    """运行视觉设计Agent（基础版）"""
    if config:
        with open(config, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = {
            "agent_name": "quote_agent",
            "agent_display_name": "报价智能体",
            "version": "2.1.0",
            "client_name": "中黔顺安建设有限公司",
            "client_short": "中黔顺安",
            "features": ["报价计算", "材料清单", "PDF导出", "历史记录"],
        }
    out = output or cfg.get("output_dir", "output")
    # 使用旧版工作流
    _run_visual_design_legacy(cfg, out, interactive=not yes)


@cli.command()
@click.argument("drawing_file")
@click.option("--output", "-o", default=None, help="输出目录(默认output)")
@click.option("--project", "-p", default="project", help="项目名称")
@click.option("--floors", "-f", default=1, help="楼层数")
def drawing(drawing_file, output, project, floors):
    """运行图纸识别与翻模Agent"""
    out = output or "output"
    run_drawing_recognition_agent(drawing_file, out, project, floors)


@cli.command()
@click.option("--config", "-c", default=None, help="配置文件路径(JSON)")
@click.option("--output", "-o", default=None, help="输出目录(默认从配置读取或output)")
def analysis(config, output):
    """运行建筑性能分析Agent"""
    if config:
        with open(config, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = {
            "project_name": "中黔顺安办公楼",
            "location": "贵阳",
            "building_type": "office",
            "total_area": 2400,
            "floor_count": 6,
            "floor_height": 3.0,
            "window_ratio": 0.35,
            "orientation": "south",
        }
    out = output or cfg.get("output_dir", "output")
    run_performance_analysis_agent(cfg, out)


@cli.command()
def demo():
    """运行v1.2四层架构全链路演示"""
    print("\n" + "=" * 60)
    print("  AKO_visual_design_agent v1.2 - 全链路演示")
    print("  功能感知型四层架构: Perceptor -> Planner -> Reviewer -> Producer")
    print("=" * 60)

    # 1. 功能感知型视觉设计Agent（v1.2核心）
    functional_config = {
        "agent_name": "quote_agent",
        "agent_display_name": "报价智能体",
        "version": "2.1.0",
        "client_name": "中黔顺安建设有限公司",
        "client_short": "中黔顺安",
        "features": [
            {"name": "报价计算", "type": "calculation", "ui_pattern": "form + result_panel",
             "data_density": "high", "interaction": "input -> calculate -> display"},
            {"name": "材料清单", "type": "data_table", "ui_pattern": "editable_table",
             "data_density": "very_high", "interaction": "crud_operations"},
            {"name": "PDF导出", "type": "export", "ui_pattern": "button + progress + save_dialog",
             "data_density": "low", "interaction": "trigger -> process -> complete"},
            {"name": "历史记录", "type": "history", "ui_pattern": "list + detail_view",
             "data_density": "medium", "interaction": "select -> view -> compare"},
        ],
        "interaction_scenarios": ["首次启动引导", "日常高频操作", "数据批量处理", "结果导出分享"],
        "user_profile": {"role": "造价工程师", "technical_level": "intermediate",
                         "daily_usage_hours": 4, "primary_device": "desktop_1920x1080"},
        "design_intent": {"industry_tone": "construction", "style_variance": "conservative",
                          "lighting_mode": "light", "accent_preference": "warm"},
    }
    run_functional_design_agent(functional_config, interactive=False)

    # 2. 建筑性能分析Agent
    analysis_config = {
        "project_name": "中黔顺安办公楼",
        "location": "贵阳",
        "building_type": "office",
        "total_area": 2400,
        "floor_count": 6,
        "floor_height": 3.0,
        "window_ratio": 0.35,
        "orientation": "south",
    }
    run_performance_analysis_agent(analysis_config)

    print("\n" + "=" * 60)
    print("  全链路演示完成！")
    print("  输出目录: output/")
    print("=" * 60)


def _run_visual_design_legacy(config: dict, output_dir: str = "output",
                               interactive: bool = True):
    """旧版视觉设计Agent工作流（保留兼容）"""
    print("\n" + "=" * 60)
    print("  AKO 视觉设计Agent（基础版）- 开始工作")
    print("=" * 60)

    agent_name = config.get("agent_name", "AKO_Agent")
    version = config.get("version", "1.0.0")
    client_name = config.get("client_short", config.get("client_name", "客户"))
    features = config.get("features", [])

    # 输出文件夹与项目名称保持一致
    agent_dir = os.path.join(output_dir, agent_name)
    os.makedirs(agent_dir, exist_ok=True)

    print(f"\n[Step 1] 生成主图标...")
    icon = IconBuilder(
        base_shape="hexagon",
        inner_symbol="calculator",
        primary_color=AMBER_GOLD.rgb,
        secondary_color=CREAM_GOLD.rgb,
        size=256,
    )
    ico_path = icon.generate_multi_resolution(
        sizes=ICO_STANDARD_SIZES,
        output=os.path.join(agent_dir, f"AKO_{agent_name}_icon_v{version}.ico"),
    )
    print(f"  主图标: {ico_path}")

    print(f"\n[Step 2] 生成Splash Screen...")
    splash = SplashGenerator(
        template="classic",
        agent_name=agent_name,
        client_name=client_name,
        version=version,
    )
    splash_path = splash.generate(
        output=os.path.join(agent_dir, f"splash_{agent_name}_{client_name}_v{version}.png"),
    )
    print(f"  Splash: {splash_path}")

    # 小样确认交互
    if interactive:
        print(f"\n{'='*50}")
        print(f"  小样预览确认")
        print(f"{'='*50}")
        print(f"  小样已生成，请查看:")
        print(f"    [icon] {os.path.abspath(ico_path)}")
        print(f"    [splash] {os.path.abspath(splash_path)}")
        print(f"\n  提示: 可打开上述文件预览效果")
        while True:
            confirm = input("\n  确认小样，继续生成成品？(y/n): ").strip().lower()
            if confirm in ("y", "yes", ""):
                print("  已确认，继续...")
                break
            elif confirm in ("n", "no"):
                print("  已取消。")
                return None
            else:
                print("  请输入 y 或 n")

    print(f"\n[Step 3] 质量检查...")
    qg = QualityGate(project_name=agent_name)
    qg.check_ico_file(ico_path)
    qg.check_png_file(splash_path)
    qg.check_image_colors(ico_path)
    qg.check_image_colors(splash_path)
    print(f"\n{qg.generate_summary()}")

    print(f"\n视觉设计Agent（基础版）工作完成！输出目录: {agent_dir}")
    return agent_dir


if __name__ == "__main__":
    cli()
