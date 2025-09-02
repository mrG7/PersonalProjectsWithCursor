"""
CRM Integrator - External CRM System Integration

This module handles integration with external CRM systems for lead synchronization,
activity tracking, and data enrichment.
"""

import asyncio
import logging
import json
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import aiohttp


@dataclass
class CRMConfig:
    """CRM system configuration"""
    system_type: str  # 'salesforce', 'hubspot', 'pipedrive', etc.
    api_endpoint: str
    api_key: str
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    custom_fields: Dict[str, str] = None

    def __post_init__(self):
        if self.custom_fields is None:
            self.custom_fields = {}


@dataclass
class CRMLead:
    """CRM lead/contact representation"""
    crm_id: Optional[str]
    first_name: str
    last_name: str
    email: str
    company: str
    title: str
    phone: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    lead_source: str = 'Lead Generation Agent'
    lead_status: str = 'New'
    lead_score: Optional[float] = None
    notes: Optional[str] = None
    custom_fields: Dict[str, Any] = None

    def __post_init__(self):
        if self.custom_fields is None:
            self.custom_fields = {}


class CRMIntegrator:
    """
    CRM Integration Manager for synchronizing leads and activities.

    Supports multiple CRM systems:
    - Salesforce
    - HubSpot
    - Pipedrive
    - Zoho CRM
    - Custom REST APIs
    """

    def __init__(self, config):
        """
        Initialize CRM Integrator

        Args:
            config: LeadGenerationConfig object
        """
        self.config = config
        self.logger = logging.getLogger('CRMIntegrator')

        # CRM configurations (in production, load from secure config)
        self.crm_configs = {
            'salesforce': CRMConfig(
                system_type='salesforce',
                api_endpoint='https://yourinstance.salesforce.com/services/data/v55.0',
                api_key='mock_salesforce_key',
                custom_fields={
                    'lead_score': 'Lead_Score__c',
                    'qualification_level': 'Qualification_Level__c'
                }
            ),
            'hubspot': CRMConfig(
                system_type='hubspot',
                api_endpoint='https://api.hubapi.com',
                api_key='mock_hubspot_key',
                custom_fields={
                    'lead_score': 'lead_score',
                    'qualification_level': 'qualification_level'
                }
            ),
            'pipedrive': CRMConfig(
                system_type='pipedrive',
                api_endpoint='https://api.pipedrive.com/v1',
                api_key='mock_pipedrive_key'
            )
        }

        # Current CRM system
        self.current_crm = None
        self.auth_token = None

    async def connect_crm(self, crm_type: str = 'salesforce') -> bool:
        """
        Connect to CRM system

        Args:
            crm_type: Type of CRM system

        Returns:
            True if connection successful
        """
        if crm_type not in self.crm_configs:
            self.logger.error(f"Unsupported CRM type: {crm_type}")
            return False

        self.current_crm = crm_type
        config = self.crm_configs[crm_type]

        try:
            # Simulate authentication
            await asyncio.sleep(0.5)  # Simulate network delay

            # In real implementation, this would perform OAuth or API key auth
            self.auth_token = f"mock_token_{crm_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            self.logger.info(f"Successfully connected to {crm_type} CRM")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to {crm_type} CRM: {e}")
            return False

    async def sync_leads(self, qualified_leads: List[Any]) -> Dict[str, Any]:
        """
        Sync qualified leads to CRM system

        Args:
            qualified_leads: List of qualified leads to sync

        Returns:
            Sync operation results
        """
        if not self.current_crm or not self.auth_token:
            raise RuntimeError("CRM not connected")

        self.logger.info(f"Syncing {len(qualified_leads)} leads to {self.current_crm}")

        results = {
            'total_leads': len(qualified_leads),
            'successful_syncs': 0,
            'failed_syncs': 0,
            'duplicates_found': 0,
            'leads_created': 0,
            'leads_updated': 0,
            'errors': []
        }

        for lead in qualified_leads:
            try:
                crm_lead = self._convert_to_crm_lead(lead)
                sync_result = await self._sync_single_lead(crm_lead)

                if sync_result['success']:
                    results['successful_syncs'] += 1
                    if sync_result['action'] == 'created':
                        results['leads_created'] += 1
                    elif sync_result['action'] == 'updated':
                        results['leads_updated'] += 1
                    elif sync_result['action'] == 'duplicate':
                        results['duplicates_found'] += 1
                else:
                    results['failed_syncs'] += 1
                    results['errors'].append(sync_result.get('error', 'Unknown error'))

            except Exception as e:
                self.logger.error(f"Error syncing lead: {e}")
                results['failed_syncs'] += 1
                results['errors'].append(str(e))

        self.logger.info(f"Lead sync completed: {results}")
        return results

    def _convert_to_crm_lead(self, lead) -> CRMLead:
        """Convert qualified lead to CRM lead format"""
        # Extract lead data
        prospect_data = lead.prospect_data if hasattr(lead, 'prospect_data') else lead
        lead_score = lead.lead_score if hasattr(lead, 'lead_score') else None

        # Find primary contact
        primary_contact = None
        contacts = prospect_data.get('key_contacts', [])
        if contacts:
            primary_contact = contacts[0]  # Use first contact

        # Extract contact information
        first_name = "Unknown"
        last_name = "Contact"
        email = f"contact@{prospect_data.get('website', 'example.com').replace('https://', '').replace('http://', '')}"

        if primary_contact:
            full_name = primary_contact.get('name', 'Unknown Contact').split()
            first_name = full_name[0] if full_name else "Unknown"
            last_name = ' '.join(full_name[1:]) if len(full_name) > 1 else "Contact"
            email = primary_contact.get('email', email)

        # Create CRM lead
        crm_lead = CRMLead(
            crm_id=None,  # Will be set by CRM
            first_name=first_name,
            last_name=last_name,
            email=email,
            company=prospect_data.get('company_name', 'Unknown Company'),
            title=primary_contact.get('title', 'Unknown Title') if primary_contact else 'Unknown Title',
            phone=None,  # Not available in mock data
            website=prospect_data.get('website'),
            industry=prospect_data.get('industry'),
            lead_score=lead_score.overall_score if lead_score else None,
            notes=self._generate_lead_notes(prospect_data, lead_score)
        )

        # Add custom fields based on CRM type
        if self.current_crm in self.crm_configs:
            custom_fields = self.crm_configs[self.current_crm].custom_fields
            if custom_fields:
                if lead_score:
                    crm_lead.custom_fields[custom_fields.get('lead_score', 'lead_score')] = lead_score.overall_score
                    crm_lead.custom_fields[custom_fields.get('qualification_level', 'qualification_level')] = lead_score.qualification_level.value

        return crm_lead

    def _generate_lead_notes(self, prospect_data: Dict[str, Any], lead_score) -> str:
        """Generate comprehensive lead notes for CRM"""
        notes = []

        # Company information
        notes.append(f"Company: {prospect_data.get('company_name', 'Unknown')}")
        notes.append(f"Industry: {prospect_data.get('industry', 'Unknown')}")
        notes.append(f"Size: {prospect_data.get('company_size', 'Unknown')} employees")
        notes.append(f"Location: {prospect_data.get('location', 'Unknown')}")

        # Lead score information
        if lead_score:
            notes.append(f"Lead Score: {lead_score.overall_score:.2f}")
            notes.append(f"Qualification Level: {lead_score.qualification_level.value.title()}")

            # Add top recommendations
            if lead_score.recommendations:
                notes.append("Key Recommendations:")
                for rec in lead_score.recommendations[:2]:  # Top 2
                    notes.append(f"- {rec}")

        # Technologies
        technologies = prospect_data.get('technologies', [])
        if technologies:
            notes.append(f"Technologies: {', '.join(technologies[:3])}")

        # Recent news
        recent_news = prospect_data.get('recent_news', [])
        if recent_news:
            notes.append("Recent News:")
            for news in recent_news[:2]:  # Top 2
                notes.append(f"- {news}")

        return '\n'.join(notes)

    async def _sync_single_lead(self, crm_lead: CRMLead) -> Dict[str, Any]:
        """Sync a single lead to CRM system"""
        try:
            # Simulate API call
            await asyncio.sleep(0.2)  # Simulate network delay

            # Check for existing lead (simulate duplicate detection)
            if random.random() < 0.3:  # 30% chance of duplicate
                return {
                    'success': True,
                    'action': 'duplicate',
                    'crm_id': f"existing_{random.randint(10000, 99999)}",
                    'message': 'Lead already exists in CRM'
                }

            # Simulate successful creation/update
            crm_id = f"crm_{self.current_crm}_{random.randint(10000, 99999)}"
            crm_lead.crm_id = crm_id

            action = 'created' if random.random() > 0.5 else 'updated'

            return {
                'success': True,
                'action': action,
                'crm_id': crm_id,
                'message': f'Lead {action} successfully'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to sync lead'
            }

    async def get_lead_status(self, crm_id: str) -> Optional[Dict[str, Any]]:
        """
        Get lead status from CRM

        Args:
            crm_id: CRM lead identifier

        Returns:
            Lead status information
        """
        if not self.current_crm or not self.auth_token:
            return None

        try:
            # Simulate API call to get lead status
            await asyncio.sleep(0.1)

            # Mock lead status data
            return {
                'crm_id': crm_id,
                'status': random.choice(['New', 'Contacted', 'Qualified', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost']),
                'last_activity': datetime.now().isoformat(),
                'owner': f'Sales Rep {random.randint(1, 10)}',
                'last_modified': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error getting lead status: {e}")
            return None

    async def update_lead_activities(self, lead_activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update lead activities in CRM (emails sent, calls made, etc.)

        Args:
            lead_activities: List of lead activities to log

        Returns:
            Update operation results
        """
        if not self.current_crm or not self.auth_token:
            raise RuntimeError("CRM not connected")

        results = {
            'total_activities': len(lead_activities),
            'successful_updates': 0,
            'failed_updates': 0,
            'errors': []
        }

        for activity in lead_activities:
            try:
                # Simulate activity logging
                await asyncio.sleep(0.05)

                # Mock successful update
                results['successful_updates'] += 1

            except Exception as e:
                results['failed_updates'] += 1
                results['errors'].append(str(e))

        return results

    async def get_crm_reports(self, report_type: str = 'leads',
                             date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """
        Get CRM reports and analytics

        Args:
            report_type: Type of report ('leads', 'activities', 'pipeline')
            date_range: Date range for report

        Returns:
            Report data
        """
        if not self.current_crm or not self.auth_token:
            raise RuntimeError("CRM not connected")

        # Simulate report generation
        await asyncio.sleep(0.3)

        if report_type == 'leads':
            return {
                'total_leads': random.randint(1000, 5000),
                'new_leads_this_month': random.randint(100, 300),
                'qualified_leads': random.randint(50, 150),
                'conversion_rate': random.uniform(0.05, 0.15),
                'top_sources': ['Lead Generation Agent', 'Website', 'Referrals', 'Tradeshows']
            }
        elif report_type == 'activities':
            return {
                'total_activities': random.randint(5000, 15000),
                'emails_sent': random.randint(2000, 5000),
                'calls_made': random.randint(1000, 3000),
                'meetings_booked': random.randint(100, 300),
                'proposals_sent': random.randint(50, 150)
            }
        elif report_type == 'pipeline':
            return {
                'total_value': random.randint(1000000, 5000000),
                'average_deal_size': random.randint(25000, 75000),
                'pipeline_velocity': random.uniform(30, 90),  # days
                'win_rate': random.uniform(0.15, 0.35)
            }

        return {}

    # CRM-Specific Implementations

    async def _salesforce_create_lead(self, crm_lead: CRMLead) -> Dict[str, Any]:
        """Salesforce-specific lead creation"""
        # In real implementation, this would use Salesforce REST API
        endpoint = f"{self.crm_configs['salesforce'].api_endpoint}/sobjects/Lead"

        # Mock Salesforce API call
        await asyncio.sleep(0.2)

        return {
            'success': True,
            'crm_id': f"00Q{random.randint(100000000000000, 999999999999999)}",
            'action': 'created'
        }

    async def _hubspot_create_contact(self, crm_lead: CRMLead) -> Dict[str, Any]:
        """HubSpot-specific contact creation"""
        # In real implementation, this would use HubSpot API
        endpoint = f"{self.crm_configs['hubspot'].api_endpoint}/crm/v3/objects/contacts"

        # Mock HubSpot API call
        await asyncio.sleep(0.2)

        return {
            'success': True,
            'crm_id': str(random.randint(1000000000, 9999999999)),
            'action': 'created'
        }

    async def _pipedrive_create_person(self, crm_lead: CRMLead) -> Dict[str, Any]:
        """Pipedrive-specific person creation"""
        # In real implementation, this would use Pipedrive API
        endpoint = f"{self.crm_configs['pipedrive'].api_endpoint}/persons"

        # Mock Pipedrive API call
        await asyncio.sleep(0.2)

        return {
            'success': True,
            'crm_id': str(random.randint(1000, 9999)),
            'action': 'created'
        }

    # Utility Methods

    def list_supported_crms(self) -> List[str]:
        """List supported CRM systems"""
        return list(self.crm_configs.keys())

    def get_crm_config(self, crm_type: str) -> Optional[CRMConfig]:
        """Get CRM configuration"""
        return self.crm_configs.get(crm_type)

    async def test_connection(self) -> bool:
        """Test CRM connection"""
        if not self.current_crm or not self.auth_token:
            return False

        try:
            # Simulate connection test
            await asyncio.sleep(0.1)
            return random.random() > 0.1  # 90% success rate
        except Exception:
            return False

    async def disconnect(self):
        """Disconnect from CRM system"""
        if self.current_crm:
            self.logger.info(f"Disconnected from {self.current_crm} CRM")
            self.current_crm = None
            self.auth_token = None


# Import required modules for random functionality
import random
