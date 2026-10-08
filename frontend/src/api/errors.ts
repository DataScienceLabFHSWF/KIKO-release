// frontend/src/api/errors.ts
export type ApiErrorPayload = {
  error?: {
    code?: string;
    message?: string;
    details?: unknown;
    request_id?: string | null;
  };
};

export class ApiClientError extends Error {
  status: number;
  code?: string;
  details?: unknown;
  requestId?: string | null;

  constructor(status: number, payload?: ApiErrorPayload) {
    super(payload?.error?.message ?? `Request failed with status ${status}`);
    this.status = status;
    this.code = payload?.error?.code;
    this.details = payload?.error?.details;
    this.requestId = payload?.error?.request_id;
  }
}
