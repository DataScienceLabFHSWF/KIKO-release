// frontend/src/app/router.tsx

import { createBrowserRouter, Navigate } from "react-router-dom";
import { AppShell } from "@/components";

import { LoginPage } from "@/features/auth/pages/LoginPage";
import { RegisterPage } from "@/features/auth/pages/RegisterPage";
import { ProtectedRoute, RoleRoute } from "@/features/auth/Guards";
import { AppRouteErrorPage } from "./AppRouteErrorPage";

import { ChatAssistantPage } from "@/features/chat/pages/ChatAssistantPage";
import { PlaceholderPage } from "@/features/dashboard/pages/PlaceholderPage";
import { DashboardPage } from "@/features/dashboard/pages/DashboardPage";
import { ProfilePage } from "@/features/profile/pages/ProfilePage";
import { MyDocumentsPage } from "@/features/documents/pages/MyDocumentsPage";
import { FaqPage } from "@/features/faq/pages/FaqPage";
import { EvaluationResultsPage } from "@/features/evaluation/pages/EvaluationResultsPage";
import { MyCoursesPage } from "@/features/courses/pages/MyCoursesPage";
import { LearnerCourseDetailsPage } from "@/features/courseDetails/pages/LearnerCourseDetailsPage";
import { KnowledgeAssessmentPage } from "@/features/knowledgeAssessment/pages/KnowledgeAssessmentPage";
import { CourseGeneratorPage } from "@/features/courseGenerator/pages/CourseGeneratorPage";
import { MediaManagerPage } from "@/features/mediaManager/pages/MediaManagerPage";
import { AdminKnowledgeCheckConfigPage } from "@/features/adminKnowledgeCheck/pages/AdminKnowledgeCheckConfigPage";
import { AdminAppConfigPage } from "@/features/adminAppConfig/pages/AdminAppConfigPage";
import { ForgotPasswordPage } from "@/features/auth/pages/ForgotPasswordPage";
import { ResetPasswordPage } from "@/features/auth/pages/ResetPasswordPage";
import { ChangePasswordPage } from "@/features/auth/pages/ChangePasswordPage";
import { VerifyEmailNoticePage } from "@/features/auth/pages/VerifyEmailNoticePage";
import { VerifyEmailPage } from "@/features/auth/pages/VerifyEmailPage";

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/register",
    element: <RegisterPage />,
  },
  {
    path: "/forgot-password",
    element: <ForgotPasswordPage />,
  },
  {
    path: "/reset-password",
    element: <ResetPasswordPage />,
  },
  {
    path: "/verify-email-notice",
    element: <VerifyEmailNoticePage />,
  },
  {
    path: "/verify-email",
    element: <VerifyEmailPage />,
  },
  {
    path: "/",
    element: <ProtectedRoute />,
    errorElement: <AppRouteErrorPage />,
    children: [
      {
        element: <AppShell />,
        children: [
          {
            index: true,
            element: <Navigate to="/dashboard" replace />,
          },

          /**
           * Shared dashboard URL.
           * URL stays /dashboard for Learner, Instructor, and Admin.
           */
          {
            path: "dashboard",
            element: <DashboardPage />,
          },

          /**
           * Shared authenticated routes.
           * Available for Learner, Instructor, and Admin.
           */
          {
            path: "chat",
            element: <ChatAssistantPage />,
          },
          {
            path: "documents",
            element: <MyDocumentsPage />,
          },
          {
            path: "profile",
            element: <ProfilePage />,
          },
          {
            path: "change-password",
            element: <ChangePasswordPage />,
          },
          {
            path: "faq",
            element: <FaqPage />,
          },
          {
            path: "evaluation",
            element: <EvaluationResultsPage />,
          },

          /**
           * Learner-only routes.
           */
          {
            element: <RoleRoute roles={["Learner"]} />,
            children: [
              {
                path: "courses/:courseId",
                element: <LearnerCourseDetailsPage />,
              },
              {
                path: "knowledge-assessment",
                element: <KnowledgeAssessmentPage />,
              },
            ],
          },

          /**
           * Learner + Instructor routes.
           */
          {
            element: <RoleRoute roles={["Learner", "Instructor"]} />,
            children: [
              {
                path: "courses",
                element: <MyCoursesPage />,
              },
            ],
          },

          /**
           * Instructor-only routes.
           */
          {
            element: <RoleRoute roles={["Instructor"]} />,
            children: [
              {
                path: "media-manager",
                element: <MediaManagerPage />,
              },
              {
                path: "course-generator",
                element: <CourseGeneratorPage />,
              },
            ],
          },

          /**
           * Admin-only routes.
           */
          {
            element: <RoleRoute roles={["Admin"]} />,
            children: [
              {
                path: "knowledge-check-config",
                element: <AdminKnowledgeCheckConfigPage />,
              },
              {
                path: "admin-console",
                element: <AdminAppConfigPage />,
              },
            ],
          },

          /**
           * Fallback inside authenticated app.
           */
          {
            path: "*",
            element: <Navigate to="/dashboard" replace />,
          },
        ],
      },
    ],
  },
  {
    path: "*",
    element: <Navigate to="/login" replace />,
  },
]);
