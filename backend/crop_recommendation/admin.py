from django.contrib import admin
from .models import Crop, CropRecommendationRequest, CropRecommendationResult

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('name', 'scientific_name', 'created_at')
    search_fields = ('name', 'scientific_name')
    list_filter = ('created_at',)
    ordering = ('name',)

class CropRecommendationResultInline(admin.TabularInline):
    model = CropRecommendationResult
    extra = 0
    readonly_fields = ('rank', 'crop', 'score')
    can_delete = False

@admin.register(CropRecommendationRequest)
class CropRecommendationRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'temperature', 'humidity', 'ph')
    list_filter = ('created_at',)
    search_fields = ('id',)
    ordering = ('-created_at',)
    readonly_fields = ('nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall', 'created_at')
    inlines = [CropRecommendationResultInline]

@admin.register(CropRecommendationResult)
class CropRecommendationResultAdmin(admin.ModelAdmin):
    list_display = ('request', 'crop', 'rank', 'score')
    list_filter = ('rank', 'crop')
    search_fields = ('request__id', 'crop__name')
    ordering = ('-request__created_at', 'rank')
    readonly_fields = ('request', 'crop', 'rank', 'score')
