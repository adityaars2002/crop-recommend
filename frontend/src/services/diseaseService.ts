import { apiClient } from './api';
import type { ApiSuccessResponse, DiseasePredictionResponse } from '../types';

const API_PREFIX = '/api/v1/crops';

/**
 * Uploads a plant leaf image for disease prediction.
 * Uses multipart/form-data as required by the backend.
 */
export async function predictDisease(
  imageFile: File
): Promise<DiseasePredictionResponse> {
  const formData = new FormData();
  formData.append('image', imageFile);

  const response = await apiClient.post<
    ApiSuccessResponse<DiseasePredictionResponse>
  >(`${API_PREFIX}/disease/predict/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 60000, // 60s — model inference may take longer
  });

  return response.data.data;
}
