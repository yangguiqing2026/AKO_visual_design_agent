"""
AKO Reviewer - 审批层（Layer 3）
规则引擎自动预检 + 人工审批流程管理
"""

import os
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

from ako_colors import ALL_VALID_RGB_SET, FORBIDDEN_BG_COLORS
from planner import DesignProposal
from perceptor import FunctionalPerceptionReport


# =============================================
# 审批状态枚举
# =============================================
APPROVED = "APPROVED"
REVISION_REQUIRED = "REVISION_REQUIRED"
REJECTED = "REJECTED"


@dataclass
class PreCheckResult:
    """自动预检结果"""
    color_compliance: bool = True
    naming_compliance: bool = True
    file_completeness: bool = True
    semantic_match: bool = False  # 需人工确认
    details: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "color_compliance": self.color_compliance,
            "naming_compliance": self.naming_compliance,
            "file_completeness": self.file_completeness,
            "semantic_match": self.semantic_match,
            "details": self.details,
        }


@dataclass
class ApprovalRecord:
    """审批记录"""
    trace_id: str = ""
    agent_name: str = ""
    version: str = ""
    proposal_version: str = ""
    submitted_at: str = ""
    reviewed_at: str = ""

    # 预检结果
    pre_check: dict = field(default_factory=dict)

    # 人工审批
    human_review: dict = field(default_factory=dict)

    # 最终结果
    status: str = REVISION_REQUIRED
    compliance_score: int = 0
    revision_round: int = 0
    max_revisions: int = 3
    revision_notes: List[dict] = field(default_factory=list)
    final_comment: str = ""
    reviewer: str = "AKO_studio"

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "agent_name": self.agent_name,
            "version": self.version,
            "proposal_version": self.proposal_version,
            "submitted_at": self.submitted_at,
            "reviewed_at": self.reviewed_at,
            "pre_check": self.pre_check,
            "human_review": self.human_review,
            "status": self.status,
            "compliance_score": self.compliance_score,
            "revision_round": self.revision_round,
            "max_revisions": self.max_revisions,
            "revision_notes": self.revision_notes,
            "final_comment": self.final_comment,
            "reviewer": self.reviewer,
        }

    def save_json(self, output: str) -> str:
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        return output

    def save_markdown(self, output: str) -> str:
        """保存审批记录Markdown"""
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        status_text = {
            APPROVED: "已通过",
            REVISION_REQUIRED: "需修改",
            REJECTED: "已拒绝",
        }.get(self.status, self.status)

        lines = [
            f"# 视觉设计方案审批记录",
            f"",
            f"> Trace ID: {self.trace_id}",
            f"> Agent: {self.agent_name} v{self.version}",
            f"> 提交时间: {self.submitted_at}",
            f"> 审批时间: {self.reviewed_at}",
            f"> 审批人: {self.reviewer}",
            f"",
            f"## 自动预检结果",
            f"",
        ]

        pc = self.pre_check
        lines.append(f"- {'[x]' if pc.get('color_compliance') else '[ ]'} 色彩合规")
        lines.append(f"- {'[x]' if pc.get('naming_compliance') else '[ ]'} 命名规范")
        lines.append(f"- {'[x]' if pc.get('file_completeness') else '[ ]'} 文件完整")
        lines.append(f"- {'[x]' if pc.get('semantic_match') else '[ ]'} 语义匹配（待人工确认）")

        lines.extend([
            f"",
            f"## 审批结果",
            f"",
            f"**状态**: {status_text}",
            f"**合规评分**: {self.compliance_score}/100",
            f"**修改轮次**: {self.revision_round}/{self.max_revisions}",
            f"",
        ])

        if self.revision_notes:
            lines.append("## 修改意见")
            lines.append("")
            for note in self.revision_notes:
                lines.append(f"### 第{note.get('round', '?')}轮")
                lines.append(f"- 整体评估: {note.get('overall', '')}")
                for issue in note.get("issues", []):
                    lines.append(f"  - [{issue.get('priority', 'medium')}] {issue.get('item', '')}: {issue.get('issue', '')}")
                    lines.append(f"    建议: {issue.get('suggestion', '')}")
            lines.append("")

        if self.final_comment:
            lines.extend([f"## 最终意见", f"", self.final_comment])

        with open(output, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return output


class Reviewer:
    """审批层：规则引擎预检 + 人工审批流程"""

    def __init__(self):
        self.max_revisions = 3

    def pre_check(self, proposal: DesignProposal, report: FunctionalPerceptionReport) -> PreCheckResult:
        """规则引擎自动预检"""
        result = PreCheckResult()

        # 1. 色彩合规检查
        color_ok = True
        for category, colors in proposal.color_scheme.items():
            if isinstance(colors, dict):
                for name, info in colors.items():
                    if isinstance(info, dict) and "rgb" in info:
                        rgb = tuple(info["rgb"])
                        if rgb not in ALL_VALID_RGB_SET:
                            color_ok = False
                            result.details.append(f"色彩不合规: {category}/{name} = {rgb}")
                        if rgb in FORBIDDEN_BG_COLORS:
                            color_ok = False
                            result.details.append(f"禁止色: {category}/{name} = {rgb}")
        result.color_compliance = color_ok

        # 2. 命名规范检查
        result.naming_compliance = bool(proposal.agent_name and proposal.trace_id)

        # 3. 文件完整性检查
        has_overview = bool(proposal.overview)
        has_layout = bool(proposal.layout)
        has_colors = bool(proposal.color_scheme)
        result.file_completeness = has_overview and has_layout and has_colors

        if not has_overview:
            result.details.append("缺少设计概述")
        if not has_layout:
            result.details.append("缺少布局规范")
        if not has_colors:
            result.details.append("缺少色彩方案")

        return result

    def calculate_compliance_score(self, pre_check: PreCheckResult, proposal: DesignProposal) -> int:
        """计算合规评分（0-100）"""
        score = 100

        if not pre_check.color_compliance:
            score -= 10
        if not pre_check.naming_compliance:
            score -= 5
        if not pre_check.file_completeness:
            score -= 5

        # 语义匹配加分/扣分
        if proposal.icon_plan:
            unmatched = sum(1 for i in proposal.icon_plan if "待确认" in str(i))
            if unmatched > 0:
                score -= min(15, unmatched * 5)

        # 审批完整性
        if not proposal.checklist:
            score -= 10

        return max(0, min(100, score))

    def auto_approve(self, proposal: DesignProposal, report: FunctionalPerceptionReport) -> ApprovalRecord:
        """自动审批（当合规评分 >= 90 且预检全通过时）"""
        record = ApprovalRecord()
        record.trace_id = proposal.trace_id
        record.agent_name = proposal.agent_name
        record.version = proposal.version
        record.submitted_at = datetime.now().isoformat()

        # 预检
        pre_check = self.pre_check(proposal, report)
        record.pre_check = pre_check.to_dict()

        # 评分
        score = self.calculate_compliance_score(pre_check, proposal)
        record.compliance_score = score

        # 自动审批逻辑：评分 >= 90 且预检全通过
        if score >= 90 and pre_check.color_compliance and pre_check.file_completeness:
            record.status = APPROVED
            record.final_comment = f"自动审批通过。合规评分: {score}/100。所有预检项通过。"
        elif score >= 70:
            record.status = REVISION_REQUIRED
            record.revision_round = 1
            record.revision_notes.append({
                "round": 1,
                "overall": "方案基本可行，部分细节需调整",
                "issues": self._generate_revision_issues(pre_check, proposal),
            })
            record.final_comment = f"需修改后重新提交。合规评分: {score}/100。"
        else:
            record.status = REJECTED
            record.final_comment = f"方案不达标，需重新规划。合规评分: {score}/100。"

        record.reviewed_at = datetime.now().isoformat()
        return record

    def manual_review(self, proposal: DesignProposal, report: FunctionalPerceptionReport,
                      decision: str = APPROVED, comment: str = "",
                      issues: List[dict] = None) -> ApprovalRecord:
        """人工审批"""
        record = ApprovalRecord()
        record.trace_id = proposal.trace_id
        record.agent_name = proposal.agent_name
        record.version = proposal.version
        record.submitted_at = datetime.now().isoformat()

        # 预检
        pre_check = self.pre_check(proposal, report)
        record.pre_check = pre_check.to_dict()

        # 评分
        score = self.calculate_compliance_score(pre_check, proposal)
        record.compliance_score = score

        # 人工决定
        record.status = decision
        record.final_comment = comment

        if decision == REVISION_REQUIRED and issues:
            record.revision_round = 1
            record.revision_notes.append({
                "round": 1,
                "overall": comment,
                "issues": issues,
            })

        record.reviewed_at = datetime.now().isoformat()
        return record

    def _generate_revision_issues(self, pre_check: PreCheckResult, proposal: DesignProposal) -> list:
        """根据预检结果生成修改意见"""
        issues = []

        if not pre_check.color_compliance:
            for detail in pre_check.details:
                if "色彩" in detail or "禁止" in detail:
                    issues.append({
                        "item": "色彩合规",
                        "issue": detail,
                        "suggestion": "请检查并修正为AKO色彩系统内的色值",
                        "priority": "high",
                    })

        if not pre_check.file_completeness:
            for detail in pre_check.details:
                if "缺少" in detail:
                    issues.append({
                        "item": "文件完整性",
                        "issue": detail,
                        "suggestion": "请补充缺失的内容",
                        "priority": "medium",
                    })

        if not issues:
            issues.append({
                "item": "综合评估",
                "issue": "方案需进一步优化",
                "suggestion": "请参考审批检查表逐项确认",
                "priority": "medium",
            })

        return issues

    def generate_approval_summary(self, record: ApprovalRecord) -> str:
        """生成审批摘要文本"""
        status_text = {
            APPROVED: "APPROVED (通过)",
            REVISION_REQUIRED: "REVISION_REQUIRED (需修改)",
            REJECTED: "REJECTED (拒绝)",
        }.get(record.status, record.status)

        lines = [
            f"=== 审批结果 ===",
            f"Trace ID: {record.trace_id}",
            f"Agent: {record.agent_name} v{record.version}",
            f"状态: {status_text}",
            f"合规评分: {record.compliance_score}/100",
            f"审批人: {record.reviewer}",
        ]

        if record.status == APPROVED:
            lines.append(">> 可以进入Producer生产阶段")
        elif record.status == REVISION_REQUIRED:
            lines.append(f">> 需修改（第{record.revision_round}/{record.max_revisions}轮）")
            if record.revision_notes:
                for note in record.revision_notes:
                    for issue in note.get("issues", []):
                        lines.append(f"   - [{issue.get('priority', '?')}] {issue.get('item', '')}: {issue.get('issue', '')}")
        else:
            lines.append(">> 方案被拒绝，需重新规划")

        return "\n".join(lines)
