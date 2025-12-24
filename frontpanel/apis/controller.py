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
    Education,
    Experience,
    Resume,
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
    
    
    ExperienceSchema,
    ExperienceFilterSchema,
    EducationSchema,
    EducationFilterSchema,
    ResumeSchema,
)
from frontpanel.utils import get_absolute_url
from my_port import settings


# Public API Controllers
@api_controller("/public", tags=["Public"], auth=None, permissions=[AllowAny])
class PublicController:
    """Public endpoints accessible to everyone"""

    @route.get("/home", response=HomeDataResponse)
    def get_home_data(self, request):
        """Get homepage data"""
        stats = StatsResponse(
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
            total_experiences=Experience.objects.count(),
            total_education=Education.objects.count(),
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
        
        # New: Featured experiences and education
        featured_experiences = Experience.objects.filter(is_featured=True).order_by("-start_date")[:3]
        featured_education = Education.objects.filter(is_featured=True).order_by("-start_date")[:3]
        
        # New: Primary resume
        primary_resume = Resume.objects.filter(is_primary=True, is_public=True).first()
        
        # Convert experiences using custom method
        experiences_data = []
        for exp in featured_experiences:
            experiences_data.append(ExperienceSchema.from_experience(exp, request))
        
        # Convert education using custom method
        education_data = []
        for edu in featured_education:
            education_data.append(EducationSchema.from_education(edu, request))
        
        # Convert resume using custom method
        resume_data = None
        if primary_resume:
            resume_data = ResumeSchema.from_resume(primary_resume, request)

        return HomeDataResponse(
            stats=stats,
            featured_projects=[ProjectSchema.from_orm(p) for p in featured_projects],
            featured_technologies=[
                TechnologySchema.from_orm(t) for t in featured_technologies
            ],
            recent_projects=[ProjectSchema.from_orm(p) for p in recent_projects],
            content_blocks=[ContentBlockSchema.from_orm(c) for c in content_blocks],
            featured_experiences=experiences_data,
            featured_education=education_data,
            primary_resume=resume_data,
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
        if settings_obj.my_image:
            my_image_url = f"{base_url}{settings_obj.my_image.url}"

        return {
            "site": {
                "name": settings_obj.site_name,
                "tagline": settings_obj.site_tagline,
                "contact_email": settings_obj.contact_email,
                "contact_phone": settings_obj.contact_phone,
                "location": settings_obj.location,
                "logo": logo_url,
                "favicon": favicon_url,
                "my_image": my_image_url,
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
    
    
    @route.get("/experiences", response=PaginatedResponse)
    def get_experiences(self, request, filters: ExperienceFilterSchema = Query(...)):
        """Get paginated work experiences with filtering"""
        queryset = Experience.objects.all()

        # Apply filters
        if filters.experience_type:
            queryset = queryset.filter(experience_type=filters.experience_type)

        if filters.is_current is not None:
            queryset = queryset.filter(is_current=filters.is_current)

        if filters.is_featured is not None:
            queryset = queryset.filter(is_featured=filters.is_featured)

        if filters.search:
            queryset = queryset.filter(
                Q(position__icontains=filters.search)
                | Q(company__icontains=filters.search)
                | Q(description__icontains=filters.search)
            )

        # Pagination
        paginator = Paginator(queryset.order_by("-start_date", "order"), filters.page_size)
        page_obj = paginator.get_page(filters.page)

        experiences_data = []
        for experience in page_obj.object_list:
            # Use your custom from_experience method instead of from_orm
            exp_schema = ExperienceSchema.from_experience(experience, request)
            if exp_schema:
                exp_dict = exp_schema.dict()
                experiences_data.append(exp_dict)

        return PaginatedResponse(
            items=experiences_data,
            total=paginator.count,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=paginator.num_pages,
            has_next=page_obj.has_next(),
            has_previous=page_obj.has_previous(),
        )

    @route.get("/experiences/{experience_id}", response={200: ExperienceSchema, 404: NotFoundResponse})
    def get_experience_detail(self, request, experience_id: str):
        """Get single experience by ID"""
        try:
            experience = Experience.objects.get(id=experience_id)
        except Experience.DoesNotExist:
            return 404, {"detail": "Experience not found"}
        
        # Use from_experience instead of from_orm
        exp_schema = ExperienceSchema.from_experience(experience, request)
        if exp_schema:
            return exp_schema
        return 404, {"detail": "Experience not found"}

    @route.get("/about/experience", response=List[ExperienceSchema])
    def get_featured_experiences(self, request):
        """Get featured experiences for about page"""
        experiences = Experience.objects.filter(is_featured=True).order_by("-start_date", "order")[:5]
        # Use from_experience for each experience
        return [ExperienceSchema.from_experience(exp, request) for exp in experiences if ExperienceSchema.from_experience(exp, request)]


    @route.get("/education", response=PaginatedResponse)
    def get_education(self, request, filters: EducationFilterSchema = Query(...)):
        """Get paginated education records with filtering"""
        queryset = Education.objects.all()

        # Apply filters
        if filters.education_type:
            queryset = queryset.filter(education_type=filters.education_type)

        if filters.is_current is not None:
            queryset = queryset.filter(is_current=filters.is_current)

        if filters.is_featured is not None:
            queryset = queryset.filter(is_featured=filters.is_featured)

        if filters.search:
            queryset = queryset.filter(
                Q(institution__icontains=filters.search)
                | Q(degree__icontains=filters.search)
                | Q(field_of_study__icontains=filters.search)
            )

        # Pagination
        paginator = Paginator(queryset.order_by("-start_date", "order"), filters.page_size)
        page_obj = paginator.get_page(filters.page)

        education_data = []
        for edu in page_obj.object_list:
            # Use from_education instead of from_orm
            edu_schema = EducationSchema.from_education(edu, request)
            if edu_schema:
                edu_dict = edu_schema.dict()
                education_data.append(edu_dict)

        return PaginatedResponse(
            items=education_data,
            total=paginator.count,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=paginator.num_pages,
            has_next=page_obj.has_next(),
            has_previous=page_obj.has_previous(),
        )

    @route.get("/education/{education_id}", response={200: EducationSchema, 404: NotFoundResponse})
    def get_education_detail(self, request, education_id: str):
        """Get single education record by ID"""
        try:
            education = Education.objects.get(id=education_id)
        except Education.DoesNotExist:
            return 404, {"detail": "Education record not found"}
        
        # Use from_education instead of from_orm
        edu_schema = EducationSchema.from_education(education, request)
        if edu_schema:
            return edu_schema
        return 404, {"detail": "Education record not found"}

    @route.get("/resumes", response=List[ResumeSchema])
    def get_resumes(self, request):
        """Get all public resumes"""
        resumes = Resume.objects.filter(is_public=True).order_by("-is_primary", "-last_updated")
        
        resumes_data = []
        for resume in resumes:
            # Get file URL
            file_url = None
            if resume.file:
                file_url = get_absolute_url(resume.file.url)
            
            # Convert experiences using from_experience
            experiences = []
            if hasattr(resume, 'experiences'):
                experiences = [ExperienceSchema.from_experience(exp, request) for exp in resume.experiences.all()]
                experiences = [exp for exp in experiences if exp]  # Filter out None values
            
            # Convert education using from_education
            education = []
            if hasattr(resume, 'education'):
                education = [EducationSchema.from_education(edu, request) for edu in resume.education.all()]
                education = [edu for edu in education if edu]  # Filter out None values
            
            # Convert projects and technologies (these should work with from_orm)
            projects = []
            if hasattr(resume, 'projects'):
                projects = [ProjectSchema.from_orm(proj).dict() for proj in resume.projects.all()]
            
            technologies = []
            if hasattr(resume, 'technologies'):
                technologies = [TechnologySchema.from_orm(tech).dict() for tech in resume.technologies.all()]
            
            resume_dict = {
                'id': str(resume.id),
                'title': resume.title,
                'file': file_url,
                'file_type': resume.file_type,
                'resume_type': resume.resume_type,
                'language': resume.language,
                'version': resume.version,
                'is_primary': resume.is_primary,
                'is_public': resume.is_public,
                'last_updated': resume.last_updated.isoformat() if resume.last_updated else None,
                'file_size': resume.file_size,
                'download_count': resume.download_count,
                'view_count': resume.view_count,
                'description': resume.description,
                'metadata': resume.metadata if resume.metadata else {},
                'file_size_human': resume.file_size_human if hasattr(resume, 'file_size_human') else None,
                'download_url': resume.download_url if hasattr(resume, 'download_url') else None,
                'preview_url': resume.preview_url if hasattr(resume, 'preview_url') else None,
                'experiences': experiences,
                'education': education,
                'projects': projects,
                'technologies': technologies,
            }
            
            resumes_data.append(resume_dict)
        
        return resumes_data


    @route.get("/resumes/{resume_id}", response={200: ResumeSchema, 404: NotFoundResponse})
    def get_resume_detail(self, request, resume_id: str):
        """Get single resume by ID"""
        try:
            resume = Resume.objects.get(id=resume_id, is_public=True)
        except Resume.DoesNotExist:
            return 404, {"detail": "Resume not found or not public"}
        
        # Use the same logic as above
        file_url = None
        if resume.file:
            file_url = get_absolute_url(resume.file.url)
        
        experiences = []
        if hasattr(resume, 'experiences'):
            experiences = [ExperienceSchema.from_experience(exp, request) for exp in resume.experiences.all()]
            experiences = [exp for exp in experiences if exp]
        
        education = []
        if hasattr(resume, 'education'):
            education = [EducationSchema.from_education(edu, request) for edu in resume.education.all()]
            education = [edu for edu in education if edu]
        
        projects = []
        if hasattr(resume, 'projects'):
            projects = [ProjectSchema.from_orm(proj).dict() for proj in resume.projects.all()]
        
        technologies = []
        if hasattr(resume, 'technologies'):
            technologies = [TechnologySchema.from_orm(tech).dict() for tech in resume.technologies.all()]
        
        resume_dict = {
            'id': str(resume.id),
            'title': resume.title,
            'file': file_url,
            'file_type': resume.file_type,
            'resume_type': resume.resume_type,
            'language': resume.language,
            'version': resume.version,
            'is_primary': resume.is_primary,
            'is_public': resume.is_public,
            'last_updated': resume.last_updated.isoformat() if resume.last_updated else None,
            'file_size': resume.file_size,
            'download_count': resume.download_count,
            'view_count': resume.view_count,
            'description': resume.description,
            'metadata': resume.metadata if resume.metadata else {},
            'file_size_human': resume.file_size_human if hasattr(resume, 'file_size_human') else None,
            'download_url': resume.download_url if hasattr(resume, 'download_url') else None,
            'preview_url': resume.preview_url if hasattr(resume, 'preview_url') else None,
            'experiences': experiences,
            'education': education,
            'projects': projects,
            'technologies': technologies,
        }
        
        return resume_dict


    @route.get("/resumes/primary", response={200: ResumeSchema, 404: NotFoundResponse})
    def get_primary_resume(self, request):
        """Get the primary resume"""
        try:
            resume = Resume.objects.get(is_primary=True, is_public=True)
        except Resume.DoesNotExist:
            return 404, {"detail": "No primary resume found"}
        
        resume_dict = ResumeSchema.from_orm(resume).dict()
        
        # Get absolute URL for resume file
        if resume.file:
            resume_dict["file"] = get_absolute_url(resume.file.url)
        
        # Get related experiences
        resume_dict["experiences"] = [
            ExperienceSchema.from_orm(exp).dict()
            for exp in resume.experiences.all()
        ]
        
        # Get related education
        resume_dict["education"] = [
            EducationSchema.from_orm(edu).dict()
            for edu in resume.education.all()
        ]
        
        # Get related projects
        resume_dict["projects"] = [
            ProjectSchema.from_orm(proj).dict()
            for proj in resume.projects.all()
        ]
        
        # Get related technologies
        resume_dict["technologies"] = [
            TechnologySchema.from_orm(tech).dict()
            for tech in resume.technologies.all()
        ]
        
        return resume_dict

    @route.get("/resumes/{resume_id}/download", response={200: Any, 404: NotFoundResponse})
    def download_resume(self, request, resume_id: str):
        """Download resume file"""
        try:
            resume = Resume.objects.get(id=resume_id, is_public=True)
        except Resume.DoesNotExist:
            return 404, {"detail": "Resume not found or not public"}
        
        # Increment download count
        resume.increment_download_count()
        
        # Return a FileResponse directly
        from django.http import FileResponse
        import os
        
        file_path = resume.file.path
        file_name = os.path.basename(file_path)
        
        # Get the content type
        import mimetypes
        content_type, _ = mimetypes.guess_type(file_name)
        
        # Create and return the FileResponse
        response = FileResponse(open(file_path, 'rb'), 
                            content_type=content_type or 'application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        
        # Django Ninja will automatically handle FileResponse objects
        return response

    @route.get("/about/experience", response=List[ExperienceSchema])
    def get_featured_experiences(self):
        """Get featured experiences for about page"""
        experiences = Experience.objects.filter(is_featured=True).order_by("-start_date", "order")[:5]
        return [ExperienceSchema.from_orm(exp) for exp in experiences]

    @route.get("/about/education", response=List[EducationSchema])
    def get_featured_education(self):
        """Get featured education for about page"""
        education = Education.objects.filter(is_featured=True).order_by("-start_date", "order")[:5]
        return [EducationSchema.from_orm(edu) for edu in education]

    @route.get("/about/cv", response=Optional[ResumeSchema])
    def get_about_resume(self, request):
        """Get resume for about page (prefers primary)"""
        try:
            resume = Resume.objects.filter(is_public=True).order_by("-is_primary", "-last_updated").first()
            if not resume:
                return None
            
            resume_dict = ResumeSchema.from_orm(resume).dict()
            
            if resume.file:
                resume_dict["file"] = get_absolute_url(resume.file.file.url)
            
            return resume_dict
            
        except Exception as e:
            print(f"Error getting resume: {e}")
            return None
    
    
    
    


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
