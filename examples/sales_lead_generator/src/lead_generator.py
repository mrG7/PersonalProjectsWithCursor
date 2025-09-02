"""
Sales Lead Generator - Main Orchestrator Class

This is the main orchestrator for the Sales Lead Generator agent system.
It coordinates prospect research, qualification, email automation, and analytics.
"""

import asyncio
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import aiofiles

from .prospect_researcher import ProspectResearcher
from .lead_qualifier import LeadQualifier
from .email_automation import EmailAutomationAgent
from .crm_integrator import CRMIntegrator
from .analytics_tracker import AnalyticsTracker


@dataclass
class LeadGenerationConfig:
    """Configuration for lead generation campaigns"""
    target_industry: str = "technology"
    company_size_range: tuple = (50, 1000)
    geographic_focus: List[str] = None
    budget_minimum: int = 50000
    qualification_criteria: Dict[str, Any] = None
    daily_lead_target: int = 25
    max_concurrent_tasks: int = 5
    email_sequence_enabled: bool = True
    crm_integration: bool = False
    analytics_enabled: bool = True

    def __post_init__(self):
        if self.geographic_focus is None:
            self.geographic_focus = ["United States"]
        if self.qualification_criteria is None:
            self.qualification_criteria = {
                "decision_timeline": "3-6 months",
                "technical_fit": 0.7,
                "budget_alignment": 0.8
            }


@dataclass
class CampaignMetrics:
    """Real-time campaign performance metrics"""
    campaign_id: str
    start_date: datetime
    prospects_researched: int = 0
    leads_qualified: int = 0
    emails_sent: int = 0
    responses_received: int = 0
    meetings_booked: int = 0
    deals_closed: int = 0
    total_pipeline_value: float = 0.0
    conversion_rate: float = 0.0

    def update_conversion_rate(self):
        """Calculate conversion rate from prospects to qualified leads"""
        if self.prospects_researched > 0:
            self.conversion_rate = self.leads_qualified / self.prospects_researched

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['start_date'] = self.start_date.isoformat()
        return data


class SalesLeadGenerator:
    """
    Main Sales Lead Generator orchestrator.

    Coordinates all components of the lead generation system including:
    - Prospect research and discovery
    - Lead qualification and scoring
    - Email sequence automation
    - CRM integration
    - Performance analytics and reporting
    """

    def __init__(self, config_path: str = None, log_level: str = "INFO"):
        """
        Initialize the Sales Lead Generator

        Args:
            config_path: Path to configuration file
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), '..', 'config', 'lead_generator_config.json'
        )
        self.config = self._load_config()
        self._setup_logging(log_level)

        # Initialize components
        self.prospect_researcher = ProspectResearcher(self.config)
        self.lead_qualifier = LeadQualifier(self.config)
        self.email_automation = EmailAutomationAgent(self.config)
        self.crm_integrator = CRMIntegrator(self.config) if self.config.crm_integration else None
        self.analytics = AnalyticsTracker(self.config) if self.config.analytics_enabled else None

        # Runtime state
        self.is_running = False
        self.campaign_metrics = None
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_concurrent_tasks)

        # Data directories
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(self.data_dir, exist_ok=True)

        self.logger.info("Sales Lead Generator initialized successfully")

    def _load_config(self) -> LeadGenerationConfig:
        """Load configuration from file or create default"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                    return LeadGenerationConfig(**config_data)
            else:
                self.logger.warning(f"Config file not found: {self.config_path}, using defaults")
        except Exception as e:
            self.logger.error(f"Error loading config: {e}, using defaults")

        return LeadGenerationConfig()

    def _setup_logging(self, log_level: str):
        """Setup logging configuration"""
        self.logger = logging.getLogger('SalesLeadGenerator')
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))

        # File handler
        log_file = os.path.join(self.data_dir, 'lead_generator.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    async def start_campaign(self, campaign_id: str = None) -> str:
        """
        Start a new lead generation campaign

        Args:
            campaign_id: Optional campaign identifier

        Returns:
            Campaign ID
        """
        if self.is_running:
            raise RuntimeError("Campaign already running")

        campaign_id = campaign_id or f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.campaign_metrics = CampaignMetrics(
            campaign_id=campaign_id,
            start_date=datetime.now()
        )

        self.is_running = True
        self.logger.info(f"Started campaign: {campaign_id}")

        # Save campaign state
        await self._save_campaign_state()

        return campaign_id

    async def run_daily_cycle(self) -> Dict[str, Any]:
        """
        Run the complete daily lead generation cycle

        Returns:
            Daily cycle results
        """
        if not self.is_running or not self.campaign_metrics:
            raise RuntimeError("No active campaign")

        self.logger.info("Starting daily lead generation cycle")

        try:
            # Phase 1: Prospect Research
            prospects = await self.prospect_researcher.research_prospects(
                target_count=self.config.daily_lead_target
            )
            self.campaign_metrics.prospects_researched += len(prospects)

            # Phase 2: Lead Qualification
            qualified_leads = await self.lead_qualifier.qualify_leads(prospects)
            self.campaign_metrics.leads_qualified += len(qualified_leads)

            # Phase 3: Email Automation (if enabled)
            if self.config.email_sequence_enabled and qualified_leads:
                email_results = await self.email_automation.send_sequences(qualified_leads)
                self.campaign_metrics.emails_sent += email_results.get('sent', 0)
                self.campaign_metrics.responses_received += email_results.get('responses', 0)

            # Phase 4: CRM Integration (if enabled)
            if self.crm_integrator and qualified_leads:
                await self.crm_integrator.sync_leads(qualified_leads)

            # Phase 5: Analytics Update
            if self.analytics:
                await self.analytics.update_metrics(self.campaign_metrics)

            # Update conversion rate
            self.campaign_metrics.update_conversion_rate()

            # Save progress
            await self._save_campaign_state()

            results = {
                'campaign_id': self.campaign_metrics.campaign_id,
                'prospects_found': len(prospects),
                'leads_qualified': len(qualified_leads),
                'emails_sent': self.campaign_metrics.emails_sent,
                'responses_received': self.campaign_metrics.responses_received,
                'conversion_rate': self.campaign_metrics.conversion_rate,
                'timestamp': datetime.now().isoformat()
            }

            self.logger.info(f"Daily cycle completed: {results}")
            return results

        except Exception as e:
            self.logger.error(f"Error in daily cycle: {e}")
            raise

    async def get_campaign_status(self) -> Dict[str, Any]:
        """
        Get current campaign status and metrics

        Returns:
            Campaign status information
        """
        if not self.campaign_metrics:
            return {'status': 'no_active_campaign'}

        # Calculate additional metrics
        days_running = (datetime.now() - self.campaign_metrics.start_date).days + 1
        daily_average = self.campaign_metrics.prospects_researched / days_running

        status = {
            'campaign_id': self.campaign_metrics.campaign_id,
            'status': 'running' if self.is_running else 'paused',
            'start_date': self.campaign_metrics.start_date.isoformat(),
            'days_running': days_running,
            'metrics': self.campaign_metrics.to_dict(),
            'daily_average': daily_average,
            'target_achievement': daily_average / self.config.daily_lead_target,
            'last_updated': datetime.now().isoformat()
        }

        return status

    async def pause_campaign(self):
        """Pause the current campaign"""
        if not self.is_running:
            return

        self.is_running = False
        await self._save_campaign_state()
        self.logger.info("Campaign paused")

    async def resume_campaign(self):
        """Resume a paused campaign"""
        if self.is_running:
            return

        self.is_running = True
        await self._save_campaign_state()
        self.logger.info("Campaign resumed")

    async def stop_campaign(self):
        """Stop the current campaign"""
        if not self.is_running:
            return

        self.is_running = False
        self.logger.info(f"Campaign stopped: {self.campaign_metrics.campaign_id}")

        # Generate final report
        final_report = await self._generate_final_report()
        await self._save_final_report(final_report)

        # Cleanup
        self.campaign_metrics = None

    async def _save_campaign_state(self):
        """Save current campaign state to disk"""
        if not self.campaign_metrics:
            return

        state_file = os.path.join(self.data_dir, f"{self.campaign_metrics.campaign_id}_state.json")

        state_data = {
            'campaign_metrics': self.campaign_metrics.to_dict(),
            'is_running': self.is_running,
            'config': asdict(self.config),
            'last_updated': datetime.now().isoformat()
        }

        async with aiofiles.open(state_file, 'w') as f:
            await f.write(json.dumps(state_data, indent=2))

    async def _generate_final_report(self) -> Dict[str, Any]:
        """Generate final campaign report"""
        if not self.campaign_metrics:
            return {}

        days_running = (datetime.now() - self.campaign_metrics.start_date).days + 1

        report = {
            'campaign_id': self.campaign_metrics.campaign_id,
            'start_date': self.campaign_metrics.start_date.isoformat(),
            'end_date': datetime.now().isoformat(),
            'duration_days': days_running,
            'final_metrics': self.campaign_metrics.to_dict(),
            'performance_summary': {
                'daily_average_prospects': self.campaign_metrics.prospects_researched / days_running,
                'qualification_rate': self.campaign_metrics.conversion_rate,
                'email_response_rate': (
                    self.campaign_metrics.responses_received / self.campaign_metrics.emails_sent
                    if self.campaign_metrics.emails_sent > 0 else 0
                ),
                'target_achievement': (
                    self.campaign_metrics.prospects_researched / (self.config.daily_lead_target * days_running)
                )
            },
            'generated_at': datetime.now().isoformat()
        }

        return report

    async def _save_final_report(self, report: Dict[str, Any]):
        """Save final campaign report"""
        if not report:
            return

        report_file = os.path.join(
            self.data_dir,
            f"{report['campaign_id']}_final_report.json"
        )

        async with aiofiles.open(report_file, 'w') as f:
            await f.write(json.dumps(report, indent=2))

        self.logger.info(f"Final report saved: {report_file}")

    async def cleanup(self):
        """Cleanup resources"""
        if self.executor:
            self.executor.shutdown(wait=True)

        if self.is_running:
            await self.stop_campaign()

        self.logger.info("Sales Lead Generator cleanup completed")


# Convenience functions for quick usage
async def run_daily_campaign(config_path: str = None) -> Dict[str, Any]:
    """
    Run a single daily campaign cycle

    Args:
        config_path: Path to configuration file

    Returns:
        Campaign results
    """
    generator = SalesLeadGenerator(config_path)

    try:
        await generator.start_campaign()
        results = await generator.run_daily_cycle()
        await generator.stop_campaign()
        return results
    finally:
        await generator.cleanup()


def create_campaign_config(
    target_industry: str = "technology",
    company_size_range: tuple = (50, 1000),
    geographic_focus: List[str] = None,
    budget_minimum: int = 50000,
    daily_lead_target: int = 25
) -> LeadGenerationConfig:
    """
    Create a lead generation configuration

    Args:
        target_industry: Target industry for prospects
        company_size_range: Tuple of (min_size, max_size)
        geographic_focus: List of target geographic regions
        budget_minimum: Minimum budget requirement
        daily_lead_target: Number of leads to generate daily

    Returns:
        LeadGenerationConfig object
    """
    return LeadGenerationConfig(
        target_industry=target_industry,
        company_size_range=company_size_range,
        geographic_focus=geographic_focus or ["United States"],
        budget_minimum=budget_minimum,
        daily_lead_target=daily_lead_target
    )


# CLI interface for direct execution
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sales Lead Generator Agent")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--campaign-id", help="Campaign identifier")
    parser.add_argument("--single-run", action="store_true", help="Run single campaign cycle")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    args = parser.parse_args()

    async def main():
        if args.single_run:
            results = await run_daily_campaign(args.config)
            print(json.dumps(results, indent=2))
        else:
            generator = SalesLeadGenerator(args.config, args.log_level)

            try:
                campaign_id = await generator.start_campaign(args.campaign_id)
                print(f"Started campaign: {campaign_id}")

                # Keep running until interrupted
                while True:
                    try:
                        results = await generator.run_daily_cycle()
                        print(f"Daily cycle completed: {json.dumps(results, indent=2)}")

                        # Wait for next day (or shorter for testing)
                        await asyncio.sleep(86400)  # 24 hours

                    except KeyboardInterrupt:
                        print("Stopping campaign...")
                        await generator.stop_campaign()
                        break
                    except Exception as e:
                        print(f"Error in campaign cycle: {e}")
                        await asyncio.sleep(3600)  # Wait 1 hour before retry

            finally:
                await generator.cleanup()

    asyncio.run(main())
