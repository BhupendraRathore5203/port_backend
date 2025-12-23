from ninja_extra import api_controller, route, ControllerBase, paginate
from ninja_extra.permissions import IsAuthenticated, IsAdminUser, AllowAny
from ninja_extra.schemas import NinjaPaginationResponseSchema
from ninja_jwt.authentication import JWTAuth
from ninja import Query, Form, File, UploadedFile
from ninja.files import UploadedFile as NinjaUploadedFile
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.db import transaction
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta

from accounts.models import (
    AdminUser,
    RotatingText,
    Technology,
    Project,
    ProjectCategory,
    DemoInstance,
    ContactMessage,
    SiteSettings,
    ContentBlock,
    Testimonial,
    CodeSnippet,
    ProjectImage,
    VisitorAnalytics,
)
from frontpanel.schemas import (
    # Admin schemas
    AdminProfileSchema,
    AdminUpdateSchema,
    AdminCreateSchema,
    RotatingTextCreateSchema,
    RotatingTextResponse,
    RotatingTextSchema,
    SiteSettingsPublicSchema,
    SocialLinksSchema,
    # Technology schemas
    TechnologySchema,
    TechnologyCreateSchema,
    # Project schemas
    ProjectSchema,
    ProjectCreateSchema,
    ProjectUpdateSchema,
    ProjectCategorySchema,
    # Demo schemas
    DemoInstanceSchema,
    # Contact schemas
    ContactMessageSchema,
    ContactMessageCreateSchema,
    # Site schemas
    SiteSettingsSchema,
    # Content schemas
    ContentBlockSchema,
    # Testimonial schemas
    TestimonialSchema,
    # Code schemas
    CodeSnippetSchema,
    # Filter schemas
    ProjectFilterSchema,
    TechnologyFilterSchema,
    # Response schemas
    PaginatedResponse,
    StatsResponse,
    HomeDataResponse,
    # Error schemas
    ErrorResponse,
    ValidationErrorResponse,
    NotFoundResponse,
)
from frontpanel.utils import get_absolute_url
from my_port import settings


# Public API Controllers
@api_controller("/public", tags=["Public"], auth=None, permissions=[AllowAny])
class PublicController:
    """Public endpoints accessible to everyone"""

    @route.get("/home", response=HomeDataResponse)
    def get_home_data(self):
        """Get homepage data"""
        stats = StatsResponse(
            total_projects=Project.objects.filter(is_public=True).count(),
            total_technologies=Technology.objects.count(),
            total_demos=DemoInstance.objects.filter(
                is_public=True, status="online"
            ).count(),
            total_messages=0,  # Not public
            featured_projects=Project.objects.filter(
                is_featured=True, is_public=True
            ).count(),
            featured_technologies=Technology.objects.filter(is_featured=True).count(),
        )

        featured_projects = Project.objects.filter(
            is_featured=True, is_public=True
        ).order_by("order")[:6]

        featured_technologies = Technology.objects.filter(is_featured=True).order_by(
            "order"
        )[:8]

        recent_projects = Project.objects.filter(is_public=True).order_by(
            "-created_at"
        )[:4]

        content_blocks = ContentBlock.objects.filter(is_active=True).order_by("order")

        return HomeDataResponse(
            stats=stats,
            featured_projects=[ProjectSchema.from_orm(p) for p in featured_projects],
            featured_technologies=[
                TechnologySchema.from_orm(t) for t in featured_technologies
            ],
            recent_projects=[ProjectSchema.from_orm(p) for p in recent_projects],
            content_blocks=[ContentBlockSchema.from_orm(c) for c in content_blocks],
        )


    @route.get("/projects", response=PaginatedResponse)
    def get_projects(self, request, filters: ProjectFilterSchema = Query(...)):
        """Get paginated projects with filtering"""
        queryset = Project.objects.filter(is_public=True)

        # Apply filters
        if filters.category:
            queryset = queryset.filter(category__slug=filters.category)

        if filters.technology:
            queryset = queryset.filter(technologies__slug=filters.technology)

        if filters.status:
            queryset = queryset.filter(status=filters.status)

        if filters.featured is not None:
            queryset = queryset.filter(is_featured=filters.featured)

        if filters.search:
            queryset = queryset.filter(
                Q(title__icontains=filters.search)
                | Q(short_description__icontains=filters.search)
                | Q(tags__contains=[filters.search])
            )

        # Pagination
        paginator = Paginator(queryset.order_by("order", "-created_at"), filters.page_size)
        page_obj = paginator.get_page(filters.page)

        projects_data = []
        for project in page_obj.object_list:
            project_dict = ProjectSchema.from_orm(project).dict()

            # Get absolute URLs for images
            if project.featured_image:
                project_dict["featured_image"] = get_absolute_url(
                    project.featured_image.url
                )

            project_dict["technologies"] = [
                TechnologySchema.from_orm(t).dict() for t in project.technologies.all()
            ]

            if project.category:
                project_dict["category"] = ProjectCategorySchema.from_orm(
                    project.category
                ).dict()

            projects_data.append(project_dict)

        return PaginatedResponse(
            items=projects_data,
            total=paginator.count,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=paginator.num_pages,
            has_next=page_obj.has_next(),
            has_previous=page_obj.has_previous(),
        )

    @route.get("/projects/{project_slug}", response={200: ProjectSchema, 404: NotFoundResponse})
    def get_project_detail(self, request, project_slug: str):
        """Get single project by slug"""
        project = get_object_or_404(Project, slug=project_slug, is_public=True)

        # Add related data
        project_data = ProjectSchema.from_orm(project).dict()
        
        # Ensure featured_image has absolute URL
        if project.featured_image:
            project_data["featured_image"] = get_absolute_url(project.featured_image.url)
        
        project_data["technologies"] = [
            TechnologySchema.from_orm(t).dict() for t in project.technologies.all()
        ]
        
        if project.category:
            project_data["category"] = ProjectCategorySchema.from_orm(
                project.category
            ).dict()

        # Get absolute URLs for all project images
        project_data["images"] = [
            {
                "id": str(img.id),
                "image": get_absolute_url(img.image.url),
                "caption": img.caption,
                "order": img.order
            }
            for img in ProjectImage.objects.filter(project=project).order_by('order')
        ]

        if hasattr(project, "demo_instance"):
            project_data["demo_instance"] = DemoInstanceSchema.from_orm(
                project.demo_instance
            ).dict()

        project_data["code_snippets"] = [
            CodeSnippetSchema.from_orm(s).dict()
            for s in project.code_snippets.filter(is_public=True)
        ]

        return project_data

    @route.get("/technologies", response=List[TechnologySchema])
    def get_technologies(self, filters: TechnologyFilterSchema = Query(...)):
        """Get technologies with filtering"""
        queryset = Technology.objects.all()

        if filters.category:
            queryset = queryset.filter(category=filters.category)

        if filters.type:
            queryset = queryset.filter(type=filters.type)

        if filters.featured is not None:
            queryset = queryset.filter(is_featured=filters.featured)

        if filters.search:
            queryset = queryset.filter(name__icontains=filters.search)

        return [
            TechnologySchema.from_orm(t) for t in queryset.order_by("order", "name")
        ]

    @route.get("/categories", response=List[ProjectCategorySchema])
    def get_categories(self):
        """Get all project categories"""
        categories = ProjectCategory.objects.all().order_by("order", "name")
        return [ProjectCategorySchema.from_orm(c) for c in categories]

    @route.get("/demos", response=List[DemoInstanceSchema])
    def get_demos(self):
        """Get all live demos"""
        demos = DemoInstance.objects.filter(
            is_public=True, status="online"
        ).select_related("project")

        demos_data = []
        for demo in demos:
            demo_dict = DemoInstanceSchema.from_orm(demo).dict()
            demo_dict["project"] = ProjectSchema.from_orm(demo.project).dict()
            demos_data.append(demo_dict)

        return demos_data

    @route.get("/testimonials", response=List[TestimonialSchema])
    def get_testimonials(self):
        """Get approved testimonials"""
        testimonials = Testimonial.objects.filter(is_approved=True).order_by(
            "order", "-created_at"
        )[:10]

        return [TestimonialSchema.from_orm(t) for t in testimonials]

    @route.get("/stats", response=StatsResponse)
    def get_stats(self):
        """Get portfolio statistics"""
        return StatsResponse(
            total_projects=Project.objects.filter(is_public=True).count(),
            total_technologies=Technology.objects.count(),
            total_demos=DemoInstance.objects.filter(
                is_public=True, status="online"
            ).count(),
            total_messages=0,
            featured_projects=Project.objects.filter(
                is_featured=True, is_public=True
            ).count(),
            featured_technologies=Technology.objects.filter(is_featured=True).count(),
        )

    @route.post("/contact", response={201: Dict[str, str], 400: ErrorResponse})
    def send_contact_message(self, message: ContactMessageCreateSchema):
        """Send contact message"""
        try:
            contact_message = ContactMessage.objects.create(
                name=message.name,
                email=message.email,
                subject=message.subject,
                message=message.message,
            )
            return 201, {"message": "Message sent successfully!"}
        except Exception as e:
            return 400, {"detail": str(e)}

    @route.get("/settings", response=SiteSettingsPublicSchema)
    def get_site_settings(self, request):
        """Get public site settings"""
        settings_obj = SiteSettings.get_active_settings()

        # Get request scheme and host for absolute URLs
        scheme = request.scheme
        host = request.get_host()
        base_url = f"{scheme}://{host}"

        # Build absolute URLs for media files
        logo_url = None
        favicon_url = None

        if settings_obj.logo:
            logo_url = f"{base_url}{settings_obj.logo.url}"

        if settings_obj.favicon:
            favicon_url = f"{base_url}{settings_obj.favicon.url}"

        # Prepare public data (exclude sensitive fields)
        return SiteSettingsPublicSchema(
            site_name=settings_obj.site_name,
            site_tagline=settings_obj.site_tagline,
            contact_email=settings_obj.contact_email,
            logo=logo_url,
            favicon=favicon_url,
            primary_color=settings_obj.primary_color,
            secondary_color=settings_obj.secondary_color,
            dark_mode=settings_obj.dark_mode,
            social_links=(
                SocialLinksSchema(**settings_obj.social_links)
                if settings_obj.social_links
                else None
            ),
            seo_description=settings_obj.seo_description,
            seo_keywords=settings_obj.seo_keywords,
            maintenance_mode=settings_obj.maintenance_mode,
            maintenance_message=settings_obj.maintenance_message,
            self_description=settings_obj.self_description,
            self_long_description=settings_obj.self_long_description,
        )

    @route.get("/settings/maintenance", response=Dict[str, Any])
    def get_maintenance_status(self, request):
        """Check if site is in maintenance mode"""
        settings_obj = SiteSettings.get_active_settings()

        return {
            "maintenance_mode": settings_obj.maintenance_mode,
            "maintenance_message": settings_obj.maintenance_message,
            "site_name": settings_obj.site_name,
        }

    @route.get("/settings/theme", response=Dict[str, Any])
    def get_theme_settings(self, request):
        """Get theme/UI settings for frontend"""
        settings_obj = SiteSettings.get_active_settings()

        # Get request scheme and host for absolute URLs
        scheme = request.scheme
        host = request.get_host()
        base_url = f"{scheme}://{host}"

        # Build absolute URLs
        logo_url = None
        favicon_url = None

        if settings_obj.logo:
            logo_url = f"{base_url}{settings_obj.logo.url}"

        if settings_obj.favicon:
            favicon_url = f"{base_url}{settings_obj.favicon.url}"

        return {
            "primary_color": settings_obj.primary_color,
            "secondary_color": settings_obj.secondary_color,
            "dark_mode": settings_obj.dark_mode,
            "site_name": settings_obj.site_name,
            "logo": logo_url,
            "favicon": favicon_url,
        }

    @route.get("/settings/seo", response=Dict[str, Any])
    def get_seo_settings(self, request):
        """Get SEO settings for frontend"""
        settings_obj = SiteSettings.get_active_settings()

        # Get request scheme and host for absolute URLs
        scheme = request.scheme
        host = request.get_host()
        base_url = f"{scheme}://{host}"

        # Build absolute URL for logo
        logo_url = None
        if settings_obj.logo:
            logo_url = f"{base_url}{settings_obj.logo.url}"

        return {
            "site_name": settings_obj.site_name,
            "site_tagline": settings_obj.site_tagline,
            "seo_description": settings_obj.seo_description,
            "seo_keywords": settings_obj.seo_keywords,
            "logo": logo_url,
            "self_description": settings_obj.self_description,
            "self_long_description": settings_obj.self_long_description,
        }

    @route.get("/settings/social", response=SocialLinksSchema)
    def get_social_links(self):
        """Get social media links"""
        settings_obj = SiteSettings.get_active_settings()

        if settings_obj.social_links:
            return SocialLinksSchema(**settings_obj.social_links)
        return SocialLinksSchema()

    @route.get("/settings/all", response=Dict[str, Any])
    def get_all_settings(self, request):
        """Get all public settings in one endpoint"""
        settings_obj = SiteSettings.get_active_settings()

        # Get request scheme and host for absolute URLs
        scheme = request.scheme
        host = request.get_host()
        base_url = f"{scheme}://{host}"

        # Build absolute URLs
        logo_url = None
        favicon_url = None

        if settings_obj.logo:
            logo_url = f"{base_url}{settings_obj.logo.url}"

        if settings_obj.favicon:
            favicon_url = f"{base_url}{settings_obj.favicon.url}"

        return {
            "site": {
                "name": settings_obj.site_name,
                "tagline": settings_obj.site_tagline,
                "contact_email": settings_obj.contact_email,
                "logo": logo_url,
                "favicon": favicon_url,
                "self_description": settings_obj.self_description,
                "self_long_description": settings_obj.self_long_description,
            },
            "theme": {
                "primary_color": settings_obj.primary_color,
                "secondary_color": settings_obj.secondary_color,
                "dark_mode": settings_obj.dark_mode,
            },
            "seo": {
                "description": settings_obj.seo_description,
                "keywords": settings_obj.seo_keywords,
            },
            "maintenance": {
                "enabled": settings_obj.maintenance_mode,
                "message": settings_obj.maintenance_message,
            },
            "social": settings_obj.social_links if settings_obj.social_links else {},
        }

    @route.get("/rotating-text", response=RotatingTextResponse)
    def get_rotating_texts(self, request):
        """Get all active rotating texts for frontend"""
        texts = RotatingText.objects.filter(is_active=True)
        return RotatingTextResponse.from_queryset(texts)


def get_absolute_media_url(relative_url):
    """Convert relative media URL to absolute URL"""
    if not relative_url:
        return None

    # If it's already an absolute URL, return as is
    if relative_url.startswith(("http://", "https://")):
        return relative_url

    # Build absolute URL
    request = None  # We'll get this from the view context

    # In Django Ninja, we can access request in the method
    # We'll handle this differently in each method
    return (
        f"{settings.SITE_URL}{relative_url}"
        if hasattr(settings, "SITE_URL")
        else relative_url
    )
