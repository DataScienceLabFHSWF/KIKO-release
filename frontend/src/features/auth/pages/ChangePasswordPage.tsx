// frontend/src/features/auth/pages/ChangePasswordPage.tsx

import { useState, type ComponentProps } from "react";
import { KeyRound, RotateCcw, Save } from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { useAuth } from "@/app/providers/AuthProvider";
import { usePageMeta } from "@/app/hooks/usePageMeta";
import { Button, PageHeader } from "@/components";
import { changePassword } from "../api/AuthApi";
import "./ChangePasswordPage.css";

export function ChangePasswordPage() {
  const { t } = useTranslation("auth");
  const { replaceAccessToken } = useAuth();

  usePageMeta({
    title: t("changePassword.title"),
  });

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [isSubmitting, setIsSubmitting] = useState(false);

  const canSubmit =
    currentPassword.length >= 8 &&
    newPassword.length >= 8 &&
    confirmPassword.length >= 8 &&
    !isSubmitting;

  function handleReset() {
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
    setError(null);
    setSuccessMessage(null);
  }

  const handleSubmit: ComponentProps<"form">["onSubmit"] = async (event) => {
    event.preventDefault();

    setError(null);
    setSuccessMessage(null);

    if (newPassword !== confirmPassword) {
      setError(t("changePassword.passwordMismatch"));
      return;
    }

    if (currentPassword === newPassword) {
      setError(t("changePassword.samePassword"));
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });

      await replaceAccessToken(response.access_token);

      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setSuccessMessage(t("changePassword.success"));
    } catch (error) {
      setError(
        error instanceof Error ? error.message : t("changePassword.failed"),
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="change-password-page">
      <PageHeader
        icon={<KeyRound size={42} strokeWidth={1.8} />}
        title={t("changePassword.title")}
        subtitle={t("changePassword.subtitle")}
      />

      <form className="change-password-card" onSubmit={handleSubmit}>
        <label className="change-password-card__field">
          <span>{t("changePassword.currentPassword")}</span>
          <input
            type="password"
            value={currentPassword}
            autoComplete="current-password"
            minLength={8}
            required
            disabled={isSubmitting}
            onChange={(event) => setCurrentPassword(event.currentTarget.value)}
          />
        </label>

        <label className="change-password-card__field">
          <span>{t("changePassword.newPassword")}</span>
          <input
            type="password"
            value={newPassword}
            autoComplete="new-password"
            minLength={8}
            required
            disabled={isSubmitting}
            onChange={(event) => setNewPassword(event.currentTarget.value)}
          />
        </label>

        <label className="change-password-card__field">
          <span>{t("changePassword.confirmPassword")}</span>
          <input
            type="password"
            value={confirmPassword}
            autoComplete="new-password"
            minLength={8}
            required
            disabled={isSubmitting}
            onChange={(event) => setConfirmPassword(event.currentTarget.value)}
          />
        </label>

        {error && (
          <p className="change-password-card__error" role="alert">
            {error}
          </p>
        )}

        {successMessage && (
          <p className="change-password-card__success" role="status">
            {successMessage}
          </p>
        )}

        <div className="change-password-card__actions">
          <Button
            type="button"
            variant="ghost"
            onClick={handleReset}
            disabled={isSubmitting}
          >
            <RotateCcw size={16} strokeWidth={2.3} />
            {t("changePassword.reset")}
          </Button>

          <Button type="submit" isLoading={isSubmitting} disabled={!canSubmit}>
            <Save size={16} strokeWidth={2.3} />
            {isSubmitting
              ? t("changePassword.saving")
              : t("changePassword.save")}
          </Button>
        </div>
      </form>
    </section>
  );
}
