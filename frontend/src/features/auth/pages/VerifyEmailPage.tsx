// frontend/src/features/auth/pages/VerifyEmailPage.tsx

import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useTranslation } from "node_modules/react-i18next";
import { CheckCircle2, LockKeyhole, XCircle } from "lucide-react";
import { AuthLayout } from "@/components";
import { verifyEmail } from "../api/AuthApi";
import { usePageMeta } from "@/app/hooks/usePageMeta";

type VerifyStatus = "loading" | "success" | "error";

export function VerifyEmailPage() {
  const { t } = useTranslation("auth");
  const [searchParams] = useSearchParams();

  const token = useMemo(() => searchParams.get("token") ?? "", [searchParams]);

  const [status, setStatus] = useState<VerifyStatus>("loading");
  const [error, setError] = useState<string | null>(null);

  usePageMeta({
    title: t("verifyEmail.title"),
  });

  useEffect(() => {
    let isMounted = true;

    async function runVerification() {
      if (!token) {
        setStatus("error");
        setError(t("verifyEmail.missingToken"));
        return;
      }

      try {
        await verifyEmail({ token });

        if (isMounted) {
          setStatus("success");
        }
      } catch (error) {
        if (isMounted) {
          setStatus("error");
          setError(
            error instanceof Error ? error.message : t("verifyEmail.failed"),
          );
        }
      }
    }

    runVerification();

    return () => {
      isMounted = false;
    };
  }, [token, t]);

  const isSuccess = status === "success";

  return (
    <AuthLayout
      title={isSuccess ? t("verifyEmail.successTitle") : t("verifyEmail.title")}
      titleIcon={
        isSuccess ? (
          <CheckCircle2 size={34} strokeWidth={2.4} />
        ) : (
          <XCircle size={34} strokeWidth={2.4} />
        )
      }
      footer={
        <Link to="/login">
          <LockKeyhole size={18} strokeWidth={2.2} />
          {t("verifyEmail.login")}
        </Link>
      }
    >
      <div className="auth-panel-message">
        {status === "loading" ? <p>{t("verifyEmail.loading")}</p> : null}

        {status === "success" ? (
          <div className="form-success">{t("verifyEmail.successMessage")}</div>
        ) : null}

        {status === "error" ? (
          <div className="form-error">{error ?? t("verifyEmail.failed")}</div>
        ) : null}
      </div>
    </AuthLayout>
  );
}
