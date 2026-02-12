from rest_framework import generics, permissions, filters, status
from accounts.permissions import IsAdminUser, IsRegularUser
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import ListeningTest, ReadingPassage, WritingTask, VocabularyWord, SmartArticle, ListeningMaterial
from .serializers import (
    ListeningTestDetailSerializer, ListeningTestCreateUpdateSerializer,
    ReadingPassageDetailSerializer, ReadingPassageCreateUpdateSerializer,
    WritingTaskDetailSerializer, WritingTaskCreateUpdateSerializer,
    SmartArticleDetailSerializer, SmartArticleCreateUpdateSerializer,
    ListeningMaterialCreateUpdateSerializer, ListeningMaterialDetailSerializer,
    VocabularyWordCreateUpdateSerializer, VocabularyWordDetailSerializer
                           )


class ListeningTestListCreateAPIView(generics.ListCreateAPIView):
    queryset = ListeningTest.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['difficulty', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    parser_classes = [MultiPartParser, FormParser]  # fayl va image upload uchun

    def get_permissions(self):
        if self.request.method == 'GET':
            return [(IsRegularUser | IsAdminUser)()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ListeningTestCreateUpdateSerializer
        return ListeningTestDetailSerializer


class ListeningTestRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ListeningTest.objects.all()
    parser_classes = [MultiPartParser, FormParser]

    lookup_field = 'slug'  # URL da slug orqali olish

    def get_permissions(self):
        if self.request.method == 'GET':
            return [(IsRegularUser | IsAdminUser)()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ListeningTestCreateUpdateSerializer
        return ListeningTestDetailSerializer


class ReadingPassageListCreateAPIView(generics.ListCreateAPIView):
    queryset = ReadingPassage.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['difficulty', 'is_active']
    search_fields = ['title']
    ordering_fields = ['created_at', 'title']
    parser_classes = [MultiPartParser, FormParser]  # HTML fayl va rasm upload

    def get_permissions(self):
        if self.request.method == 'GET':
            return [(IsRegularUser | IsAdminUser)()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReadingPassageCreateUpdateSerializer
        return ReadingPassageDetailSerializer


class ReadingPassageRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReadingPassage.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'slug'  # URL da slug orqali olish

    def get_permissions(self):
        if self.request.method == 'GET':
            return [(IsRegularUser | IsAdminUser)()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ReadingPassageCreateUpdateSerializer
        return ReadingPassageDetailSerializer


class WritingTaskListCreateAPIView(generics.ListCreateAPIView):
    queryset = WritingTask.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['difficulty', 'is_active']
    search_fields = ['title', 'topic_category', 'task1_question', 'task2_question']
    ordering_fields = ['created_at', 'title']
    parser_classes = [MultiPartParser, FormParser]  # task1_image upload uchun

    def get_permissions(self):
        if self.request.method == 'GET':
            return [(IsRegularUser | IsAdminUser)()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WritingTaskCreateUpdateSerializer
        return WritingTaskDetailSerializer


class WritingTaskRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WritingTask.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'slug'  # URL da slug orqali olish

    def get_permissions(self):
        if self.request.method == 'GET':
            return [(IsRegularUser | IsAdminUser)()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return WritingTaskCreateUpdateSerializer
        return WritingTaskDetailSerializer


class SmartArticleListCreateAPIView(generics.ListCreateAPIView):
    queryset = SmartArticle.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['level']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'title']
    parser_classes = [MultiPartParser, FormParser]  # featured_image upload uchun

    def get_permissions(self):
        if self.request.method == 'GET':
            return [(IsRegularUser | IsAdminUser)()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SmartArticleCreateUpdateSerializer
        return SmartArticleDetailSerializer


class SmartArticleRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SmartArticle.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'slug'  # URL da slug orqali olish

    def get_permissions(self):
        if self.request.method == 'GET':
            return [(IsRegularUser | IsAdminUser)()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SmartArticleCreateUpdateSerializer
        return SmartArticleDetailSerializer


class ListeningMaterialListCreateAPIView(generics.ListCreateAPIView):
    queryset = ListeningMaterial.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'difficulty', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    parser_classes = [MultiPartParser, FormParser]  # agar kelajakda fayl qo‘shilsa tayyor

    def get_permissions(self):
        if self.request.method == 'GET':
            return [(IsRegularUser | IsAdminUser)()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ListeningMaterialCreateUpdateSerializer
        return ListeningMaterialDetailSerializer


class ListeningMaterialRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ListeningMaterial.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'slug'  # URL da slug orqali olish

    def get_permissions(self):
        if self.request.method == 'GET':
            return [(IsRegularUser | IsAdminUser)()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ListeningMaterialCreateUpdateSerializer
        return ListeningMaterialDetailSerializer


class VocabularyWordListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Admin so'zlarini va o'z foydalanuvchining so'zlarini ko‘rsatadi
        return VocabularyWord.objects.filter(
            Q(is_public=True) | Q(created_by=user)
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return VocabularyWordCreateUpdateSerializer
        return VocabularyWordDetailSerializer


class VocabularyWordRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Admin so'zlari va o'z foydalanuvchining so'zlari
        return VocabularyWord.objects.filter(
            Q(is_public=True) | Q(created_by=user)
        )

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return VocabularyWordCreateUpdateSerializer
        return VocabularyWordDetailSerializer

@swagger_auto_schema(
    method='post',
    operation_description="Admin qo‘shgan public vocabulary so‘zni user o‘z bazasiga import qiladi.",
    responses={
        201: openapi.Response("Imported successfully"),
        400: "Already imported",
        404: "Word not found"
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def import_vocab_word(request, pk):
    # Asl so'zni topish
    original = get_object_or_404(VocabularyWord, pk=pk, is_public=True)

    user = request.user

    # Allaqachon import qilinganligini tekshirish
    if VocabularyWord.objects.filter(imported_from=original, created_by=user).exists():
        return Response({"detail": "Already imported"}, status=status.HTTP_400_BAD_REQUEST)

    # Is_public statusini hisoblash
    is_public = True if getattr(user, "role", "") == "admin" else False

    # Yangi so'zni yaratish
    new_word = VocabularyWord.objects.create(
        word=original.word,
        definition=original.definition,
        cefr_level=original.cefr_level,
        example_sentences=original.example_sentences,
        topic=original.topic,
        created_by=user,
        imported_from=original,
        is_public=is_public,
    )

    return Response(
        {"detail": "Imported successfully", "id": new_word.id},
        status=status.HTTP_201_CREATED
    )