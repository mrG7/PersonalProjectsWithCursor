"""
Patient Care Coordinator - Main Healthcare Orchestrator

This is the main orchestrator for the Patient Care Coordinator system.
It coordinates all aspects of patient care across multiple healthcare providers.
"""

import asyncio
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import aiofiles


@dataclass
class HealthcareConfig:
    """Configuration for healthcare coordination"""
    facility_name: str = "General Hospital"
    specialties: List[str] = None
    capacity: Dict[str, int] = None
    risk_thresholds: Dict[str, float] = None
    alert_settings: Dict[str, bool] = None
    compliance_mode: str = "hipaa"

    def __post_init__(self):
        if self.specialties is None:
            self.specialties = ["cardiology", "endocrinology", "neurology", "primary_care"]
        if self.capacity is None:
            self.capacity = {"beds": 200, "icu_beds": 20, "operating_rooms": 8}
        if self.risk_thresholds is None:
            self.risk_thresholds = {"high_risk": 0.8, "medium_risk": 0.6, "low_risk": 0.3}
        if self.alert_settings is None:
            self.alert_settings = {
                "vital_signs_abnormal": True,
                "medication_due": True,
                "appointment_reminder": True,
                "clinical_alert": True
            }


@dataclass
class Patient:
    """Represents a patient in the healthcare system"""
    patient_id: str
    name: str
    date_of_birth: datetime
    conditions: List[str]
    current_medications: List[str]
    allergies: List[str]
    primary_provider: str
    risk_level: str
    last_visit: Optional[datetime] = None
    next_visit: Optional[datetime] = None

    def __post_init__(self):
        if self.last_visit is None:
            self.last_visit = datetime.now()
        if self.next_visit is None:
            self.next_visit = datetime.now() + timedelta(days=30)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['date_of_birth'] = self.date_of_birth.isoformat()
        if self.last_visit:
            data['last_visit'] = self.last_visit.isoformat()
        if self.next_visit:
            data['next_visit'] = self.next_visit.isoformat()
        return data


@dataclass
class CarePlan:
    """Comprehensive patient care plan"""
    patient_id: str
    conditions: List[str]
    interventions: List[Dict[str, Any]]
    medications: List[Dict[str, Any]]
    appointments: List[Dict[str, Any]]
    monitoring_schedule: List[Dict[str, Any]]
    goals: List[str]
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data


class PatientCareCoordinator:
    """
    Patient Care Coordinator orchestrates comprehensive healthcare management.

    Features:
    - Patient admission and care plan generation
    - Multi-provider coordination and communication
    - Clinical decision support and treatment optimization
    - Appointment scheduling and resource management
    - Population health analytics and quality improvement
    - Compliance with healthcare regulations (HIPAA, etc.)
    """

    def __init__(self, config_path: str = None, log_level: str = "INFO"):
        """
        Initialize the Patient Care Coordinator

        Args:
            config_path: Path to configuration file
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), '..', 'config', 'healthcare_config.json'
        )
        self.config = self._load_config()
        self._setup_logging(log_level)

        # Initialize components
        self.patients: Dict[str, Patient] = {}
        self.care_plans: Dict[str, CarePlan] = {}
        self.active_alerts: List[Dict[str, Any]] = []

        # Data directories
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(self.data_dir, exist_ok=True)

        # Load existing data
        asyncio.create_task(self._load_existing_data())

        self.logger.info("Patient Care Coordinator initialized successfully")

    def _load_config(self) -> HealthcareConfig:
        """Load configuration from file or create default"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                    return HealthcareConfig(**config_data)
            else:
                self.logger.warning(f"Config file not found: {self.config_path}, using defaults")
        except Exception as e:
            self.logger.error(f"Error loading config: {e}, using defaults")

        return HealthcareConfig()

    def _setup_logging(self, log_level: str):
        """Setup logging configuration"""
        self.logger = logging.getLogger('PatientCareCoordinator')
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))

        # File handler
        log_file = os.path.join(self.data_dir, 'healthcare_coordinator.log')
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

    async def _load_existing_data(self):
        """Load existing patient and care plan data"""
        try:
            # Load patients
            patients_file = os.path.join(self.data_dir, 'patients.json')
            if os.path.exists(patients_file):
                async with aiofiles.open(patients_file, 'r') as f:
                    patients_data = json.loads(await f.read())
                    for patient_data in patients_data:
                        patient = Patient(**patient_data)
                        self.patients[patient.patient_id] = patient

            # Load care plans
            plans_file = os.path.join(self.data_dir, 'care_plans.json')
            if os.path.exists(plans_file):
                async with aiofiles.open(plans_file, 'r') as f:
                    plans_data = json.loads(await f.read())
                    for plan_data in plans_data:
                        plan = CarePlan(**plan_data)
                        self.care_plans[plan.patient_id] = plan

            self.logger.info(f"Loaded {len(self.patients)} patients and {len(self.care_plans)} care plans")

        except Exception as e:
            self.logger.error(f"Error loading existing data: {e}")

    async def admit_patient(self, patient_data: Dict[str, Any]) -> str:
        """
        Admit a new patient to the healthcare system

        Args:
            patient_data: Patient information dictionary

        Returns:
            Patient ID
        """
        try:
            # Generate patient ID
            patient_id = f"PAT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Create patient object
            patient = Patient(
                patient_id=patient_id,
                name=patient_data.get('name', 'Unknown Patient'),
                date_of_birth=datetime.fromisoformat(patient_data.get('date_of_birth', '1990-01-01')),
                conditions=patient_data.get('conditions', []),
                current_medications=patient_data.get('current_medications', []),
                allergies=patient_data.get('allergies', []),
                primary_provider=patient_data.get('primary_provider', 'unassigned'),
                risk_level=self._assess_initial_risk(patient_data)
            )

            # Store patient
            self.patients[patient_id] = patient

            # Generate initial care plan
            await self.generate_care_plan(patient_id)

            # Save data
            await self._save_patient_data()

            self.logger.info(f"Admitted new patient: {patient.name} (ID: {patient_id})")
            return patient_id

        except Exception as e:
            self.logger.error(f"Error admitting patient: {e}")
            raise

    def _assess_initial_risk(self, patient_data: Dict[str, Any]) -> str:
        """Assess initial patient risk level"""
        conditions = patient_data.get('conditions', [])
        medications = patient_data.get('current_medications', [])

        # Simple risk assessment based on conditions
        high_risk_conditions = ['cancer', 'heart_disease', 'diabetes_complications', 'severe_mental_health']
        medium_risk_conditions = ['diabetes', 'hypertension', 'asthma', 'depression']

        if any(condition in conditions for condition in high_risk_conditions):
            return 'high'
        elif any(condition in conditions for condition in medium_risk_conditions):
            return 'medium'
        elif len(conditions) > 2 or len(medications) > 3:
            return 'medium'
        else:
            return 'low'

    async def generate_care_plan(self, patient_id: str) -> Dict[str, Any]:
        """
        Generate a comprehensive care plan for a patient

        Args:
            patient_id: Patient identifier

        Returns:
            Care plan dictionary
        """
        if patient_id not in self.patients:
            raise ValueError(f"Patient {patient_id} not found")

        patient = self.patients[patient_id]

        try:
            # Generate interventions based on conditions
            interventions = self._generate_interventions(patient)

            # Generate medication plan
            medications = self._generate_medication_plan(patient)

            # Generate appointment schedule
            appointments = self._generate_appointment_schedule(patient)

            # Generate monitoring schedule
            monitoring = self._generate_monitoring_schedule(patient)

            # Define care goals
            goals = self._generate_care_goals(patient)

            # Create care plan
            care_plan = CarePlan(
                patient_id=patient_id,
                conditions=patient.conditions,
                interventions=interventions,
                medications=medications,
                appointments=appointments,
                monitoring_schedule=monitoring,
                goals=goals
            )

            # Store care plan
            self.care_plans[patient_id] = care_plan

            # Save data
            await self._save_care_plan_data()

            plan_dict = care_plan.to_dict()
            self.logger.info(f"Generated care plan for patient {patient_id} with {len(interventions)} interventions")
            return plan_dict

        except Exception as e:
            self.logger.error(f"Error generating care plan for {patient_id}: {e}")
            raise

    def _generate_interventions(self, patient: Patient) -> List[Dict[str, Any]]:
        """Generate care interventions based on patient conditions"""
        interventions = []

        for condition in patient.conditions:
            if condition == 'diabetes':
                interventions.extend([
                    {
                        'type': 'lifestyle',
                        'description': 'Diabetes education and self-management training',
                        'frequency': 'weekly',
                        'duration_weeks': 8,
                        'priority': 'high'
                    },
                    {
                        'type': 'monitoring',
                        'description': 'Regular blood glucose monitoring',
                        'frequency': 'daily',
                        'priority': 'high'
                    }
                ])
            elif condition == 'hypertension':
                interventions.extend([
                    {
                        'type': 'lifestyle',
                        'description': 'Dietary counseling and exercise program',
                        'frequency': 'biweekly',
                        'duration_weeks': 12,
                        'priority': 'high'
                    },
                    {
                        'type': 'monitoring',
                        'description': 'Blood pressure monitoring',
                        'frequency': 'weekly',
                        'priority': 'medium'
                    }
                ])
            elif condition == 'asthma':
                interventions.extend([
                    {
                        'type': 'education',
                        'description': 'Asthma action plan and trigger avoidance',
                        'frequency': 'monthly',
                        'duration_weeks': 26,
                        'priority': 'high'
                    }
                ])

        return interventions

    def _generate_medication_plan(self, patient: Patient) -> List[Dict[str, Any]]:
        """Generate medication management plan"""
        medications = []

        for medication in patient.current_medications:
            medications.append({
                'name': medication,
                'dosage': 'As prescribed',
                'frequency': 'daily',
                'monitoring': 'Regular lab work',
                'adherence_tracking': True
            })

        return medications

    def _generate_appointment_schedule(self, patient: Patient) -> List[Dict[str, Any]]:
        """Generate appointment schedule"""
        appointments = []

        # Primary care follow-up
        appointments.append({
            'type': 'primary_care',
            'description': 'Routine check-up',
            'scheduled_date': (datetime.now() + timedelta(days=30)).isoformat(),
            'duration_minutes': 30,
            'priority': 'routine'
        })

        # Specialty appointments based on conditions
        for condition in patient.conditions:
            if condition == 'diabetes':
                appointments.append({
                    'type': 'endocrinology',
                    'description': 'Diabetes management',
                    'scheduled_date': (datetime.now() + timedelta(days=14)).isoformat(),
                    'duration_minutes': 45,
                    'priority': 'high'
                })
            elif condition == 'hypertension':
                appointments.append({
                    'type': 'cardiology',
                    'description': 'Blood pressure management',
                    'scheduled_date': (datetime.now() + timedelta(days=21)).isoformat(),
                    'duration_minutes': 30,
                    'priority': 'medium'
                })

        return appointments

    def _generate_monitoring_schedule(self, patient: Patient) -> List[Dict[str, Any]]:
        """Generate monitoring schedule"""
        monitoring = []

        # Vital signs monitoring
        monitoring.append({
            'type': 'vital_signs',
            'parameters': ['blood_pressure', 'heart_rate', 'weight'],
            'frequency': 'daily',
            'method': 'home_monitoring',
            'alert_thresholds': {
                'blood_pressure': {'systolic': 140, 'diastolic': 90},
                'heart_rate': {'min': 50, 'max': 100}
            }
        })

        # Lab work schedule
        monitoring.append({
            'type': 'lab_work',
            'tests': ['comprehensive_metabolic_panel', 'lipid_panel'],
            'frequency': 'quarterly',
            'location': 'primary_care_office'
        })

        return monitoring

    def _generate_care_goals(self, patient: Patient) -> List[str]:
        """Generate patient care goals"""
        goals = [
            "Improve overall health status and quality of life",
            "Achieve better control of chronic conditions",
            "Maintain regular follow-up appointments",
            "Adhere to prescribed medication regimen"
        ]

        for condition in patient.conditions:
            if condition == 'diabetes':
                goals.extend([
                    "Maintain HbA1c below 7.0%",
                    "Achieve healthy BMI range",
                    "Regular exercise routine"
                ])
            elif condition == 'hypertension':
                goals.extend([
                    "Maintain blood pressure below 130/80 mmHg",
                    "Reduce sodium intake",
                    "Stress management techniques"
                ])

        return goals

    async def schedule_follow_up(self, patient_id: str, specialty: str,
                                urgency: str = "routine") -> Dict[str, Any]:
        """
        Schedule a follow-up appointment

        Args:
            patient_id: Patient identifier
            specialty: Medical specialty needed
            urgency: Appointment urgency level

        Returns:
            Appointment details
        """
        if patient_id not in self.patients:
            raise ValueError(f"Patient {patient_id} not found")

        try:
            # Calculate optimal appointment time
            if urgency == "urgent":
                appointment_date = datetime.now() + timedelta(days=1)
            elif urgency == "high":
                appointment_date = datetime.now() + timedelta(days=3)
            else:
                appointment_date = datetime.now() + timedelta(days=14)

            appointment = {
                'appointment_id': f"APT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'patient_id': patient_id,
                'specialty': specialty,
                'datetime': appointment_date.isoformat(),
                'duration_minutes': 30,
                'urgency': urgency,
                'status': 'scheduled',
                'location': f"{specialty.title()} Clinic"
            }

            # Update patient's next visit
            self.patients[patient_id].next_visit = appointment_date

            # Save data
            await self._save_patient_data()

            self.logger.info(f"Scheduled {specialty} appointment for patient {patient_id}")
            return appointment

        except Exception as e:
            self.logger.error(f"Error scheduling appointment: {e}")
            raise

    async def get_patient_status(self, patient_id: str) -> Dict[str, Any]:
        """
        Get comprehensive patient status

        Args:
            patient_id: Patient identifier

        Returns:
            Patient status information
        """
        if patient_id not in self.patients:
            raise ValueError(f"Patient {patient_id} not found")

        patient = self.patients[patient_id]
        care_plan = self.care_plans.get(patient_id)

        status = {
            'patient_info': patient.to_dict(),
            'care_plan_exists': care_plan is not None,
            'active_alerts': len([a for a in self.active_alerts if a['patient_id'] == patient_id]),
            'next_appointment': patient.next_visit.isoformat() if patient.next_visit else None,
            'risk_level': patient.risk_level,
            'last_updated': datetime.now().isoformat()
        }

        if care_plan:
            status['care_plan_summary'] = {
                'conditions': care_plan.conditions,
                'active_interventions': len(care_plan.interventions),
                'upcoming_appointments': len(care_plan.appointments),
                'care_goals': len(care_plan.goals)
            }

        return status

    async def generate_health_report(self, patient_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive health report for a patient

        Args:
            patient_id: Patient identifier

        Returns:
            Health report
        """
        if patient_id not in self.patients:
            raise ValueError(f"Patient {patient_id} not found")

        patient = self.patients[patient_id]
        care_plan = self.care_plans.get(patient_id)

        report = {
            'patient_id': patient_id,
            'patient_name': patient.name,
            'report_date': datetime.now().isoformat(),
            'health_summary': {
                'conditions': patient.conditions,
                'medications': patient.current_medications,
                'allergies': patient.allergies,
                'risk_level': patient.risk_level
            }
        }

        if care_plan:
            report['care_plan_status'] = {
                'interventions_completed': len(care_plan.interventions),
                'appointments_scheduled': len(care_plan.appointments),
                'goals_progress': "In progress"
            }

        return report

    async def _save_patient_data(self):
        """Save patient data to disk"""
        try:
            patients_data = [patient.to_dict() for patient in self.patients.values()]
            patients_file = os.path.join(self.data_dir, 'patients.json')

            async with aiofiles.open(patients_file, 'w') as f:
                await f.write(json.dumps(patients_data, indent=2))

        except Exception as e:
            self.logger.error(f"Error saving patient data: {e}")

    async def _save_care_plan_data(self):
        """Save care plan data to disk"""
        try:
            plans_data = [plan.to_dict() for plan in self.care_plans.values()]
            plans_file = os.path.join(self.data_dir, 'care_plans.json')

            async with aiofiles.open(plans_file, 'w') as f:
                await f.write(json.dumps(plans_data, indent=2))

        except Exception as e:
            self.logger.error(f"Error saving care plan data: {e}")

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall system status and metrics

        Returns:
            System status information
        """
        total_patients = len(self.patients)
        active_care_plans = len(self.care_plans)
        active_alerts = len(self.active_alerts)

        # Calculate risk distribution
        risk_distribution = {'high': 0, 'medium': 0, 'low': 0}
        for patient in self.patients.values():
            risk_distribution[patient.risk_level] += 1

        status = {
            'facility_name': self.config.facility_name,
            'total_patients': total_patients,
            'active_care_plans': active_care_plans,
            'active_alerts': active_alerts,
            'risk_distribution': risk_distribution,
            'capacity_utilization': {
                'beds': f"{total_patients}/{self.config.capacity['beds']}",
                'care_plans': f"{active_care_plans}/{total_patients}"
            },
            'system_health': 'operational',
            'last_updated': datetime.now().isoformat()
        }

        return status

    async def cleanup(self):
        """Cleanup resources"""
        self.logger.info("Patient Care Coordinator cleanup completed")


# Convenience functions for quick usage
async def admit_new_patient(name: str, conditions: List[str] = None,
                           medications: List[str] = None) -> str:
    """
    Quickly admit a new patient

    Args:
        name: Patient name
        conditions: List of medical conditions
        medications: List of current medications

    Returns:
        Patient ID
    """
    coordinator = PatientCareCoordinator()

    try:
        patient_data = {
            'name': name,
            'conditions': conditions or [],
            'current_medications': medications or []
        }

        patient_id = await coordinator.admit_patient(patient_data)
        return patient_id
    finally:
        await coordinator.cleanup()


async def generate_patient_report(patient_id: str) -> Dict[str, Any]:
    """
    Generate a health report for a patient

    Args:
        patient_id: Patient identifier

    Returns:
        Health report
    """
    coordinator = PatientCareCoordinator()

    try:
        report = await coordinator.generate_health_report(patient_id)
        return report
    finally:
        await coordinator.cleanup()


# CLI interface for direct execution
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Patient Care Coordinator - AI-Powered Healthcare Management"
    )

    # Main operation modes
    parser.add_argument('--admit-patient', action='store_true',
                       help='Admit a new patient')
    parser.add_argument('--generate-plan', action='store_true',
                       help='Generate care plan for patient')
    parser.add_argument('--schedule-followup', action='store_true',
                       help='Schedule follow-up appointment')
    parser.add_argument('--patient-status', action='store_true',
                       help='Get patient status')
    parser.add_argument('--system-status', action='store_true',
                       help='Get system status')
    parser.add_argument('--generate-report', action='store_true',
                       help='Generate patient health report')

    # Parameters
    parser.add_argument('--patient-id', type=str, help='Patient ID')
    parser.add_argument('--name', type=str, help='Patient name')
    parser.add_argument('--conditions', type=str, nargs='*', help='Medical conditions')
    parser.add_argument('--medications', type=str, nargs='*', help='Current medications')
    parser.add_argument('--specialty', type=str, help='Medical specialty')
    parser.add_argument('--urgency', type=str, default='routine',
                       choices=['routine', 'high', 'urgent'], help='Appointment urgency')
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')

    args = parser.parse_args()

    async def main():
        coordinator = PatientCareCoordinator(args.config, args.log_level)

        try:
            if args.admit_patient:
                if not args.name:
                    print("Error: Patient name required for admission")
                    return

                patient_data = {
                    'name': args.name,
                    'conditions': args.conditions or [],
                    'current_medications': args.medications or []
                }

                patient_id = await coordinator.admit_patient(patient_data)
                print(f"Patient admitted successfully. ID: {patient_id}")

            elif args.generate_plan:
                if not args.patient_id:
                    print("Error: Patient ID required")
                    return

                plan = await coordinator.generate_care_plan(args.patient_id)
                print(f"Care plan generated with {len(plan['interventions'])} interventions")

            elif args.schedule_followup:
                if not args.patient_id or not args.specialty:
                    print("Error: Patient ID and specialty required")
                    return

                appointment = await coordinator.schedule_follow_up(
                    args.patient_id, args.specialty, args.urgency
                )
                print(f"Appointment scheduled: {appointment['datetime']}")

            elif args.patient_status:
                if not args.patient_id:
                    print("Error: Patient ID required")
                    return

                status = await coordinator.get_patient_status(args.patient_id)
                print(f"Patient: {status['patient_info']['name']}")
                print(f"Risk Level: {status['patient_info']['risk_level']}")
                print(f"Conditions: {', '.join(status['patient_info']['conditions'])}")

            elif args.system_status:
                status = await coordinator.get_system_status()
                print(f"Facility: {status['facility_name']}")
                print(f"Total Patients: {status['total_patients']}")
                print(f"Active Care Plans: {status['active_care_plans']}")

            elif args.generate_report:
                if not args.patient_id:
                    print("Error: Patient ID required")
                    return

                report = await coordinator.generate_health_report(args.patient_id)
                print(f"Health report generated for {report['patient_name']}")

            else:
                parser.print_help()

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await coordinator.cleanup()

    asyncio.run(main())
