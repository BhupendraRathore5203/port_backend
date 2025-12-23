from django.core.management.base import BaseCommand
from accounts.models import (
    Technology, ProjectCategory, SiteSettings, ContentBlock
)
from django.contrib.auth import get_user_model
import uuid

class Command(BaseCommand):
    help = 'Initialize portfolio with default data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Initializing portfolio data...')
        
        # Create super admin
        AdminUser = get_user_model()
        if not AdminUser.objects.filter(username='admin').exists():
            AdminUser.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                is_superuser=True,
                is_super_admin=True,
                department='IT'
            )
            self.stdout.write(self.style.SUCCESS('Created super admin user'))
        
        # Create default technologies
        technologies = [
            {
                'name': 'Python',
                'slug': 'python',
                'type': Technology.TechnologyType.LANGUAGE,
                'category': 'Backend',
                'icon': '🐍',
                'color': 'from-yellow-500 to-orange-500',
                'proficiency': 95,
                'description': 'Versatile programming language for web development, data science, and automation.',
                'website_url': 'https://python.org',
                'is_featured': True,
                'order': 1
            },
            {
                'name': 'Django',
                'slug': 'django',
                'type': Technology.TechnologyType.FRAMEWORK,
                'category': 'Backend',
                'icon': '🎸',
                'color': 'from-green-600 to-emerald-500',
                'proficiency': 90,
                'description': 'High-level Python web framework for rapid development.',
                'website_url': 'https://djangoproject.com',
                'is_featured': True,
                'order': 2
            },
            {
                'name': 'React',
                'slug': 'react',
                'type': Technology.TechnologyType.FRAMEWORK,
                'category': 'Frontend',
                'icon': '⚛️',
                'color': 'from-blue-500 to-cyan-500',
                'proficiency': 85,
                'description': 'JavaScript library for building user interfaces.',
                'website_url': 'https://reactjs.org',
                'is_featured': True,
                'order': 3
            },
            {
                'name': 'JavaScript',
                'slug': 'javascript',
                'type': Technology.TechnologyType.LANGUAGE,
                'category': 'Frontend',
                'icon': '📜',
                'color': 'from-yellow-400 to-amber-500',
                'proficiency': 88,
                'description': 'Programming language for interactive web applications.',
                'website_url': 'https://javascript.com',
                'is_featured': True,
                'order': 4
            },
            {
                'name': 'MySQL',
                'slug': 'mysql',
                'type': Technology.TechnologyType.DATABASE,
                'category': 'Database',
                'icon': '🐬',
                'color': 'from-orange-500 to-amber-500',
                'proficiency': 80,
                'description': 'Popular open-source relational database.',
                'website_url': 'https://mysql.com',
                'is_featured': True,
                'order': 5
            },
        ]
        
        for tech_data in technologies:
            Technology.objects.get_or_create(
                slug=tech_data['slug'],
                defaults=tech_data
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(technologies)} technologies'))
        
        # Create default categories
        categories = [
            {'name': 'Web Applications', 'slug': 'web-apps', 'order': 1},
            {'name': 'APIs', 'slug': 'apis', 'order': 2},
            {'name': 'Machine Learning', 'slug': 'ml', 'order': 3},
            {'name': 'Mobile Apps', 'slug': 'mobile', 'order': 4},
            {'name': 'DevOps', 'slug': 'devops', 'order': 5},
        ]
        
        for cat_data in categories:
            ProjectCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))
        
        # Create site settings
        SiteSettings.objects.get_or_create(
            defaults={
                'site_name': 'DevPortfolio',
                'site_tagline': 'Multi-Language Portfolio',
                'admin_email': 'admin@example.com',
                'contact_email': 'contact@example.com',
                'primary_color': '#3b82f6',
                'secondary_color': '#8b5cf6',
                'dark_mode': True,
                'social_links': {
                    'github': 'https://github.com',
                    'linkedin': 'https://linkedin.com',
                    'twitter': 'https://twitter.com',
                }
            }
        )
        
        # Create content blocks
        content_blocks = [
            {
                'block_type': 'hero',
                'title': 'Welcome to My Portfolio',
                'content': 'Showcasing amazing projects across multiple technologies and frameworks.',
                'button_text': 'View Projects',
                'button_url': '/projects',
                'is_active': True,
                'order': 1
            },
            {
                'block_type': 'features',
                'title': 'Portfolio Features',
                'content': 'Interactive showcase of all my work with live demos and detailed documentation.',
                'is_active': True,
                'order': 2
            },
        ]
        
        for block_data in content_blocks:
            ContentBlock.objects.get_or_create(
                block_type=block_data['block_type'],
                defaults=block_data
            )
        
        self.stdout.write(self.style.SUCCESS('Portfolio initialized successfully!'))