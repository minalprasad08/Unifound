import axios from 'axios';
import {
  AuthResponse,
  HealthStatus,
  LoginCredentials,
  ProfileUpdateData,
  RegisterData,
  User,
  Item,
  ItemReportInput,
  ItemUpdateInput,
  ItemType,
  ItemSearchParams,
  ItemSearchResponse,
  Claim,
  ClaimSubmitInput,
  ClaimReviewInput,
  AdminClaimsResponse,
  Notification,
  AdminStats,
  AdminAnalytics,
  ItemMatchesResponse,
  ImageAnalysis,
} from '../types/auth';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://127.0.0.1:8000/api/v1'
    : 'https://unifound-mqga.onrender.com/api/v1');

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Request interceptor to attach JWT
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('unifound_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for auth expiration
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Don't auto-redirect if this was a login attempt
      if (!error.config.url.includes('/auth/login')) {
        localStorage.removeItem('unifound_token');
        localStorage.removeItem('unifound_user');
        window.dispatchEvent(new Event('unifound:unauthorized'));
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
    return response.data;
  },

  register: async (data: RegisterData): Promise<User> => {
    const response = await apiClient.post<User>('/auth/register', data);
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await apiClient.get<User>('/users/me');
    return response.data;
  },

  updateProfile: async (data: ProfileUpdateData): Promise<User> => {
    const response = await apiClient.put<User>('/users/me', data);
    return response.data;
  },

  checkHealth: async (): Promise<HealthStatus> => {
    const response = await apiClient.get<HealthStatus>('/health');
    return response.data;
  },
};

export const itemApi = {
  createLost: async (data: ItemReportInput): Promise<Item> => {
    const response = await apiClient.post<Item>('/items/lost', data);
    return response.data;
  },

  createFound: async (data: ItemReportInput): Promise<Item> => {
    const response = await apiClient.post<Item>('/items/found', data);
    return response.data;
  },

  getMyReports: async (itemType?: ItemType): Promise<Item[]> => {
    const params = itemType ? { item_type: itemType } : {};
    const response = await apiClient.get<Item[]>('/items/my', { params });
    return response.data;
  },

  getItem: async (id: number): Promise<Item> => {
    const response = await apiClient.get<Item>(`/items/${id}`);
    return response.data;
  },

  updateItem: async (id: number, data: ItemUpdateInput): Promise<Item> => {
    const response = await apiClient.put<Item>(`/items/${id}`, data);
    return response.data;
  },

  closeItem: async (id: number): Promise<Item> => {
    const response = await apiClient.delete<Item>(`/items/${id}`);
    return response.data;
  },

  uploadImage: async (file: File): Promise<{ image_url: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<{ image_url: string }>('/items/upload-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  searchItems: async (params: ItemSearchParams): Promise<ItemSearchResponse> => {
    const response = await apiClient.get<ItemSearchResponse>('/items/search', { params });
    return response.data;
  },

  analyzeImage: async (
    id: number
  ): Promise<{ item_id: number; image_url: string; image_analysis: ImageAnalysis }> => {
    const response = await apiClient.post<{ item_id: number; image_url: string; image_analysis: ImageAnalysis }>(
      `/items/${id}/analyze-image`
    );
    return response.data;
  },
};

export const claimApi = {
  submitClaim: async (data: ClaimSubmitInput): Promise<Claim> => {
    const response = await apiClient.post<Claim>('/claims', data);
    return response.data;
  },

  getMyClaims: async (): Promise<Claim[]> => {
    const response = await apiClient.get<Claim[]>('/claims/my');
    return response.data;
  },

  getClaim: async (id: number): Promise<Claim> => {
    const response = await apiClient.get<Claim>(`/claims/${id}`);
    return response.data;
  },

  cancelClaim: async (id: number): Promise<Claim> => {
    const response = await apiClient.put<Claim>(`/claims/${id}/cancel`);
    return response.data;
  },

  getAdminClaims: async (params?: { status?: string; page?: number; page_size?: number }): Promise<AdminClaimsResponse> => {
    const response = await apiClient.get<AdminClaimsResponse>('/admin/claims', { params });
    return response.data;
  },

  getAdminClaim: async (id: number): Promise<Claim> => {
    const response = await apiClient.get<Claim>(`/admin/claims/${id}`);
    return response.data;
  },

  approveClaim: async (id: number, data?: ClaimReviewInput): Promise<Claim> => {
    const response = await apiClient.put<Claim>(`/admin/claims/${id}/approve`, data || {});
    return response.data;
  },

  rejectClaim: async (id: number, data?: ClaimReviewInput): Promise<Claim> => {
    const response = await apiClient.put<Claim>(`/admin/claims/${id}/reject`, data || {});
    return response.data;
  },
};

export const notificationApi = {
  getMyNotifications: async (unreadOnly = false): Promise<Notification[]> => {
    const response = await apiClient.get<Notification[]>('/notifications/my', {
      params: { unread_only: unreadOnly },
    });
    return response.data;
  },

  markAsRead: async (id: number): Promise<Notification> => {
    const response = await apiClient.put<Notification>(`/notifications/${id}/read`);
    return response.data;
  },

  markAllAsRead: async (): Promise<{ message: string; count: number }> => {
    const response = await apiClient.put<{ message: string; count: number }>('/notifications/read-all');
    return response.data;
  },
};

export const adminApi = {
  getStats: async (): Promise<AdminStats> => {
    const response = await apiClient.get<AdminStats>('/admin/stats');
    return response.data;
  },

  getAnalytics: async (period = '30d', fromDate?: string, toDate?: string): Promise<AdminAnalytics> => {
    const params: Record<string, string> = { period };
    if (fromDate) params.from_date = fromDate;
    if (toDate) params.to_date = toDate;
    const response = await apiClient.get<AdminAnalytics>('/admin/analytics', { params });
    return response.data;
  },

  getUsers: async (skip = 0, limit = 50): Promise<User[]> => {
    const response = await apiClient.get<User[]>('/users/', { params: { skip, limit } });
    return response.data;
  },
};

export const matchApi = {
  getItemMatches: async (
    itemId: number,
    minConfidence = 0.0,
    page = 1,
    pageSize = 10
  ): Promise<ItemMatchesResponse> => {
    const response = await apiClient.get<ItemMatchesResponse>(`/matches/item/${itemId}`, {
      params: { min_confidence: minConfidence, page, page_size: pageSize },
    });
    return response.data;
  },
};




