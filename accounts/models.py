from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
import uuid
from django.core.exceptions import ValidationError
from django.utils import timezone
from ckeditor.fields import RichTextField




class AdminUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_super_admin", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(username, email, password, **extra_fields)








class AdminUser(AbstractUser):
    """
    Custom User model for Admin-only system.
    Extends Django's AbstractUser to add admin-specific fields.
    """
    
    # Remove unwanted fields from AbstractUser
    first_name = None
    last_name = None
    
    # Custom fields for admin users
    admin_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_("Admin ID")
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        verbose_name=_("Phone Number")
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Department"),
        help_text=_("Department/Division the admin belongs to")
    )
    
    is_super_admin = models.BooleanField(
        default=False,
        verbose_name=_("Super Admin"),
        help_text=_("Designates whether this admin has all permissions")
    )
    
    last_login_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name=_("Last Login IP")
    )
    
    # Override email to make it required and unique
    email = models.EmailField(
        _("Email Address"),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        }
    )
    
    profile_picture = models.ImageField(
        upload_to='admin_profiles/',
        blank=True,
        null=True,
        verbose_name=_("Profile Picture")
    )
    
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Bio"),
        max_length=500
    )
    
    social_links = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Social Links"),
        help_text=_("JSON object containing social media links")
    )
    
    # Add custom permissions for admin roles
    class Meta:
        verbose_name = _("Admin User")
        verbose_name_plural = _("Admin Users")
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    def get_full_name(self):
        """Return the username since we removed first/last names"""
        return self.username
    
    def get_short_name(self):
        """Return the username"""
        return self.username
    
    # @property
    # def is_admin(self):
    #     """All users in this model are admins by default"""
    #     return True
    
    # @property
    # def is_staff(self):
    #     """All admin users are staff"""
    #     return True
    
    def save(self, *args, **kwargs):
        """Override save to ensure all users are staff and superuser if is_super_admin"""
        self.is_staff = True
        if self.is_super_admin:
            self.is_superuser = True
        else:
            self.is_superuser = False
        super().save(*args, **kwargs)





class RotatingText(models.Model):
    """Model to store rotating text entries for the portfolio hero section"""
    
    TEXT_TYPES = [
        ('hero', 'Hero Section Typing Text'),
        ('tagline', 'Tagline/Subtitle'),
        ('achievement', 'Achievement/Stat'),
        ('feature', 'Feature Highlight'),
    ]
    
    text = models.CharField(
        max_length=200,
        help_text="Text to display in the typing animation (e.g., 'Python Developer')"
    )
    
    text_type = models.CharField(
        max_length=20,
        choices=TEXT_TYPES,
        default='hero',
        help_text="Where this text will be used"
    )
    
    order = models.IntegerField(
        default=0,
        help_text="Order in which texts appear (lower numbers first)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this text should be displayed"
    )
    
    delay_seconds = models.FloatField(
        default=2.0,
        help_text="How long to display this text before switching (in seconds)"
    )
    
    typing_speed = models.IntegerField(
        default=100,
        help_text="Typing speed in milliseconds per character"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Rotating Text"
        verbose_name_plural = "Rotating Texts"
        ordering = ['text_type', 'order', 'created_at']
        indexes = [
            models.Index(fields=['text_type', 'is_active', 'order']),
        ]
    
    def clean(self):
        """Validate the model data"""
        if not self.text.strip():
            raise ValidationError("Text cannot be empty")
        
        if self.delay_seconds < 0.5:
            raise ValidationError("Delay should be at least 0.5 seconds")
        
        if self.typing_speed < 50:
            raise ValidationError("Typing speed should be at least 50ms per character")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.text} ({self.get_text_type_display()})"






class Technology(models.Model):
    """
    Model for programming languages, frameworks, and tools
    """
    class TechnologyType(models.TextChoices):
        LANGUAGE = 'language', _('Programming Language')
        FRAMEWORK = 'framework', _('Framework/Library')
        TOOL = 'tool', _('Tool/Platform')
        DATABASE = 'database', _('Database')
        SERVICE = 'service', _('Cloud Service')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Technology Name")
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name=_("URL Slug")
    )
    type = models.CharField(
        max_length=20,
        choices=TechnologyType.choices,
        verbose_name=_("Technology Type")
    )
    category = models.CharField(
        max_length=50,
        verbose_name=_("Category"),
        help_text=_("e.g., Frontend, Backend, DevOps")
    )
    icon = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("SVG Code of icon"),
        help_text=_("SVG Code of icon for display")
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Color Theme"),
        help_text=_("Tailwind CSS color classes")
    )
    proficiency = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=50,
        verbose_name=_("Proficiency Level"),
        help_text=_("0-100 percentage")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description")
    )
    website_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Official Website")
    )
    documentation_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Documentation URL")
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Featured Technology")
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_("Display Order")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Technology")
        verbose_name_plural = _("Technologies")
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class ProjectCategory(models.Model):
    """
    Model for project categories
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Category Name")
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name=_("URL Slug")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description")
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Icon")
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Color Theme")
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_("Display Order")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Project Category")
        verbose_name_plural = _("Project Categories")
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Project(models.Model):
    """
    Model for portfolio projects
    """
    class ProjectStatus(models.TextChoices):
        COMPLETED = 'completed', _('Completed')
        IN_PROGRESS = 'in_progress', _('In Progress')
        PLANNED = 'planned', _('Planned')
        ARCHIVED = 'archived', _('Archived')
    
    class DemoType(models.TextChoices):
        LIVE = 'live', _('Live Demo')
        VIDEO = 'video', _('Video Demo')
        SCREENSHOT = 'screenshot', _('Screenshots Only')
        NONE = 'none', _('No Demo')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("Project Title")
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name=_("URL Slug")
    )
    short_description = models.CharField(
        max_length=300,
        verbose_name=_("Short Description")
    )
    long_description = RichTextField(
        verbose_name=_("Detailed Description"),
        config_name='default'
    )
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
        verbose_name=_("Category")
    )
    status = models.CharField(
        max_length=20,
        choices=ProjectStatus.choices,
        default=ProjectStatus.COMPLETED,
        verbose_name=_("Project Status")
    )
    demo_type = models.CharField(
        max_length=20,
        choices=DemoType.choices,
        default=DemoType.NONE,
        verbose_name=_("Demo Type")
    )
    demo_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Demo URL")
    )
    github_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("GitHub Repository URL")
    )
    documentation_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Documentation URL")
    )
    featured_image = models.ImageField(
        upload_to='projects/featured/',
        blank=True,
        null=True,
        verbose_name=_("Featured Image")
    )
    technologies = models.ManyToManyField(
        Technology,
        related_name='projects',
        verbose_name=_("Technologies Used"),
        blank=True
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Tags"),
        help_text=_("List of tags for filtering")
    )
    features = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Features List"),
        help_text=_("List of key features")
    )
    installation_guide = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Installation Guide")
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Featured Project")
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name=_("Publicly Visible")
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_("Display Order")
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Start Date")
    )
    completion_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Completion Date")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title
    
    def clean(self):
        """Validate project dates"""
        if self.start_date and self.completion_date:
            if self.start_date > self.completion_date:
                raise ValidationError(_("Start date cannot be after completion date."))
    
    @property
    def duration_days(self):
        """Calculate project duration in days"""
        if self.start_date and self.completion_date:
            return (self.completion_date - self.start_date).days
        return None


class ProjectImage(models.Model):
    """
    Model for project screenshots/images
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_("Project")
    )
    image = models.ImageField(
        upload_to='projects/screenshots/',
        verbose_name=_("Image")
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Caption")
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_("Display Order")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Project Image")
        verbose_name_plural = _("Project Images")
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.project.title} - Image {self.order}"


class DemoInstance(models.Model):
    """
    Model for live demo instances
    """
    class DemoStatus(models.TextChoices):
        ONLINE = 'online', _('Online')
        OFFLINE = 'offline', _('Offline')
        MAINTENANCE = 'maintenance', _('Under Maintenance')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='demo_instance',
        verbose_name=_("Project")
    )
    status = models.CharField(
        max_length=20,
        choices=DemoStatus.choices,
        default=DemoStatus.ONLINE,
        verbose_name=_("Demo Status")
    )
    instance_url = models.URLField(
        verbose_name=_("Instance URL")
    )
    admin_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Admin URL")
    )
    admin_username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Admin Username")
    )
    admin_password = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Admin Password")
    )
    container_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Container ID")
    )
    last_checked = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Last Status Check")
    )
    check_interval = models.IntegerField(
        default=300,
        verbose_name=_("Status Check Interval (seconds)")
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name=_("Public Demo")
    )
    max_users = models.IntegerField(
        default=10,
        verbose_name=_("Maximum Concurrent Users")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Demo Instance")
        verbose_name_plural = _("Demo Instances")
    
    def __str__(self):
        return f"Demo: {self.project.title}"


class DemoStat(models.Model):
    """
    Model for demo usage statistics
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    demo = models.ForeignKey(
        DemoInstance,
        on_delete=models.CASCADE,
        related_name='stats',
        verbose_name=_("Demo")
    )
    session_id = models.CharField(
        max_length=100,
        verbose_name=_("Session ID")
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name=_("IP Address")
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("User Agent")
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("End Time")
    )
    duration = models.IntegerField(
        default=0,
        verbose_name=_("Duration (seconds)")
    )
    actions_count = models.IntegerField(
        default=0,
        verbose_name=_("Actions Performed")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Demo Stat")
        verbose_name_plural = _("Demo Stats")
    
    def save(self, *args, **kwargs):
        """Calculate duration when ending session"""
        if self.end_time:
            self.duration = (self.end_time - self.start_time).seconds
        super().save(*args, **kwargs)


class ContactMessage(models.Model):
    """
    Model for contact form messages
    """
    class MessageStatus(models.TextChoices):
        NEW = 'new', _('New')
        READ = 'read', _('Read')
        REPLIED = 'replied', _('Replied')
        ARCHIVED = 'archived', _('Archived')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Name")
    )
    email = models.EmailField(
        verbose_name=_("Email")
    )
    subject = models.CharField(
        max_length=200,
        verbose_name=_("Subject")
    )
    message = models.TextField(
        verbose_name=_("Message")
    )
    status = models.CharField(
        max_length=20,
        choices=MessageStatus.choices,
        default=MessageStatus.NEW,
        verbose_name=_("Status")
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name=_("IP Address")
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("User Agent")
    )
    is_spam = models.BooleanField(
        default=False,
        verbose_name=_("Marked as Spam")
    )
    admin_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Admin Notes")
    )
    replied_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Replied At")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Contact Message")
        verbose_name_plural = _("Contact Messages")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class SiteSettings(models.Model):
    """
    Model for site-wide settings
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    site_name = models.CharField(
        max_length=100,
        default="DevPortfolio",
        verbose_name=_("Site Name")
    )
    site_tagline = models.CharField(
        max_length=200,
        default="Multi-Language Portfolio",
        verbose_name=_("Site Tagline")
    )
    admin_email = models.EmailField(
        default="admin@example.com",
        verbose_name=_("Admin Email")
    )
    contact_email = models.EmailField(
        default="contact@example.com",
        verbose_name=_("Contact Email")
    )
    logo = models.ImageField(
        upload_to='site/',
        blank=True,
        null=True,
        verbose_name=_("Logo")
    )
    favicon = models.ImageField(
        upload_to='site/',
        blank=True,
        null=True,
        verbose_name=_("Favicon")
    )
    
    self_description = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name=_("Self Description")
    )
    self_long_description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Self Long Description")
    )
    primary_color = models.CharField(
        max_length=50,
        default="#3b82f6",
        verbose_name=_("Primary Color")
    )
    secondary_color = models.CharField(
        max_length=50,
        default="#8b5cf6",
        verbose_name=_("Secondary Color")
    )
    dark_mode = models.BooleanField(
        default=True,
        verbose_name=_("Enable Dark Mode")
    )
    social_links = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Social Links")
    )
    analytics_code = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Analytics Code")
    )
    seo_description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("SEO Description")
    )
    seo_keywords = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("SEO Keywords")
    )
    maintenance_mode = models.BooleanField(
        default=False,
        verbose_name=_("Maintenance Mode")
    )
    maintenance_message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Maintenance Message")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Site Settings")
        verbose_name_plural = _("Site Settings")
    
    def __str__(self):
        return "Site Settings"
    
    def save(self, *args, **kwargs):
        """Ensure only one settings instance exists"""
        self.__class__.objects.exclude(id=self.id).delete()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_settings(cls):
        """Get or create the active site settings instance"""
        settings, created = cls.objects.get_or_create()
        return settings


class VisitorAnalytics(models.Model):
    """
    Model for tracking website visitors
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    session_id = models.CharField(
        max_length=100,
        verbose_name=_("Session ID")
    )
    ip_address = models.GenericIPAddressField(
        verbose_name=_("IP Address")
    )
    user_agent = models.TextField(
        verbose_name=_("User Agent")
    )
    referrer = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Referrer URL")
    )
    page_visited = models.CharField(
        max_length=200,
        verbose_name=_("Page Visited")
    )
    time_on_page = models.IntegerField(
        default=0,
        verbose_name=_("Time on Page (seconds)")
    )
    is_bounce = models.BooleanField(
        default=True,
        verbose_name=_("Is Bounce")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Visitor Analytic")
        verbose_name_plural = _("Visitor Analytics")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.ip_address} - {self.page_visited}"


class ContentBlock(models.Model):
    """
    Model for reusable content blocks (hero section, about, etc.)
    """
    class BlockType(models.TextChoices):
        HERO = 'hero', _('Hero Section')
        ABOUT = 'about', _('About Section')
        FEATURES = 'features', _('Features Section')
        TESTIMONIALS = 'testimonials', _('Testimonials')
        CTA = 'cta', _('Call to Action')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    block_type = models.CharField(
        max_length=50,
        choices=BlockType.choices,
        verbose_name=_("Block Type")
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Title")
    )
    content = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Content")
    )
    image = models.ImageField(
        upload_to='content/',
        blank=True,
        null=True,
        verbose_name=_("Image")
    )
    button_text = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Button Text")
    )
    button_url = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Button URL")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active")
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_("Display Order")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Content Block")
        verbose_name_plural = _("Content Blocks")
        ordering = ['order', 'block_type']
    
    def __str__(self):
        return f"{self.get_block_type_display()} - {self.title or 'No Title'}"


class Testimonial(models.Model):
    """
    Model for testimonials/reviews
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    client_name = models.CharField(
        max_length=100,
        verbose_name=_("Client Name")
    )
    client_role = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Client Role/Company")
    )
    client_image = models.ImageField(
        upload_to='testimonials/',
        blank=True,
        null=True,
        verbose_name=_("Client Image")
    )
    content = models.TextField(
        verbose_name=_("Testimonial Content")
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5,
        verbose_name=_("Rating (1-5)")
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='testimonials',
        verbose_name=_("Related Project")
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Featured Testimonial")
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_("Approved for Display")
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_("Display Order")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Testimonial")
        verbose_name_plural = _("Testimonials")
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.client_name} - {self.rating}★"


class CodeSnippet(models.Model):
    """
    Model for storing code snippets/examples
    """
    class Language(models.TextChoices):
        PYTHON = 'python', _('Python')
        JAVASCRIPT = 'javascript', _('JavaScript')
        JAVA = 'java', _('Java')
        HTML = 'html', _('HTML')
        CSS = 'css', _('CSS')
        SQL = 'sql', _('SQL')
        BASH = 'bash', _('Bash/Shell')
        OTHER = 'other', _('Other')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("Snippet Title")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description")
    )
    language = models.CharField(
        max_length=20,
        choices=Language.choices,
        verbose_name=_("Programming Language")
    )
    code = models.TextField(
        verbose_name=_("Code Content")
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='code_snippets',
        verbose_name=_("Project")
    )
    file_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("File Name")
    )
    line_count = models.IntegerField(
        default=0,
        verbose_name=_("Line Count")
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name=_("Public Snippet")
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_("Display Order")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Code Snippet")
        verbose_name_plural = _("Code Snippets")
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_language_display()})"
    
    def save(self, *args, **kwargs):
        """Calculate line count automatically"""
        self.line_count = self.code.count('\n') + 1
        super().save(*args, **kwargs)