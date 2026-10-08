// frontend/src/components/organisms/Sidebar/sidebarConfig.ts

import {
  BarChart3,
  BookOpen,
  Bot,
  ClipboardCheck,
  FileText,
  HelpCircle,
  Image,
  SearchCheck,
  UserRound,
  Wrench,
  PenLine,
  Brain,
  KeyRound,
} from "lucide-react";
import type { UserRole } from "@/api/types/auth";

export type SidebarNavItem = {
  to: string;
  key: string;
  icon: React.ComponentType<{
    size?: number;
    strokeWidth?: number;
  }>;
  roles: readonly UserRole[];
};

export const sidebarNavItems: readonly SidebarNavItem[] = [
  {
    to: "/dashboard",
    key: "dashboard",
    icon: BarChart3,
    roles: ["Learner", "Instructor", "Admin"],
  },
  {
    to: "/courses",
    key: "myCourses",
    icon: BookOpen,
    roles: ["Learner", "Instructor"],
  },
  {
    to: "/chat",
    key: "chatAssistant",
    icon: Bot,
    roles: ["Learner", "Instructor", "Admin"],
  },
  {
    to: "/course-generator",
    key: "courseGenerator",
    icon: PenLine,
    roles: ["Instructor"],
  },
  {
    to: "/media-manager",
    key: "mediaManager",
    icon: Image,
    roles: ["Instructor"],
  },
  {
    to: "/knowledge-assessment",
    key: "knowledgeAssessment",
    icon: ClipboardCheck,
    roles: ["Learner"],
  },
  {
    to: "/knowledge-check-config",
    key: "knowledgeCheckConfig",
    icon: Brain,
    roles: ["Admin"],
  },
  {
    to: "/admin-console",
    key: "adminConsole",
    icon: Wrench,
    roles: ["Admin"],
  },
  {
    to: "/documents",
    key: "myDocuments",
    icon: FileText,
    roles: ["Learner", "Instructor", "Admin"],
  },
  {
    to: "/profile",
    key: "profile",
    icon: UserRound,
    roles: ["Learner", "Instructor", "Admin"],
  },
  {
    to: "/change-password",
    key: "changePassword",
    icon: KeyRound,
    roles: ["Learner", "Instructor", "Admin"],
  },
  {
    to: "/faq",
    key: "faq",
    icon: HelpCircle,
    roles: ["Learner", "Instructor", "Admin"],
  },
  {
    to: "/evaluation",
    key: "evaluationResults",
    icon: SearchCheck,
    roles: ["Learner", "Instructor", "Admin"],
  },
];
