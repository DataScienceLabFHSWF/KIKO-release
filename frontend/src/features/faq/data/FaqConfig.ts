// frontend/src/features/faq/data/FaqConfig.ts

import type { LucideIcon } from "lucide-react";
import {
  BarChart3,
  BookOpen,
  Bot,
  ClipboardCheck,
  FileText,
  HelpCircle,
  Image,
  LayoutDashboard,
  SearchCheck,
  Settings,
  UserRound,
  Wrench,
  PenLine,
} from "lucide-react";
import type { UserRole } from "@/api/types/auth";

export type FaqQuickLink = {
  key: string;
  to: string;
  icon: LucideIcon;
  roles: readonly UserRole[];
};

export type FaqItemConfig = {
  key: string;
  roles: readonly UserRole[];
};

export const faqQuickLinks: readonly FaqQuickLink[] = [
  {
    key: "learningDashboard",
    to: "/dashboard",
    icon: BarChart3,
    roles: ["Learner"],
  },
  {
    key: "myCourses",
    to: "/courses",
    icon: BookOpen,
    roles: ["Learner", "Instructor"],
  },
  {
    key: "mediaManager",
    to: "/media-manager",
    icon: Image,
    roles: ["Instructor"],
  },
  {
    key: "courseGenerator",
    to: "/course-generator",
    icon: PenLine,
    roles: ["Instructor"],
  },
  {
    key: "chatAssistant",
    to: "/chat",
    icon: Bot,
    roles: ["Learner", "Instructor"],
  },
  {
    key: "knowledgeAssessment",
    to: "/knowledge-assessment",
    icon: ClipboardCheck,
    roles: ["Learner"],
  },
  {
    key: "adminDashboard",
    to: "/admin",
    icon: LayoutDashboard,
    roles: ["Admin"],
  },
  {
    key: "knowledgeCheckConfig",
    to: "/knowledge-check-config",
    icon: Settings,
    roles: ["Admin"],
  },
  {
    key: "adminConsole",
    to: "/admin-console",
    icon: Wrench,
    roles: ["Admin"],
  },
  {
    key: "myDocuments",
    to: "/documents",
    icon: FileText,
    roles: ["Learner", "Instructor", "Admin"],
  },
  {
    key: "profile",
    to: "/profile",
    icon: UserRound,
    roles: ["Learner", "Instructor", "Admin"],
  },
  {
    key: "faq",
    to: "/faq",
    icon: HelpCircle,
    roles: ["Learner", "Instructor", "Admin"],
  },
  {
    key: "evaluationResults",
    to: "/evaluation",
    icon: SearchCheck,
    roles: ["Learner", "Instructor", "Admin"],
  },
];

export const learnerFaqItems: readonly FaqItemConfig[] = [
  { key: "learningDashboard", roles: ["Learner"] },
  { key: "chatAssistant", roles: ["Learner"] },
  { key: "myCoursesLearner", roles: ["Learner"] },
  { key: "knowledgeAssessment", roles: ["Learner"] },
  { key: "myDocumentsLearner", roles: ["Learner"] },
  { key: "profileEvaluation", roles: ["Learner"] },
];

export const instructorFaqItems: readonly FaqItemConfig[] = [
  { key: "chatAssistant", roles: ["Instructor"] },
  { key: "courseGenerator", roles: ["Instructor"] },
  { key: "myCoursesInstructor", roles: ["Instructor"] },
  { key: "mediaManager", roles: ["Instructor"] },
  { key: "myDocumentsInstructor", roles: ["Instructor"] },
  { key: "profileEvaluation", roles: ["Instructor"] },
];

export const adminFaqItems: readonly FaqItemConfig[] = [
  { key: "adminDashboard", roles: ["Admin"] },
  { key: "knowledgeCheckConfig", roles: ["Admin"] },
  { key: "adminConsole", roles: ["Admin"] },
  { key: "myDocumentsAdmin", roles: ["Admin"] },
  { key: "profileEvaluation", roles: ["Admin"] },
];

export const commonFaqItems: readonly FaqItemConfig[] = [
  { key: "confirmations", roles: ["Learner", "Instructor", "Admin"] },
  { key: "recommendations", roles: ["Learner", "Instructor", "Admin"] },
  { key: "uploadsPreviews", roles: ["Learner", "Instructor", "Admin"] },
];

export function getRoleFaqItems(role: UserRole) {
  if (role === "Admin") return adminFaqItems;
  if (role === "Instructor") return instructorFaqItems;
  return learnerFaqItems;
}
