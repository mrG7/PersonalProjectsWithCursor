"""
Analytics Tracker - Performance Monitoring and Analytics

This module handles comprehensive analytics tracking for the sales lead generation system,
including performance metrics, conversion tracking, and predictive analytics.
"""

import asyncio
import logging
import json
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict
import os


@dataclass
class PerformanceMetrics:
    """Real-time performance metrics"""
    total_prospects_researched: int = 0
    prospects_qualified: int = 0
    qualification_rate: float = 0.0
    emails_sent: int = 0
    email_responses: int = 0
    response_rate: float = 0.0
    meetings_booked: int = 0
    conversion_rate: float = 0.0
    average_lead_score: float = 0.0
    campaigns_run: int = 0
    active_campaigns: int = 0

    def update_rates(self):
        """Update calculated rates"""
        if self.total_prospects_researched > 0:
            self.qualification_rate = self.prospects_qualified / self.total_prospects_researched

        if self.emails_sent > 0:
            self.response_rate = self.email_responses / self.emails_sent

        if self.prospects_qualified > 0:
            self.conversion_rate = self.meetings_booked / self.prospects_qualified


@dataclass
class CampaignAnalytics:
    """Campaign-specific analytics"""
    campaign_id: str
    start_date: datetime
    end_date: Optional[datetime] = None
    duration_days: int = 0
    total_prospects: int = 0
    qualified_leads: int = 0
    emails_sent: int = 0
    responses_received: int = 0
    meetings_booked: int = 0
    revenue_generated: float = 0.0
    cost_per_lead: float = 0.0
    roi_percentage: float = 0.0

    def calculate_metrics(self):
        """Calculate derived metrics"""
        if self.end_date and self.start_date:
            self.duration_days = (self.end_date - self.start_date).days

        if self.qualified_leads > 0:
            self.cost_per_lead = (self.emails_sent * 0.1) / self.qualified_leads  # Assuming $0.10 per email

        if self.cost_per_lead > 0:
            self.roi_percentage = (self.revenue_generated / (self.qualified_leads * self.cost_per_lead) - 1) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['start_date'] = self.start_date.isoformat()
        if self.end_date:
            data['end_date'] = self.end_date.isoformat()
        return data


@dataclass
class PredictiveInsights:
    """Predictive analytics insights"""
    next_day_prospects: int
    confidence_level: float
    trend_direction: str  # 'up', 'down', 'stable'
    recommended_actions: List[str]
    risk_factors: List[str]
    generated_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['generated_at'] = self.generated_at.isoformat()
        return data


class AnalyticsTracker:
    """
    Analytics Tracker for comprehensive performance monitoring and insights.

    Features:
    - Real-time performance metrics
    - Campaign analytics and reporting
    - Predictive insights and recommendations
    - Historical trend analysis
    - ROI tracking and optimization
    """

    def __init__(self, config):
        """
        Initialize Analytics Tracker

        Args:
            config: LeadGenerationConfig object
        """
        self.config = config
        self.logger = logging.getLogger('AnalyticsTracker')

        # Performance data
        self.current_metrics = PerformanceMetrics()
        self.campaign_history: List[CampaignAnalytics] = []
        self.daily_metrics: Dict[str, PerformanceMetrics] = {}

        # Predictive analytics
        self.predictive_model = None
        self.historical_data: List[Dict[str, Any]] = []

        # Data storage
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(self.data_dir, exist_ok=True)

        # Load historical data
        asyncio.create_task(self._load_historical_data())

    async def update_metrics(self, campaign_metrics):
        """
        Update performance metrics with new campaign data

        Args:
            campaign_metrics: Campaign metrics object
        """
        try:
            # Update current metrics
            self.current_metrics.total_prospects_researched += campaign_metrics.prospects_researched
            self.current_metrics.prospects_qualified += campaign_metrics.leads_qualified
            self.current_metrics.emails_sent += campaign_metrics.emails_sent
            self.current_metrics.email_responses += campaign_metrics.responses_received
            self.current_metrics.meetings_booked += campaign_metrics.meetings_booked

            # Update calculated rates
            self.current_metrics.update_rates()

            # Store daily metrics
            today = datetime.now().strftime('%Y-%m-%d')
            if today not in self.daily_metrics:
                self.daily_metrics[today] = PerformanceMetrics()

            daily = self.daily_metrics[today]
            daily.total_prospects_researched += campaign_metrics.prospects_researched
            daily.prospects_qualified += campaign_metrics.leads_qualified
            daily.emails_sent += campaign_metrics.emails_sent
            daily.email_responses += campaign_metrics.responses_received
            daily.update_rates()

            # Add to historical data
            self.historical_data.append({
                'date': datetime.now().isoformat(),
                'campaign_id': campaign_metrics.campaign_id,
                'prospects': campaign_metrics.prospects_researched,
                'qualified': campaign_metrics.leads_qualified,
                'emails': campaign_metrics.emails_sent,
                'responses': campaign_metrics.responses_received,
                'meetings': campaign_metrics.meetings_booked
            })

            # Save data
            await self._save_metrics()

            self.logger.debug(f"Updated metrics for campaign {campaign_metrics.campaign_id}")

        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")

    async def get_current_performance(self) -> Dict[str, Any]:
        """
        Get current performance metrics

        Returns:
            Current performance data
        """
        # Update rates before returning
        self.current_metrics.update_rates()

        return {
            'overall_metrics': asdict(self.current_metrics),
            'daily_metrics': {
                date: asdict(metrics)
                for date, metrics in self.daily_metrics.items()
            },
            'last_updated': datetime.now().isoformat()
        }

    async def get_campaign_analytics(self, campaign_id: str = None) -> Dict[str, Any]:
        """
        Get campaign analytics

        Args:
            campaign_id: Specific campaign ID, or None for all

        Returns:
            Campaign analytics data
        """
        if campaign_id:
            # Find specific campaign
            for campaign in self.campaign_history:
                if campaign.campaign_id == campaign_id:
                    campaign.calculate_metrics()
                    return campaign.to_dict()
            return {}
        else:
            # Return all campaigns
            campaigns_data = []
            for campaign in self.campaign_history:
                campaign.calculate_metrics()
                campaigns_data.append(campaign.to_dict())

            return {
                'campaigns': campaigns_data,
                'total_campaigns': len(campaigns_data),
                'summary': self._calculate_campaign_summary(campaigns_data)
            }

    def _calculate_campaign_summary(self, campaigns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics for campaigns"""
        if not campaigns:
            return {}

        total_prospects = sum(c.get('total_prospects', 0) for c in campaigns)
        total_qualified = sum(c.get('qualified_leads', 0) for c in campaigns)
        total_emails = sum(c.get('emails_sent', 0) for c in campaigns)
        total_revenue = sum(c.get('revenue_generated', 0) for c in campaigns)

        return {
            'total_campaigns': len(campaigns),
            'total_prospects': total_prospects,
            'total_qualified_leads': total_qualified,
            'overall_qualification_rate': total_qualified / total_prospects if total_prospects > 0 else 0,
            'total_emails_sent': total_emails,
            'average_emails_per_campaign': total_emails / len(campaigns),
            'total_revenue_generated': total_revenue,
            'average_revenue_per_campaign': total_revenue / len(campaigns)
        }

    async def generate_predictive_insights(self) -> PredictiveInsights:
        """
        Generate predictive insights based on historical data

        Returns:
            Predictive insights
        """
        try:
            # Simple predictive model based on recent trends
            recent_data = self.historical_data[-7:] if len(self.historical_data) >= 7 else self.historical_data

            if not recent_data:
                return PredictiveInsights(
                    next_day_prospects=25,  # Default
                    confidence_level=0.5,
                    trend_direction='stable',
                    recommended_actions=['Continue current strategy'],
                    risk_factors=['Insufficient historical data'],
                    generated_at=datetime.now()
                )

            # Calculate trends
            recent_prospects = [d['prospects'] for d in recent_data]
            avg_prospects = statistics.mean(recent_prospects) if recent_prospects else 25

            # Simple trend analysis
            if len(recent_prospects) >= 3:
                trend = statistics.linear_regression(
                    range(len(recent_prospects)),
                    recent_prospects
                )[0]  # Slope

                if trend > 2:
                    trend_direction = 'up'
                elif trend < -2:
                    trend_direction = 'down'
                else:
                    trend_direction = 'stable'
            else:
                trend_direction = 'stable'

            # Generate recommendations
            recommended_actions = []
            risk_factors = []

            if trend_direction == 'up':
                recommended_actions.append('Increase daily prospect targets')
                recommended_actions.append('Scale email sequences')
            elif trend_direction == 'down':
                recommended_actions.append('Review qualification criteria')
                recommended_actions.append('Optimize prospect sources')
                risk_factors.append('Declining prospect quality')

            if self.current_metrics.qualification_rate < 0.1:
                risk_factors.append('Low qualification rate')
                recommended_actions.append('Refine lead scoring algorithm')

            if self.current_metrics.response_rate < 0.03:
                risk_factors.append('Low email response rate')
                recommended_actions.append('Review email templates and timing')

            return PredictiveInsights(
                next_day_prospects=int(avg_prospects),
                confidence_level=0.75,
                trend_direction=trend_direction,
                recommended_actions=recommended_actions,
                risk_factors=risk_factors,
                generated_at=datetime.now()
            )

        except Exception as e:
            self.logger.error(f"Error generating predictive insights: {e}")
            return PredictiveInsights(
                next_day_prospects=25,
                confidence_level=0.5,
                trend_direction='stable',
                recommended_actions=['Monitor performance closely'],
                risk_factors=[f'Prediction error: {str(e)}'],
                generated_at=datetime.now()
            )

    async def generate_performance_report(self, report_type: str = 'daily',
                                        date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive performance report

        Args:
            report_type: Type of report ('daily', 'weekly', 'monthly', 'campaign')
            date_range: Date range for the report

        Returns:
            Performance report data
        """
        try:
            if report_type == 'daily':
                return await self._generate_daily_report()
            elif report_type == 'weekly':
                return await self._generate_weekly_report()
            elif report_type == 'monthly':
                return await self._generate_monthly_report()
            elif report_type == 'campaign':
                return await self.get_campaign_analytics()
            else:
                raise ValueError(f"Unknown report type: {report_type}")

        except Exception as e:
            self.logger.error(f"Error generating {report_type} report: {e}")
            return {
                'error': str(e),
                'report_type': report_type,
                'generated_at': datetime.now().isoformat()
            }

    async def _generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily performance report"""
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        today_metrics = self.daily_metrics.get(today, PerformanceMetrics())
        yesterday_metrics = self.daily_metrics.get(yesterday, PerformanceMetrics())

        # Calculate changes
        prospect_change = today_metrics.total_prospects_researched - yesterday_metrics.total_prospects_researched
        qualification_change = today_metrics.qualification_rate - yesterday_metrics.qualification_rate

        return {
            'report_type': 'daily',
            'date': today,
            'metrics': asdict(today_metrics),
            'changes_from_yesterday': {
                'prospects': prospect_change,
                'qualification_rate': qualification_change,
                'emails_sent': today_metrics.emails_sent - yesterday_metrics.emails_sent
            },
            'performance_grade': self._calculate_performance_grade(today_metrics),
            'insights': await self._generate_daily_insights(today_metrics),
            'generated_at': datetime.now().isoformat()
        }

    async def _generate_weekly_report(self) -> Dict[str, Any]:
        """Generate weekly performance report"""
        week_start = datetime.now() - timedelta(days=7)
        week_data = [
            metrics for date, metrics in self.daily_metrics.items()
            if datetime.strptime(date, '%Y-%m-%d') >= week_start
        ]

        if not week_data:
            return {'error': 'No data available for this week'}

        # Aggregate weekly metrics
        weekly_prospects = sum(m.total_prospects_researched for m in week_data)
        weekly_qualified = sum(m.prospects_qualified for m in week_data)
        weekly_emails = sum(m.emails_sent for m in week_data)

        return {
            'report_type': 'weekly',
            'week_start': week_start.strftime('%Y-%m-%d'),
            'week_end': datetime.now().strftime('%Y-%m-%d'),
            'summary': {
                'total_prospects': weekly_prospects,
                'qualified_leads': weekly_qualified,
                'qualification_rate': weekly_qualified / weekly_prospects if weekly_prospects > 0 else 0,
                'emails_sent': weekly_emails,
                'average_daily_prospects': weekly_prospects / len(week_data)
            },
            'daily_breakdown': [
                {
                    'date': date,
                    'prospects': metrics.total_prospects_researched,
                    'qualified': metrics.prospects_qualified,
                    'qualification_rate': metrics.qualification_rate
                }
                for date, metrics in self.daily_metrics.items()
                if datetime.strptime(date, '%Y-%m-%d') >= week_start
            ],
            'generated_at': datetime.now().isoformat()
        }

    async def _generate_monthly_report(self) -> Dict[str, Any]:
        """Generate monthly performance report"""
        month_start = datetime.now().replace(day=1)
        month_data = [
            metrics for date, metrics in self.daily_metrics.items()
            if datetime.strptime(date, '%Y-%m-%d') >= month_start
        ]

        # Similar to weekly report but for monthly data
        monthly_prospects = sum(m.total_prospects_researched for m in month_data)
        monthly_qualified = sum(m.prospects_qualified for m in month_data)

        return {
            'report_type': 'monthly',
            'month': month_start.strftime('%Y-%m'),
            'summary': {
                'total_prospects': monthly_prospects,
                'qualified_leads': monthly_qualified,
                'qualification_rate': monthly_qualified / monthly_prospects if monthly_prospects > 0 else 0,
                'campaigns_completed': len([c for c in self.campaign_history if c.end_date and c.end_date >= month_start])
            },
            'generated_at': datetime.now().isoformat()
        }

    def _calculate_performance_grade(self, metrics: PerformanceMetrics) -> str:
        """Calculate performance grade based on metrics"""
        score = 0

        # Qualification rate (40% weight)
        if metrics.qualification_rate >= 0.2:
            score += 40
        elif metrics.qualification_rate >= 0.15:
            score += 30
        elif metrics.qualification_rate >= 0.1:
            score += 20
        elif metrics.qualification_rate >= 0.05:
            score += 10

        # Response rate (30% weight)
        if metrics.response_rate >= 0.05:
            score += 30
        elif metrics.response_rate >= 0.03:
            score += 20
        elif metrics.response_rate >= 0.02:
            score += 10

        # Volume (30% weight)
        if metrics.total_prospects_researched >= 50:
            score += 30
        elif metrics.total_prospects_researched >= 25:
            score += 20
        elif metrics.total_prospects_researched >= 10:
            score += 10

        if score >= 80:
            return 'A'
        elif score >= 60:
            return 'B'
        elif score >= 40:
            return 'C'
        elif score >= 20:
            return 'D'
        else:
            return 'F'

    async def _generate_daily_insights(self, metrics: PerformanceMetrics) -> List[str]:
        """Generate insights based on daily performance"""
        insights = []

        if metrics.qualification_rate > 0.2:
            insights.append("Excellent qualification rate - continue current strategy")
        elif metrics.qualification_rate < 0.1:
            insights.append("Low qualification rate - review lead scoring criteria")

        if metrics.response_rate > 0.05:
            insights.append("Strong email response rate - templates are effective")
        elif metrics.response_rate < 0.02:
            insights.append("Low response rate - consider A/B testing email templates")

        if metrics.total_prospects_researched > 30:
            insights.append("High prospect volume - monitor for quality dilution")

        return insights

    async def _load_historical_data(self):
        """Load historical analytics data"""
        try:
            history_file = os.path.join(self.data_dir, 'analytics_history.json')
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    self.historical_data = json.load(f)
                self.logger.info(f"Loaded {len(self.historical_data)} historical data points")
        except Exception as e:
            self.logger.error(f"Error loading historical data: {e}")

    async def _save_metrics(self):
        """Save current metrics to disk"""
        try:
            # Save current metrics
            metrics_file = os.path.join(self.data_dir, 'current_metrics.json')
            with open(metrics_file, 'w') as f:
                json.dump(asdict(self.current_metrics), f, indent=2)

            # Save historical data
            history_file = os.path.join(self.data_dir, 'analytics_history.json')
            with open(history_file, 'w') as f:
                json.dump(self.historical_data[-1000:], f, indent=2)  # Keep last 1000 entries

            # Save daily metrics
            daily_file = os.path.join(self.data_dir, 'daily_metrics.json')
            with open(daily_file, 'w') as f:
                json.dump(
                    {date: asdict(metrics) for date, metrics in self.daily_metrics.items()},
                    f, indent=2
                )

        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")

    async def export_data(self, format: str = 'json', date_range: Optional[Tuple[datetime, datetime]] = None) -> str:
        """
        Export analytics data in specified format

        Args:
            format: Export format ('json', 'csv')
            date_range: Date range for export

        Returns:
            Path to exported file
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"analytics_export_{timestamp}.{format}"
            filepath = os.path.join(self.data_dir, filename)

            if format == 'json':
                export_data = {
                    'current_metrics': asdict(self.current_metrics),
                    'daily_metrics': {date: asdict(metrics) for date, metrics in self.daily_metrics.items()},
                    'campaign_history': [campaign.to_dict() for campaign in self.campaign_history],
                    'exported_at': datetime.now().isoformat()
                }

                with open(filepath, 'w') as f:
                    json.dump(export_data, f, indent=2)

            elif format == 'csv':
                # CSV export would be implemented here
                # For now, just create a placeholder
                with open(filepath, 'w') as f:
                    f.write("CSV export not yet implemented\n")

            self.logger.info(f"Analytics data exported to {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            raise

    async def clear_old_data(self, days_to_keep: int = 90):
        """
        Clear old analytics data to manage storage

        Args:
            days_to_keep: Number of days of data to keep
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            # Clear old daily metrics
            self.daily_metrics = {
                date: metrics for date, metrics in self.daily_metrics.items()
                if datetime.strptime(date, '%Y-%m-%d') >= cutoff_date
            }

            # Clear old historical data
            self.historical_data = [
                data for data in self.historical_data
                if datetime.fromisoformat(data['date']) >= cutoff_date
            ]

            # Clear old campaign history
            self.campaign_history = [
                campaign for campaign in self.campaign_history
                if campaign.end_date is None or campaign.end_date >= cutoff_date
            ]

            await self._save_metrics()
            self.logger.info(f"Cleared data older than {days_to_keep} days")

        except Exception as e:
            self.logger.error(f"Error clearing old data: {e}")


# Import required modules
import statistics
