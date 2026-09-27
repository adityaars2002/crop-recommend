// ============================================================================
// API Response Types
// ============================================================================

/** Standard API success envelope */
export interface ApiSuccessResponse<T> {
  success: true;
  data: T;
  pagination?: PaginationInfo;
}

/** Standard API error envelope */
export interface ApiErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    fields?: Record<string, string[]>;
  };
}

export type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;

export interface PaginationInfo {
  count: number;
  next: string | null;
  previous: string | null;
}

// ============================================================================
// Crop Types
// ============================================================================

export interface Crop {
  id: number;
  name: string;
  scientific_name: string;
  description: string;
  soil_type: string;
  min_ph: number | null;
  max_ph: number | null;
  min_temperature: number | null;
  max_temperature: number | null;
  water_requirement: string;
  growing_duration: string;
  fertilizer_information: string;
  general_information: string;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// Crop Recommendation Types
// ============================================================================

export interface CropRecommendationInput {
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  temperature: number;
  humidity: number;
  ph: number;
  rainfall: number;
}

export interface RecommendationResult {
  rank: number;
  crop: Crop;
  score: number;
}

export interface CropRecommendationResponse {
  id: number;
  created_at: string;
  input: CropRecommendationInput;
  recommendations: RecommendationResult[];
}

// ============================================================================
// Disease Detection Types
// ============================================================================

export interface DiseasePrediction {
  class_name: string;
  crop: string;
  disease: string;
  status: 'healthy' | 'diseased' | 'uncertain';
  score: number;
}

export interface DiseasePredictionResponse {
  prediction: DiseasePrediction;
  top_3: DiseasePrediction[];
}

// ============================================================================
// History Types
// ============================================================================

export interface RecommendationHistoryItem {
  id: number;
  created_at: string;
  input: CropRecommendationInput;
  recommendations: RecommendationResult[];
}
