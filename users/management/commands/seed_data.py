"""
Management command: seed_data
Creates demo users, projects, and tasks for development.

Usage: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from users.models import User
from projects.models import Project, ProjectMembership, ProjectActivity
from tasks.models import Task
from comments.models import Comment


PROJECTS = [
    {
        'name': 'Website Redesign',
        'description': 'Complete overhaul of the company website with new branding.',
        'status': 'active',
    },
    {
        'name': 'Mobile App v2.0',
        'description': 'Major feature release for the iOS and Android applications.',
        'status': 'active',
    },
    {
        'name': 'Backend API Migration',
        'description': 'Migrate legacy REST API to GraphQL for better performance.',
        'status': 'planning',
    },
    {
        'name': 'Q4 Marketing Campaign',
        'description': 'End-of-year marketing push across all digital channels.',
        'status': 'completed',
    },
]

TASKS = [
    ('Design new homepage mockup', 'Create Figma mockup for the new homepage.', 'high', 'in_progress', 5),
    ('Write API documentation', 'Document all REST endpoints with examples.', 'medium', 'todo', 7),
    ('Fix authentication bug', 'Users are being logged out unexpectedly on mobile.', 'critical', 'in_progress', 1),
    ('Set up CI/CD pipeline', 'Configure GitHub Actions for automated testing and deployment.', 'high', 'completed', -3),
    ('Update privacy policy', 'Ensure compliance with latest GDPR requirements.', 'low', 'todo', 14),
    ('Performance audit', 'Analyse and fix slow database queries.', 'medium', 'review', 3),
    ('User onboarding flow', 'Design and implement new user onboarding screens.', 'high', 'in_progress', 6),
    ('Email notification system', 'Build transactional email templates and delivery pipeline.', 'medium', 'todo', 10),
    ('Write unit tests', 'Increase code coverage to 80%.', 'medium', 'todo', 8),
    ('Accessibility audit', 'WCAG 2.1 AA compliance review.', 'low', 'completed', -5),
    ('Deploy to staging', 'Set up staging environment and deploy latest build.', 'high', 'completed', -2),
    ('Customer feedback analysis', 'Review and categorise last quarter support tickets.', 'low', 'todo', 20),
]


class Command(BaseCommand):
    help = 'Seed the database with demo data'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding demo data...\n')

        # Create Users
        admin = self._create_user('admin', 'Admin', 'User', 'admin@taskhive.com', 'admin123', 'admin', superuser=True)
        manager = self._create_user('varsha', 'Varsha', 'Morthala', 'varsha@taskhive.com', 'demo1234', 'manager')
        dev1 = self._create_user('hima', 'Hima', 'Ballam', 'hima@taskhive.com', 'demo1234', 'member')
        dev2 = self._create_user('sreeja', 'Sreeja', 'Rachuri', 'sreeja@taskhive.com', 'demo1234', 'member')
        dev3 = self._create_user('vyshnavi', 'Vyshnavi', 'Dandu', 'vyshnavi@taskhive.com', 'demo1234', 'member')
        members = [dev1, dev2, dev3]

        today = timezone.now().date()
        projects_created = []

        for i, p_data in enumerate(PROJECTS):
            if Project.objects.filter(name=p_data['name']).exists():
                self.stdout.write(f'  ⏭  Project "{p_data["name"]}" already exists, skipping.')
                continue

            project = Project.objects.create(
                name=p_data['name'],
                description=p_data['description'],
                status=p_data['status'],
                owner=manager,
                start_date=today - timedelta(days=random.randint(10, 60)),
                end_date=today + timedelta(days=random.randint(10, 90)),
            )

            # Add team members
            for member in random.sample(members, k=random.randint(1, 3)):
                ProjectMembership.objects.create(project=project, user=member, role='member')

            ProjectActivity.objects.create(
                project=project, user=manager,
                action=f'Project "{project.name}" was created.'
            )

            projects_created.append(project)
            self.stdout.write(f'  ✅ Created project: {project.name}')

        # Get all projects (including existing)
        all_projects = list(Project.objects.all())
        if not all_projects:
            self.stdout.write(self.style.WARNING('No projects available to add tasks.'))
            return

        tasks_created = 0
        for title, desc, priority, status, days_offset in TASKS:
            if Task.objects.filter(title=title).exists():
                continue
            project = random.choice(all_projects)
            assignee = random.choice(members + [manager])
            deadline = today + timedelta(days=days_offset)

            task = Task.objects.create(
                title=title,
                description=desc,
                project=project,
                assigned_user=assignee,
                created_by=manager,
                priority=priority,
                status=status,
                deadline=deadline,
            )

            ProjectActivity.objects.create(
                project=project, user=manager,
                action=f'Task "{task.title}" was created.'
            )

            # Add a comment to some tasks
            if random.random() > 0.5:
                commenter = random.choice(members)
                Comment.objects.create(
                    task=task,
                    user=commenter,
                    message=random.choice([
                        'Working on this now, should be done by EOD.',
                        'Needs more clarification from the design team.',
                        'Almost done — just need to run final tests.',
                        'Blocked on a dependency, will update soon.',
                        'This is more complex than estimated. Updating the deadline.',
                    ])
                )

            tasks_created += 1

        self.stdout.write(f'  ✅ Created {tasks_created} tasks\n')

        self.stdout.write(self.style.SUCCESS('\n✅ Demo data seeded successfully!\n'))
        self.stdout.write('─' * 50)
        self.stdout.write('Demo accounts:')
        self.stdout.write('  👑 Admin    → username: admin     / password: admin123')
        self.stdout.write('  📋 Manager  → username: varsha     / password: demo1234')
        self.stdout.write('  👤 Member   → username: hima      / password: demo1234')
        self.stdout.write('─' * 50)
        self.stdout.write('Run: python manage.py runserver')

    def _create_user(self, username, first, last, email, password, role, superuser=False):
        if User.objects.filter(username=username).exists():
            self.stdout.write(f'  ⏭  User "{username}" already exists, skipping.')
            return User.objects.get(username=username)
        if superuser:
            user = User.objects.create_superuser(username=username, email=email, password=password)
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first
        user.last_name = last
        user.role = role
        user.save()
        self.stdout.write(f'  ✅ Created user: {username} ({role})')
        return user
