// frontend/src/features/auth/pages/ResetPasswordPage.tsx

import { useState, type ComponentProps } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { LockKeyhole, ShieldCheck } from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { AuthLayout, Button } from "@/components";
import { usePageMeta } from "@/app/hooks/usePageMeta";
import { resetPassword } from "../api/AuthApi";
import "./PasswordPage.css";

export function ResetPasswordPage() {
  const { t } = useTranslation("auth");
  const [searchParams] = useSearchParams();

  usePageMeta({
    title: t("resetPassword.title"),
  });

  const token = searchParams.get("token") ?? "";

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isReset, setIsReset] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit: ComponentProps<"form">["onSubmit"] = async (event) => {
    event.preventDefault();

    setError(null);

    if (!token) {
      setError(t("resetPassword.missingToken"));
      return;
    }

    if (newPassword !== confirmPassword) {
      setError(t("resetPassword.passwordMismatch"));
      return;
    }

    setIsSubmitting(true);

    try {
      await resetPassword({
        token,
        new_password: newPassword,
      });

      setIsReset(true);
    } catch (error) {
      setError(
        error instanceof Error ? error.message : t("resetPassword.failed"),
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthLayout
      title={t("resetPassword.title")}
      titleIcon={<ShieldCheck size={34} strokeWidth={2.4} />}
      footer={
        <Link to="/login">
          <LockKeyhole size={18} strokeWidth={2.2} />
          {t("resetPassword.backToLogin")}
        </Link>
      }
    >
      {isReset ? (
        <p className="auth-form__success">{t("resetPassword.success")}</p>
      ) : (
        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="auth-form__field">
            <span>{t("resetPassword.newPasswordLabel")}</span>

            <input
              type="password"
              value={newPassword}
              autoComplete="new-password"
              required
              minLength={8}
              disabled={isSubmitting}
              placeholder={t("resetPassword.newPasswordPlaceholder")}
              onChange={(event) => setNewPassword(event.currentTarget.value)}
            />
          </label>

          <label className="auth-form__field">
            <span>{t("resetPassword.confirmPasswordLabel")}</span>

            <input
              type="password"
              value={confirmPassword}
              autoComplete="new-password"
              required
              minLength={8}
              disabled={isSubmitting}
              placeholder={t("resetPassword.confirmPasswordPlaceholder")}
              onChange={(event) =>
                setConfirmPassword(event.currentTarget.value)
              }
            />
          </label>

          {error && (
            <p className="auth-form__error" role="alert">
              {error}
            </p>
          )}

          <Button type="submit" isLoading={isSubmitting}>
            {isSubmitting
              ? t("resetPassword.submitting")
              : t("resetPassword.submit")}
          </Button>
        </form>
      )}
    </AuthLayout>
  );
}
