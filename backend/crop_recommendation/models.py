from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Crop(models.Model):
    """
    Represents a specific type of crop and its ideal growing conditions.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Common name of the crop (e.g., Rice, Maize)")
    scientific_name = models.CharField(max_length=150, blank=True, help_text="Scientific/botanical name")
    description = models.TextField(blank=True)
    
    soil_type = models.CharField(max_length=200, blank=True, help_text="Preferred soil types")
    min_ph = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0), MaxValueValidator(14.0)])
    max_ph = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0), MaxValueValidator(14.0)])
    
    min_temperature = models.FloatField(null=True, blank=True, help_text="Minimum growing temperature in Celsius")
    max_temperature = models.FloatField(null=True, blank=True, help_text="Maximum growing temperature in Celsius")
    
    water_requirement = models.CharField(max_length=200, blank=True, help_text="General water needs (e.g., High, Moderate)")
    growing_duration = models.CharField(max_length=100, blank=True, help_text="Approximate time to harvest")
    
    fertilizer_information = models.TextField(blank=True, help_text="General fertilizer requirements")
    general_information = models.TextField(blank=True, help_text="Any additional growing tips or facts")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.CheckConstraint(
                check=models.Q(min_ph__lte=models.F('max_ph')),
                name='check_ph_range'
            ),
            models.CheckConstraint(
                check=models.Q(min_temperature__lte=models.F('max_temperature')),
                name='check_temp_range'
            ),
        ]

    def __str__(self):
        return self.name


class CropRecommendationRequest(models.Model):
    """
    Stores the input parameters for a crop recommendation prediction.
    """
    nitrogen = models.FloatField(validators=[MinValueValidator(0.0)])
    phosphorus = models.FloatField(validators=[MinValueValidator(0.0)])
    potassium = models.FloatField(validators=[MinValueValidator(0.0)])
    temperature = models.FloatField()
    humidity = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    ph = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(14.0)])
    rainfall = models.FloatField(validators=[MinValueValidator(0.0)])
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Request {self.id} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class CropRecommendationResult(models.Model):
    """
    Stores a specific predicted crop result (rank 1, 2, or 3) for a recommendation request.
    """
    request = models.ForeignKey(
        CropRecommendationRequest, 
        on_delete=models.CASCADE, 
        related_name='recommendations'
    )
    crop = models.ForeignKey(
        Crop, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='recommendation_results'
    )
    score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Model confidence score/probability (0.0 to 1.0)"
    )
    rank = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)]
    )

    class Meta:
        ordering = ['request', 'rank']
        constraints = [
            models.UniqueConstraint(
                fields=['request', 'rank'], 
                name='unique_rank_per_request'
            )
        ]

    def __str__(self):
        crop_name = self.crop.name if self.crop else "Unknown Crop"
        return f"Request {self.request.id} - Rank {self.rank}: {crop_name} ({self.score:.2f})"
