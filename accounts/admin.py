from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from .models import (
    AdminUser,
    RotatingText,
    Technology,
    ProjectCategory,
    Project,
    ProjectImage,
    DemoInstance,
    DemoStat,
    ContactMessage,
    SiteSettings,
    VisitorAnalytics,
    ContentBlock,
    Testimonial,
    CodeSnippet,
)

from django import forms
from ckeditor.widgets import CKEditorWidget

# =========================
# Admin User
# =========================

@admin.register(AdminUser)
class AdminUserAdmin(UserAdmin):
    model = AdminUser

    list_display = (
        "username",
        "email",
        "is_super_admin",
        "department",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_super_admin", "is_active", "department")
    search_fields = ("username", "email", "phone_number")
    ordering = ("-date_joined",)

    readonly_fields = ("admin_id", "last_login", "date_joined", "last_login_ip")

    fieldsets = (
        ("Authentication", {"fields": ("username", "password")}),
        ("Personal Info", {
            "fields": (
                "email",
                "phone_number",
                "department",
                "profile_picture",
                "bio",
                "social_links",
            )
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_super_admin",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Activity", {"fields": ("last_login", "last_login_ip", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "is_super_admin"),
        }),
    )


# =========================
# Technology
# =========================

@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "category", "proficiency", "is_featured")
    list_filter = ("type", "category", "is_featured")
    search_fields = ("name", "category")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")


# =========================
# Project Category
# =========================

@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order",)


# =========================
# Project Image Inline
# =========================

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


# =========================
# Project
# =========================


class ProjectAdminForm(forms.ModelForm):
    # You don't need to explicitly define long_description here if using RichTextField
    # The CKEditorWidget will be automatically used for RichTextField fields
    
    class Meta:
        model = Project
        fields = '__all__'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = (
        "title",
        "status",
        "demo_type",
        "is_featured",
        "is_public",
        "created_at",
    )
    list_filter = ("status", "demo_type", "is_featured", "is_public")
    search_fields = ("title", "short_description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order", "-created_at")
    filter_horizontal = ("technologies",)
    inlines = [ProjectImageInline]
    
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }
    
    # Group fields in admin
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'status', 'tags')
        }),
        ('Descriptions', {
            'fields': ('short_description', 'long_description'),
            'classes': ('wide',),
        }),
        ('Media & Links', {
            'fields': ('featured_image', 'demo_type', 'demo_url', 'github_url', 'documentation_url')
        }),
        ('Content', {
            'fields': ('technologies', 'features', 'installation_guide')
        }),
        ('Settings', {
            'fields': ('is_featured', 'is_public', 'order', 'start_date', 'completion_date')
        }),
    )
    class Media:
        css = {
            'all': ('admin/css/project_admin.css',)
        }


# =========================
# Demo Instance
# =========================

@admin.register(DemoInstance)
class DemoInstanceAdmin(admin.ModelAdmin):
    list_display = ("project", "status", "instance_url", "last_checked")
    list_filter = ("status", "is_public")
    search_fields = ("project__title",)


# =========================
# Demo Stats
# =========================

@admin.register(DemoStat)
class DemoStatAdmin(admin.ModelAdmin):
    list_display = ("demo", "session_id", "duration", "actions_count", "created_at")
    list_filter = ("created_at",)
    search_fields = ("session_id", "ip_address")


# =========================
# Contact Messages
# =========================

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "status", "created_at")
    list_filter = ("status", "is_spam")
    search_fields = ("name", "email", "subject")
    readonly_fields = ("ip_address", "user_agent", "created_at")


# =========================
# Site Settings (Singleton)
# =========================

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


# =========================
# Visitor Analytics
# =========================

@admin.register(VisitorAnalytics)
class VisitorAnalyticsAdmin(admin.ModelAdmin):
    list_display = ("ip_address", "page_visited", "time_on_page", "created_at")
    list_filter = ("created_at",)
    search_fields = ("ip_address", "page_visited")


# =========================
# Content Blocks
# =========================

@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    list_display = ("block_type", "title", "is_active", "order")
    list_filter = ("block_type", "is_active")
    ordering = ("order",)


# =========================
# Testimonials
# =========================

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("client_name", "rating", "is_featured", "is_approved")
    list_filter = ("rating", "is_featured", "is_approved")
    search_fields = ("client_name",)


# =========================
# Code Snippets
# =========================

@admin.register(CodeSnippet)
class CodeSnippetAdmin(admin.ModelAdmin):
    list_display = ("title", "language", "project", "line_count", "is_public")
    list_filter = ("language", "is_public")
    search_fields = ("title", "project__title")



@admin.register(RotatingText)
class RotatingTextAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'text_type', 'order', 'is_active', 'typing_speed', 'delay_seconds', 'created_at')
    list_filter = ('text_type', 'is_active', 'created_at')
    list_editable = ('order', 'is_active', 'typing_speed', 'delay_seconds')
    search_fields = ('text',)
    ordering = ('text_type', 'order')
    actions = ['activate_texts', 'deactivate_texts']
    
    fieldsets = (
        ('Text Content', {
            'fields': ('text', 'text_type', 'order')
        }),
        ('Animation Settings', {
            'fields': ('delay_seconds', 'typing_speed'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',),
            'classes': ('collapse',)
        }),
    )
    
    def text_preview(self, obj):
        """Display truncated text preview"""
        if len(obj.text) > 40:
            return f"{obj.text[:40]}..."
        return obj.text
    text_preview.short_description = "Text"
    
    def activate_texts(self, request, queryset):
        """Admin action to activate selected texts"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} text(s) activated successfully")
    activate_texts.short_description = "Activate selected texts"
    
    def deactivate_texts(self, request, queryset):
        """Admin action to deactivate selected texts"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} text(s) deactivated successfully")
    deactivate_texts.short_description = "Deactivate selected texts"