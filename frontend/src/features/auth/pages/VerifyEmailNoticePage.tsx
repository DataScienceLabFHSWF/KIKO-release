// frontend/src/features/auth/pages/VerifyEmailNoticePage.tsx

import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useTranslation } from "node_modules/react-i18next";
import { MailCheck, RotateCcw, LockKeyhole } from "lucide-react";
import { AuthLayout, Button } from "@/components";
import { resendVerificationEmail } from "../api/AuthApi";
import { usePageMeta } from "@/app/hooks/usePageMeta";

type LocationState = {
  email?: string;
};

export function VerifyEmailNoticePage() {
  const { t } = useTranslation("auth");
  const location = useLocation();

  const state = location.state as LocationState | null;
  const email = state?.email ?? "";

  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);

  usePageMeta({
    title: t("verifyEmailNotice.title"),
  });

  async function handleResend() {
    if (!email) {
      setError(t("verifyEmailNotice.missingEmail"));
      return;
    }

    setMessage(null);
    setError(null);
    setIsSending(true);

    try {
      await resendVerificationEmail({ email });
      setMessage(t("verifyEmailNotice.resent"));
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : t("verifyEmailNotice.resendFailed"),
      );
    } finally {
      setIsSending(false);
    }
  }

  return (
    <AuthLayout
      title={t("verifyEmailNotice.title")}
      titleIcon={<MailCheck size={34} strokeWidth={2.4} />}
      footer={
        <Link to="/login">
          <LockKeyhole size={18} strokeWidth={2.2} />
          {t("verifyEmailNotice.backToLogin")}
        </Link>
      }
    >
      <div className="auth-panel-message">
        <p>{t("verifyEmailNotice.description")}</p>

        {email ? (
          <p>
            <strong>{email}</strong>
          </p>
        ) : null}

        {message ? <div className="form-success">{message}</div> : null}
        {error ? <div className="form-error">{error}</div> : null}

        <Button
          type="button"
          variant="secondary"
          onClick={handleResend}
          isLoading={isSending}
          disabled={isSending || !email}
          leftIcon={<RotateCcw size={18} />}
        >
          {t("verifyEmailNotice.resend")}
        </Button>
      </div>
    </AuthLayout>
  );
}
