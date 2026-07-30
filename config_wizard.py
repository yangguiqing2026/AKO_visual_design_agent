"""
AKO 配置向导 - 交互式输入设计条件
双击 cli.bat 后自动进入此向导
"""

import json
import os
import sys
from color_schemes import COLOR_SCHEMES, DEFAULT_SCHEME, list_schemes

# 功能类型定义
FEATURE_TYPES = {
    "calculation":  {"desc": "计算型（表单+结果面板）", "template": "A", "ui": "form + result_panel"},
    "data_table":   {"desc": "数据表格型（可编辑表格）", "template": "A", "ui": "editable_table"},
    "form":         {"desc": "表单工作流（多步骤）", "template": "A", "ui": "multi_step_form"},
    "dashboard":    {"desc": "仪表盘型（指标卡+图表）", "template": "B", "ui": "indicator_cards + charts"},
    "monitoring":   {"desc": "实时监控型（数据流）", "template": "B", "ui": "chart + indicator_cards"},
    "chart":        {"desc": "图表展示型", "template": "B", "ui": "chart + indicator_cards"},
    "canvas":       {"desc": "画布/编辑器型", "template": "C", "ui": "canvas + toolbar"},
    "document":     {"desc": "文档编辑型", "template": "C", "ui": "document + sidebar"},
    "map":          {"desc": "地图型", "template": "C", "ui": "map + sidebar"},
    "export":       {"desc": "导出功能", "template": "-", "ui": "button + progress + save_dialog"},
    "history":      {"desc": "历史记录/列表", "template": "-", "ui": "list + detail_view"},
    "chat":         {"desc": "对话/消息型", "template": "C", "ui": "chat + input_bar"},
}

DENSITY_OPTIONS = {
    "1": ("low", "低（少量数据）"),
    "2": ("medium", "中（常规数据量）"),
    "3": ("high", "高（大量数据）"),
    "4": ("very_high", "极高（密集表格/实时流）"),
}


def _input(prompt: str, default: str = "") -> str:
    """带默认值的输入"""
    if default:
        result = input(f"  {prompt} [{default}]: ").strip()
        return result if result else default
    else:
        return input(f"  {prompt}: ").strip()


def _choose(prompt: str, options: dict) -> str:
    """选择菜单"""
    print(f"\n  {prompt}")
    for key, (_, desc) in options.items():
        print(f"    {key}. {desc}")
    while True:
        choice = input("  请选择编号: ").strip()
        if choice in options:
            return options[choice][0]
        print("  无效选择，请重新输入")


def _add_feature(index: int) -> dict:
    """添加一个功能"""
    print(f"\n  --- 功能 {index} ---")
    name = _input("功能名称（如：报价计算）")
    if not name:
        return None

    print("\n  可用功能类型:")
    type_keys = list(FEATURE_TYPES.keys())
    for i, (ftype, info) in enumerate(FEATURE_TYPES.items(), 1):
        tpl = f"→模板{info['template']}" if info['template'] != '-' else ""
        print(f"    {i:2d}. {ftype:14s} {info['desc']} {tpl}")

    while True:
        choice = input("  请选择类型编号或输入类型名: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(type_keys):
            ftype = type_keys[int(choice) - 1]
            break
        elif choice in FEATURE_TYPES:
            ftype = choice
            break
        print("  无效选择")

    density = _choose("数据密度:", DENSITY_OPTIONS)

    ui_pattern = FEATURE_TYPES[ftype]["ui"]
    interaction = _input("交互方式描述（可选，回车跳过）", default="default")
    if interaction == "default":
        interaction_map = {
            "calculation": "input -> calculate -> display",
            "data_table": "crud_operations",
            "form": "step1 -> step2 -> confirm",
            "dashboard": "auto_refresh -> drill_down",
            "monitoring": "real_time_stream -> alert",
            "chart": "filter -> zoom -> export",
            "canvas": "select -> draw -> export",
            "document": "edit -> format -> save",
            "map": "pan -> zoom -> locate",
            "export": "trigger -> process -> complete",
            "history": "select -> view -> compare",
            "chat": "type -> send -> receive",
        }
        interaction = interaction_map.get(ftype, "default_interaction")

    return {
        "name": name,
        "type": ftype,
        "ui_pattern": ui_pattern,
        "data_density": density,
        "interaction": interaction,
    }


def run_wizard(auto_run: bool = True):
    """运行配置向导"""
    print()
    print("=" * 60)
    print("  AKO 视觉设计Agent - 设计条件输入向导")
    print("=" * 60)

    # Step 1: 基本信息
    print("\n[1/5] 基本信息")
    agent_name = _input("Agent英文标识（如 quote_agent）", "quote_agent")
    display_name = _input("Agent中文名称（如 报价智能体）", "报价智能体")
    version = _input("版本号", "1.0.0")
    client_name = _input("客户全称", "我的客户")
    client_short = _input("客户简称", client_name[:4] if client_name else "客户")

    # Step 2: 功能列表
    print("\n[2/5] 功能定义（至少1个，输入空名称结束）")
    features = []
    i = 1
    while True:
        feat = _add_feature(i)
        if feat is None:
            if not features:
                print("  至少需要一个功能！")
                continue
            break
        features.append(feat)
        i += 1
        cont = _input("继续添加功能？(y/n)", "y")
        if cont.lower() != "y":
            break

    # Step 3: 用户画像
    print("\n[3/5] 用户画像")
    role = _input("用户角色（如 造价工程师）", "工程师")
    tech_level = _choose("技术水平:", {
        "1": ("beginner", "初级"),
        "2": ("intermediate", "中级"),
        "3": ("expert", "高级"),
    })
    usage_hours = _input("日均使用时长（小时）", "4")
    device = _choose("主设备:", {
        "1": ("desktop_1920x1080", "桌面端 1920x1080"),
        "2": ("desktop_2560x1440", "桌面端 2560x1440"),
        "3": ("laptop_1920x1080", "笔记本 1920x1080"),
        "4": ("tablet", "平板"),
    })

    # Step 4: 设计意图
    print("\n[4/5] 设计意图")
    industry = _choose("行业调性:", {
        "1": ("construction", "建筑工程"),
        "2": ("tech", "科技互联网"),
        "3": ("finance", "金融财务"),
        "4": ("medical", "医疗健康"),
        "5": ("education", "教育培训"),
    })
    style = _choose("风格倾向:", {
        "1": ("conservative", "稳重保守"),
        "2": ("modern", "现代简洁"),
        "3": ("creative", "创意活泼"),
    })
    lighting = _choose("明暗模式:", {
        "1": ("light", "浅色"),
        "2": ("dark", "深色"),
    })

    # 配色方案选择
    print("\n  配色方案:")
    schemes = list_schemes()
    for i, scheme in enumerate(schemes, 1):
        print(f"    {i}. {scheme.name} - {scheme.description}")
    while True:
        scheme_choice = input("  请选择配色方案编号 [1]: ").strip()
        if not scheme_choice:
            color_scheme_id = DEFAULT_SCHEME.id
            break
        if scheme_choice.isdigit() and 1 <= int(scheme_choice) <= len(schemes):
            color_scheme_id = schemes[int(scheme_choice) - 1].id
            break
        print("  无效选择")
    print(f"  已选择: {[s for s in schemes if s.id == color_scheme_id][0].name}")

    # Step 5: 输出目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_output = os.path.join(script_dir, "output")
    print("\n[5/5] 输出设置")
    print("  输出目录用于存放生成的设计资源（图标、闪屏、面板等）")
    print("  必须使用绝对路径，以便 AKO_pack_agent 准确定位")
    output_dir = _input("输出目录（绝对路径）", default_output)
    # 确保为绝对路径
    if not os.path.isabs(output_dir):
        output_dir = os.path.abspath(output_dir)
        print(f"  已转为绝对路径: {output_dir}")

    # 生成配置
    config = {
        "agent_name": agent_name,
        "agent_display_name": display_name,
        "version": version,
        "client_name": client_name,
        "client_short": client_short,
        "output_dir": output_dir,
        "color_scheme_id": color_scheme_id,
        "features": features,
        "interaction_scenarios": ["首次启动引导", "日常高频操作"],
        "user_profile": {
            "role": role,
            "technical_level": tech_level,
            "daily_usage_hours": int(usage_hours) if usage_hours.isdigit() else 4,
            "primary_device": device,
        },
        "design_intent": {
            "industry_tone": industry,
            "style_variance": style,
            "lighting_mode": lighting,
            "accent_preference": "warm",
        },
    }

    # 打印摘要
    print("\n" + "=" * 60)
    print("  设计条件摘要")
    print("=" * 60)
    print(f"  Agent: {display_name} v{version}")
    print(f"  客户: {client_name}")
    print(f"  功能数: {len(features)}个")
    for f in features:
        tpl = FEATURE_TYPES.get(f["type"], {}).get("template", "?")
        print(f"    - {f['name']} [{f['type']}] → 模板{tpl}")
    print(f"  用户: {role}（{tech_level}）")
    scheme_name = [s.name for s in schemes if s.id == color_scheme_id]
    print(f"  配色: {scheme_name[0] if scheme_name else color_scheme_id}")
    print(f"  输出: {output_dir}/")
    print(f"  风格: {industry} / {style} / {lighting}")
    print("=" * 60)

    # 保存配置
    config_filename = f"{agent_name}_config.json"
    config_dir = os.path.join(output_dir, "configs")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, config_filename)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"\n  配置已保存: {config_path}")
    print(f"  输出目录: {os.path.abspath(output_dir)}")

    if auto_run:
        print("\n  正在启动设计流程...\n")
        from main import run_functional_design_agent
        run_functional_design_agent(config, output_dir)
    else:
        print(f"\n  稍后可运行: cli.bat functional -c {config_path} -o {output_dir}")

    return config


if __name__ == "__main__":
    auto = "--no-run" not in sys.argv
    run_wizard(auto_run=auto)
