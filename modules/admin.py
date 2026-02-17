from django.contrib import admin
from .models import (
    ListeningTest,
    ReadingPassage,
    WritingTask,
    SmartArticle,
    ListeningMaterial,
    VocabularyWord,
    Topic
)


@admin.register(ListeningTest)
class ListeningTestAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'is_active', 'created_at', 'updated_at')
    list_filter = ('difficulty', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(ReadingPassage)
class ReadingPassageAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'word_count', 'is_active', 'created_at', 'updated_at')
    list_filter = ('difficulty', 'is_active', 'created_at')
    search_fields = ('title',)
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ('created_at', 'updated_at', 'word_count')
    ordering = ('-created_at',)


@admin.register(WritingTask)
class WritingTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic_category', 'created_at', 'updated_at')
    list_filter = ('topic_category', 'is_active', 'created_at')
    search_fields = ('title', 'task1_question', 'task2_question')
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(SmartArticle)
class SmartArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'word_count', 'created_at', 'updated_at')
    list_filter = ('level', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ('created_at', 'updated_at', 'word_count')
    ordering = ('-created_at',)


@admin.register(ListeningMaterial)
class ListeningMaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'difficulty', 'duration_minutes', 'is_active', 'created_at', 'updated_at')
    list_filter = ('category', 'difficulty', 'is_active', 'created_at')
    search_fields = ('name', 'youtube_url', 'description')
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(VocabularyWord)
class VocabularyWordAdmin(admin.ModelAdmin):
    list_display = ("word", "cefr_level", "topic", "created_by", "is_public", "imported_from")
    list_filter = ("cefr_level", "topic", "is_public")
    search_fields = ("word", "definition")
    readonly_fields = ("imported_from", "is_public")

    def get_readonly_fields(self, request, obj=None):
        # Foydalanuvchi admin so‘zlarini o‘chira/tahrirlash imkoniyatiga ega bo‘lmasin
        readonly = list(super().get_readonly_fields(request, obj))
        if obj and obj.is_public and obj.created_by and obj.created_by.role == "admin":
            readonly += ["word", "definition", "cefr_level", "topic", "example_sentences"]
        return readonly
