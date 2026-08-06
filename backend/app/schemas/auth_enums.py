"""
Authentication and Authorization Domain Enumerations.

This module defines the explicit, strongly-typed enums for system roles,
token categories, and granular permissions used across the RBAC system.
"""

from enum import Enum


class UserRole(str, Enum):
    """
    Core system roles within the Digital Biomarker Platform.
    Hierarchical order: ADMINISTRATOR > RESEARCHER > CLINICIAN > PATIENT.
    """
    ADMINISTRATOR = "administrator"
    RESEARCHER = "researcher"
    CLINICIAN = "clinician"
    PATIENT = "patient"


class TokenType(str, Enum):
    """
    Categorizes JSON Web Tokens to enforce strict context-aware usage.
    """
    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"


class Permission(str, Enum):
    """
    Granular permissions for Fine-Grained Access Control (FGAC).
    Guards domain resources across clinical, research, and admin boundaries.
    """
    # User Management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_MANAGE_ROLES = "user:manage_roles"

    # Patient Data & Clinical Telemetry
    PATIENT_READ = "patient:read"
    PATIENT_WRITE = "patient:write"
    PATIENT_DELETE = "patient:delete"
    CLINICAL_NOTE_CREATE = "clinical_note:create"

    # Biomarker & AI Model Operations
    BIOMARKER_READ = "biomarker:read"
    BIOMARKER_EXPORT = "biomarker:export"
    AI_MODEL_EXECUTE = "ai_model:execute"
    AI_MODEL_READ_METRICS = "ai_model:read_metrics"

    # Research & Dataset Analytics
    RESEARCH_DATASET_READ = "research_dataset:read"
    RESEARCH_DATASET_EXPORT = "research_dataset:export"

    # System & Audit Logs
    AUDIT_LOG_READ = "audit_log:read"
    SYSTEM_CONFIG_MANAGE = "system_config:manage"