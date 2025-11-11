/**
 * API service for backend communication.
 */

import axios, { AxiosInstance } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retried, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = await AsyncStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token } = response.data;
          await AsyncStorage.setItem('accessToken', access_token);

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        await AsyncStorage.removeItem('accessToken');
        await AsyncStorage.removeItem('refreshToken');
        // Navigate to login (handled by app)
      }
    }

    return Promise.reject(error);
  },
);

// Auth API
export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await apiClient.post('/api/v1/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  register: async (userData: {
    email: string;
    username: string;
    password: string;
    full_name?: string;
  }) => {
    const response = await apiClient.post('/api/v1/auth/register', userData);
    return response.data;
  },

  logout: async (accessToken: string, refreshToken: string) => {
    const response = await apiClient.post('/api/v1/auth/logout', {
      access_token: accessToken,
      refresh_token: refreshToken,
    });
    return response.data;
  },

  refresh: async (refreshToken: string) => {
    const response = await apiClient.post('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    });
    return {
      access_token: response.data.access_token,
      refresh_token: response.data.refresh_token || refreshToken,
      token_type: response.data.token_type,
    };
  },

  registerPushToken: async (tokenData: {
    token: string;
    platform: 'ios' | 'android';
    device_id?: string;
  }) => {
    const response = await apiClient.post('/api/v1/push-tokens/register', tokenData);
    return response.data;
  },

  unregisterPushToken: async (token: string) => {
    const response = await apiClient.post('/api/v1/push-tokens/deactivate', { token });
    return response.data;
  },
};

export default apiClient;

