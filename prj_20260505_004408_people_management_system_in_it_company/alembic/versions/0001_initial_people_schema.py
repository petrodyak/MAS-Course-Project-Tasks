"""0001 initial people schema

Revision ID: 0001_initial_people_schema
Revises:
Create Date: 2026-05-05
"""
from __future__ import annotations

from alembic import op

revision = "0001_initial_people_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            user_email VARCHAR(320) NOT NULL,
            user_password_hash VARCHAR(255) NOT NULL,
            is_active BOOLEAN NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # roles
    op.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            role_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            role_name VARCHAR(200) NOT NULL,
            role_description TEXT NOT NULL,
            is_active BOOLEAN NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # user_roles
    op.execute("""
        CREATE TABLE IF NOT EXISTS user_roles (
            user_role_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            user_id INTEGER NOT NULL REFERENCES users(user_id),
            role_id INTEGER NOT NULL REFERENCES roles(role_id),
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # permissions
    op.execute("""
        CREATE TABLE IF NOT EXISTS permissions (
            permission_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            permission_key VARCHAR(200) NOT NULL,
            permission_description TEXT NOT NULL,
            is_active BOOLEAN NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # role_permissions
    op.execute("""
        CREATE TABLE IF NOT EXISTS role_permissions (
            role_permission_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            role_id INTEGER NOT NULL REFERENCES roles(role_id),
            permission_id INTEGER NOT NULL REFERENCES permissions(permission_id),
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # departments
    op.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            department_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            department_name VARCHAR(200) NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # teams
    op.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            team_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            team_name VARCHAR(200) NOT NULL,
            department_id INTEGER NOT NULL REFERENCES departments(department_id),
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # legal_statuses
    op.execute("""
        CREATE TABLE IF NOT EXISTS legal_statuses (
            legal_status_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            legal_status_name VARCHAR(200) NOT NULL,
            legal_status_description TEXT,
            is_active BOOLEAN NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # employees
    op.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            employee_first_name VARCHAR(200) NOT NULL,
            employee_last_name VARCHAR(200) NOT NULL,
            employee_middle_name VARCHAR(200) NOT NULL,
            employee_work_email VARCHAR(320) NOT NULL,
            employee_phone VARCHAR(50),
            department_id INTEGER NOT NULL REFERENCES departments(department_id),
            team_id INTEGER NOT NULL REFERENCES teams(team_id),
            current_position_title VARCHAR(200) NOT NULL,
            legal_status_id INTEGER NOT NULL REFERENCES legal_statuses(legal_status_id),
            is_terminated BOOLEAN NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # employment_assignments
    op.execute("""
        CREATE TABLE IF NOT EXISTS employment_assignments (
            employment_assignment_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
            department_id INTEGER NOT NULL REFERENCES departments(department_id),
            team_id INTEGER NOT NULL REFERENCES teams(team_id),
            position_title VARCHAR(200) NOT NULL,
            legal_status_id INTEGER NOT NULL REFERENCES legal_statuses(legal_status_id),
            assigned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            unassigned_at DATETIME,
            is_current BOOLEAN NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # employment_events
    op.execute("""
        CREATE TABLE IF NOT EXISTS employment_events (
            employment_event_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
            employment_event_type VARCHAR(50) NOT NULL,
            actor_user_id INTEGER NOT NULL REFERENCES users(user_id),
            event_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            department_id INTEGER NOT NULL REFERENCES departments(department_id),
            team_id INTEGER NOT NULL REFERENCES teams(team_id),
            position_title VARCHAR(200) NOT NULL,
            legal_status_id INTEGER NOT NULL REFERENCES legal_statuses(legal_status_id),
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # job_postings
    op.execute("""
        CREATE TABLE IF NOT EXISTS job_postings (
            job_posting_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            job_title VARCHAR(250) NOT NULL,
            job_description TEXT NOT NULL,
            location VARCHAR(200) NOT NULL,
            is_active BOOLEAN NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # applicants
    op.execute("""
        CREATE TABLE IF NOT EXISTS applicants (
            applicant_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            job_posting_id INTEGER NOT NULL REFERENCES job_postings(job_posting_id),
            applicant_first_name VARCHAR(200) NOT NULL,
            applicant_last_name VARCHAR(200) NOT NULL,
            applicant_email VARCHAR(320) NOT NULL,
            applicant_phone VARCHAR(50),
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # applicant_stages
    op.execute("""
        CREATE TABLE IF NOT EXISTS applicant_stages (
            applicant_stage_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            applicant_id INTEGER NOT NULL REFERENCES applicants(applicant_id),
            stage_name VARCHAR(200) NOT NULL,
            stage_started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            performed_by_user_id INTEGER NOT NULL REFERENCES users(user_id),
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # applicant_stage_transitions
    op.execute("""
        CREATE TABLE IF NOT EXISTS applicant_stage_transitions (
            applicant_stage_transition_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            applicant_stage_id INTEGER NOT NULL REFERENCES applicant_stages(applicant_stage_id),
            from_stage_name VARCHAR(200) NOT NULL,
            to_stage_name VARCHAR(200) NOT NULL,
            transitioned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            performed_by_user_id INTEGER NOT NULL REFERENCES users(user_id),
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # leave_types
    op.execute("""
        CREATE TABLE IF NOT EXISTS leave_types (
            leave_type_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            leave_type_name VARCHAR(200) NOT NULL,
            leave_type_description TEXT NOT NULL,
            is_active BOOLEAN NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # leave_requests
    op.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            leave_request_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
            leave_type_id INTEGER NOT NULL REFERENCES leave_types(leave_type_id),
            leave_status VARCHAR(20) NOT NULL,
            start_date DATETIME NOT NULL,
            end_date DATETIME NOT NULL,
            leave_reason VARCHAR(1000) NOT NULL,
            created_by_user_id INTEGER NOT NULL REFERENCES users(user_id),
            approved_by_user_id INTEGER REFERENCES users(user_id),
            approved_at DATETIME,
            rejected_at DATETIME,
            rejection_reason VARCHAR(1000),
            is_conflicted BOOLEAN NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # leave_approvals
    op.execute("""
        CREATE TABLE IF NOT EXISTS leave_approvals (
            leave_approval_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            leave_request_id INTEGER NOT NULL REFERENCES leave_requests(leave_request_id),
            approval_status VARCHAR(20) NOT NULL,
            decided_by_user_id INTEGER NOT NULL REFERENCES users(user_id),
            decided_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # performance_review_templates
    op.execute("""
        CREATE TABLE IF NOT EXISTS performance_review_templates (
            review_template_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            template_name VARCHAR(200) NOT NULL,
            template_description TEXT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # performance_reviews
    op.execute("""
        CREATE TABLE IF NOT EXISTS performance_reviews (
            performance_review_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
            review_template_id INTEGER NOT NULL REFERENCES performance_review_templates(review_template_id),
            reviewer_user_id INTEGER NOT NULL REFERENCES users(user_id),
            due_date DATETIME NOT NULL,
            final_rating INTEGER,
            review_notes TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # goals
    op.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            goal_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
            owner_user_id INTEGER NOT NULL REFERENCES users(user_id),
            goal_status VARCHAR(100) NOT NULL,
            target_date DATETIME NOT NULL,
            measurable_description VARCHAR(1000) NOT NULL,
            goal_title VARCHAR(250) NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # courses
    op.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            course_title VARCHAR(250) NOT NULL,
            course_description TEXT NOT NULL,
            is_active BOOLEAN NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # course_modules
    op.execute("""
        CREATE TABLE IF NOT EXISTS course_modules (
            course_module_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            course_id INTEGER NOT NULL REFERENCES courses(course_id),
            module_title VARCHAR(200) NOT NULL,
            module_order INTEGER NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # enrollments
    op.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
            course_id INTEGER NOT NULL REFERENCES courses(course_id),
            course_module_id INTEGER REFERENCES course_modules(course_module_id),
            enrolled_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            enrollment_status VARCHAR(100) NOT NULL,
            progress_percent INTEGER NOT NULL,
            completed_at DATETIME,
            completion_status_reason TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # compensation_salary_bands
    op.execute("""
        CREATE TABLE IF NOT EXISTS compensation_salary_bands (
            salary_band_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            band_name VARCHAR(200) NOT NULL,
            min_salary INTEGER NOT NULL,
            max_salary INTEGER NOT NULL,
            currency VARCHAR(10) NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # employee_salary_history
    op.execute("""
        CREATE TABLE IF NOT EXISTS employee_salary_history (
            salary_history_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
            salary_band_id INTEGER NOT NULL REFERENCES compensation_salary_bands(salary_band_id),
            base_salary INTEGER NOT NULL,
            currency VARCHAR(10) NOT NULL,
            effective_date DATETIME NOT NULL,
            changed_by_user_id INTEGER NOT NULL REFERENCES users(user_id),
            reason TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # audit_logs
    op.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            audit_log_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            actor_user_id INTEGER NOT NULL REFERENCES users(user_id),
            entity_type VARCHAR(100) NOT NULL,
            entity_id INTEGER NOT NULL,
            change_action VARCHAR(50) NOT NULL,
            changed_fields_json TEXT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            request_ip VARCHAR(100),
            user_agent VARCHAR(255)
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS audit_logs")
    op.execute("DROP TABLE IF EXISTS employee_salary_history")
    op.execute("DROP TABLE IF EXISTS compensation_salary_bands")
    op.execute("DROP TABLE IF EXISTS enrollments")
    op.execute("DROP TABLE IF EXISTS course_modules")
    op.execute("DROP TABLE IF EXISTS courses")
    op.execute("DROP TABLE IF EXISTS goals")
    op.execute("DROP TABLE IF EXISTS performance_reviews")
    op.execute("DROP TABLE IF EXISTS performance_review_templates")
    op.execute("DROP TABLE IF EXISTS leave_approvals")
    op.execute("DROP TABLE IF EXISTS leave_requests")
    op.execute("DROP TABLE IF EXISTS leave_types")
    op.execute("DROP TABLE IF EXISTS applicant_stage_transitions")
    op.execute("DROP TABLE IF EXISTS applicant_stages")
    op.execute("DROP TABLE IF EXISTS applicants")
    op.execute("DROP TABLE IF EXISTS job_postings")
    op.execute("DROP TABLE IF EXISTS employment_events")
    op.execute("DROP TABLE IF EXISTS employment_assignments")
    op.execute("DROP TABLE IF EXISTS employees")
    op.execute("DROP TABLE IF EXISTS legal_statuses")
    op.execute("DROP TABLE IF EXISTS teams")
    op.execute("DROP TABLE IF EXISTS departments")
    op.execute("DROP TABLE IF EXISTS role_permissions")
    op.execute("DROP TABLE IF EXISTS permissions")
    op.execute("DROP TABLE IF EXISTS user_roles")
    op.execute("DROP TABLE IF EXISTS roles")
    op.execute("DROP TABLE IF EXISTS users")
