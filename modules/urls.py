from django.urls import path
from .views import (
    ListeningTestListCreateAPIView, ListeningTestRetrieveUpdateDestroyAPIView,
    ReadingPassageListCreateAPIView, ReadingPassageRetrieveUpdateDestroyAPIView,
    WritingTaskListCreateAPIView, WritingTaskRetrieveUpdateDestroyAPIView,
    SmartArticleListCreateAPIView, SmartArticleRetrieveUpdateDestroyAPIView,
    ListeningMaterialListCreateAPIView, ListeningMaterialRetrieveUpdateDestroyAPIView,
    VocabularyWordListCreateAPIView, VocabularyWordRetrieveUpdateDestroyAPIView,
    import_vocab_word
                     )
urlpatterns = [
    path('listening-tests/', ListeningTestListCreateAPIView.as_view(), name='listening-test-list-create'),
    path('listening-tests/<slug:slug>/', ListeningTestRetrieveUpdateDestroyAPIView.as_view(), name='listening-test-detail'),
    path('reading-passages/', ReadingPassageListCreateAPIView.as_view(), name='reading-passage-list-create'),
    path('reading-passages/<slug:slug>/', ReadingPassageRetrieveUpdateDestroyAPIView.as_view(),
         name='reading-passage-detail'),
    path('writing-tasks/', WritingTaskListCreateAPIView.as_view(), name='writing-task-list-create'),
    path('writing-tasks/<slug:slug>/', WritingTaskRetrieveUpdateDestroyAPIView.as_view(), name='writing-task-detail'),
    path('smart-articles/', SmartArticleListCreateAPIView.as_view(), name='smart-article-list-create'),
    path('smart-articles/<slug:slug>/', SmartArticleRetrieveUpdateDestroyAPIView.as_view(), name='smart-article-detail'),
    path('listening-materials/', ListeningMaterialListCreateAPIView.as_view(), name='listening-material-list-create'),
    path('listening-materials/<slug:slug>/', ListeningMaterialRetrieveUpdateDestroyAPIView.as_view(), name='listening-material-detail'),
    path('vocabulary-words/', VocabularyWordListCreateAPIView.as_view(), name='vocabulary-word-list-create'),
    path('vocabulary-words/<int:id>/', VocabularyWordRetrieveUpdateDestroyAPIView.as_view(), name='vocabulary-word-detail'),
    path('vocabulary/import/<int:pk>/', import_vocab_word, name='import_vocab_word'),
]
