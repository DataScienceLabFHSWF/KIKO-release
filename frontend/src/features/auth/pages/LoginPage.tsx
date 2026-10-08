// frontend/src/features/auth/pages/LoginPage.tsx

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "node_modules/react-i18next";
import { LockKeyhole, FilePenLine } from "lucide-react";
import { useAuth } from "@/app/providers/AuthProvider";
import { LoginForm, AuthLayout } from "@/components";
import type { UserLoginRequest } from "@/api/types/auth";
import { usePageMeta } from "@/app/hooks/usePageMeta";
import "./LoginPage.css";

export function LoginPage() {
  const { t } = useTranslation("auth");

  usePageMeta({
    title: t("login.title"),
  });

  const { login } = useAuth();
  const navigate = useNavigate();

  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleLogin(payload: UserLoginRequest) {
    setError(null);
    setIsSubmitting(true);

    try {
      await login(payload);
      navigate("/dashboard", { replace: true });
    } catch (error) {
      setError(error instanceof Error ? error.message : t("login.failed"));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthLayout
      title={t("login.title")}
      titleIcon={<LockKeyhole size={34} strokeWidth={2.4} />}
      footer={
        <div className="auth-footer-stack">
          <Link to="/forgot-password">
            <LockKeyhole size={18} strokeWidth={2.2} />
            {t("login.forgotPassword")}
          </Link>

          <span>
            {t("login.noAccount")}{" "}
            <Link to="/register">
              <FilePenLine size={18} strokeWidth={2.2} />
              {t("login.createAccount")}
            </Link>
          </span>
        </div>
      }
    >
      <LoginForm
        isSubmitting={isSubmitting}
        error={error}
        onSubmit={handleLogin}
      />
    </AuthLayout>
  );
}
