#!/usr/bin/env python3
"""
Sales Lead Generator - Main Application Entry Point

This is the main entry point for running the Sales Lead Generator agent.
It provides both programmatic and command-line interfaces for running
lead generation campaigns.
"""

import asyncio
import argparse
import logging
import sys
import os
from typing import Optional

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from lead_generator import SalesLeadGenerator, create_campaign_config
from prospect_researcher import ProspectResearcher
from lead_qualifier import LeadQualifier
from email_automation import EmailAutomationAgent
from crm_integrator import CRMIntegrator
from analytics_tracker import AnalyticsTracker


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )


async def run_single_campaign(config_path: Optional[str] = None,
                            campaign_id: Optional[str] = None,
                            log_level: str = "INFO") -> dict:
    """
    Run a single lead generation campaign

    Args:
        config_path: Path to configuration file
        campaign_id: Optional campaign identifier
        log_level: Logging level

    Returns:
        Campaign results dictionary
    """
    setup_logging(log_level)

    logger = logging.getLogger(__name__)
    logger.info("Starting Sales Lead Generator single campaign")

    generator = SalesLeadGenerator(config_path, log_level)

    try:
        # Start campaign
        campaign_id = await generator.start_campaign(campaign_id)
        logger.info(f"Campaign started: {campaign_id}")

        # Run daily cycle
        results = await generator.run_daily_cycle()
        logger.info(f"Campaign cycle completed: {results}")

        # Stop campaign
        await generator.stop_campaign()
        logger.info("Campaign completed successfully")

        return results

    except Exception as e:
        logger.error(f"Campaign failed: {e}")
        raise
    finally:
        await generator.cleanup()


async def run_continuous_campaign(config_path: Optional[str] = None,
                                campaign_id: Optional[str] = None,
                                log_level: str = "INFO",
                                max_cycles: Optional[int] = None):
    """
    Run a continuous lead generation campaign

    Args:
        config_path: Path to configuration file
        campaign_id: Optional campaign identifier
        log_level: Logging level
        max_cycles: Maximum number of cycles to run
    """
    setup_logging(log_level)

    logger = logging.getLogger(__name__)
    logger.info("Starting Sales Lead Generator continuous campaign")

    generator = SalesLeadGenerator(config_path, log_level)
    cycle_count = 0

    try:
        # Start campaign
        campaign_id = await generator.start_campaign(campaign_id)
        logger.info(f"Continuous campaign started: {campaign_id}")

        while True:
            try:
                # Check if we've reached max cycles
                if max_cycles and cycle_count >= max_cycles:
                    logger.info(f"Reached maximum cycles ({max_cycles}), stopping campaign")
                    break

                # Run daily cycle
                results = await generator.run_daily_cycle()
                cycle_count += 1
                logger.info(f"Cycle {cycle_count} completed: {results}")

                # Get campaign status
                status = await generator.get_campaign_status()
                logger.info(f"Campaign status: Qualification Rate {status['metrics']['qualification_rate']:.1%}")

                # Wait for next cycle (in production, this would be 24 hours)
                await asyncio.sleep(1)  # 1 second for demo

            except KeyboardInterrupt:
                logger.info("Received interrupt signal, stopping campaign")
                break
            except Exception as e:
                logger.error(f"Error in campaign cycle: {e}")
                await asyncio.sleep(5)  # Wait before retry

    except Exception as e:
        logger.error(f"Continuous campaign failed: {e}")
        raise
    finally:
        await generator.stop_campaign()
        await generator.cleanup()
        logger.info("Continuous campaign stopped")


async def run_prospect_research_only(config_path: Optional[str] = None,
                                   target_count: int = 25,
                                   log_level: str = "INFO") -> dict:
    """
    Run only the prospect research component

    Args:
        config_path: Path to configuration file
        target_count: Number of prospects to research
        log_level: Logging level

    Returns:
        Research results
    """
    setup_logging(log_level)

    logger = logging.getLogger(__name__)
    logger.info(f"Starting prospect research for {target_count} targets")

    # Load config or create default
    if config_path and os.path.exists(config_path):
        import json
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        config = create_campaign_config(**config_data)
    else:
        config = create_campaign_config()

    researcher = ProspectResearcher(config)

    try:
        prospects = await researcher.research_prospects(target_count)
        logger.info(f"Research completed: {len(prospects)} prospects found")

        return {
            'prospects_found': len(prospects),
            'prospects': [prospect.to_dict() for prospect in prospects],
            'target_industry': config.target_industry,
            'company_size_range': config.company_size_range,
            'geographic_focus': config.geographic_focus
        }

    except Exception as e:
        logger.error(f"Prospect research failed: {e}")
        raise


async def run_qualification_only(config_path: Optional[str] = None,
                               prospects_data: Optional[list] = None,
                               log_level: str = "INFO") -> dict:
    """
    Run only the lead qualification component

    Args:
        config_path: Path to configuration file
        prospects_data: List of prospect data dictionaries
        log_level: Logging level

    Returns:
        Qualification results
    """
    setup_logging(log_level)

    logger = logging.getLogger(__name__)
    logger.info("Starting lead qualification")

    # Load config or create default
    if config_path and os.path.exists(config_path):
        import json
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        config = create_campaign_config(**config_data)
    else:
        config = create_campaign_config()

    qualifier = LeadQualifier(config)

    try:
        # Convert prospect data to objects
        prospects = []
        if prospects_data:
            from .prospect_researcher import Prospect
            for data in prospects_data:
                prospect = Prospect(
                    company_name=data.get('company_name', 'Unknown'),
                    website=data.get('website', ''),
                    industry=data.get('industry', 'unknown'),
                    company_size=data.get('company_size', 100),
                    location=data.get('location', 'Unknown'),
                    description=data.get('description', ''),
                    research_score=data.get('research_score', 0.5)
                )
                prospects.append(prospect)
        else:
            # Generate sample prospects for testing
            researcher = ProspectResearcher(config)
            prospects = await researcher.research_prospects(10)

        qualified_leads = await qualifier.qualify_leads(prospects)
        logger.info(f"Qualification completed: {len(qualified_leads)} qualified leads")

        return {
            'total_prospects': len(prospects),
            'qualified_leads': len(qualified_leads),
            'qualification_rate': len(qualified_leads) / len(prospects) if prospects else 0,
            'leads': [lead.to_dict() for lead in qualified_leads]
        }

    except Exception as e:
        logger.error(f"Lead qualification failed: {e}")
        raise


async def run_email_test(config_path: Optional[str] = None,
                        log_level: str = "INFO") -> dict:
    """
    Test email automation functionality

    Args:
        config_path: Path to configuration file
        log_level: Logging level

    Returns:
        Email test results
    """
    setup_logging(log_level)

    logger = logging.getLogger(__name__)
    logger.info("Starting email automation test")

    # Load config or create default
    if config_path and os.path.exists(config_path):
        import json
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        config = create_campaign_config(**config_data)
    else:
        config = create_campaign_config()

    email_agent = EmailAutomationAgent(config)

    try:
        # Create a mock qualified lead for testing
        from .lead_qualifier import QualifiedLead, LeadScore
        from .prospect_researcher import Prospect

        mock_prospect = Prospect(
            company_name="Test Company",
            website="https://testcompany.com",
            industry="technology",
            company_size=150,
            location="San Francisco, CA",
            description="A test technology company",
            research_score=0.8
        )

        mock_lead_score = LeadScore(
            overall_score=0.85,
            qualification_level="hot",
            component_scores={
                'company_fit': 0.9,
                'budget_alignment': 0.8,
                'authority_level': 0.85,
                'need_intensity': 0.9,
                'timing_urgency': 0.8,
                'engagement_potential': 0.85
            },
            scoring_breakdown={},
            recommendations=["High-potential lead", "Fast-track to sales team"],
            next_steps=["Send introduction email", "Schedule discovery call"],
            disqualifying_factors=[]
        )

        mock_qualified_lead = QualifiedLead(
            prospect_data=mock_prospect.to_dict(),
            lead_score=mock_lead_score,
            priority_rank=1,
            estimated_value=75000,
            conversion_probability=0.25,
            recommended_approach="Direct executive outreach"
        )

        # Test email sequence
        results = await email_agent.send_sequences([mock_qualified_lead])

        logger.info(f"Email test completed: {results}")

        return {
            'test_type': 'email_sequence',
            'results': results,
            'available_templates': email_agent.list_templates(),
            'available_sequences': email_agent.list_sequences()
        }

    except Exception as e:
        logger.error(f"Email test failed: {e}")
        raise


async def get_system_status(config_path: Optional[str] = None,
                          log_level: str = "INFO") -> dict:
    """
    Get system status and health information

    Args:
        config_path: Path to configuration file
        log_level: Logging level

    Returns:
        System status information
    """
    setup_logging(log_level)

    logger = logging.getLogger(__name__)
    logger.info("Getting system status")

    try:
        generator = SalesLeadGenerator(config_path, log_level)

        # Get current status
        status = await generator.get_campaign_status()

        # Get analytics
        performance = await generator.analytics.get_current_performance()

        # Get predictive insights
        insights = await generator.analytics.generate_predictive_insights()

        return {
            'system_status': status,
            'performance_metrics': performance,
            'predictive_insights': insights.to_dict(),
            'timestamp': asyncio.get_event_loop().time()
        }

    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        return {
            'error': str(e),
            'status': 'error',
            'timestamp': asyncio.get_event_loop().time()
        }


def main():
    """Main entry point for command-line usage"""
    parser = argparse.ArgumentParser(
        description="Sales Lead Generator - Professional B2B Lead Generation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run single campaign
  python main.py --single-run

  # Run continuous campaign
  python main.py --continuous --max-cycles 5

  # Research prospects only
  python main.py --research-only --target-count 50

  # Test qualification only
  python main.py --qualification-only

  # Test email automation
  python main.py --email-test

  # Get system status
  python main.py --status

  # Run with custom config
  python main.py --config /path/to/config.json --single-run
        """
    )

    # Main operation modes
    parser.add_argument('--single-run', action='store_true',
                       help='Run a single campaign cycle')
    parser.add_argument('--continuous', action='store_true',
                       help='Run continuous campaign')
    parser.add_argument('--research-only', action='store_true',
                       help='Run prospect research only')
    parser.add_argument('--qualification-only', action='store_true',
                       help='Run lead qualification only')
    parser.add_argument('--email-test', action='store_true',
                       help='Test email automation')
    parser.add_argument('--status', action='store_true',
                       help='Get system status')

    # Configuration options
    parser.add_argument('--config', type=str,
                       help='Path to configuration file')
    parser.add_argument('--campaign-id', type=str,
                       help='Campaign identifier')
    parser.add_argument('--target-count', type=int, default=25,
                       help='Number of prospects to research (default: 25)')
    parser.add_argument('--max-cycles', type=int,
                       help='Maximum number of cycles for continuous mode')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level (default: INFO)')

    # Parse arguments
    args = parser.parse_args()

    # Validate arguments
    operation_modes = [
        args.single_run, args.continuous, args.research_only,
        args.qualification_only, args.email_test, args.status
    ]

    if sum(operation_modes) != 1:
        parser.error("Exactly one operation mode must be specified")

    # Set up logging
    log_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'lead_generator.log')
    setup_logging(args.log_level, log_file)

    logger = logging.getLogger(__name__)

    try:
        # Execute requested operation
        if args.single_run:
            logger.info("Running single campaign cycle")
            result = asyncio.run(run_single_campaign(
                args.config, args.campaign_id, args.log_level
            ))
            print("\n=== Campaign Results ===")
            print(f"Campaign ID: {result.get('campaign_id')}")
            print(f"Prospects Found: {result.get('prospects_found')}")
            print(f"Leads Qualified: {result.get('leads_qualified')}")
            print(f"Emails Sent: {result.get('emails_sent')}")
            print(f"Responses Received: {result.get('responses_received')}")
            print(".1%")

        elif args.continuous:
            logger.info("Running continuous campaign")
            asyncio.run(run_continuous_campaign(
                args.config, args.campaign_id, args.log_level, args.max_cycles
            ))

        elif args.research_only:
            logger.info(f"Running prospect research for {args.target_count} targets")
            result = asyncio.run(run_prospect_research_only(
                args.config, args.target_count, args.log_level
            ))
            print("\n=== Research Results ===")
            print(f"Prospects Found: {result.get('prospects_found')}")
            print(f"Target Industry: {result.get('target_industry')}")
            print(f"Company Size Range: {result.get('company_size_range')}")
            print(f"Geographic Focus: {', '.join(result.get('geographic_focus', []))}")

        elif args.qualification_only:
            logger.info("Running lead qualification")
            result = asyncio.run(run_qualification_only(
                args.config, None, args.log_level
            ))
            print("\n=== Qualification Results ===")
            print(f"Total Prospects: {result.get('total_prospects')}")
            print(f"Qualified Leads: {result.get('qualified_leads')}")
            print(".1%")

        elif args.email_test:
            logger.info("Running email automation test")
            result = asyncio.run(run_email_test(args.config, args.log_level))
            print("\n=== Email Test Results ===")
            print(f"Emails Sent: {result.get('results', {}).get('sent', 0)}")
            print(f"Available Templates: {', '.join(result.get('available_templates', []))}")
            print(f"Available Sequences: {', '.join(result.get('available_sequences', []))}")

        elif args.status:
            logger.info("Getting system status")
            result = asyncio.run(get_system_status(args.config, args.log_level))
            print("\n=== System Status ===")
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                status = result.get('system_status', {})
                print(f"Campaign Status: {status.get('status', 'unknown')}")
                if status.get('campaign_id'):
                    print(f"Campaign ID: {status.get('campaign_id')}")
                    print(".1%")
                    print(f"Daily Target Achievement: {status.get('target_achievement', 0):.1%}")

        logger.info("Operation completed successfully")

    except KeyboardInterrupt:
        logger.info("Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
