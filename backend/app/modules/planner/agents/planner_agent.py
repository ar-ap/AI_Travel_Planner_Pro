"""
Travel Planner Agent V2.0
基于真实用户需求重新设计

This module contains AI agent responsible for generating travel itineraries.
It uses LLM to create intelligent, personalized travel plans with rich practical information.
"""

from typing import List, Dict, Any, Optional
from app.core.ai.factory import LLMFactory
from app.core.config.settings import settings
from langchain_core.messages import HumanMessage, SystemMessage
from app.modules.planner.prompts.planning_prompts import (
    PLANNING_SYSTEM_PROMPT,
    STRICT_JSON_OUTPUT,
    FLEXIBLE_JSON_OUTPUT,
    CULTURAL_PROMPT,
    ADVENTURE_PROMPT,
    FOODIE_PROMPT,
    LEISURE_PROMPT,
    PRICING_GUIDANCE
)
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class TravelPlannerAgent:
    """
    AI agent for travel planning.
    Generates intelligent travel itineraries based on user preferences.

    V2.0 特性：
    - 丰富的实用信息（门票、预订、最佳时间等）
    - 完整的行前准备清单
    - 详细的实用提示
    - 隐藏技术细节（coordinates），突出用户关心内容
    """

    def __init__(self, use_strict_json: bool = True):
        """
        Initialize planner agent.

        Args:
            use_strict_json: Whether to use strict JSON output format
        """
        self.use_strict_json = use_strict_json
        # 显式设置max_tokens以确保生成完整的行程
        self.llm = LLMFactory.create_client(
            provider="minimax",
            model_name="MiniMax-M2.1",
            temperature=0.7,
            max_tokens=settings.AI_MAX_TOKENS  # 使用配置的max_tokens
        )

    def _get_style_prompt(self, travel_style: str) -> str:
        """Get style-specific prompt"""
        style_prompts = {
            "leisure": LEISURE_PROMPT,
            "adventure": ADVENTURE_PROMPT,
            "foodie": FOODIE_PROMPT,
            "cultural": CULTURAL_PROMPT
        }
        return style_prompts.get(travel_style, "")

    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """
        Parse AI response into structured data with enhanced error handling.

        Args:
            response: Raw AI response

        Returns:
            Structured itinerary data
        """
        # 保存原始响应用于调试
        self._save_debug_response(response)
        
        if self.use_strict_json:
            try:
                # 清理可能的markdown代码块标记
                cleaned = response.strip()
                if cleaned.startswith('```json'):
                    cleaned = cleaned[7:]
                if cleaned.startswith('```'):
                    cleaned = cleaned[3:]
                if cleaned.endswith('```'):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()

                # 尝试直接解析
                data = json.loads(cleaned)
                logger.info(f"✅ Successfully parsed JSON response")
                return data
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ JSON decode error at line {e.lineno}, col {e.colno}: {e.msg}")
                # 尝试修复JSON
                repaired = self._repair_json(cleaned)
                if repaired:
                    try:
                        data = json.loads(repaired)
                        logger.info("✅ Successfully parsed repaired JSON")
                        return data
                    except json.JSONDecodeError as e2:
                        logger.error(f"❌ Repaired JSON failed at line {e2.lineno}: {e2.msg}")
                        return self._flexible_parse(response)
                else:
                    return self._flexible_parse(response)
        else:
            return self._flexible_parse(response)

    def _flexible_parse(self, response: str) -> Dict[str, Any]:
        """
        Flexible parsing for non-JSON responses.
        Extract structure from text with enhanced error recovery.
        """
        import re

        logger.info(f"Attempting flexible parse, response length: {len(response)}")
        
        # 尝试从文本中提取JSON部分
        json_pattern = r'\{[\s\S]*\}'
        matches = re.findall(json_pattern, response)

        if matches:
            logger.info(f"Found {len(matches)} JSON-like structures")
            # 尝试从最大的JSON对象开始
            candidates = sorted(matches, key=len, reverse=True)

            for idx, json_str in enumerate(candidates):
                logger.info(f"Trying candidate {idx + 1}/{len(candidates)}, length: {len(json_str)}")
                # 尝试修复并解析
                repaired = self._repair_json(json_str)
                if repaired:
                    try:
                        data = json.loads(repaired)
                        logger.info(f"✅ Successfully parsed repaired JSON (length: {len(repaired)})")
                        logger.info(f"✅ Parsed data has {len(data.get('days', []))} days")
                        return data
                    except json.JSONDecodeError as e:
                        logger.warning(f"❌ Failed to parse candidate {idx + 1}: {e}")
                        continue

        # 如果完全失败，返回基础结构
        logger.error("❌ All parse attempts failed, returning basic structure")
        logger.error(f"Response preview (first 1000 chars): {response[:1000]}")
        return {
            "title": "AI生成的旅行计划",
            "summary": "解析失败，请重新生成",
            "days": [],
            "preparation": {},
            "tips": {}
        }

    def _repair_json(self, json_str: str) -> Optional[str]:
        """
        Attempt to repair malformed JSON with aggressive strategies.

        Args:
            json_str: Potentially malformed JSON string

        Returns:
            Repaired JSON string or None if repair failed
        """
        import re

        try:
            # 先尝试直接解析
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError as e:
            logger.debug(f"Initial parse failed at line {e.lineno}: {e.msg}")

        # 第一轮：基本清理 - 替换所有中文标点为英文标点
        repaired = json_str
        repaired = repaired.replace('"', '"').replace('"', '"')
        repaired = repaired.replace(''', "'").replace(''', "'")
        repaired = repaired.replace('，', ',').replace('：', ':')
        repaired = repaired.replace('；', ';').replace('（', '(').replace('）', ')')
        repaired = repaired.replace('　', ' ')  # 全角空格
        
        # 尝试解析
        try:
            json.loads(repaired)
            logger.info("✅ JSON repaired with punctuation fixes")
            return repaired
        except json.JSONDecodeError:
            pass

        # 第二轮：正则表达式修复
        repairs = [
            # 修复缺少的逗号（对象结束后跟字段名）
            (r'}\s+\"', '},\n\"'),
            # 修复缺少的逗号（数组结束后跟字段名）
            (r']\s+\"', '],\n\"'),
            # 修复缺少的逗号（字符串值后直接跟字段名）
            (r'\"\s+\"(\w+)\":', '\",\n\"\\1\":'),
            # 修复缺少的逗号（数字后跟字段名）
            (r'(\d)\s+\"', r'\1,\n\"'),
            # 修复缺少的逗号（布尔值后跟字段名）
            (r'(true|false)\s+\"', r'\1,\n\"'),
            # 移除多余的逗号
            (r',(\s*[}\]])', r'\1'),
        ]

        for iteration in range(10):
            original = repaired
            for pattern, replacement in repairs:
                repaired = re.sub(pattern, replacement, repaired)

            # 如果没有变化，停止
            if repaired == original:
                break

            # 尝试解析
            try:
                json.loads(repaired)
                logger.info(f"✅ JSON repaired after {iteration + 1} iterations")
                return repaired
            except json.JSONDecodeError:
                # 如果没有变化，跳出循环
                if repaired == original:
                    break

        # 如果所有修复都失败，返回 None
        return None

    def _save_debug_response(self, response: str):
        """保存AI响应用于调试"""
        try:
            debug_dir = "backend/test_results"
            os.makedirs(debug_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(debug_dir, f"ai_response_{timestamp}.txt")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response)
            logger.debug(f"Saved debug response to {filename}")
        except Exception as e:
            logger.warning(f"Failed to save debug response: {e}")

    def _build_user_prompt(
        self,
        destination: str,
        days: int,
        budget: float,
        travel_style: str,
        departure: str = None,
        preferences: Dict[str, Any] = None
    ) -> str:
        """
        构建用户输入提示

        Returns:
            格式化的用户提示
        """
        prompt = f"""
请为{destination}制定一个{days}天的旅行计划。

📍 目的地：{destination}
🚅 出发地：{departure or '未指定'}
📅 天数：{days}天
💰 预算：¥{budget if budget else '不限'}
🎨 旅行风格：{travel_style}
💭 特殊偏好：{preferences or '无特殊要求'}

📋 要求：
1. 每天安排合理，避免过于紧凑
2. 推荐当地特色景点和美食
3. 考虑交通便利性
4. 控制在预算范围内
5. 提供详细的实用信息（门票价格、是否需预订、最佳时间等）
6. 给出具体的行前准备清单
7. 包含避坑指南和实用提示
"""

        # 添加定价参考
        if budget:
            prompt += f"\n\n{PRICING_GUIDANCE}\n"
            prompt += f"总预算：¥{budget}，请合理分配各项费用。"

        return prompt

    async def generate_itinerary(
        self,
        destination: str,
        days: int,
        budget: float,
        travel_style: str,
        departure: str = None,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate a travel itinerary using AI.

        Args:
            destination: Travel destination
            days: Number of days
            budget: Budget in CNY
            travel_style: Travel style (leisure, adventure, foodie)
            departure: Departure location
            preferences: Additional preferences

        Returns:
            Generated itinerary data with daily details and practical information
        """
        # 构建用户提示
        user_input = self._build_user_prompt(
            destination=destination,
            days=days,
            budget=budget,
            travel_style=travel_style,
            departure=departure,
            preferences=preferences
        )

        # 获取风格特定的提示
        style_prompt = self._get_style_prompt(travel_style)

        # 添加JSON输出要求
        if self.use_strict_json:
            user_input += "\n\n" + STRICT_JSON_OUTPUT
        else:
            user_input += "\n\n" + FLEXIBLE_JSON_OUTPUT

        # 构建系统消息（包含风格提示）
        system_content = PLANNING_SYSTEM_PROMPT
        if style_prompt:
            system_content += "\n\n" + style_prompt

        # 生成行程
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=user_input)
        ]

        try:
            logger.info(f"Generating itinerary for {destination}, {days} days, style: {travel_style}")
            response = await LLMFactory.agenerate(self.llm, messages)
            logger.info(f"AI response received, length: {len(response)}")
            logger.info(f"AI response (first 500 chars): {response[:500]}...")

            # 解析响应为结构化行程数据
            itinerary_data = self._parse_ai_response(response)

            # 补充必填字段（如果AI未生成）
            if "title" not in itinerary_data:
                itinerary_data["title"] = f"{destination}{days}日游"
            if "summary" not in itinerary_data:
                itinerary_data["summary"] = f"{destination}{days}天深度游，体验当地特色"
            if "highlights" not in itinerary_data:
                itinerary_data["highlights"] = [f"探索{destination}的精华"]
            if "best_season" not in itinerary_data:
                itinerary_data["best_season"] = "全年适宜"
            if "weather" not in itinerary_data:
                itinerary_data["weather"] = "请根据当地天气预报准备衣物"

            # 计算总花费
            if "actual_cost" not in itinerary_data and "cost_breakdown" in itinerary_data:
                cost_breakdown = itinerary_data["cost_breakdown"]
                total_cost = (
                    cost_breakdown.get("transportation", 0) +
                    cost_breakdown.get("accommodation", 0) +
                    cost_breakdown.get("food", 0) +
                    cost_breakdown.get("tickets", 0) +
                    cost_breakdown.get("shopping", 0) +
                    cost_breakdown.get("other", 0)
                )
                itinerary_data["actual_cost"] = total_cost

            # 为每天添加默认值
            for day in itinerary_data.get("days", []):
                if "total_cost" not in day:
                    # 计算当天的花费
                    day_cost = 0
                    for activity in day.get("activities", []):
                        day_cost += activity.get("average_cost", 0)
                    day["total_cost"] = day_cost

                # 确保每个活动都有必要的字段
                for activity in day.get("activities", []):
                    if "tips" not in activity or not activity["tips"]:
                        activity["tips"] = ["建议提前查看开放时间"]
                    if "average_cost" not in activity:
                        activity["average_cost"] = 0

            # 添加默认的行前准备（如果AI未生成）
            if "preparation" not in itinerary_data or not itinerary_data["preparation"]:
                itinerary_data["preparation"] = {
                    "documents": ["身份证"],
                    "essentials": ["手机", "充电器", "现金"],
                    "suggestions": ["相机", "雨伞"],
                    "booking_reminders": ["建议提前预订住宿和交通"]
                }

            # 添加默认的实用提示（如果AI未生成）
            if "tips" not in itinerary_data or not itinerary_data["tips"]:
                itinerary_data["tips"] = {
                    "transportation": f"建议使用当地交通工具游览{destination}",
                    "accommodation": "建议选择市中心或景点附近的住宿",
                    "food": f"可以尝试{destination}当地特色美食",
                    "shopping": "购买特产建议去正规商店",
                    "safety": "注意保管好随身财物",
                    "other": ["建议购买旅游保险", "保持手机电量充足"]
                }

            logger.info(f"Itinerary generated successfully: {itinerary_data.get('title')}")
            return itinerary_data

        except Exception as e:
            logger.error(f"Error generating itinerary: {str(e)}", exc_info=True)
            # 返回基础结构而不是抛出异常
            return {
                "title": f"{destination}{days}日游",
                "summary": "行程生成遇到问题，请重试",
                "destination": destination,
                "days": days,
                "budget": budget,
                "travel_style": travel_style,
                "highlights": [],
                "days": [],
                "preparation": {},
                "tips": {},
                "error": str(e)
            }

    async def optimize_itinerary(
        self,
        current_itinerary: Dict[str, Any],
        feedback: str,
        affected_days: List[int] = None,
        use_strict_json: bool = None
    ) -> Dict[str, Any]:
        """
        Optimize an existing itinerary based on user feedback.

        Args:
            current_itinerary: Current itinerary data
            feedback: User feedback for optimization
            affected_days: List of day numbers to optimize
            use_strict_json: Override strict_json setting

        Returns:
            Optimized itinerary data
        """
        strict_mode = use_strict_json if use_strict_json is not None else self.use_strict_json

        # 构建优化提示
        prompt = f"""
用户对以下行程不满意，需要根据反馈进行优化：

当前行程：
{json.dumps(current_itinerary, ensure_ascii=False, indent=2)}

用户反馈：
{feedback}

需要优化的天数：{', '.join(map(str, affected_days)) if affected_days else '全部'}

请根据用户反馈重新生成这些天的行程，保持以下原则：
1. 修正用户不满意的地方
2. 保持其他天数不变（除非用户要求修改全部）
3. 确保新的行程更符合用户需求
4. 包含详细的实用信息（门票、预订、提示等）
"""

        if strict_mode:
            prompt += "\n\n" + STRICT_JSON_OUTPUT
        else:
            prompt += "\n\n" + FLEXIBLE_JSON_OUTPUT

        messages = [
            SystemMessage(content=PLANNING_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]

        try:
            logger.info(f"Optimizing itinerary based on feedback: {feedback}")
            response = await LLMFactory.agenerate(self.llm, messages)
            logger.info(f"Optimization response received, length: {len(response)}")

            # 解析优化结果
            optimized_data = self._parse_ai_response(response)

            # 如果只优化特定天数，合并原行程
            if affected_days and "days" in optimized_data:
                # 保留未修改的天数
                original_days = current_itinerary.get("days", [])
                new_days = []

                for day in original_days:
                    if day.get("day_number") in affected_days:
                        # 从优化结果中找到新的这一天
                        for new_day in optimized_data["days"]:
                            if new_day.get("day_number") == day.get("day_number"):
                                new_days.append(new_day)
                                break
                    else:
                        new_days.append(day)

                optimized_data["days"] = new_days

            logger.info("Itinerary optimized successfully")
            return optimized_data

        except Exception as e:
            logger.error(f"Error optimizing itinerary: {str(e)}", exc_info=True)
            raise
