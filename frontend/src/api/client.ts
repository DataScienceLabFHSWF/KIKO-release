// frontend/src/api/client.ts
import { ApiClientError, type ApiErrorPayload } from "./errors";
import { getStoredToken } from "../features/auth/AuthStorage";
import { getStoredLanguage } from "@/i18n/LanguageStorage";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

type RequestOptions = RequestInit & {
  auth?: boolean;
};

async function parseError(
  response: Response,
): Promise<ApiErrorPayload | undefined> {
  try {
    return await response.json();
  } catch {
    return undefined;
  }
}

function buildHeaders(options: RequestOptions): Headers {
  const token = getStoredToken();
  const headers = new Headers(options.headers);

  if (options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  if (!headers.has("Accept-Language")) {
    headers.set("Accept-Language", getStoredLanguage());
  }

  if (options.auth !== false && token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  return headers;
}

// BE API successful response is JSON? then use apiRequest
export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const headers = buildHeaders(options);

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  if (!response.ok) {
    const payload = await parseError(response);
    throw new ApiClientError(response.status, payload);
  }

  return response.json() as Promise<T>;
}

// Use apiBlob() for /files/.../preview.png, /files/.../page/...png, image downloads, and file downloads.
export async function apiBlob(
  path: string,
  options: RequestOptions = {},
): Promise<Blob> {
  const headers = buildHeaders(options);

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const payload = await parseError(response);
    throw new ApiClientError(response.status, payload);
  }

  return response.blob();
}

// Use apiText() for /learner/course-template/md
export async function apiText(
  path: string,
  options: RequestOptions = {},
): Promise<string> {
  const headers = buildHeaders(options);

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const payload = await parseError(response);
    throw new ApiClientError(response.status, payload);
  }

  return response.text();
}
