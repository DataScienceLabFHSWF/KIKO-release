// frontend/src/api/types/auth.ts

export type UserRole = "Learner" | "Instructor" | "Admin";

export type UserLoginRequest = {
  email: string;
  password: string;
};

export type UserLoginResponse = {
  access_token: string;
  token_type: "bearer";
};

export type UserRegisterRequest = {
  email: string;
  password: string;
  role: UserRole;
  full_name: string;
};

export type UserPublicResponse = {
  user_id: number;
  email: string;
  role: UserRole;
  full_name: string;
  avatar?: string | null;
  email_verified: boolean;
};

export type UserRegisterResponse = {
  message: "success";
  user: UserPublicResponse;
  default_course_report?: Record<string, unknown> | null;
};

export type UserProfileResponse = {
  user_id: number;
  email: string;
  full_name: string;
  role: UserRole;
  avatar?: string | null;
  joined: string;
  last_login?: string | null;
};

export type UserProfileUpdateRequest = {
  full_name?: string;
  avatar?: string | null;
};

export type GenericSuccessResponse = {
  message: "success";
};

export type ForgotPasswordRequest = {
  email: string;
};

export type ResetPasswordRequest = {
  token: string;
  new_password: string;
};

export type ChangePasswordRequest = {
  current_password: string;
  new_password: string;
};

export type ChangePasswordResponse = {
  message: "success";
  access_token: string;
  token_type: "bearer";
};

export type VerifyEmailRequest = {
  token: string;
};

export type ResendVerificationEmailRequest = {
  email: string;
};
