import os, asyncio, asyncpg, logging
from sqlalchemy import select, text
from passlib.hash import pbkdf2_sha256
from app.models import (RoleModel, UserRoleModel, UserModel, KnowledgeAssessmentModel)
from app.database import AsyncSessionLocal, Engine, Base
from app.schemas import AppConfigSchema
from app.services import create_template_courses_for_instructor
from app.utils import default_avatar_for_role

DOCKER_DB_SERVICE_NAME = os.getenv("DOCKER_DB_SERVICE_NAME")
DATABASE_PORT = os.getenv("POSTGRES_DATABASE_PORT")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

logger = logging.getLogger(__name__)

config = AppConfigSchema()

async def wait_for_db(retries=10, delay=2):
    """Wait for the database to be available before proceeding.
    This function attempts to connect to the PostgreSQL database using asyncpg.
    It retries the connection a specified number of times with a delay between attempts.
    If the connection is successful, it returns; otherwise, it raises an exception after exhausting retries."""
    
    for attempt in range(retries):
        try:
            conn = await asyncpg.connect(
                user= POSTGRES_USER, 
                password= POSTGRES_PASSWORD, 
                database= POSTGRES_DB, 
                host= DOCKER_DB_SERVICE_NAME, 
                port= DATABASE_PORT
            )
            await conn.close()
            print("✅ Successfully connected to the database.")
            return
        except Exception as e:
            print(f"⏳ Waiting for DB... ({attempt+1}/{retries}) - Error: {e}")
            await asyncio.sleep(delay)
    print("❌ Database connection failed after retries.")
    raise Exception("Database connection failed after retries.")

async def seed_table(session, model, data):
    """Seed a database table with initial data if it's empty.
    This function checks if the specified table is empty.
    If empty, it inserts the provided data into the table.
    If the table already has data, it skips the seeding process."""
    
    exists = await session.execute(select(model).limit(1))
    
    if exists.scalar_one_or_none():
        print(f"✅ {model.__tablename__} already seeded.")
        return
    
    session.add_all(data)
    await session.commit()
    print(f"✅ {model.__tablename__} Seeded.")

async def init_db():
    """Initialize the database by creating tables and seeding initial data.
    This function waits for the database to be available, creates the necessary tables,
    and seeds initial data into various tables such as Roles, Users, UserRoles, Knowledge Assessments,
    Courses, Enrollments, Questions, Exams, ExamQuestions, ExamSubmissions, and ExamAnswers."""
    
    # Wait for the database to be available
    print("⏳ Waiting for DB...")    
    await wait_for_db()
    print("ℹ️ DB is available.")
    
    # Create the database tables
    async with Engine.begin() as conn:
        
        print("ℹ️ Ensuring pgvector extension is installed...")
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS public"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector SCHEMA public"))
        print("✅ pgvector extension verified.")

        # ⚠️ DANGEROUS - deletes all data start
        await conn.run_sync(Base.metadata.drop_all)
        # ⚠️ DANGEROUS - Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created.")
    
    async with AsyncSessionLocal() as db:
        await db.begin()
        print("ℹ️ seeding Roles table...")
        # Roles
        roles = [
            RoleModel(name="Learner"),
            RoleModel(name="Instructor"),
            RoleModel(name="Admin")
        ]
        await seed_table(db, RoleModel, roles)        

        print("ℹ️ seeding Users table...")        
        # Users
        users = [
            # user_id=1 - System user for template courses (visible to all learners)
            UserModel(
                # username="system",
                email="system@fh-swf.de",
                # date_of_birth=date(2000, 1, 1),
                password=pbkdf2_sha256.hash("SystemUser@2025!SecurePassword"),
                role="Instructor",
                full_name="KIKO Platform",
                avatar=default_avatar_for_role("Instructor", "KIKO Platform"),
                # bio="System account for template courses."
            ),
            # user_id=2
            UserModel(
                # username="learner1",
                email="learner1@fh-swf.de",
                # date_of_birth=date(1990, 2, 3),
                password=pbkdf2_sha256.hash("Learner@2025"),
                role="Learner",
                full_name="Sanjay",
                avatar=default_avatar_for_role("Learner", "Sanjay"),
                # bio="Passionate about clean energy."
            ),
            # user_id=3
            UserModel(
                # username="instructor1",
                email="instructor1@tum.de",
                # date_of_birth=date(1978, 2, 10),
                password=pbkdf2_sha256.hash("Instructor@2025"),
                role="Instructor",
                full_name="Dr. Anton",
                avatar=default_avatar_for_role("Instructor", "Dr. Anton"),
                # bio="Experienced Physics, Nuclear, and Reactor."
            ),
            # user_id=4
            UserModel(
                # username="admin1",
                email="admin1@fh-swf.de",
                # date_of_birth=date(1993, 12, 11),
                password=pbkdf2_sha256.hash("Admin@2025"),
                role="Admin",
                full_name="Dr. Thomas Kopinski",
                avatar=default_avatar_for_role("Admin", "Dr. Thomas Kopinski"),
                # bio="System administrator."
            ),
            # user_id=5
            UserModel(
                # username="fusion-student",
                email="fusion-student@fh-swf.de",
                # date_of_birth=date(1990, 2, 3),
                password=pbkdf2_sha256.hash("Student@2026"),
                role="Learner",
                full_name="Fusion Student",
                avatar=default_avatar_for_role("Learner", "Fusion Student"),
                # bio="Passionate about clean energy."
            ),
            # user_id=6
            UserModel(
                # username="fusion-tutor",
                email="fusion-tutor@fh-swf.de",
                # date_of_birth=date(1978, 2, 10),
                password=pbkdf2_sha256.hash("Tutor@2026"),
                role="Instructor",
                full_name="Dr. Anton",
                avatar=default_avatar_for_role("Instructor", "Dr. Anton"),
                # bio="Experienced Physics, Nuclear, and Reactor."
            ),
            # user_id=7
            UserModel(
                # username="education-student",
                email="education-student@fh-swf.de",
                # date_of_birth=date(1990, 2, 3),
                password=pbkdf2_sha256.hash("Student@2026"),
                role="Learner",
                full_name="Education Student",
                avatar=default_avatar_for_role("Learner", "Education Student"),
                # bio="Passionate about clean energy."
            ),
            # user_id=8
            UserModel(
                # username="education-tutor",
                email="education-tutor@fh-swf.de",
                # date_of_birth=date(1978, 2, 10),
                password=pbkdf2_sha256.hash("Tutor@2026"),
                role="Instructor",
                full_name="Dr. Anton",
                avatar=default_avatar_for_role("Instructor", "Dr. Anton"),
                # bio="Experienced Physics, Nuclear, and Reactor."
            ),
            # user_id=9
            # Prof. Dr. Thomas Kopinski - for fusion and smr use-case
            UserModel(
                # username="system",
                email="thomas.kopinski@gmail.com",
                # date_of_birth=date(2000, 1, 1),
                password=pbkdf2_sha256.hash("Thomas@2026!"),
                role="Instructor",
                full_name="Prof. Dr. Thomas Kopinski",
                avatar=default_avatar_for_role("Instructor", "Prof. Dr. Thomas Kopinski"),
                # bio="System account for template courses."
            ),
        ]
        await seed_table(db, UserModel, users)

        print("ℹ️ seeding UserRoles table...")
        # UserRoles
        user_roles = [
            UserRoleModel(user_id=1, role_id=2),  # system - Instructor
            UserRoleModel(user_id=2, role_id=1),  # learner1 - Learner
            UserRoleModel(user_id=3, role_id=2),  # instructor1 - Instructor
            UserRoleModel(user_id=4, role_id=3),  # admin1 - Admin
            UserRoleModel(user_id=5, role_id=1),  # fusion-student - Learner
            UserRoleModel(user_id=6, role_id=2),  # fusion-tutor - Instructor
            UserRoleModel(user_id=7, role_id=1),  # education-student - Learner
            UserRoleModel(user_id=8, role_id=2),  # education-tutor - Instructor
            UserRoleModel(user_id=9, role_id=2)   # Fusion and SMR - Instructor
        ]
        await seed_table(db, UserRoleModel, user_roles)
        
        print("ℹ️ seeding Knowledge Assessment table...")
        # Questions Test knowledge
        questions = [
            KnowledgeAssessmentModel(topic="Grundlagen der Strahlung", question="Welche ionisierende Strahlung hat die größte Durchdringungsfähigkeit in Materie? (α, β, γ, Neutronen)", type="mcq", correct_answer="γ (Gamma)" , created_by=4),
            KnowledgeAssessmentModel(topic="Einheiten und Dosimetrie", question="Die Einheit Sievert (Sv) quantifiziert was?", type="short", correct_answer="Äquivalente/effektive Dosis (biologische Wirkung)" , created_by=4),
            KnowledgeAssessmentModel(topic="Schutzprinzipien", question="Nennen Sie die drei grundlegenden Prinzipien des Strahlenschutzes.", type="short", correct_answer="Zeit, Abstand, Abschirmung" , created_by=4),
            KnowledgeAssessmentModel(topic="Stilllegung Überblick", question="Was ist die Stilllegung eines Kernkraftwerks?", type="short", correct_answer="Administrative und technische Maßnahmen zur Außerbetriebnahme einer Anlage und zur Reduzierung der Reststrahlung auf Freigabe- oder Endzustand." , created_by=4),
            KnowledgeAssessmentModel(topic="Vorschriften", question="Welches Prinzip liegt der Dosisoptimierung bei der Genehmigung zugrunde?", type="mcq", correct_answer="ALARA (As Low As Reasonably Achievable)" , created_by=4),
        ]
        await seed_table(db, KnowledgeAssessmentModel, questions)
        
        await db.commit()
        
        # Create template courses for system user
        print("ℹ️ Creating template courses for system user...")
        system_user = await db.execute(
            select(UserModel).where(UserModel.role == "Instructor")
        )
        system_user = list(system_user.scalars().all())

        for user in system_user:
            print(f"ℹ️ System user found: {user.email}. Creating template courses...")
            await create_template_courses_for_instructor(user.user_id, db)
            print(f"✅ Template courses created for user {user.email}.")
        
        await db.close()
        print("✅ Database seeded successfully.")

if __name__ == "__main__":
    print("ℹ️ Initializing database...")
    asyncio.run(init_db())
    print("Database initialized successfully.")
