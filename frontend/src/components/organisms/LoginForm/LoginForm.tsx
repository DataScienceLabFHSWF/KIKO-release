// frontend/src/components/organisms/LoginForm/LoginForm.tsx

import { useState, type ComponentProps } from "react";
import { useTranslation } from "node_modules/react-i18next";
import { LockKeyhole, Mail } from "lucide-react";
import { Button } from "../../atoms";
import { FormField } from "../../molecules";
import type { UserLoginRequest } from "@/api/types/auth";
import "./AuthForm.css";

type LoginFormProps = {
  isSubmitting?: boolean;
  error?: string | null;
  onSubmit: (payload: UserLoginRequest) => Promise<void> | void;
};

export function LoginForm({
  isSubmitting = false,
  error,
  onSubmit,
}: LoginFormProps) {
  const { t } = useTranslation("auth");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit: ComponentProps<"form">["onSubmit"] = (event) => {
    event.preventDefault();

    void onSubmit({
      email: email.trim(),
      password,
    });
  };

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <FormField
        label={t("login.email")}
        type="email"
        value={email}
        icon={<Mail size={16} strokeWidth={2.2} />}
        placeholder={t("login.emailPlaceholder")}
        onChange={(event) => setEmail(event.currentTarget.value)}
        autoComplete="email"
        required
      />

      <FormField
        label={t("login.password")}
        type="password"
        value={password}
        icon={<LockKeyhole size={16} strokeWidth={2.2} />}
        placeholder={t("login.passwordPlaceholder")}
        onChange={(event) => setPassword(event.currentTarget.value)}
        autoComplete="current-password"
        required
      />

      {error && <p className="auth-form__error">{error}</p>}

      <Button type="submit" isLoading={isSubmitting} fullWidth>
        <LockKeyhole size={16} strokeWidth={2.3} aria-hidden="true" />
        {t("login.submit")}
      </Button>
    </form>
  );
}
