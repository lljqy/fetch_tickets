from typing import List, Dict, Any

from visualization.base_visualizer import BaseVisualizer
from core.base import SSQ_CONFIG


class SSQVisualizer(BaseVisualizer):
    """双色球数据可视化"""

    def __init__(self, draws: List[Dict[str, Any]]):
        super().__init__(draws, SSQ_CONFIG.front_range, SSQ_CONFIG.back_range)

    def get_front_color(self) -> str:
        return SSQ_CONFIG.front_color

    def get_back_color(self) -> str:
        return SSQ_CONFIG.back_color

    def get_front_name(self) -> str:
        return SSQ_CONFIG.front_name

    def get_back_name(self) -> str:
        return SSQ_CONFIG.back_name 