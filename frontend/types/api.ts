export type ApiResponse<T> = {
  success: boolean;
  message: string;
  data: T;
};

export type PaginatedApiResponse<T> = {
  success: boolean;
  message: string;
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
};

export type ApiError = {
  success: false;
  message: string;
  error_code: string;
  details?: Record<string, unknown>;
};
