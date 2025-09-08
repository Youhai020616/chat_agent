"""
Base Agent 抽象类

定义所有 Agent 的通用接口和行为
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Agent 执行结果"""
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    execution_time: Optional[float] = None
    tokens_used: Optional[int] = None
    cost: Optional[float] = None


class BaseAgent(ABC):
    """所有 Agent 的基类"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"agents.{name}")
    
    @abstractmethod
    async def analyze(self, state: "SEOState") -> AgentResult:
        """
        执行分析任务
        
        Args:
            state: 全局 SEO 状态对象
            
        Returns:
            AgentResult: 分析结果
        """
        pass
    
    def validate_input(self, state: "SEOState") -> bool:
        """验证输入状态是否有效"""
        if not state.target_url:
            self.logger.error("Target URL is required")
            return False
        return True
    
    def log_execution(self, result: AgentResult):
        """记录执行日志"""
        if result.success:
            self.logger.info(
                f"Agent {self.name} completed successfully. "
                f"Time: {result.execution_time:.2f}s, "
                f"Tokens: {result.tokens_used}, "
                f"Cost: ${result.cost:.4f}"
            )
        else:
            self.logger.error(
                f"Agent {self.name} failed: {result.error}"
            )
