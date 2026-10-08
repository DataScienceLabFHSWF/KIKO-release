// frontend/src/features/profile/pages/ProfilePage.tsx

import { useState } from "react";
import { BadgeCheck, UserRound } from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { useAuth } from "@/app/providers/AuthProvider";
import {
  ErrorState,
  LoadingState,
  PageHeader,
  ProfileForm,
} from "@/components";
import type { UserProfileUpdateRequest } from "@/api/types/auth";
import { usePageMeta } from "@/app/hooks/usePageMeta";
import { updateCurrentUserProfile } from "../api/ProfileApi";
import "./ProfilePage.css";

export function ProfilePage() {
  const { t } = useTranslation("profile");
  const { user, isLoading, updateSessionUser, restoreSession } = useAuth();

  usePageMeta({
    title: t("title"),
  });

  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  async function handleSave(payload: UserProfileUpdateRequest) {
    setError(null);
    setSuccessMessage(null);
    setIsSaving(true);

    try {
      const updatedProfile = await updateCurrentUserProfile(payload);
      updateSessionUser(updatedProfile);
      setSuccessMessage(t("messages.saved"));
    } catch (error) {
      setError(
        error instanceof Error ? error.message : t("messages.saveFailed"),
      );
    } finally {
      setIsSaving(false);
    }
  }

  if (isLoading) {
    return <LoadingState description={t("messages.loading")} />;
  }

  if (!user) {
    return (
      <ErrorState
        title={t("messages.unavailableTitle")}
        description={t("messages.unavailableDescription")}
        actionLabel={t("actions.retry")}
        onAction={() => void restoreSession()}
      />
    );
  }

  return (
    <section className="profile-page">
      <PageHeader
        icon={<UserRound size={28} strokeWidth={2.2} />}
        title={t("title")}
        subtitle={t("subtitle")}
        action={
          successMessage ? (
            <div className="profile-page__success" role="status">
              <BadgeCheck size={16} strokeWidth={2.2} />
              {successMessage}
            </div>
          ) : null
        }
      />

      <div className="profile-page__card">
        <ProfileForm
          profile={user}
          isSaving={isSaving}
          error={error}
          onSave={handleSave}
        />
      </div>
    </section>
  );
}
