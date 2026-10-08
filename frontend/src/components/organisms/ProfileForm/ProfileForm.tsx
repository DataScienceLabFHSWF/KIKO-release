// frontend/src/components/organisms/ProfileForm/ProfileForm.tsx

import { useEffect, useMemo, useState, type ComponentProps } from "react";
import {
  CalendarClock,
  ImageIcon,
  Mail,
  RotateCcw,
  Save,
  ShieldCheck,
  UserRound,
} from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { Button, ReadOnlyField } from "../../atoms";
import { FormField } from "../../molecules";
import type {
  UserProfileResponse,
  UserProfileUpdateRequest,
} from "@/api/types/auth";
import "./ProfileForm.css";

type ProfileFormProps = {
  profile: UserProfileResponse;
  isSaving?: boolean;
  error?: string | null;
  onSave: (payload: UserProfileUpdateRequest) => Promise<void> | void;
};

export function ProfileForm({
  profile,
  isSaving = false,
  error,
  onSave,
}: ProfileFormProps) {
  const { t } = useTranslation("profile");

  const [fullName, setFullName] = useState(profile.full_name);
  const [avatar, setAvatar] = useState(profile.avatar ?? "");

  useEffect(() => {
    setFullName(profile.full_name);
    setAvatar(profile.avatar ?? "");
  }, [profile]);

  const isDirty = useMemo(() => {
    return (
      fullName.trim() !== profile.full_name ||
      avatar.trim() !== (profile.avatar ?? "")
    );
  }, [fullName, avatar, profile]);

  const canSave = fullName.trim().length >= 3 && isDirty && !isSaving;

  const handleSubmit: ComponentProps<"form">["onSubmit"] = (event) => {
    event.preventDefault();

    if (!canSave) return;

    const payload: UserProfileUpdateRequest = {
      full_name: fullName.trim(),
      avatar: avatar.trim() || null,
    };

    void onSave(payload);
  };

  function handleReset() {
    setFullName(profile.full_name);
    setAvatar(profile.avatar ?? "");
  }

  return (
    <form className="profile-form" onSubmit={handleSubmit}>
      <div className="profile-form__editable">
        <FormField
          label={t("fields.fullName")}
          value={fullName}
          icon={<UserRound size={16} strokeWidth={2.2} />}
          placeholder={t("placeholders.fullName")}
          onChange={(event) => setFullName(event.currentTarget.value)}
          autoComplete="name"
          required
        />

        <FormField
          label={t("fields.avatar")}
          value={avatar}
          icon={<ImageIcon size={16} strokeWidth={2.2} />}
          placeholder={t("placeholders.avatar")}
          onChange={(event) => setAvatar(event.currentTarget.value)}
        />
      </div>

      <div className="profile-form__locked">
        <ReadOnlyField
          label={t("fields.email")}
          value={
            <span className="profile-form__readonly-with-icon">
              <Mail size={15} strokeWidth={2.2} />
              {profile.email}
            </span>
          }
          helperText={t("helpers.emailLocked")}
        />

        <ReadOnlyField
          label={t("fields.role")}
          value={
            <span className="profile-form__readonly-with-icon">
              <ShieldCheck size={15} strokeWidth={2.2} />
              {profile.role}
            </span>
          }
          helperText={t("helpers.roleLocked")}
        />

        <ReadOnlyField
          label={t("fields.joined")}
          value={
            <span className="profile-form__readonly-with-icon">
              <CalendarClock size={15} strokeWidth={2.2} />
              {new Date(profile.joined).toLocaleDateString()}
            </span>
          }
        />

        <ReadOnlyField
          label={t("fields.lastLogin")}
          value={
            profile.last_login
              ? new Date(profile.last_login).toLocaleString()
              : t("notAvailable")
          }
        />
      </div>

      {error && <p className="profile-form__error">{error}</p>}

      {!isDirty && <p className="profile-form__hint">{t("hints.noChanges")}</p>}

      <div className="profile-form__actions">
        <Button
          type="button"
          variant="ghost"
          disabled={!isDirty || isSaving}
          onClick={handleReset}
        >
          <RotateCcw size={15} strokeWidth={2.2} aria-hidden="true" />
          {t("actions.reset")}
        </Button>

        <Button type="submit" isLoading={isSaving} disabled={!canSave}>
          <Save size={15} strokeWidth={2.2} aria-hidden="true" />
          {t("actions.save")}
        </Button>
      </div>
    </form>
  );
}
