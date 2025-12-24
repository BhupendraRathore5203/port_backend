from ninja import Schema, ModelSchema, UploadedFile
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
    
    class Meta:
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
        
        
        
# =========================
# Experience Schemas
# =========================
class ExperienceSchema(Schema):
    id: str
    position: str
    company: str
    company_logo: Optional[str] = None
    company_website: Optional[str] = None
    location: Optional[str] = None
    experience_type: str
    start_date: str
    end_date: Optional[str] = None
    is_current: bool
    description: Optional[str] = None
    responsibilities: List[str] = []
    technologies: List[TechnologySchema] = []
    skills_gained: List[str] = []
    is_featured: bool
    order: int
    
    # Computed fields
    duration: Optional[str] = None
    duration_months: Optional[int] = None
    
    @classmethod
    def from_experience(cls, experience, request=None):
        """Custom method to convert Experience model to schema"""
        if not experience:
            return None
            
        # Get company logo URL
        company_logo_url = None
        if experience.company_logo:
            if request:
                company_logo_url = get_absolute_url(experience.company_logo.url)
            else:
                company_logo_url = experience.company_logo.url
        
        # Convert technologies
        technologies = []
        if hasattr(experience, 'technologies'):
            technologies = [TechnologySchema.from_orm(tech) for tech in experience.technologies.all()]
        
        # Convert dates to strings
        start_date_str = experience.start_date.isoformat() if experience.start_date else None
        end_date_str = experience.end_date.isoformat() if experience.end_date else None
        
        return cls(
            id=str(experience.id),
            position=experience.position,
            company=experience.company,
            company_logo=company_logo_url,
            company_website=experience.company_website,
            location=experience.location,
            experience_type=experience.experience_type,
            start_date=start_date_str,
            end_date=end_date_str,
            is_current=experience.is_current,
            description=experience.description,
            responsibilities=experience.responsibilities if experience.responsibilities else [],
            technologies=technologies,
            skills_gained=experience.skills_gained if experience.skills_gained else [],
            is_featured=experience.is_featured,
            order=experience.order,
            duration=getattr(experience, 'duration', None),
            duration_months=getattr(experience, 'duration_months', None)
        )


class ExperienceCreateSchema(Schema):
    position: str
    company: str
    company_logo: Optional[UploadedFile] = None
    company_website: Optional[str] = None
    location: Optional[str] = None
    experience_type: str
    start_date: str  # Format: YYYY-MM-DD
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    responsibilities: List[str] = []
    technologies: List[str] = []  # List of technology IDs
    skills_gained: List[str] = []
    is_featured: bool = False
    order: int = 0


class ExperienceUpdateSchema(Schema):
    position: Optional[str] = None
    company: Optional[str] = None
    company_logo: Optional[UploadedFile] = None
    company_website: Optional[str] = None
    location: Optional[str] = None
    experience_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: Optional[bool] = None
    description: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    skills_gained: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    order: Optional[int] = None


# =========================
# Education Schemas
# =========================
class EducationSchema(Schema):
    id: str
    institution: str
    institution_logo: Optional[str] = None
    institution_website: Optional[str] = None
    location: Optional[str] = None
    degree: str
    field_of_study: Optional[str] = None
    education_type: str
    start_date: str
    end_date: Optional[str] = None
    is_current: bool
    description: Optional[str] = None
    grade_type: str
    grade_value: Optional[float] = None
    grade_scale: Optional[float] = None
    grade_display: Optional[str] = None
    achievements: List[str] = []
    courses: List[str] = []
    skills_learned: List[str] = []
    thesis_title: Optional[str] = None
    thesis_url: Optional[str] = None
    transcript_url: Optional[str] = None
    is_featured: bool
    order: int
    
    # Computed fields
    duration_years: Optional[int] = None
    formatted_grade: Optional[str] = None
    
    @classmethod
    def from_education(cls, education, request=None):
        """Custom method to convert Education model to schema"""
        if not education:
            return None
            
        # Get institution logo URL
        institution_logo_url = None
        if education.institution_logo:
            if request:
                institution_logo_url = get_absolute_url(education.institution_logo.url)
            else:
                institution_logo_url = education.institution_logo.url
        
        # Convert dates to strings
        start_date_str = education.start_date.isoformat() if education.start_date else None
        end_date_str = education.end_date.isoformat() if education.end_date else None
        
        return cls(
            id=str(education.id),
            institution=education.institution,
            institution_logo=institution_logo_url,
            institution_website=education.institution_website,
            location=education.location,
            degree=education.degree,
            field_of_study=education.field_of_study,
            education_type=education.education_type,
            start_date=start_date_str,
            end_date=end_date_str,
            is_current=education.is_current,
            description=education.description,
            grade_type=education.grade_type,
            grade_value=float(education.grade_value) if education.grade_value else None,
            grade_scale=float(education.grade_scale) if education.grade_scale else None,
            grade_display=education.grade_display,
            achievements=education.achievements if education.achievements else [],
            courses=education.courses if education.courses else [],
            skills_learned=education.skills_learned if education.skills_learned else [],
            thesis_title=education.thesis_title,
            thesis_url=education.thesis_url,
            transcript_url=education.transcript_url,
            is_featured=education.is_featured,
            order=education.order,
            duration_years=getattr(education, 'duration_years', None),
            formatted_grade=getattr(education, 'formatted_grade', None)
        )


class EducationCreateSchema(Schema):
    institution: str
    institution_logo: Optional[UploadedFile] = None
    institution_website: Optional[str] = None
    location: Optional[str] = None
    degree: str
    field_of_study: Optional[str] = None
    education_type: str
    start_date: str  # Format: YYYY-MM-DD
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    grade_type: str = 'none'
    grade_value: Optional[float] = None
    grade_scale: Optional[float] = None
    grade_display: Optional[str] = None
    achievements: List[str] = []
    courses: List[str] = []
    skills_learned: List[str] = []
    thesis_title: Optional[str] = None
    thesis_url: Optional[str] = None
    transcript_url: Optional[str] = None
    is_featured: bool = False
    order: int = 0


class EducationUpdateSchema(Schema):
    institution: Optional[str] = None
    institution_logo: Optional[UploadedFile] = None
    institution_website: Optional[str] = None
    location: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    education_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: Optional[bool] = None
    description: Optional[str] = None
    grade_type: Optional[str] = None
    grade_value: Optional[float] = None
    grade_scale: Optional[float] = None
    grade_display: Optional[str] = None
    achievements: Optional[List[str]] = None
    courses: Optional[List[str]] = None
    skills_learned: Optional[List[str]] = None
    thesis_title: Optional[str] = None
    thesis_url: Optional[str] = None
    transcript_url: Optional[str] = None
    is_featured: Optional[bool] = None
    order: Optional[int] = None



# =========================
# Resume Schemas
# =========================
class ResumeSchema(Schema):
    id: str
    title: str
    file: Optional[str] = None
    file_type: str
    resume_type: str
    language: str
    version: str
    is_primary: bool
    is_public: bool
    last_updated: str
    file_size: int
    download_count: int
    view_count: int
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}
    experiences: List[ExperienceSchema] = []
    education: List[EducationSchema] = []
    projects: List[ProjectSchema] = []
    technologies: List[TechnologySchema] = []
    
    # Computed fields
    file_size_human: Optional[str] = None
    download_url: Optional[str] = None
    preview_url: Optional[str] = None
    
    @classmethod
    def from_resume(cls, resume, request=None):
        """Custom method to convert Resume model to schema"""
        if not resume:
            return None
            
        # Get file URL
        file_url = None
        if resume.file:
            if request:
                file_url = get_absolute_url(resume.file.url)
            else:
                # Fallback if no request context
                file_url = resume.file.url
        
        # Convert experiences
        experiences = []
        if hasattr(resume, 'experiences'):
            experiences = [ExperienceSchema.from_orm(exp) for exp in resume.experiences.all()]
        
        # Convert education
        education = []
        if hasattr(resume, 'education'):
            education = [EducationSchema.from_orm(edu) for edu in resume.education.all()]
        
        # Convert projects
        projects = []
        if hasattr(resume, 'projects'):
            projects = [ProjectSchema.from_orm(proj) for proj in resume.projects.all()]
        
        # Convert technologies
        technologies = []
        if hasattr(resume, 'technologies'):
            technologies = [TechnologySchema.from_orm(tech) for tech in resume.technologies.all()]
        
        return cls(
            id=str(resume.id),
            title=resume.title,
            file=file_url,
            file_type=resume.file_type,
            resume_type=resume.resume_type,
            language=resume.language,
            version=resume.version,
            is_primary=resume.is_primary,
            is_public=resume.is_public,
            last_updated=resume.last_updated.isoformat() if resume.last_updated else None,
            file_size=resume.file_size,
            download_count=resume.download_count,
            view_count=resume.view_count,
            description=resume.description,
            metadata=resume.metadata if resume.metadata else {},
            file_size_human=resume.file_size_human if hasattr(resume, 'file_size_human') else None,
            download_url=resume.download_url if hasattr(resume, 'download_url') else None,
            preview_url=resume.preview_url if hasattr(resume, 'preview_url') else None,
            experiences=experiences,
            education=education,
            projects=projects,
            technologies=technologies
        )

class ResumeCreateSchema(Schema):
    title: str
    file: UploadedFile
    file_type: str = 'pdf'
    resume_type: str = 'current'
    language: str = 'en'
    version: str = '1.0'
    is_primary: bool = False
    is_public: bool = True
    description: Optional[str] = None
    experiences: List[str] = []  # List of experience IDs
    education: List[str] = []  # List of education IDs
    projects: List[str] = []  # List of project IDs
    technologies: List[str] = []  # List of technology IDs


class ResumeUpdateSchema(Schema):
    title: Optional[str] = None
    file: Optional[UploadedFile] = None
    file_type: Optional[str] = None
    resume_type: Optional[str] = None
    language: Optional[str] = None
    version: Optional[str] = None
    is_primary: Optional[bool] = None
    is_public: Optional[bool] = None
    description: Optional[str] = None
    experiences: Optional[List[str]] = None
    education: Optional[List[str]] = None
    projects: Optional[List[str]] = None
    technologies: Optional[List[str]] = None

# =========================
# Filter Schemas for New Models
# =========================
class ExperienceFilterSchema(Schema):
    experience_type: Optional[str] = None
    is_featured: Optional[bool] = None
    is_current: Optional[bool] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 10


class EducationFilterSchema(Schema):
    education_type: Optional[str] = None
    is_featured: Optional[bool] = None
    is_current: Optional[bool] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 10
    
    
    
class HomeDataResponse(Schema):
    stats: StatsResponse
    featured_projects: List[ProjectSchema]
    featured_technologies: List[TechnologySchema]
    recent_projects: List[ProjectSchema]
    content_blocks: List[ContentBlockSchema]
    featured_experiences: List[ExperienceSchema] = []
    featured_education: List[EducationSchema] = []
    primary_resume: Optional[ResumeSchema] = None