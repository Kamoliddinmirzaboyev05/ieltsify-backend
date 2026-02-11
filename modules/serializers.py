from rest_framework import serializers
from .models import ListeningTest, ReadingPassage, WritingTask, VocabularyWord, ListeningMaterial, SmartArticle
from django.core.validators import URLValidator


class ListeningTestDetailSerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()
    html_file_url = serializers.SerializerMethodField()

    class Meta:
        model = ListeningTest
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "html_file_url",
            "cover_image_url",
            "difficulty",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.cover_image.url) if request else obj.cover_image.url
        return None

    def get_html_file_url(self, obj):
        if obj.html_file:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.html_file.url) if request else obj.html_file.url
        return None


class ListeningTestCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeningTest
        fields = [
            "title",
            "description",
            "html_file",
            "cover_image",
            "difficulty",
            "is_active",
        ]

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Sarlavha kamida 5 ta belgidan iborat bo'lishi kerak.")
        return value

    def create(self, validated_data):
        # Slug avtomatik generatsiya qilinadi model save metodi orqali
        return ListeningTest.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ReadingPassageDetailSerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()
    html_content_url = serializers.SerializerMethodField()

    class Meta:
        model = ReadingPassage
        fields = [
            "id",
            "title",
            "slug",
            "html_content_url",
            "cover_image_url",
            "difficulty",
            "word_count",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "word_count", "created_at", "updated_at"]

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.cover_image.url) if request else obj.cover_image.url
        return None

    def get_html_content_url(self, obj):
        if obj.html_content:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.html_content.url) if request else obj.html_content.url
        return None


class ReadingPassageCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingPassage
        fields = [
            "title",
            "html_content",
            "cover_image",
            "difficulty",
            "is_active",
        ]

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Sarlavha kamida 5 ta belgidan iborat bo'lishi kerak.")
        return value

    def create(self, validated_data):
        return ReadingPassage.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class WritingTaskDetailSerializer(serializers.ModelSerializer):
    task1_image_url = serializers.SerializerMethodField()

    class Meta:
        model = WritingTask
        fields = [
            "id",
            "title",
            "slug",
            "topic_category",
            "difficulty",
            # Task 1
            "task1_question",
            "task1_image_url",
            "task1_word_count",
            "task1_time_minutes",
            # Task 2
            "task2_question",
            "task2_essay_type",
            "task2_word_count",
            "task2_time_minutes",
            # Audit
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id", "slug", "created_at", "updated_at"
        ]

    def get_task1_image_url(self, obj):
        if obj.task1_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.task1_image.url) if request else obj.task1_image.url
        return None


class WritingTaskCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WritingTask
        fields = [
            "title",
            "topic_category",
            "difficulty",
            # Task 1
            "task1_question",
            "task1_image",
            "task1_word_count",
            "task1_time_minutes",
            # Task 2
            "task2_question",
            "task2_essay_type",
            "task2_word_count",
            "task2_time_minutes",
            # Audit
            "is_active",
        ]

    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Sarlavha kamida 5 ta belgidan iborat bo'lishi kerak.")
        return value

    def validate_task1_question(self, value):
        if value and len(value.strip()) < 20:
            raise serializers.ValidationError("Task 1 savoli kamida 20 ta belgidan iborat bo'lishi kerak.")
        return value

    def validate_task2_question(self, value):
        if value and len(value.strip()) < 30:
            raise serializers.ValidationError("Task 2 savoli kamida 30 ta belgidan iborat bo'lishi kerak.")
        return value

    def create(self, validated_data):
        return WritingTask.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class SmartArticleDetailSerializer(serializers.ModelSerializer):
    featured_image_url = serializers.SerializerMethodField()
    word_count = serializers.ReadOnlyField()

    class Meta:
        model = SmartArticle
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "word_count",
            "level",
            "featured_image_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "word_count", "created_at", "updated_at"]

    def get_featured_image_url(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.featured_image.url) if request else obj.featured_image.url
        return None


class SmartArticleCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmartArticle
        fields = [
            "title",
            "content",
            "level",
            "featured_image",
        ]

    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Sarlavha kamida 5 ta belgidan iborat bo'lishi kerak.")
        return value

    def validate_content(self, value):
        if len(value.strip()) < 200:
            raise serializers.ValidationError("Maqola matni kamida 200 ta belgidan iborat bo'lishi kerak.")
        return value

    def create(self, validated_data):
        return SmartArticle.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ListeningMaterialDetailSerializer(serializers.ModelSerializer):
    youtube_id = serializers.ReadOnlyField()

    class Meta:
        model = ListeningMaterial
        fields = [
            "id",
            "name",
            "slug",
            "youtube_url",
            "youtube_id",
            "category",
            "description",
            "difficulty",
            "duration_minutes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "youtube_id", "created_at", "updated_at"]


class ListeningMaterialCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeningMaterial
        fields = [
            "name",
            "youtube_url",
            "category",
            "description",
            "difficulty",
            "duration_minutes",
            "is_active",
        ]

    def validate_name(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Nomi kamida 5 ta belgidan iborat bo'lishi kerak.")
        return value

    def validate_youtube_url(self, value):
        validator = URLValidator()
        try:
            validator(value)
        except:
            raise serializers.ValidationError("Iltimos, to‘g‘ri YouTube URL kiriting.")
        if 'youtube.com' not in value and 'youtu.be' not in value:
            raise serializers.ValidationError("URL YouTube videoga tegishli bo'lishi kerak.")
        return value

    def create(self, validated_data):
        return ListeningMaterial.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class VocabularyWordDetailSerializer(serializers.ModelSerializer):
    example_sentences_list = serializers.SerializerMethodField()
    created_by_email = serializers.SerializerMethodField()
    topic_name = serializers.CharField(source="topic.name", read_only=True)

    class Meta:
        model = VocabularyWord
        fields = [
            "id",
            "word",
            "definition",
            "cefr_level",
            "example_sentences_list",
            "created_by_email",
            "topic",
            "topic_name",
            "is_public",
            "imported_from",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "example_sentences_list",
            "created_by_email",
            "is_public",
            "imported_from",
            "created_at",
            "updated_at"
        ]

    def get_example_sentences_list(self, obj):
        return obj.get_example_sentences_list()

    def get_created_by_email(self, obj):
        return obj.created_by.email if obj.created_by else None


class VocabularyWordCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VocabularyWord
        fields = ["word", "definition", "cefr_level", "example_sentences", "topic"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["is_public"] = True if getattr(user, "role", "") == "admin" else False
        return super().create(validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()  # is_public avtomatik yangilanadi
        return instance