from ninja import Schema, ModelSchema
from typing import Optional, List, Dict, Any
from datetime import date
from pydantic import Field, EmailStr
import uuid
from enum import Enum

from accounts.models import *
from frontpanel.utils import get_absolute_url

# Enums matching models
class TechnologyType(str, Enum):
    LANGUAGE = 'language'
    FRAMEWORK = 'framework'
    TOOL = 'tool'
    DATABASE = 'database'
    SERVICE = 'service'

class ProjectStatus(str, Enum):
    COMPLETED = 'completed'
    IN_PROGRESS = 'in_progress'
    PLANNED = 'planned'
    ARCHIVED = 'archived'

class DemoType(str, Enum):
    LIVE = 'live'
    VIDEO = 'video'
    SCREENSHOT = 'screenshot'
    NONE = 'none'

class MessageStatus(str, Enum):
    NEW = 'new'
    READ = 'read'
    REPLIED = 'replied'
    ARCHIVED = 'archived'


# -------------------- Admin Schemas --------------------

class AdminProfileSchema(ModelSchema):
    class Meta:
        model = AdminUser
        fields = [
            'id', 'username', 'email', 'department',
            'phone_number', 'date_joined', 'last_login',
            'is_super_admin', 'is_active', 'profile_picture',
            'bio', 'social_links'
        ]


class AdminCreateSchema(Schema):
    username: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=10)
    department: Optional[str] = None
    phone_number: Optional[str] = None
    is_super_admin: bool = False


class AdminUpdateSchema(Schema):
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
    is_super_admin: Optional[bool] = None
    is_active: Optional[bool] = None


# -------------------- Technology --------------------

class TechnologySchema(ModelSchema):
    class Meta:
        model = Technology
        fields = [
            'id', 'name', 'slug', 'type', 'category',
            'icon', 'color', 'proficiency', 'description',
            'website_url', 'is_featured', 'order', 'created_at'
        ]


class TechnologyCreateSchema(Schema):
    name: str
    slug: str
    type: TechnologyType
    category: str
    icon: Optional[str] = None
    color: Optional[str] = None
    proficiency: int = Field(50, ge=0, le=100)
    description: Optional[str] = None
    website_url: Optional[str] = None
    is_featured: bool = False
    order: int = 0


# -------------------- Project Category --------------------

class ProjectCategorySchema(ModelSchema):
    class Meta:
        model = ProjectCategory
        fields = [
            'id', 'name', 'slug', 'description',
            'icon', 'color', 'order', 'created_at'
        ]

class ImagesSchema(ModelSchema):
    class Meta:
        model = ProjectImage
        fields = [
            "id", "image", "caption", "order"
        ]
            


# -------------------- Project --------------------

class ProjectSchema(ModelSchema):
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'short_description', 'long_description',
            'status', 'demo_type', 'demo_url', 'github_url', 'documentation_url',
            'featured_image', 'tags', 'features', 'installation_guide',
            'is_featured', 'is_public', 'order', 'start_date', 'completion_date',
            'created_at', 'updated_at'
        ]
    
    category: Optional[ProjectCategorySchema] = None
    technologies: List[TechnologySchema] = []
    images: List[ImagesSchema] = None 
    


class ProjectCreateSchema(Schema):
    title: str
    slug: str
    short_description: str
    long_description: str
    category_id: Optional[uuid.UUID] = None
    status: ProjectStatus = ProjectStatus.COMPLETED
    demo_type: DemoType = DemoType.NONE
    demo_url: Optional[str] = None
    github_url: Optional[str] = None
    documentation_url: Optional[str] = None
    tags: List[str] = []
    features: List[str] = []
    installation_guide: Optional[str] = None
    is_featured: bool = False
    is_public: bool = True
    order: int = 0
    start_date: Optional[date] = None
    completion_date: Optional[date] = None
    technology_ids: List[uuid.UUID] = []


class ProjectUpdateSchema(Schema):
    title: Optional[str] = None
    slug: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    status: Optional[ProjectStatus] = None
    demo_type: Optional[DemoType] = None
    demo_url: Optional[str] = None
    github_url: Optional[str] = None
    documentation_url: Optional[str] = None
    tags: Optional[List[str]] = None
    features: Optional[List[str]] = None
    installation_guide: Optional[str] = None
    is_featured: Optional[bool] = None
    is_public: Optional[bool] = None
    order: Optional[int] = None
    start_date: Optional[date] = None
    completion_date: Optional[date] = None
    technology_ids: Optional[List[uuid.UUID]] = None


# -------------------- Images / Demo / Contact --------------------

class ProjectImageSchema(ModelSchema):
    class Meta:
        model = ProjectImage
        fields = ['id', 'image', 'caption', 'order', 'created_at']


class DemoInstanceSchema(ModelSchema):
    class Meta:
        model = DemoInstance
        fields = [
            'id', 'status', 'instance_url', 'is_public',
            'max_users', 'last_checked', 'created_at'
        ]

    project: ProjectSchema


class ContactMessageSchema(ModelSchema):
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'name', 'email', 'subject', 'message',
            'status', 'is_spam', 'created_at', 'updated_at'
        ]


class ContactMessageCreateSchema(Schema):
    name: str
    email: EmailStr
    subject: str
    message: str


# -------------------- Simple Models --------------------

class SiteSettingsSchema(ModelSchema):
    class Meta:
        model = SiteSettings
        fields = "__all__"


class ContentBlockSchema(ModelSchema):
    class Meta:
        model = ContentBlock
        fields = "__all__"


class TestimonialSchema(ModelSchema):
    class Meta:
        model = Testimonial
        fields = [
            'id', 'client_name', 'client_role', 'client_image',
            'content', 'rating', 'is_featured', 'is_approved',
            'order', 'created_at'
        ]


class CodeSnippetSchema(ModelSchema):
    class Meta:
        model = CodeSnippet
        fields = "__all__"


# -------------------- Filters / Responses --------------------

class ProjectFilterSchema(Schema):
    category: Optional[str] = None
    technology: Optional[str] = None
    status: Optional[ProjectStatus] = None
    featured: Optional[bool] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 12


class TechnologyFilterSchema(Schema):
    category: Optional[str] = None
    type: Optional[TechnologyType] = None
    featured: Optional[bool] = None
    search: Optional[str] = None


class PaginatedResponse(Schema):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


class StatsResponse(Schema):
    total_projects: int
    total_technologies: int
    total_demos: int
    total_messages: int
    featured_projects: int
    featured_technologies: int


class HomeDataResponse(Schema):
    stats: StatsResponse
    featured_projects: List[ProjectSchema]
    featured_technologies: List[TechnologySchema]
    recent_projects: List[ProjectSchema]
    content_blocks: List[ContentBlockSchema]


class ErrorResponse(Schema):
    detail: str


class ValidationErrorResponse(Schema):
    detail: List[Dict[str, Any]]


class NotFoundResponse(Schema):
    detail: str = "Resource not found"



# Add this to your existing schemas

class SocialLinksSchema(Schema):
    github: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    youtube: Optional[str] = None
    discord: Optional[str] = None

class SiteSettingsPublicSchema(Schema):
    """Public schema for site settings (excludes sensitive data)"""
    site_name: str
    site_tagline: str
    contact_email: str
    logo: Optional[str] = None
    favicon: Optional[str] = None
    self_description : Optional[str] 
    self_long_description : Optional[str]
    primary_color: str = "#3b82f6"
    secondary_color: str = "#8b5cf6"
    dark_mode: bool = True
    social_links: Optional[SocialLinksSchema] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    maintenance_mode: bool = False
    maintenance_message: Optional[str] = None

class SiteSettingsUpdateSchema(Schema):
    """Schema for updating site settings (admin only)"""
    site_name: Optional[str] = None
    site_tagline: Optional[str] = None
    admin_email: Optional[str] = None
    contact_email: Optional[str] = None
    self_description: Optional[str] 
    self_long_description: Optional[str]
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    dark_mode: Optional[bool] = None
    social_links: Optional[SocialLinksSchema] = None
    analytics_code: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    maintenance_mode: Optional[bool] = None
    maintenance_message: Optional[str] = None
    
    
    
    
class RotatingTextSchema(Schema):
    """Schema for rotating text data"""
    id: int
    text: str
    text_type: str
    order: int
    delay_seconds: float
    typing_speed: int
    is_active: bool
    
    class Config:
        from_attributes = True

class RotatingTextCreateSchema(Schema):
    """Schema for creating rotating text"""
    text: str = Field(..., min_length=2, max_length=200)
    text_type: str = Field(default="hero", pattern="^(hero|tagline|achievement|feature)$")
    order: int = Field(default=0, ge=0)
    is_active: bool = True
    delay_seconds: float = Field(default=2.0, gt=0)
    typing_speed: int = Field(default=100, ge=50, le=1000)

class RotatingTextUpdateSchema(Schema):
    """Schema for updating rotating text"""
    text: Optional[str] = Field(None, min_length=2, max_length=200)
    text_type: Optional[str] = Field(None, pattern="^(hero|tagline|achievement|feature)$")
    order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    delay_seconds: Optional[float] = Field(None, gt=0)
    typing_speed: Optional[int] = Field(None, ge=50, le=1000)

class RotatingTextResponse(Schema):
    """Response schema with typed texts"""
    hero_texts: List[str]
    taglines: List[str]
    achievements: List[str]
    features: List[str]
    typing_speed: int = 100
    delay_seconds: float = 2.0
    
    @classmethod
    def from_queryset(cls, texts):
        """Create response from queryset"""
        hero = []
        taglines = []
        achievements = []
        features = []
        
        # Get average typing speed and delay from hero texts
        hero_texts = texts.filter(text_type='hero', is_active=True).order_by('order')
        
        for text in texts:
            if text.is_active:
                data = {
                    'text': text.text,
                    'delay': text.delay_seconds,
                    'speed': text.typing_speed
                }
                
                if text.text_type == 'hero':
                    hero.append(data)
                elif text.text_type == 'tagline':
                    taglines.append(data)
                elif text.text_type == 'achievement':
                    achievements.append(data)
                elif text.text_type == 'feature':
                    features.append(data)
        
        return cls(
            hero_texts=[item['text'] for item in sorted(hero, key=lambda x: x.get('order', 0))],
            taglines=[item['text'] for item in sorted(taglines, key=lambda x: x.get('order', 0))],
            achievements=[item['text'] for item in sorted(achievements, key=lambda x: x.get('order', 0))],
            features=[item['text'] for item in sorted(features, key=lambda x: x.get('order', 0))],
            typing_speed=hero_texts[0].typing_speed if hero_texts.exists() else 100,
            delay_seconds=hero_texts[0].delay_seconds if hero_texts.exists() else 2.0
        )