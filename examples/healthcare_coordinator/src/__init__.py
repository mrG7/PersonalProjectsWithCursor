# Patient Care Coordinator - AI-Powered Healthcare Management System
"""
Complete runnable implementation of the Patient Care Coordinator agent.

This agent provides comprehensive healthcare management including:
- Patient care coordination across multiple providers
- Clinical decision support and treatment recommendations
- Chronic disease management and monitoring
- Appointment scheduling and resource optimization
- Population health analytics and insights

Author: Cursor AI Agent Ecosystem
Version: 2.0.0
License: MIT
"""

__version__ = "2.0.0"
__author__ = "Cursor AI Agent Ecosystem"
__description__ = "AI-powered patient care coordination and healthcare management system"

from .patient_care_coordinator import PatientCareCoordinator
from .patient_advocate import PatientAdvocate
from .clinical_decision_support import ClinicalDecisionSupport
from .care_plan_generator import CarePlanGenerator
from .appointment_scheduler import AppointmentScheduler
from .population_health import PopulationHealthAnalyzer

__all__ = [
    'PatientCareCoordinator',
    'PatientAdvocate',
    'ClinicalDecisionSupport',
    'CarePlanGenerator',
    'AppointmentScheduler',
    'PopulationHealthAnalyzer'
]
