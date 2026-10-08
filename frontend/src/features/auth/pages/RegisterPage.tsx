// frontend/src/features/auth/pages/RegisterPage.tsx

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "node_modules/react-i18next";
import { FilePenLine, LockKeyhole } from "lucide-react";
import { AuthLayout, RegisterForm } from "@/components";
import type { UserRegisterRequest } from "@/api/types/auth";
import { usePageMeta } from "@/app/hooks/usePageMeta";
import { registerUser } from "../api/AuthApi";

export function RegisterPage() {
  const { t } = useTranslation("auth");

  usePageMeta({
    title: t("register.title"),
  });

  const navigate = useNavigate();

  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleRegister(payload: UserRegisterRequest) {
    setError(null);
    setIsSubmitting(true);

    try {
      const response = await registerUser(payload);

      navigate("/verify-email-notice", {
        replace: true,
        state: {
          email: response.user.email,
        },
      });
    } catch (error) {
      setError(error instanceof Error ? error.message : t("register.failed"));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthLayout
      title={t("register.title")}
      titleIcon={<FilePenLine size={34} strokeWidth={2.4} />}
      footer={
        <>
          {t("register.hasAccount")}{" "}
          <Link to="/login">
            <LockKeyhole size={18} strokeWidth={2.2} />
            {t("register.login")}
          </Link>
        </>
      }
    >
      <RegisterForm
        isSubmitting={isSubmitting}
        error={error}
        onSubmit={handleRegister}
      />
    </AuthLayout>
  );
}
