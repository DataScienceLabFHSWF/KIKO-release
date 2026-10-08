// frontend/src/i18n/i18n.ts

import i18n from "i18next";
import { initReactI18next } from "node_modules/react-i18next";

// ENGLISH IMPORT
import enCommon from "../locales/en/Common.json";
import enAuth from "../locales/en/Auth.json";
import enSidebar from "../locales/en/Sidebar.json";
import enChatAssistant from "../locales/en/ChatAssistant.json";
import enProfile from "../locales/en/Profile.json";
import enMyDocuments from "../locales/en/MyDocuments.json";
import enFaq from "../locales/en/Faq.json";
import enEvaluation from "../locales/en/Evaluation.json";
import enLearnerDashboard from "../locales/en/LearnerDashboard.json";
import enInstructorDashboard from "../locales/en/InstructorDashboard.json";
import enAdminDashboard from "../locales/en/AdminDashboard.json";
import enCourses from "../locales/en/Courses.json";
import enCourseDetails from "../locales/en/CourseDetails.json";
import enKnowledgeAssessment from "../locales/en/KnowledgeAssessment.json";
import enCourseGenerator from "../locales/en/CourseGenerator.json";
import enMediaManager from "../locales/en/MediaManager.json";
import enCoursePreview from "../locales/en/CoursePreview.json";
import enAdminKnowledgeCheck from "../locales/en/AdminKnowledgeCheck.json";
import enAdminAppConfig from "../locales/en/AdminAppConfig.json";

// GERMAN IMPORT
import deCommon from "../locales/de/Common.json";
import deAuth from "../locales/de/Auth.json";
import deSidebar from "../locales/de/Sidebar.json";
import deChatAssistant from "../locales/de/ChatAssistant.json";
import deProfile from "../locales/de/Profile.json";
import deMyDocuments from "../locales/de/MyDocuments.json";
import deFaq from "../locales/de/Faq.json";
import deEvaluation from "../locales/de/Evaluation.json";
import deLearnerDashboard from "../locales/de/LearnerDashboard.json";
import deInstructorDashboard from "../locales/de/InstructorDashboard.json";
import deAdminDashboard from "../locales/de/AdminDashboard.json";
import deCourses from "../locales/de/Courses.json";
import deCourseDetails from "../locales/de/CourseDetails.json";
import deKnowledgeAssessment from "../locales/de/KnowledgeAssessment.json";
import deCourseGenerator from "../locales/de/CourseGenerator.json";
import deMediaManager from "../locales/de/MediaManager.json";
import deCoursePreview from "../locales/de/CoursePreview.json";
import deAdminKnowledgeCheck from "../locales/de/AdminKnowledgeCheck.json";
import deAdminAppConfig from "../locales/de/AdminAppConfig.json";

export const supportedLanguages = ["en", "de"] as const;
export type SupportedLanguage = (typeof supportedLanguages)[number];

const storedLanguage = localStorage.getItem("kiko.lang");

const initialLanguage: SupportedLanguage =
  storedLanguage === "de" || storedLanguage === "en" ? storedLanguage : "en";

void i18n.use(initReactI18next).init({
  resources: {
    en: {
      common: enCommon,
      auth: enAuth,
      sidebar: enSidebar,
      chatAssistant: enChatAssistant,
      profile: enProfile,
      myDocuments: enMyDocuments,
      faq: enFaq,
      evaluation: enEvaluation,
      learnerDashboard: enLearnerDashboard,
      instructorDashboard: enInstructorDashboard,
      adminDashboard: enAdminDashboard,
      courses: enCourses,
      courseDetails: enCourseDetails,
      knowledgeAssessment: enKnowledgeAssessment,
      courseGenerator: enCourseGenerator,
      mediaManager: enMediaManager,
      coursePreview: enCoursePreview,
      adminKnowledgeCheck: enAdminKnowledgeCheck,
      adminAppConfig: enAdminAppConfig,
    },
    de: {
      common: deCommon,
      auth: deAuth,
      sidebar: deSidebar,
      chatAssistant: deChatAssistant,
      profile: deProfile,
      myDocuments: deMyDocuments,
      faq: deFaq,
      evaluation: deEvaluation,
      learnerDashboard: deLearnerDashboard,
      instructorDashboard: deInstructorDashboard,
      adminDashboard: deAdminDashboard,
      courses: deCourses,
      courseDetails: deCourseDetails,
      knowledgeAssessment: deKnowledgeAssessment,
      courseGenerator: deCourseGenerator,
      mediaManager: deMediaManager,
      coursePreview: deCoursePreview,
      adminKnowledgeCheck: deAdminKnowledgeCheck,
      adminAppConfig: deAdminAppConfig,
    },
  },
  lng: initialLanguage,
  fallbackLng: "en",
  supportedLngs: supportedLanguages,
  ns: [
    "common",
    "auth",
    "sidebar",
    "chatAssistant",
    "profile",
    "myDocuments",
    "faq",
    "evaluation",
    "learnerDashboard",
    "instructorDashboard",
    "adminDashboard",
    "courses",
    "courseDetails",
    "knowledgeAssessment",
    "courseGenerator",
    "mediaManager",
    "coursePreview",
    "adminKnowledgeCheck",
    "adminAppConfig",
  ],
  defaultNS: "common",
  fallbackNS: "common",
  interpolation: {
    escapeValue: false,
  },
  returnNull: false,
});

export default i18n;
