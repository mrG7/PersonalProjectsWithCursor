"""
Lead Qualifier - Lead Scoring and Qualification Component

This module handles lead qualification, scoring, and prioritization based on
multiple criteria including company fit, budget, authority, need, and timing.
"""

import asyncio
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import statistics


class QualificationLevel(Enum):
    """Lead qualification levels"""
    HOT = "hot"
    WARM = "warm"
    COOL = "cool"
    COLD = "cold"


@dataclass
class QualificationCriteria:
    """Criteria for lead qualification"""
    budget_minimum: int = 50000
    decision_timeline_max_months: int = 6
    technical_fit_threshold: float = 0.7
    authority_level_minimum: int = 3  # 1-5 scale
    company_size_minimum: int = 50
    company_size_maximum: int = 1000
    industry_match_required: bool = True
    technology_match_threshold: float = 0.5


@dataclass
class LeadScore:
    """Comprehensive lead scoring results"""
    overall_score: float
    qualification_level: QualificationLevel
    component_scores: Dict[str, float]
    scoring_breakdown: Dict[str, Any]
    recommendations: List[str]
    next_steps: List[str]
    disqualifying_factors: List[str]
    scored_at: datetime

    def __post_init__(self):
        if self.scored_at is None:
            self.scored_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['qualification_level'] = self.qualification_level.value
        data['scored_at'] = self.scored_at.isoformat()
        return data


@dataclass
class QualifiedLead:
    """Represents a qualified sales lead"""
    prospect_data: Dict[str, Any]
    lead_score: LeadScore
    qualification_date: datetime
    priority_rank: int
    estimated_value: Optional[float] = None
    conversion_probability: Optional[float] = None
    recommended_approach: Optional[str] = None

    def __post_init__(self):
        if self.qualification_date is None:
            self.qualification_date = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'prospect_data': self.prospect_data,
            'lead_score': self.lead_score.to_dict(),
            'qualification_date': self.qualification_date.isoformat(),
            'priority_rank': self.priority_rank,
            'estimated_value': self.estimated_value,
            'conversion_probability': self.conversion_probability,
            'recommended_approach': self.recommended_approach
        }


class LeadQualifier:
    """
    Lead Qualifier for scoring and prioritizing sales leads.

    Features:
    - Multi-criteria lead scoring (BANT + custom criteria)
    - Qualification level assignment (Hot/Warm/Cool/Cold)
    - Priority ranking and recommendations
    - Conversion probability estimation
    - Value assessment and forecasting
    """

    def __init__(self, config):
        """
        Initialize the Lead Qualifier

        Args:
            config: LeadGenerationConfig object
        """
        self.config = config
        self.logger = logging.getLogger('LeadQualifier')

        # Initialize qualification criteria
        self.criteria = QualificationCriteria(
            budget_minimum=config.budget_minimum,
            decision_timeline_max_months=config.qualification_criteria.get('decision_timeline', 6),
            technical_fit_threshold=config.qualification_criteria.get('technical_fit', 0.7),
            company_size_minimum=config.company_size_range[0],
            company_size_maximum=config.company_size_range[1]
        )

        # Scoring weights
        self.scoring_weights = {
            'company_fit': 0.20,
            'budget_alignment': 0.25,
            'authority_level': 0.15,
            'need_intensity': 0.20,
            'timing_urgency': 0.10,
            'engagement_potential': 0.10
        }

        # Qualification thresholds
        self.qualification_thresholds = {
            'hot': 0.85,
            'warm': 0.70,
            'cool': 0.55,
            'cold': 0.0
        }

    async def qualify_leads(self, prospects: List[Any]) -> List[QualifiedLead]:
        """
        Qualify a list of prospects

        Args:
            prospects: List of prospect objects to qualify

        Returns:
            List of qualified leads with scoring
        """
        self.logger.info(f"Starting qualification of {len(prospects)} prospects")

        qualified_leads = []

        for prospect in prospects:
            try:
                # Score the lead
                lead_score = await self._score_lead(prospect)

                # Determine qualification level
                qualification_level = self._determine_qualification_level(lead_score.overall_score)

                # Only include warm or better leads
                if qualification_level in [QualificationLevel.HOT, QualificationLevel.WARM]:
                    # Create qualified lead
                    qualified_lead = QualifiedLead(
                        prospect_data=prospect.to_dict() if hasattr(prospect, 'to_dict') else prospect,
                        lead_score=lead_score,
                        priority_rank=0,  # Will be set after all leads are qualified
                        estimated_value=self._estimate_lead_value(prospect, lead_score),
                        conversion_probability=self._estimate_conversion_probability(lead_score),
                        recommended_approach=self._generate_recommended_approach(lead_score)
                    )

                    qualified_leads.append(qualified_lead)
                    self.logger.debug(f"Qualified lead: {prospect.company_name if hasattr(prospect, 'company_name') else 'Unknown'}")

            except Exception as e:
                self.logger.error(f"Error qualifying prospect: {e}")
                continue

        # Sort by priority and assign ranks
        qualified_leads.sort(key=lambda x: x.lead_score.overall_score, reverse=True)
        for i, lead in enumerate(qualified_leads, 1):
            lead.priority_rank = i

        self.logger.info(f"Qualification completed: {len(qualified_leads)} qualified leads")
        return qualified_leads

    async def _score_lead(self, prospect) -> LeadScore:
        """Score a single lead across multiple criteria"""
        # Extract prospect data
        prospect_data = prospect.to_dict() if hasattr(prospect, 'to_dict') else prospect

        # Calculate component scores
        component_scores = {}

        # Company Fit Score (0-1)
        component_scores['company_fit'] = self._score_company_fit(prospect_data)

        # Budget Alignment Score (0-1)
        component_scores['budget_alignment'] = self._score_budget_alignment(prospect_data)

        # Authority Level Score (0-1)
        component_scores['authority_level'] = self._score_authority_level(prospect_data)

        # Need Intensity Score (0-1)
        component_scores['need_intensity'] = self._score_need_intensity(prospect_data)

        # Timing Urgency Score (0-1)
        component_scores['timing_urgency'] = self._score_timing_urgency(prospect_data)

        # Engagement Potential Score (0-1)
        component_scores['engagement_potential'] = self._score_engagement_potential(prospect_data)

        # Calculate overall score
        overall_score = sum(
            score * self.scoring_weights[criterion]
            for criterion, score in component_scores.items()
        )

        # Generate recommendations and next steps
        recommendations, next_steps = self._generate_recommendations(component_scores, prospect_data)
        disqualifying_factors = self._identify_disqualifying_factors(component_scores, prospect_data)

        return LeadScore(
            overall_score=overall_score,
            qualification_level=self._determine_qualification_level(overall_score),
            component_scores=component_scores,
            scoring_breakdown=self._create_scoring_breakdown(component_scores),
            recommendations=recommendations,
            next_steps=next_steps,
            disqualifying_factors=disqualifying_factors
        )

    def _score_company_fit(self, prospect_data: Dict[str, Any]) -> float:
        """Score company fit based on industry, size, and target criteria"""
        score = 0.0
        factors = 0

        # Industry match
        if prospect_data.get('industry') == self.config.target_industry:
            score += 1.0
        factors += 1

        # Company size fit
        company_size = prospect_data.get('company_size', 0)
        if (self.criteria.company_size_minimum <= company_size <= self.criteria.company_size_maximum):
            score += 1.0
        elif company_size < self.criteria.company_size_minimum:
            score += 0.3  # Partial credit for smaller companies
        factors += 1

        # Geographic fit
        location = prospect_data.get('location', '')
        if any(region.lower() in location.lower() for region in self.config.geographic_focus):
            score += 1.0
        factors += 1

        return score / factors if factors > 0 else 0.0

    def _score_budget_alignment(self, prospect_data: Dict[str, Any]) -> float:
        """Score budget alignment and financial capacity"""
        revenue_range = prospect_data.get('revenue_range', '')

        # Parse revenue range (simplified)
        if '$100M+' in revenue_range or '$50M-$100M' in revenue_range:
            return 1.0  # High budget capacity
        elif '$25M-$50M' in revenue_range or '$10M-$25M' in revenue_range:
            return 0.8  # Medium budget capacity
        elif '$5M-$10M' in revenue_range:
            return 0.6  # Lower budget capacity
        elif '$1M-$5M' in revenue_range:
            return 0.3  # Limited budget capacity
        else:
            return 0.5  # Unknown, assume moderate

    def _score_authority_level(self, prospect_data: Dict[str, Any]) -> float:
        """Score based on contacts' authority and decision-making power"""
        contacts = prospect_data.get('key_contacts', [])

        if not contacts:
            return 0.2  # No contacts found

        authority_scores = []
        for contact in contacts:
            title = contact.get('title', '').lower()

            # Score based on title keywords
            if any(keyword in title for keyword in ['ceo', 'chief', 'president', 'owner']):
                authority_scores.append(1.0)
            elif any(keyword in title for keyword in ['vp', 'vice president', 'director']):
                authority_scores.append(0.8)
            elif any(keyword in title for keyword in ['manager', 'senior']):
                authority_scores.append(0.6)
            elif any(keyword in title for keyword in ['specialist', 'analyst', 'associate']):
                authority_scores.append(0.3)
            else:
                authority_scores.append(0.4)  # Default

        return statistics.mean(authority_scores) if authority_scores else 0.2

    def _score_need_intensity(self, prospect_data: Dict[str, Any]) -> float:
        """Score based on indicators of need and pain points"""
        score = 0.5  # Base score

        # Recent news indicating growth/challenges
        recent_news = prospect_data.get('recent_news', [])
        if recent_news:
            # Look for keywords indicating need
            need_keywords = ['expansion', 'growth', 'scaling', 'challenge', 'problem', 'solution']
            news_text = ' '.join(recent_news).lower()

            if any(keyword in news_text for keyword in need_keywords):
                score += 0.3

        # Company size as indicator of need
        company_size = prospect_data.get('company_size', 0)
        if company_size > 200:
            score += 0.2  # Larger companies often have more complex needs

        # Technology stack as need indicator
        technologies = prospect_data.get('technologies', [])
        if len(technologies) > 5:
            score += 0.1  # More technologies might indicate more complex needs

        return min(score, 1.0)  # Cap at 1.0

    def _score_timing_urgency(self, prospect_data: Dict[str, Any]) -> float:
        """Score based on decision timeline and urgency indicators"""
        # This would typically be determined through research
        # For demo, we'll use some heuristics

        score = 0.5  # Base moderate timing

        # Company size can indicate timeline
        company_size = prospect_data.get('company_size', 0)
        if company_size > 500:
            score += 0.2  # Larger companies often have longer decision cycles
        elif company_size < 100:
            score += 0.1  # Smaller companies can decide faster

        # Recent news indicating urgency
        recent_news = prospect_data.get('recent_news', [])
        urgency_keywords = ['urgent', 'immediate', 'deadline', 'crisis', 'problem']
        news_text = ' '.join(recent_news).lower()

        if any(keyword in news_text for keyword in urgency_keywords):
            score += 0.2

        return min(score, 1.0)

    def _score_engagement_potential(self, prospect_data: Dict[str, Any]) -> float:
        """Score based on social media presence and engagement indicators"""
        score = 0.5  # Base score

        # Social media presence
        social_profiles = prospect_data.get('social_profiles', {})
        if social_profiles:
            score += 0.2
            if len(social_profiles) > 2:
                score += 0.1

        # Website quality (simplified heuristic)
        website = prospect_data.get('website', '')
        if website and 'https://' in website:
            score += 0.1

        # Company description length as engagement indicator
        description = prospect_data.get('description', '')
        if len(description) > 100:
            score += 0.1

        return min(score, 1.0)

    def _determine_qualification_level(self, overall_score: float) -> QualificationLevel:
        """Determine qualification level based on overall score"""
        if overall_score >= self.qualification_thresholds['hot']:
            return QualificationLevel.HOT
        elif overall_score >= self.qualification_thresholds['warm']:
            return QualificationLevel.WARM
        elif overall_score >= self.qualification_thresholds['cool']:
            return QualificationLevel.COOL
        else:
            return QualificationLevel.COLD

    def _create_scoring_breakdown(self, component_scores: Dict[str, float]) -> Dict[str, Any]:
        """Create detailed scoring breakdown for transparency"""
        return {
            'weighted_scores': {
                criterion: score * self.scoring_weights[criterion]
                for criterion, score in component_scores.items()
            },
            'weight_distribution': self.scoring_weights,
            'score_interpretation': {
                score: self._interpret_component_score(criterion, score)
                for criterion, score in component_scores.items()
            }
        }

    def _interpret_component_score(self, criterion: str, score: float) -> str:
        """Provide human-readable interpretation of component scores"""
        if score >= 0.8:
            return f"Excellent {criterion.replace('_', ' ')}"
        elif score >= 0.6:
            return f"Good {criterion.replace('_', ' ')}"
        elif score >= 0.4:
            return f"Fair {criterion.replace('_', ' ')}"
        else:
            return f"Poor {criterion.replace('_', ' ')}"

    def _generate_recommendations(self, component_scores: Dict[str, float],
                                prospect_data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Generate recommendations and next steps based on scoring"""
        recommendations = []
        next_steps = []

        # Budget-related recommendations
        if component_scores['budget_alignment'] < 0.6:
            recommendations.append("Focus on cost-effective solutions and ROI demonstrations")
            next_steps.append("Prepare detailed pricing proposals and ROI calculations")

        # Authority recommendations
        if component_scores['authority_level'] < 0.5:
            recommendations.append("Identify and connect with key decision-makers")
            next_steps.append("Research executive contacts and LinkedIn connections")

        # Need intensity recommendations
        if component_scores['need_intensity'] > 0.7:
            recommendations.append("Emphasize problem-solution fit in communications")
            next_steps.append("Prepare case studies addressing similar challenges")

        # Timing recommendations
        if component_scores['timing_urgency'] > 0.7:
            recommendations.append("Accelerate sales process with immediate value props")
            next_steps.append("Schedule discovery calls within 48 hours")

        # General recommendations
        if all(score > 0.7 for score in component_scores.values()):
            recommendations.append("High-potential lead - prioritize immediate outreach")
            next_steps.append("Send personalized introduction email today")

        return recommendations, next_steps

    def _identify_disqualifying_factors(self, component_scores: Dict[str, float],
                                      prospect_data: Dict[str, Any]) -> List[str]:
        """Identify factors that might disqualify the lead"""
        factors = []

        if component_scores['budget_alignment'] < 0.3:
            factors.append("Insufficient budget capacity for our solutions")

        if component_scores['company_fit'] < 0.3:
            factors.append("Company profile doesn't match target criteria")

        if component_scores['authority_level'] < 0.2:
            factors.append("Unable to identify decision-making contacts")

        company_size = prospect_data.get('company_size', 0)
        if company_size < self.criteria.company_size_minimum:
            factors.append(f"Company size ({company_size}) below minimum threshold")

        return factors

    def _estimate_lead_value(self, prospect, lead_score: LeadScore) -> Optional[float]:
        """Estimate the potential value of the lead"""
        # Simplified estimation based on company size and score
        company_size = prospect.company_size if hasattr(prospect, 'company_size') else 100

        # Base value calculation
        base_value = company_size * 100  # Rough estimate

        # Adjust based on lead score
        value_multiplier = 0.5 + (lead_score.overall_score * 0.5)  # 0.5 to 1.0

        return base_value * value_multiplier

    def _estimate_conversion_probability(self, lead_score: LeadScore) -> Optional[float]:
        """Estimate conversion probability based on lead score"""
        # Simplified model: higher score = higher conversion probability
        return lead_score.overall_score * 0.8 + 0.1  # 0.1 to 0.9 range

    def _generate_recommended_approach(self, lead_score: LeadScore) -> Optional[str]:
        """Generate recommended sales approach"""
        if lead_score.overall_score >= 0.85:
            return "Direct executive outreach with value proposition"
        elif lead_score.overall_score >= 0.7:
            return "Multi-touch campaign with educational content"
        elif lead_score.overall_score >= 0.55:
            return "Nurture campaign with case studies and webinars"
        else:
            return "Monitor for future opportunities"

    async def re_score_leads(self, qualified_leads: List[QualifiedLead]) -> List[QualifiedLead]:
        """
        Re-score existing qualified leads with updated information

        Args:
            qualified_leads: List of previously qualified leads

        Returns:
            List of re-scored leads
        """
        self.logger.info(f"Re-scoring {len(qualified_leads)} leads")

        re_scored_leads = []

        for lead in qualified_leads:
            # In a real implementation, this would fetch updated prospect data
            # For demo, we'll slightly adjust the scores
            try:
                # Simulate score changes over time
                score_adjustment = (0.05 - 0.1) * (1 if lead.lead_score.overall_score < 0.8 else -1)

                new_overall_score = min(1.0, max(0.0, lead.lead_score.overall_score + score_adjustment))
                lead.lead_score.overall_score = new_overall_score
                lead.lead_score.qualification_level = self._determine_qualification_level(new_overall_score)

                re_scored_leads.append(lead)

            except Exception as e:
                self.logger.error(f"Error re-scoring lead: {e}")
                continue

        # Re-sort by new scores
        re_scored_leads.sort(key=lambda x: x.lead_score.overall_score, reverse=True)
        for i, lead in enumerate(re_scored_leads, 1):
            lead.priority_rank = i

        self.logger.info("Lead re-scoring completed")
        return re_scored_leads
