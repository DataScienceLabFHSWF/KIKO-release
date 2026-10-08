// frontend/src/features/auth/api/AuthApi.ts

import { apiRequest } from "@/api/client";
import type {
  ForgotPasswordRequest,
  GenericSuccessResponse,
  ResetPasswordRequest,
  ChangePasswordRequest,
  ChangePasswordResponse,
  ResendVerificationEmailRequest,
  UserRegisterRequest,
  UserRegisterResponse,
  VerifyEmailRequest,
} from "@/api/types/auth";

export function registerUser(
  payload: UserRegisterRequest,
): Promise<UserRegisterResponse> {
  return apiRequest<UserRegisterResponse>("/authentication/register", {
    method: "POST",
    auth: false,
    body: JSON.stringify(payload),
  });
}

export function verifyEmail(
  payload: VerifyEmailRequest,
): Promise<GenericSuccessResponse> {
  return apiRequest<GenericSuccessResponse>("/authentication/verify-email", {
    method: "POST",
    auth: false,
    body: JSON.stringify(payload),
  });
}

export function resendVerificationEmail(
  payload: ResendVerificationEmailRequest,
): Promise<GenericSuccessResponse> {
  return apiRequest<GenericSuccessResponse>(
    "/authentication/resend-verification-email",
    {
      method: "POST",
      auth: false,
      body: JSON.stringify(payload),
    },
  );
}

export function forgotPassword(
  payload: ForgotPasswordRequest,
): Promise<GenericSuccessResponse> {
  return apiRequest<GenericSuccessResponse>("/authentication/forgot-password", {
    method: "POST",
    auth: false,
    body: JSON.stringify(payload),
  });
}

export function resetPassword(
  payload: ResetPasswordRequest,
): Promise<GenericSuccessResponse> {
  return apiRequest<GenericSuccessResponse>("/authentication/reset-password", {
    method: "POST",
    auth: false,
    body: JSON.stringify(payload),
  });
}

export function changePassword(
  payload: ChangePasswordRequest,
): Promise<ChangePasswordResponse> {
  return apiRequest<ChangePasswordResponse>("/authentication/change-password", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
