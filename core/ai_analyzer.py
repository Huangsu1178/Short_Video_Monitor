"""
TikTok Monitor - AI Analyzer Module

保留旧导入路径，底层实现已迁移到 `skills.TikTokAIAnalysisSkill`。
"""
import warnings

from config import DEFAULT_AI_MODEL
from skills.tiktok_ai_analysis import TikTokAIAnalysisSkill

__all__ = ["AIAnalyzer"]


class AIAnalyzer(TikTokAIAnalysisSkill):
    """兼容旧接口的 AI 分析器包装层。"""

    def __init__(self, api_key: str = "", api_base: str = "", model: str = DEFAULT_AI_MODEL):
        warnings.warn(
            "AIAnalyzer 已迁移至 skills.TikTokAIAnalysisSkill，请更新导入路径",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(api_key, api_base, model)

    def analyze_video(self, video: dict, username: str = "", progress_callback=None):
        """向后兼容：调用新的单视频分析接口。"""
        return self.analyze_single_video(video, username)

    def analyze_batch(self, videos: list, username: str = "", progress_callback=None):
        """向后兼容：调用新的批量分析接口。"""
        return self.analyze_batch_videos(videos, username)

    def analyze_ab(self, group_a, group_b, **kwargs):
        """向后兼容：调用新的 AB 对比分析接口。"""
        return self.analyze_ab_comparison(group_a, group_b, **kwargs)
