# Sales Lead Generator Agent - Professional Prospect Discovery System
"""
Complete runnable implementation of the Sales Lead Generator agent.

This agent provides comprehensive B2B lead generation capabilities including:
- Prospect discovery and research
- Lead qualification and scoring
- Email sequence automation
- Performance tracking and analytics
- CRM integration support

Author: Cursor AI Agent Ecosystem
Version: 2.0.0
License: MIT
"""

__version__ = "2.0.0"
__author__ = "Cursor AI Agent Ecosystem"
__description__ = "Professional B2B lead generation and qualification system"

from lead_generator import SalesLeadGenerator
from prospect_researcher import ProspectResearcher
from lead_qualifier import LeadQualifier
from email_automation import EmailAutomationAgent
from crm_integrator import CRMIntegrator
from analytics_tracker import AnalyticsTracker

__all__ = [
    'SalesLeadGenerator',
    'ProspectResearcher',
    'LeadQualifier',
    'EmailAutomationAgent',
    'CRMIntegrator',
    'AnalyticsTracker'
]
