"""
Email Automation - Automated Email Sequence Management

This module handles automated email sequences for lead nurturing and follow-up.
It manages templates, personalization, scheduling, and performance tracking.
"""

import asyncio
import logging
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from string import Template
import random
import os


@dataclass
class EmailTemplate:
    """Email template with subject and body"""
    name: str
    subject_template: str
    body_template: str
    category: str
    variables: List[str]

    def render_subject(self, context: Dict[str, Any]) -> str:
        """Render subject template with context variables"""
        try:
            template = Template(self.subject_template)
            return template.safe_substitute(context)
        except Exception:
            return self.subject_template

    def render_body(self, context: Dict[str, Any]) -> str:
        """Render body template with context variables"""
        try:
            template = Template(self.body_template)
            return template.safe_substitute(context)
        except Exception:
            return self.body_template


@dataclass
class EmailSequence:
    """Email sequence configuration"""
    name: str
    description: str
    steps: List[Dict[str, Any]]
    target_audience: str
    success_criteria: Dict[str, Any]

    def get_step_by_number(self, step_number: int) -> Optional[Dict[str, Any]]:
        """Get sequence step by number"""
        for step in self.steps:
            if step.get('step_number') == step_number:
                return step
        return None


@dataclass
class EmailResult:
    """Result of sending an email"""
    email_id: str
    recipient: str
    subject: str
    sent_at: datetime
    status: str  # 'sent', 'failed', 'bounced'
    sequence_step: int
    lead_id: str
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.sent_at is None:
            self.sent_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['sent_at'] = self.sent_at.isoformat()
        return data


@dataclass
class SequencePerformance:
    """Performance metrics for email sequences"""
    sequence_name: str
    total_emails_sent: int
    open_rate: float
    click_rate: float
    response_rate: float
    conversion_rate: float
    average_response_time: Optional[timedelta]
    best_performing_step: int
    generated_opportunities: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        if self.average_response_time:
            data['average_response_time'] = str(self.average_response_time)
        return data


class EmailAutomationAgent:
    """
    Email Automation Agent for managing lead nurturing sequences.

    Features:
    - Template-based email creation
    - Personalized content generation
    - Automated sequence scheduling
    - Performance tracking and analytics
    - A/B testing capabilities
    """

    def __init__(self, config):
        """
        Initialize the Email Automation Agent

        Args:
            config: LeadGenerationConfig object
        """
        self.config = config
        self.logger = logging.getLogger('EmailAutomationAgent')

        # Email configuration (replace with real SMTP settings)
        self.smtp_config = {
            'server': 'smtp.gmail.com',
            'port': 587,
            'username': 'your-email@gmail.com',
            'password': 'your-app-password',
            'use_tls': True
        }

        # Initialize templates and sequences
        self.templates = self._load_email_templates()
        self.sequences = self._load_email_sequences()

        # Performance tracking
        self.email_history = []
        self.sequence_performance = {}

        # Sequence delays (in hours)
        self.sequence_delays = {
            1: 0,      # Immediate
            2: 24,     # 1 day
            3: 72,     # 3 days
            4: 168,    # 1 week
            5: 336     # 2 weeks
        }

    def _load_email_templates(self) -> Dict[str, EmailTemplate]:
        """Load email templates"""
        templates = {}

        # Introduction Email Template
        templates['introduction'] = EmailTemplate(
            name='introduction',
            subject_template='Exploring Solutions for ${company_name}',
            body_template="""
Dear ${contact_name},

I hope this email finds you well. My name is ${sender_name} and I'm with ${sender_company}, where we help companies like ${company_name} optimize their ${industry} operations through innovative technology solutions.

I came across ${company_name} and was impressed by your work in ${industry_specific_detail}. Many organizations in your space are facing similar challenges around ${pain_point}, and we've helped companies achieve ${benefit} through our ${solution_type} solutions.

I'd love to learn more about your current priorities and explore whether there's an opportunity for us to collaborate. Are you available for a brief 15-minute call next week to discuss?

Best regards,
${sender_name}
${sender_title}
${sender_company}
${sender_phone}
${sender_email}
""",
            category='introduction',
            variables=['contact_name', 'company_name', 'sender_name', 'sender_company',
                      'industry', 'industry_specific_detail', 'pain_point', 'benefit',
                      'solution_type', 'sender_title', 'sender_phone', 'sender_email']
        )

        # Value Proposition Email Template
        templates['value_proposition'] = EmailTemplate(
            name='value_proposition',
            subject_template='How ${company_name} Can Achieve ${benefit} with Our Solution',
            body_template="""
Hi ${contact_name},

Following up on my previous message about ${company_name}'s impressive work in ${industry}.

We've helped ${case_study_count} companies in ${industry} achieve:
• ${benefit_1}
• ${benefit_2}
• ${benefit_3}

Our ${solution_name} solution is specifically designed to address ${pain_point} that many ${industry} companies face. Unlike traditional approaches, our solution delivers ${unique_value_proposition}.

Would you be interested in seeing a quick demo of how this could work for ${company_name}?

Looking forward to your thoughts.

Best,
${sender_name}
""",
            category='follow_up',
            variables=['contact_name', 'company_name', 'industry', 'case_study_count',
                      'benefit_1', 'benefit_2', 'benefit_3', 'solution_name',
                      'pain_point', 'unique_value_proposition', 'sender_name']
        )

        # Case Study Email Template
        templates['case_study'] = EmailTemplate(
            name='case_study',
            subject_template='Case Study: ${similar_company} Achieved ${benefit} Using Our Solution',
            body_template="""
Hello ${contact_name},

I wanted to share a relevant case study that might interest you at ${company_name}.

${similar_company}, a ${company_size} ${industry} company similar to ${company_name}, was facing ${challenge}. They implemented our ${solution_name} and achieved:
• ${result_1}
• ${result_2}
• ${result_3}

The implementation took ${timeline} and delivered ${roi} return on investment.

Would this type of result be valuable for ${company_name}? I'd be happy to discuss how we could achieve similar outcomes.

Best regards,
${sender_name}
""",
            category='nurture',
            variables=['contact_name', 'company_name', 'similar_company', 'company_size',
                      'industry', 'challenge', 'solution_name', 'result_1', 'result_2',
                      'result_3', 'timeline', 'roi', 'sender_name']
        )

        return templates

    def _load_email_sequences(self) -> Dict[str, EmailSequence]:
        """Load email sequences"""
        sequences = {}

        # Standard Sales Sequence
        sequences['standard_sales'] = EmailSequence(
            name='standard_sales',
            description='Standard 5-step sales email sequence',
            steps=[
                {
                    'step_number': 1,
                    'template': 'introduction',
                    'delay_hours': 0,
                    'purpose': 'Initial introduction and value proposition'
                },
                {
                    'step_number': 2,
                    'template': 'value_proposition',
                    'delay_hours': 24,
                    'purpose': 'Detailed value proposition and benefits'
                },
                {
                    'step_number': 3,
                    'template': 'case_study',
                    'delay_hours': 72,
                    'purpose': 'Social proof through case study'
                },
                {
                    'step_number': 4,
                    'template': 'introduction',  # Could be different template
                    'delay_hours': 168,
                    'purpose': 'Final follow-up with specific ask'
                },
                {
                    'step_number': 5,
                    'template': 'value_proposition',  # Could be different template
                    'delay_hours': 336,
                    'purpose': 'Last attempt with urgency'
                }
            ],
            target_audience='qualified_leads',
            success_criteria={
                'response_rate_target': 0.05,
                'meeting_booked_target': 0.02,
                'max_sequence_length': 5
            }
        )

        # Nurture Sequence for Warm Leads
        sequences['nurture_sequence'] = EmailSequence(
            name='nurture_sequence',
            description='Long-term nurture sequence for warm leads',
            steps=[
                {
                    'step_number': 1,
                    'template': 'introduction',
                    'delay_hours': 0,
                    'purpose': 'Gentle introduction'
                },
                {
                    'step_number': 2,
                    'template': 'value_proposition',
                    'delay_hours': 168,  # 1 week
                    'purpose': 'Share educational content'
                },
                {
                    'step_number': 3,
                    'template': 'case_study',
                    'delay_hours': 336,  # 2 weeks
                    'purpose': 'Industry insights'
                }
            ],
            target_audience='warm_leads',
            success_criteria={
                'engagement_rate_target': 0.10,
                'max_sequence_length': 3
            }
        )

        return sequences

    async def send_sequences(self, qualified_leads: List[Any]) -> Dict[str, Any]:
        """
        Send email sequences to qualified leads

        Args:
            qualified_leads: List of qualified leads to contact

        Returns:
            Summary of email sending results
        """
        self.logger.info(f"Sending email sequences to {len(qualified_leads)} qualified leads")

        results = {
            'sent': 0,
            'failed': 0,
            'responses': 0,
            'sequence_type': 'standard_sales',
            'details': []
        }

        for lead in qualified_leads:
            try:
                # Determine appropriate sequence based on lead score
                sequence_name = self._select_sequence_for_lead(lead)

                # Send first email in sequence
                email_result = await self._send_sequence_email(lead, sequence_name, step_number=1)

                if email_result and email_result.status == 'sent':
                    results['sent'] += 1
                    results['details'].append(email_result.to_dict())

                    # Schedule remaining sequence emails
                    await self._schedule_sequence_follow_ups(lead, sequence_name)
                else:
                    results['failed'] += 1

            except Exception as e:
                self.logger.error(f"Error sending sequence to lead: {e}")
                results['failed'] += 1
                continue

        # Update performance metrics
        await self._update_sequence_performance(results)

        self.logger.info(f"Email sequence sending completed: {results}")
        return results

    def _select_sequence_for_lead(self, lead) -> str:
        """Select appropriate email sequence based on lead characteristics"""
        lead_score = lead.lead_score.overall_score if hasattr(lead, 'lead_score') else 0.7

        if lead_score >= 0.85:
            return 'standard_sales'  # Aggressive for hot leads
        elif lead_score >= 0.7:
            return 'standard_sales'  # Standard for warm leads
        else:
            return 'nurture_sequence'  # Gentle for cooler leads

    async def _send_sequence_email(self, lead, sequence_name: str, step_number: int) -> Optional[EmailResult]:
        """Send a single email in a sequence"""
        try:
            sequence = self.sequences.get(sequence_name)
            if not sequence:
                raise ValueError(f"Unknown sequence: {sequence_name}")

            step = sequence.get_step_by_number(step_number)
            if not step:
                return None

            template = self.templates.get(step['template'])
            if not template:
                raise ValueError(f"Unknown template: {step['template']}")

            # Generate email content
            context = self._generate_email_context(lead, step_number)
            subject = template.render_subject(context)
            body = template.render_body(context)

            # Send email (mock implementation)
            email_result = await self._send_email_mock(
                recipient=lead.prospect_data.get('email', 'contact@example.com'),
                subject=subject,
                body=body,
                lead_id=str(id(lead)),
                sequence_step=step_number
            )

            # Track email in history
            self.email_history.append(email_result)

            return email_result

        except Exception as e:
            self.logger.error(f"Error sending sequence email: {e}")
            return EmailResult(
                email_id=f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                recipient=lead.prospect_data.get('email', 'unknown@example.com'),
                subject="Error in email generation",
                status='failed',
                sequence_step=step_number,
                lead_id=str(id(lead)),
                error_message=str(e)
            )

    def _generate_email_context(self, lead, step_number: int) -> Dict[str, Any]:
        """Generate context variables for email templates"""
        prospect_data = lead.prospect_data if hasattr(lead, 'prospect_data') else lead

        context = {
            'contact_name': prospect_data.get('contact_name', 'there'),
            'company_name': prospect_data.get('company_name', 'your company'),
            'sender_name': 'Alex Johnson',
            'sender_company': 'TechSolutions Pro',
            'sender_title': 'Senior Solutions Consultant',
            'sender_email': 'alex.johnson@techsolutions.com',
            'sender_phone': '(555) 123-4567',
            'industry': prospect_data.get('industry', 'technology'),
            'industry_specific_detail': 'innovative approach to technology solutions',
            'pain_point': 'scaling operations efficiently',
            'benefit': '30% improvement in operational efficiency',
            'solution_type': 'cloud-based',
            'case_study_count': '50+',
            'benefit_1': 'Reduced operational costs by 25%',
            'benefit_2': 'Improved team productivity by 40%',
            'benefit_3': 'Enhanced customer satisfaction scores',
            'solution_name': 'TechSolutions Platform',
            'unique_value_proposition': 'AI-powered automation that adapts to your needs',
            'similar_company': 'TechCorp Solutions',
            'company_size': 'similar-sized',
            'challenge': 'similar operational challenges',
            'result_1': '25% cost reduction',
            'result_2': '40% productivity increase',
            'result_3': '95% customer satisfaction',
            'timeline': '8 weeks',
            'roi': '300%'
        }

        return context

    async def _send_email_mock(self, recipient: str, subject: str, body: str,
                              lead_id: str, sequence_step: int) -> EmailResult:
        """Mock email sending (replace with real SMTP implementation)"""
        # Simulate network delay
        await asyncio.sleep(0.1)

        # Simulate occasional failures
        if random.random() < 0.05:  # 5% failure rate
            raise Exception("Simulated email sending failure")

        # In real implementation, this would use smtplib or an email service
        email_id = f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"

        return EmailResult(
            email_id=email_id,
            recipient=recipient,
            subject=subject,
            status='sent',
            sequence_step=sequence_step,
            lead_id=lead_id
        )

    async def _schedule_sequence_follow_ups(self, lead, sequence_name: str):
        """Schedule remaining emails in the sequence"""
        sequence = self.sequences.get(sequence_name)
        if not sequence:
            return

        # Schedule follow-up emails
        for step in sequence.steps[1:]:  # Skip first email (already sent)
            delay_hours = step.get('delay_hours', 24)
            step_number = step.get('step_number', 1)

            # In a real implementation, this would use a task scheduler
            # For demo, we'll just log the scheduling
            scheduled_time = datetime.now() + timedelta(hours=delay_hours)
            self.logger.debug(
                f"Scheduled email {step_number} for lead {lead.prospect_data.get('company_name')} "
                f"at {scheduled_time}"
            )

    async def _update_sequence_performance(self, results: Dict[str, Any]):
        """Update sequence performance metrics"""
        sequence_name = results.get('sequence_type', 'unknown')

        if sequence_name not in self.sequence_performance:
            self.sequence_performance[sequence_name] = SequencePerformance(
                sequence_name=sequence_name,
                total_emails_sent=0,
                open_rate=0.0,
                click_rate=0.0,
                response_rate=0.0,
                conversion_rate=0.0,
                best_performing_step=1,
                generated_opportunities=0
            )

        perf = self.sequence_performance[sequence_name]
        perf.total_emails_sent += results.get('sent', 0)

        # Simulate performance metrics (in real implementation, these would be tracked)
        perf.open_rate = random.uniform(0.15, 0.35)
        perf.click_rate = random.uniform(0.03, 0.08)
        perf.response_rate = results.get('responses', 0) / max(1, results.get('sent', 1))
        perf.conversion_rate = random.uniform(0.01, 0.05)

    async def get_sequence_performance(self, sequence_name: str = None) -> Dict[str, Any]:
        """
        Get performance metrics for email sequences

        Args:
            sequence_name: Specific sequence name, or None for all

        Returns:
            Performance metrics
        """
        if sequence_name:
            perf = self.sequence_performance.get(sequence_name)
            return perf.to_dict() if perf else {}
        else:
            return {
                seq_name: perf.to_dict()
                for seq_name, perf in self.sequence_performance.items()
            }

    def create_custom_sequence(self, name: str, description: str,
                             steps: List[Dict[str, Any]]) -> EmailSequence:
        """
        Create a custom email sequence

        Args:
            name: Sequence name
            description: Sequence description
            steps: List of sequence steps

        Returns:
            EmailSequence object
        """
        sequence = EmailSequence(
            name=name,
            description=description,
            steps=steps,
            target_audience='custom',
            success_criteria={
                'response_rate_target': 0.05,
                'max_sequence_length': len(steps)
            }
        )

        self.sequences[name] = sequence
        self.logger.info(f"Created custom sequence: {name}")
        return sequence

    async def track_email_responses(self, email_id: str, response_type: str):
        """
        Track responses to sent emails

        Args:
            email_id: Email identifier
            response_type: Type of response ('opened', 'clicked', 'replied', 'unsubscribed')
        """
        # Find email in history
        for email in self.email_history:
            if email.email_id == email_id:
                # In a real implementation, this would update tracking systems
                self.logger.debug(f"Tracked {response_type} response for email {email_id}")
                break

    # Real SMTP Implementation (for production use)
    async def _send_email_smtp(self, recipient: str, subject: str, body: str) -> bool:
        """Send email using SMTP (production implementation)"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['username']
            msg['To'] = recipient
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html'))

            server = smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port'])
            if self.smtp_config['use_tls']:
                server.starttls()

            server.login(self.smtp_config['username'], self.smtp_config['password'])
            server.send_message(msg)
            server.quit()

            return True

        except Exception as e:
            self.logger.error(f"SMTP email sending failed: {e}")
            return False

    # Template Management Methods
    def add_template(self, template: EmailTemplate):
        """Add a new email template"""
        self.templates[template.name] = template
        self.logger.info(f"Added email template: {template.name}")

    def get_template(self, template_name: str) -> Optional[EmailTemplate]:
        """Get email template by name"""
        return self.templates.get(template_name)

    def list_templates(self) -> List[str]:
        """List available email templates"""
        return list(self.templates.keys())

    def list_sequences(self) -> List[str]:
        """List available email sequences"""
        return list(self.sequences.keys())
