// frontend/src/components/organisms/RegisterForm/RegisterForm.tsx

import { useState, type ComponentProps } from "react";
import { useTranslation } from "node_modules/react-i18next";
import {
  FilePenLine,
  LockKeyhole,
  Mail,
  UserRound,
  ShieldCheck,
} from "lucide-react";
import { Button } from "../../atoms";
import { FormField } from "../../molecules";
import type { UserRegisterRequest, UserRole } from "@/api/types/auth";
import "../LoginForm/AuthForm.css";

const registerableRoles: UserRole[] = ["Learner", "Instructor"];

type RegisterFormProps = {
  isSubmitting?: boolean;
  error?: string | null;
  onSubmit: (payload: UserRegisterRequest) => Promise<void> | void;
};

export function RegisterForm({
  isSubmitting = false,
  error,
  onSubmit,
}: RegisterFormProps) {
  const { t } = useTranslation("auth");

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<UserRole>("Learner");
  const [password, setPassword] = useState("");

  const handleSubmit: ComponentProps<"form">["onSubmit"] = (event) => {
    event.preventDefault();

    void onSubmit({
      full_name: fullName.trim(),
      email: email.trim(),
      role,
      password,
    });
  };

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <FormField
        label={t("register.fullName")}
        value={fullName}
        icon={<UserRound size={16} strokeWidth={2.2} />}
        placeholder={t("register.fullNamePlaceholder")}
        onChange={(event) => setFullName(event.currentTarget.value)}
        autoComplete="name"
        required
      />

      <FormField
        label={t("register.email")}
        type="email"
        value={email}
        icon={<Mail size={16} strokeWidth={2.2} />}
        placeholder={t("register.emailPlaceholder")}
        onChange={(event) => setEmail(event.currentTarget.value)}
        autoComplete="email"
        required
      />

      <label
        className="ui-form-field ui-form-field--row"
        htmlFor="register-role"
      >
        <span className="ui-form-field__label">{t("register.role")}</span>

        <span className="ui-form-field__control">
          <span className="ui-form-field__icon" aria-hidden="true">
            <ShieldCheck size={16} strokeWidth={2.2} />
          </span>

          <select
            id="register-role"
            className="ui-form-field__input--with-icon"
            value={role}
            onChange={(event) => setRole(event.currentTarget.value as UserRole)}
          >
            {registerableRoles.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </span>
      </label>

      <FormField
        label={t("register.password")}
        type="password"
        value={password}
        icon={<LockKeyhole size={16} strokeWidth={2.2} />}
        placeholder={t("register.passwordPlaceholder")}
        onChange={(event) => setPassword(event.currentTarget.value)}
        autoComplete="new-password"
        required
      />

      {error && <p className="auth-form__error">{error}</p>}

      <Button type="submit" isLoading={isSubmitting} fullWidth>
        <FilePenLine size={16} strokeWidth={2.3} aria-hidden="true" />
        {t("register.submit")}
      </Button>
    </form>
  );
}
