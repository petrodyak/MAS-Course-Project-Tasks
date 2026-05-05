import os
import sqlite3


def ensure_setup(db_path: str, artifacts_path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    os.makedirs(artifacts_path, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_email TEXT NOT NULL,
                user_password_hash TEXT NOT NULL,
                is_active INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS roles (
                role_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                role_name TEXT NOT NULL,
                role_description TEXT NOT NULL,
                is_active INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_roles (
                user_role_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_id INTEGER NOT NULL REFERENCES users(user_id),
                role_id INTEGER NOT NULL REFERENCES roles(role_id),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS permissions (
                permission_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                permission_key TEXT NOT NULL,
                permission_description TEXT NOT NULL,
                is_active INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS role_permissions (
                role_permission_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                role_id INTEGER NOT NULL REFERENCES roles(role_id),
                permission_id INTEGER NOT NULL REFERENCES permissions(permission_id),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS departments (
                department_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                department_name TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS teams (
                team_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                team_name TEXT NOT NULL,
                department_id INTEGER NOT NULL REFERENCES departments(department_id),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS legal_statuses (
                legal_status_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                legal_status_name TEXT NOT NULL,
                legal_status_description TEXT,
                is_active INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS employees (
                employee_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                employee_first_name TEXT NOT NULL,
                employee_last_name TEXT NOT NULL,
                employee_middle_name TEXT NOT NULL,
                employee_work_email TEXT NOT NULL,
                employee_phone TEXT,
                department_id INTEGER NOT NULL REFERENCES departments(department_id),
                team_id INTEGER NOT NULL REFERENCES teams(team_id),
                current_position_title TEXT NOT NULL,
                legal_status_id INTEGER NOT NULL REFERENCES legal_statuses(legal_status_id),
                is_terminated INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS employment_assignments (
                employment_assignment_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
                department_id INTEGER NOT NULL REFERENCES departments(department_id),
                team_id INTEGER NOT NULL REFERENCES teams(team_id),
                position_title TEXT NOT NULL,
                legal_status_id INTEGER NOT NULL REFERENCES legal_statuses(legal_status_id),
                assigned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                unassigned_at DATETIME,
                is_current INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS employment_events (
                employment_event_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
                employment_event_type TEXT NOT NULL,
                actor_user_id INTEGER NOT NULL REFERENCES users(user_id),
                event_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                department_id INTEGER NOT NULL REFERENCES departments(department_id),
                team_id INTEGER NOT NULL REFERENCES teams(team_id),
                position_title TEXT NOT NULL,
                legal_status_id INTEGER NOT NULL REFERENCES legal_statuses(legal_status_id),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS job_postings (
                job_posting_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                job_title TEXT NOT NULL,
                job_description TEXT NOT NULL,
                location TEXT NOT NULL,
                is_active INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS applicants (
                applicant_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                job_posting_id INTEGER NOT NULL REFERENCES job_postings(job_posting_id),
                applicant_first_name TEXT NOT NULL,
                applicant_last_name TEXT NOT NULL,
                applicant_email TEXT NOT NULL,
                applicant_phone TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS applicant_stages (
                applicant_stage_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                applicant_id INTEGER NOT NULL REFERENCES applicants(applicant_id),
                stage_name TEXT NOT NULL,
                stage_started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                performed_by_user_id INTEGER NOT NULL REFERENCES users(user_id),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS applicant_stage_transitions (
                applicant_stage_transition_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                applicant_stage_id INTEGER NOT NULL REFERENCES applicant_stages(applicant_stage_id),
                from_stage_name TEXT NOT NULL,
                to_stage_name TEXT NOT NULL,
                transitioned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                performed_by_user_id INTEGER NOT NULL REFERENCES users(user_id),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leave_types (
                leave_type_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                leave_type_name TEXT NOT NULL,
                leave_type_description TEXT NOT NULL,
                is_active INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leave_requests (
                leave_request_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
                leave_type_id INTEGER NOT NULL REFERENCES leave_types(leave_type_id),
                leave_status TEXT NOT NULL,
                start_date DATETIME NOT NULL,
                end_date DATETIME NOT NULL,
                leave_reason TEXT NOT NULL,
                created_by_user_id INTEGER NOT NULL REFERENCES users(user_id),
                approved_by_user_id INTEGER REFERENCES users(user_id),
                approved_at DATETIME,
                rejected_at DATETIME,
                rejection_reason TEXT,
                is_conflicted INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leave_approvals (
                leave_approval_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                leave_request_id INTEGER NOT NULL REFERENCES leave_requests(leave_request_id),
                approval_status TEXT NOT NULL,
                decided_by_user_id INTEGER NOT NULL REFERENCES users(user_id),
                decided_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS performance_review_templates (
                review_template_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                template_name TEXT NOT NULL,
                template_description TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
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
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS goals (
                goal_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
                owner_user_id INTEGER NOT NULL REFERENCES users(user_id),
                goal_status TEXT NOT NULL,
                target_date DATETIME NOT NULL,
                measurable_description TEXT NOT NULL,
                goal_title TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                course_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                course_title TEXT NOT NULL,
                course_description TEXT NOT NULL,
                is_active INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS course_modules (
                course_module_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                course_id INTEGER NOT NULL REFERENCES courses(course_id),
                module_title TEXT NOT NULL,
                module_order INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS enrollments (
                enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
                course_id INTEGER NOT NULL REFERENCES courses(course_id),
                course_module_id INTEGER REFERENCES course_modules(course_module_id),
                enrolled_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                enrollment_status TEXT,
                progress_percent INTEGER,
                completed_at DATETIME,
                completion_status_reason TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS compensation_salary_bands (
                salary_band_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                band_name TEXT NOT NULL,
                min_salary INTEGER NOT NULL,
                max_salary INTEGER NOT NULL,
                currency TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS employee_salary_history (
                salary_history_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
                salary_band_id INTEGER NOT NULL REFERENCES compensation_salary_bands(salary_band_id),
                base_salary INTEGER NOT NULL,
                currency TEXT NOT NULL,
                effective_date DATETIME NOT NULL,
                changed_by_user_id INTEGER NOT NULL REFERENCES users(user_id),
                reason TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                audit_log_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                actor_user_id INTEGER NOT NULL REFERENCES users(user_id),
                entity_type TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                change_action TEXT NOT NULL,
                changed_fields_json TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                request_ip TEXT,
                user_agent TEXT
            )
            """
        )
        conn.commit()
