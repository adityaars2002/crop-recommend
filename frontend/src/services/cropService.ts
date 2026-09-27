import { apiClient } from './api';
import type {
  ApiSuccessResponse,
  CropRecommendationInput,
  CropRecommendationResponse,
  Crop,
  RecommendationHistoryItem,
  PaginationInfo,
} from '../types';

const API_PREFIX = '/api/v1/crops';

// ============================================================================
// Crop Recommendation
// ============================================================================

export async function recommendCrops(
  input: CropRecommendationInput
): Promise<CropRecommendationResponse> {
  const response = await apiClient.post<ApiSuccessResponse<CropRecommendationResponse>>(
    `${API_PREFIX}/recommend/`,
    input
  );
  return response.data.data;
}

// ============================================================================
// Crop Directory
// ============================================================================

export interface CropListResponse {
  crops: Crop[];
  pagination: PaginationInfo;
}

export async function getCrops(page = 1, pageSize = 10): Promise<CropListResponse> {
  const response = await apiClient.get<
    ApiSuccessResponse<Crop[]> & { pagination: PaginationInfo }
  >(`${API_PREFIX}/`, {
    params: { page, page_size: pageSize },
  });
  return {
    crops: response.data.data,
    pagination: response.data.pagination!,
  };
}

export async function getCropById(id: number): Promise<Crop> {
  const response = await apiClient.get<ApiSuccessResponse<Crop>>(
    `${API_PREFIX}/${id}/`
  );
  return response.data.data;
}

// ============================================================================
// Recommendation History
// ============================================================================

export interface HistoryListResponse {
  items: RecommendationHistoryItem[];
  pagination: PaginationInfo;
}

export async function getRecommendationHistory(
  page = 1,
  pageSize = 10
): Promise<HistoryListResponse> {
  const response = await apiClient.get<
    ApiSuccessResponse<RecommendationHistoryItem[]> & { pagination: PaginationInfo }
  >(`${API_PREFIX}/recommendations/history/`, {
    params: { page, page_size: pageSize },
  });
  return {
    items: response.data.data,
    pagination: response.data.pagination!,
  };
}
