"""
Unit tests for the Sales Lead Generator

This module contains comprehensive tests for all components of the
Sales Lead Generator system.
"""

import pytest
import asyncio
import json
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Import the modules to test
from src.lead_generator import SalesLeadGenerator, create_campaign_config
from src.prospect_researcher import ProspectResearcher, Prospect
from src.lead_qualifier import LeadQualifier, LeadScore
from src.email_automation import EmailAutomationAgent
from src.crm_integrator import CRMIntegrator
from src.analytics_tracker import AnalyticsTracker


class TestSalesLeadGenerator:
    """Test the main SalesLeadGenerator class"""

    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return create_campaign_config(
            target_industry="technology",
            company_size_range=(50, 500),
            daily_lead_target=10
        )

    @pytest.fixture
    def generator(self, config):
        """Create test generator instance"""
        return SalesLeadGenerator()

    @pytest.mark.asyncio
    async def test_campaign_lifecycle(self, generator):
        """Test complete campaign lifecycle"""
        # Start campaign
        campaign_id = await generator.start_campaign("test_campaign")
        assert campaign_id == "test_campaign"
        assert generator.is_running is True

        # Run cycle
        results = await generator.run_daily_cycle()
        assert isinstance(results, dict)
        assert "campaign_id" in results
        assert "prospects_found" in results

        # Stop campaign
        await generator.stop_campaign()
        assert generator.is_running is False

    @pytest.mark.asyncio
    async def test_campaign_status(self, generator):
        """Test campaign status retrieval"""
        # Start campaign
        await generator.start_campaign("status_test")

        # Get status
        status = await generator.get_campaign_status()
        assert status["status"] == "running"
        assert status["campaign_id"] == "status_test"

        # Stop and check status
        await generator.stop_campaign()
        status = await generator.get_campaign_status()
        assert status["status"] == "paused"


class TestProspectResearcher:
    """Test the ProspectResearcher class"""

    @pytest.fixture
    def config(self):
        return create_campaign_config()

    @pytest.fixture
    def researcher(self, config):
        return ProspectResearcher(config)

    @pytest.mark.asyncio
    async def test_research_prospects(self, researcher):
        """Test prospect research functionality"""
        prospects = await researcher.research_prospects(target_count=5)

        assert isinstance(prospects, list)
        assert len(prospects) <= 5

        if prospects:
            prospect = prospects[0]
            assert isinstance(prospect, Prospect)
            assert hasattr(prospect, 'company_name')
            assert hasattr(prospect, 'industry')
            assert hasattr(prospect, 'company_size')

    @pytest.mark.asyncio
    async def test_search_by_criteria(self, researcher):
        """Test criteria-based search"""
        prospects = await researcher.search_by_criteria(
            industry="technology",
            company_size_min=100,
            company_size_max=300
        )

        assert isinstance(prospects, list)
        for prospect in prospects:
            assert prospect.industry == "technology"
            assert 100 <= prospect.company_size <= 300


class TestLeadQualifier:
    """Test the LeadQualifier class"""

    @pytest.fixture
    def config(self):
        return create_campaign_config()

    @pytest.fixture
    def qualifier(self, config):
        return LeadQualifier(config)

    @pytest.mark.asyncio
    async def test_qualify_leads(self, qualifier):
        """Test lead qualification process"""
        # Create mock prospects
        prospects = [
            Mock(
                company_name="Test Company",
                industry="technology",
                company_size=150,
                to_dict=lambda: {
                    'company_name': 'Test Company',
                    'industry': 'technology',
                    'company_size': 150,
                    'revenue_range': '$10M-$25M',
                    'key_contacts': [{'title': 'CEO'}]
                }
            )
        ]

        qualified_leads = await qualifier.qualify_leads(prospects)

        assert isinstance(qualified_leads, list)
        if qualified_leads:
            lead = qualified_leads[0]
            assert hasattr(lead, 'lead_score')
            assert hasattr(lead, 'priority_rank')
            assert isinstance(lead.lead_score, LeadScore)

    def test_scoring_components(self, qualifier):
        """Test individual scoring components"""
        prospect_data = {
            'industry': 'technology',
            'company_size': 200,
            'revenue_range': '$25M-$50M',
            'key_contacts': [{'title': 'VP of Engineering'}]
        }

        # Test company fit scoring
        fit_score = qualifier._score_company_fit(prospect_data)
        assert 0 <= fit_score <= 1

        # Test budget alignment
        budget_score = qualifier._score_budget_alignment(prospect_data)
        assert 0 <= budget_score <= 1

        # Test authority level
        authority_score = qualifier._score_authority_level(prospect_data)
        assert 0 <= authority_score <= 1


class TestEmailAutomation:
    """Test the EmailAutomationAgent class"""

    @pytest.fixture
    def config(self):
        return create_campaign_config()

    @pytest.fixture
    def email_agent(self, config):
        return EmailAutomationAgent(config)

    @pytest.mark.asyncio
    async def test_send_sequences(self, email_agent):
        """Test email sequence sending"""
        # Create mock qualified lead
        mock_lead = Mock()
        mock_lead.prospect_data = {
            'company_name': 'Test Company',
            'email': 'contact@test.com'
        }

        results = await email_agent.send_sequences([mock_lead])

        assert isinstance(results, dict)
        assert 'sent' in results
        assert 'failed' in results

    def test_template_rendering(self, email_agent):
        """Test email template rendering"""
        template = email_agent.templates.get('introduction')
        assert template is not None

        context = {
            'contact_name': 'John Doe',
            'company_name': 'Test Company',
            'sender_name': 'Sales Rep'
        }

        subject = template.render_subject(context)
        body = template.render_body(context)

        assert 'John Doe' in body
        assert 'Test Company' in body
        assert 'Sales Rep' in body

    def test_sequence_management(self, email_agent):
        """Test email sequence management"""
        sequences = email_agent.list_sequences()
        assert isinstance(sequences, list)
        assert len(sequences) > 0

        templates = email_agent.list_templates()
        assert isinstance(templates, list)
        assert len(templates) > 0


class TestCRMIntegrator:
    """Test the CRMIntegrator class"""

    @pytest.fixture
    def config(self):
        return create_campaign_config()

    @pytest.fixture
    def crm(self, config):
        return CRMIntegrator(config)

    @pytest.mark.asyncio
    async def test_crm_connection(self, crm):
        """Test CRM connection"""
        connected = await crm.connect_crm('salesforce')
        assert isinstance(connected, bool)

    @pytest.mark.asyncio
    async def test_lead_sync(self, crm):
        """Test lead synchronization"""
        # Mock qualified lead
        mock_lead = Mock()
        mock_lead.prospect_data = {
            'company_name': 'Test Company',
            'website': 'https://test.com',
            'industry': 'technology',
            'company_size': 150,
            'location': 'San Francisco, CA',
            'key_contacts': [{'name': 'John Doe', 'title': 'CEO'}]
        }

        # Connect first
        await crm.connect_crm('salesforce')

        # Sync leads
        results = await crm.sync_leads([mock_lead])

        assert isinstance(results, dict)
        assert 'total_leads' in results
        assert 'successful_syncs' in results


class TestAnalyticsTracker:
    """Test the AnalyticsTracker class"""

    @pytest.fixture
    def config(self):
        return create_campaign_config()

    @pytest.fixture
    def analytics(self, config):
        return AnalyticsTracker(config)

    @pytest.mark.asyncio
    async def test_performance_tracking(self, analytics):
        """Test performance metrics tracking"""
        # Mock campaign metrics
        mock_metrics = Mock()
        mock_metrics.prospects_researched = 25
        mock_metrics.leads_qualified = 8
        mock_metrics.emails_sent = 8
        mock_metrics.responses_received = 2
        mock_metrics.meetings_booked = 1

        await analytics.update_metrics(mock_metrics)

        # Check that metrics were updated
        performance = await analytics.get_current_performance()
        assert 'overall_metrics' in performance

    @pytest.mark.asyncio
    async def test_predictive_insights(self, analytics):
        """Test predictive insights generation"""
        insights = await analytics.generate_predictive_insights()

        assert hasattr(insights, 'next_day_prospects')
        assert hasattr(insights, 'confidence_level')
        assert hasattr(insights, 'trend_direction')
        assert hasattr(insights, 'recommended_actions')

    @pytest.mark.asyncio
    async def test_performance_reports(self, analytics):
        """Test performance report generation"""
        report = await analytics.generate_performance_report('daily')

        assert 'report_type' in report
        assert report['report_type'] == 'daily'


# Integration Tests
class TestIntegration:
    """Integration tests for the complete system"""

    @pytest.fixture
    def config(self):
        return create_campaign_config(daily_lead_target=3)

    @pytest.mark.asyncio
    async def test_full_campaign_workflow(self, config):
        """Test complete campaign workflow integration"""
        generator = SalesLeadGenerator()

        try:
            # Start campaign
            campaign_id = await generator.start_campaign("integration_test")

            # Run campaign cycle
            results = await generator.run_daily_cycle()

            # Verify results structure
            assert 'campaign_id' in results
            assert 'prospects_found' in results
            assert 'leads_qualified' in results

            # Check that analytics were updated
            performance = await generator.analytics.get_current_performance()
            assert performance is not None

        finally:
            await generator.stop_campaign()
            await generator.cleanup()

    @pytest.mark.asyncio
    async def test_component_interaction(self, config):
        """Test interaction between components"""
        # Test prospect research -> qualification flow
        researcher = ProspectResearcher(config)
        qualifier = LeadQualifier(config)

        # Research prospects
        prospects = await researcher.research_prospects(3)
        assert len(prospects) <= 3

        # Qualify prospects
        qualified_leads = await qualifier.qualify_leads(prospects)
        assert isinstance(qualified_leads, list)

        # Verify qualified leads have proper structure
        for lead in qualified_leads:
            assert hasattr(lead, 'lead_score')
            assert hasattr(lead, 'prospect_data')
            assert hasattr(lead, 'priority_rank')


# Performance Tests
class TestPerformance:
    """Performance tests for system components"""

    @pytest.fixture
    def config(self):
        return create_campaign_config()

    @pytest.mark.asyncio
    async def test_research_performance(self, config):
        """Test prospect research performance"""
        researcher = ProspectResearcher(config)

        import time
        start_time = time.time()

        prospects = await researcher.research_prospects(10)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within reasonable time
        assert duration < 5.0  # Less than 5 seconds
        assert len(prospects) <= 10

    @pytest.mark.asyncio
    async def test_qualification_performance(self, config):
        """Test lead qualification performance"""
        qualifier = LeadQualifier(config)

        # Create test prospects
        prospects = []
        for i in range(5):
            prospect = Mock()
            prospect.to_dict = lambda: {
                'company_name': f'Test Company {i}',
                'industry': 'technology',
                'company_size': 150 + i * 20,
                'revenue_range': '$10M-$25M',
                'key_contacts': [{'title': 'CEO'}]
            }
            prospects.append(prospect)

        import time
        start_time = time.time()

        qualified_leads = await qualifier.qualify_leads(prospects)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete quickly
        assert duration < 2.0  # Less than 2 seconds
        assert len(qualified_leads) <= len(prospects)


# Configuration Tests
def test_config_creation():
    """Test configuration creation"""
    config = create_campaign_config(
        target_industry="healthcare",
        company_size_range=(100, 1000),
        geographic_focus=["California", "New York"]
    )

    assert config.target_industry == "healthcare"
    assert config.company_size_range == (100, 1000)
    assert "California" in config.geographic_focus
    assert "New York" in config.geographic_focus


def test_config_validation():
    """Test configuration validation"""
    config = create_campaign_config()

    # Check required attributes
    assert hasattr(config, 'target_industry')
    assert hasattr(config, 'company_size_range')
    assert hasattr(config, 'geographic_focus')
    assert hasattr(config, 'budget_minimum')
    assert hasattr(config, 'daily_lead_target')

    # Check default values
    assert config.target_industry == "technology"
    assert config.daily_lead_target == 25


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"])
