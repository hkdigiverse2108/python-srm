# backend/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import urlparse, unquote
import psycopg2
from app.core.config import settings

# Parse the DATABASE_URL manually so URL-encoded characters (e.g. %20 for space)
# are properly decoded before being passed to psycopg2.
def _make_psycopg2_connection():
    parsed = urlparse(settings.DATABASE_URL)
    return psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        dbname=unquote(parsed.path.lstrip("/")),
        user=parsed.username,
        password=unquote(parsed.password) if parsed.password else "",
    )

engine = create_engine("postgresql+psycopg2://", creator=_make_psycopg2_connection)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    from sqlalchemy import inspect, text
    # Ensure all models are registered by importing them here (avoids circular imports)
    try:
        from app.modules.feedback.models import Feedback, UserFeedback
    except ImportError:
        pass
        
    Base.metadata.create_all(bind=engine)
    
    # Manual schema checks for existing tables
    inspector = inspect(engine)
    with engine.connect() as conn:
        # 1. incentive_slabs
        if inspector.has_table("incentive_slabs"):
            cols = [c['name'] for c in inspector.get_columns('incentive_slabs')]
            if 'min_units' not in cols:
                conn.execute(text("ALTER TABLE incentive_slabs ADD COLUMN min_units INTEGER DEFAULT 1"))
            if 'max_units' not in cols:
                conn.execute(text("ALTER TABLE incentive_slabs ADD COLUMN max_units INTEGER DEFAULT 10"))
            if 'incentive_per_unit' not in cols:
                conn.execute(text("ALTER TABLE incentive_slabs ADD COLUMN incentive_per_unit FLOAT DEFAULT 0.0"))
            if 'slab_bonus' not in cols:
                conn.execute(text("ALTER TABLE incentive_slabs ADD COLUMN slab_bonus FLOAT DEFAULT 0.0"))
        
        # 2. incentive_slips
        if inspector.has_table("incentive_slips"):
            cols = [c['name'] for c in inspector.get_columns('incentive_slips')]
            if 'amount_per_unit' not in cols:
                conn.execute(text("ALTER TABLE incentive_slips ADD COLUMN amount_per_unit FLOAT DEFAULT 0.0"))

        # 3. bills (invoice workflow extensions)
        if inspector.has_table("bills"):
            cols = [c['name'] for c in inspector.get_columns('bills')]
            if 'payment_type' not in cols:
                conn.execute(text("ALTER TABLE bills ADD COLUMN payment_type VARCHAR DEFAULT 'PERSONAL_ACCOUNT'"))
            if 'gst_type' not in cols:
                conn.execute(text("ALTER TABLE bills ADD COLUMN gst_type VARCHAR DEFAULT 'WITH_GST'"))
            if 'invoice_series' not in cols:
                conn.execute(text("ALTER TABLE bills ADD COLUMN invoice_series VARCHAR DEFAULT 'INV'"))
            if 'invoice_sequence' not in cols:
                conn.execute(text("ALTER TABLE bills ADD COLUMN invoice_sequence INTEGER DEFAULT 1"))
            if 'requires_qr' not in cols:
                conn.execute(text("ALTER TABLE bills ADD COLUMN requires_qr BOOLEAN DEFAULT TRUE"))
            if 'billing_month' not in cols:
                conn.execute(text("ALTER TABLE bills ADD COLUMN billing_month VARCHAR"))
        
        # 4. system_settings
        if inspector.has_table("system_settings"):
            cols = [c['name'] for c in inspector.get_columns('system_settings')]
            if 'access_policy' not in cols:
                conn.execute(text("ALTER TABLE system_settings ADD COLUMN access_policy JSON DEFAULT '{}'"))
            if 'policy_version' not in cols:
                conn.execute(text("ALTER TABLE system_settings ADD COLUMN policy_version INTEGER DEFAULT 1"))

        # 5. Global Deletion Policy & Soft Delete Column Checks
        tables_to_check = [
            "clients", "projects", "issues", "areas", "shops", "todos", 
            "meeting_summaries", "bills", "attendance", "feedbacks", 
            "user_feedbacks", "payments", "incentive_slabs", 
            "employee_performances", "incentive_slips", "notifications", 
            "timetable_events", "salary_slips", "leave_records", "visits"
        ]
        
        for table_name in tables_to_check:
            if inspector.has_table(table_name):
                cols = [c['name'] for c in inspector.get_columns(table_name)]
                if 'is_deleted' not in cols:
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE"))
                
                # Special check for meeting_summaries assignment fields
                if table_name == "meeting_summaries":
                    if 'host_id' not in cols:
                        conn.execute(text("ALTER TABLE meeting_summaries ADD COLUMN host_id INTEGER REFERENCES users(id)"))
                    if 'todo_id' not in cols:
                        conn.execute(text("ALTER TABLE meeting_summaries ADD COLUMN todo_id INTEGER REFERENCES todos(id)"))
                    if 'reminder_sent' not in cols:
                        conn.execute(text("ALTER TABLE meeting_summaries ADD COLUMN reminder_sent BOOLEAN DEFAULT FALSE"))
                    if 'priority' not in cols:
                        conn.execute(text("ALTER TABLE meeting_summaries ADD COLUMN priority VARCHAR DEFAULT 'MEDIUM'"))
                
                # Special check for timetable_events priority
                if table_name == "timetable_events":
                    if 'priority' not in cols:
                        conn.execute(text("ALTER TABLE timetable_events ADD COLUMN priority VARCHAR DEFAULT 'MEDIUM'"))

        # 5.1 Create meeting_participants table if not exists
        if not inspector.has_table("meeting_participants"):
            conn.execute(text("""
                CREATE TABLE meeting_participants (
                    meeting_id INTEGER REFERENCES meeting_summaries(id) ON DELETE CASCADE,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    PRIMARY KEY (meeting_id, user_id)
                )
            """))
        
        # 6. activity_logs (nullable user_id for system/synthetic logs)
        if inspector.has_table("activity_logs"):
            cols = inspector.get_columns('activity_logs')
            target_col = next((c for c in cols if c['name'] == 'user_id'), None)
            if target_col and not target_col.get('nullable', True):
                conn.execute(text("ALTER TABLE activity_logs ALTER COLUMN user_id DROP NOT NULL"))

        # 7. clients (PM and Owner assignments, Status)
        if inspector.has_table("clients"):
            cols = [c['name'] for c in inspector.get_columns('clients')]
            if 'pm_id' not in cols:
                conn.execute(text("ALTER TABLE clients ADD COLUMN pm_id INTEGER REFERENCES users(id)"))
            if 'pm_assigned_by_id' not in cols:
                conn.execute(text("ALTER TABLE clients ADD COLUMN pm_assigned_by_id INTEGER REFERENCES users(id)"))
            if 'owner_id' not in cols:
                conn.execute(text("ALTER TABLE clients ADD COLUMN owner_id INTEGER REFERENCES users(id)"))
            if 'status' not in cols:
                conn.execute(text("ALTER TABLE clients ADD COLUMN status VARCHAR DEFAULT 'ACTIVE'"))
            if 'is_active' not in cols:
                conn.execute(text("ALTER TABLE clients ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))

        
        # 3. shops (full schema expansion for demo pipeline and assignments)
        if inspector.has_table("shops"):
            cols = [c['name'] for c in inspector.get_columns('shops')]
            # Base Meta
            if 'is_archived' not in cols:
                conn.execute(text("ALTER TABLE shops ADD COLUMN is_archived BOOLEAN DEFAULT FALSE"))
            if 'archived_by_id' not in cols:
                conn.execute(text("ALTER TABLE shops ADD COLUMN archived_by_id INTEGER REFERENCES users(id)"))
            
            # Legacy/Creation fields
            if 'assigned_by_id' not in cols:
                conn.execute(text("ALTER TABLE shops ADD COLUMN assigned_by_id INTEGER REFERENCES users(id)"))
            if 'accepted_at' not in cols:
                conn.execute(text("ALTER TABLE shops ADD COLUMN accepted_at TIMESTAMP WITH TIME ZONE"))
            if 'created_by_id' not in cols:
                conn.execute(text("ALTER TABLE shops ADD COLUMN created_by_id INTEGER REFERENCES users(id)"))

            # PM Demo Pipeline
            if 'project_manager_id' not in cols:
                conn.execute(text("ALTER TABLE shops ADD COLUMN project_manager_id INTEGER REFERENCES users(id)"))
            if 'demo_stage' not in cols:
                conn.execute(text("ALTER TABLE shops ADD COLUMN demo_stage INTEGER DEFAULT 0"))
            if 'demo_scheduled_at' not in cols:
                conn.execute(text("ALTER TABLE shops ADD COLUMN demo_scheduled_at TIMESTAMP WITH TIME ZONE"))
            if 'demo_title' not in cols:
                conn.execute(text("ALTER TABLE shops ADD COLUMN demo_title VARCHAR"))
            if 'demo_type' not in cols:
                conn.execute(text("ALTER TABLE shops ADD COLUMN demo_type VARCHAR"))
            if 'demo_notes' not in cols:
                conn.execute(text("ALTER TABLE shops ADD COLUMN demo_notes TEXT"))
            if 'demo_meet_link' not in cols:
                conn.execute(text("ALTER TABLE shops ADD COLUMN demo_meet_link VARCHAR"))
            if 'scheduled_by_id' not in cols:
                conn.execute(text("ALTER TABLE shops ADD COLUMN scheduled_by_id INTEGER REFERENCES users(id)"))

        # 4. feedbacks
        if inspector.has_table("feedbacks"):
            cols = [c['name'] for c in inspector.get_columns('feedbacks')]
            if 'mobile' not in cols:
                conn.execute(text("ALTER TABLE feedbacks ADD COLUMN mobile VARCHAR"))
            if 'shop_name' not in cols:
                conn.execute(text("ALTER TABLE feedbacks ADD COLUMN shop_name VARCHAR"))
            if 'product' not in cols:
                conn.execute(text("ALTER TABLE feedbacks ADD COLUMN product VARCHAR"))
            if 'agent_name' not in cols:
                conn.execute(text("ALTER TABLE feedbacks ADD COLUMN agent_name VARCHAR"))
            if 'referral_code' not in cols:
                conn.execute(text("ALTER TABLE feedbacks ADD COLUMN referral_code VARCHAR"))
        
        # 4. users
        if inspector.has_table("users"):
            cols = [c['name'] for c in inspector.get_columns('users')]
            if 'referral_code' not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN referral_code VARCHAR"))
        
        conn.commit()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
