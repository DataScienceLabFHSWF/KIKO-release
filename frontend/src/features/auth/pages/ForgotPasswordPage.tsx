// frontend/src/features/auth/pages/ForgotPasswordPage.tsx

import { useState, type ComponentProps } from "react";
import { Link } from "react-router-dom";
import { MailCheck, LockKeyhole } from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { AuthLayout, Button } from "@/components";
import { usePageMeta } from "@/app/hooks/usePageMeta";
import { forgotPassword } from "../api/AuthApi";
import "./PasswordPage.css";

export function ForgotPasswordPage() {
  const { t } = useTranslation("auth");

  usePageMeta({
    title: t("forgotPassword.title"),
  });

  const [email, setEmail] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSent, setIsSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit: ComponentProps<"form">["onSubmit"] = async (event) => {
    event.preventDefault();

    setError(null);
    setIsSubmitting(true);

    try {
      await forgotPassword({
        email: email.trim(),
      });

      setIsSent(true);
    } catch (error) {
      setError(
        error instanceof Error ? error.message : t("forgotPassword.failed"),
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthLayout
      title={t("forgotPassword.title")}
      titleIcon={<MailCheck size={34} strokeWidth={2.4} />}
      footer={
        <Link to="/login">
          <LockKeyhole size={18} strokeWidth={2.2} />
          {t("forgotPassword.backToLogin")}
        </Link>
      }
    >
      {isSent ? (
        <p className="auth-form__success">{t("forgotPassword.success")}</p>
      ) : (
        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="auth-form__field">
            <span>{t("forgotPassword.emailLabel")}</span>

            <input
              type="email"
              value={email}
              autoComplete="email"
              required
              disabled={isSubmitting}
              placeholder={t("forgotPassword.emailPlaceholder")}
              onChange={(event) => setEmail(event.currentTarget.value)}
            />
          </label>

          {error && (
            <p className="auth-form__error" role="alert">
              {error}
            </p>
          )}

          <Button type="submit" isLoading={isSubmitting}>
            {isSubmitting
              ? t("forgotPassword.submitting")
              : t("forgotPassword.submit")}
          </Button>
        </form>
      )}
    </AuthLayout>
  );
}
