// frontend/src/features/coursePreview/components/CoursePreviewContent.tsx

import {
  AlertTriangle,
  BookOpen,
  BookOpenCheck,
  ClipboardCheck,
  FileQuestion,
  FileText,
  GraduationCap,
  Info,
  Settings,
} from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { MarkdownView } from "@/components";
import { CoursePreviewTabs } from "./CoursePreviewTabs";
import type {
  CoursePreviewCourse,
  CoursePreviewModule,
  CoursePreviewModuleTabKey,
  CoursePreviewQuiz,
  CoursePreviewSectionKey,
} from "../types/CoursePreview";

type CoursePreviewContentRenderers = {
  overview?: (course: CoursePreviewCourse) => React.ReactNode;
  courseInfo?: (course: CoursePreviewCourse) => React.ReactNode;
  module?: (params: {
    course: CoursePreviewCourse;
    module: CoursePreviewModule;
    moduleIndex: number;
    activeModuleTab: CoursePreviewModuleTabKey;
  }) => React.ReactNode;
  finalAssessment?: (course: CoursePreviewCourse) => React.ReactNode;
  grades?: (course: CoursePreviewCourse) => React.ReactNode;
  resources?: (course: CoursePreviewCourse) => React.ReactNode;
};

type CoursePreviewContentProps = {
  course: CoursePreviewCourse;
  activeSection: CoursePreviewSectionKey;
  activeModuleTab: CoursePreviewModuleTabKey;
  onModuleTabChange: (key: CoursePreviewModuleTabKey) => void;
  renderers?: CoursePreviewContentRenderers;
};

function getActiveModule(
  course: CoursePreviewCourse,
  activeSection: CoursePreviewSectionKey,
) {
  if (!activeSection.startsWith("module:")) return null;

  const moduleId = activeSection.replace("module:", "");
  const index = course.modules.findIndex((module) => module.id === moduleId);

  if (index < 0) return null;

  return {
    module: course.modules[index],
    index,
  };
}

function SectionTitle({
  icon,
  title,
}: {
  icon: React.ReactNode;
  title: string;
}) {
  return (
    <div className="course-preview-content__title">
      {icon}
      <h2>{title}</h2>
    </div>
  );
}

function ResourceList({ course }: { course: CoursePreviewCourse }) {
  const { t } = useTranslation("coursePreview");
  if (course.resources.length === 0) {
    return <p className="course-preview-empty">{t("sections.noItems")}</p>;
  }

  return (
    <div className="course-preview-resource-list">
      {course.resources.map((resource, index) => (
        <article key={`${resource.title}-${resource.url ?? index}`}>
          <strong>{resource.title}</strong>

          {resource.type && <span>{resource.type}</span>}

          {resource.url && (
            <a href={resource.url} target="_blank" rel="noreferrer">
              {resource.url}
            </a>
          )}
        </article>
      ))}
    </div>
  );
}

function CourseInfo({ course }: { course: CoursePreviewCourse }) {
  const { t } = useTranslation("coursePreview");
  return (
    <div className="course-preview-info">
      <div className="course-preview-info__card">
        <p>
          <strong>{t("sections.provider")}:</strong> {course.provider}
        </p>
        <p>
          <strong>{t("sections.language")}:</strong> {course.language}
        </p>
        <p>
          <strong>{t("sections.difficulty")}:</strong> {course.difficulty}
        </p>
        <p>
          <strong>{t("sections.duration")}:</strong> {course.duration}
        </p>
      </div>

      <h3>{t("sections.skillsAndTags")}</h3>
      {course.tags.length > 0 ? (
        <div className="course-preview-chip-list">
          {course.tags.map((tag) => (
            <span key={tag}>{tag}</span>
          ))}
        </div>
      ) : (
        <p className="course-preview-empty">{t("sections.noItems")}</p>
      )}

      <h3>{t("sections.prerequisites")}</h3>
      {course.prerequisites.length > 0 ? (
        <ul>
          {course.prerequisites.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="course-preview-info-box">
          {t("sections.noPrerequisites")}
        </p>
      )}

      <h3>{t("sections.instructors")}</h3>
      {course.instructors.length > 0 ? (
        <div className="course-preview-resource-list">
          {course.instructors.map((instructor, index) => (
            <article key={`${instructor.name}-${index}`}>
              <strong>{instructor.name}</strong>
              {instructor.bio && <p>{instructor.bio}</p>}
            </article>
          ))}
        </div>
      ) : (
        <p className="course-preview-empty">{t("sections.noItems")}</p>
      )}

      {course.gradingNotes.length > 0 && (
        <>
          <h3>{t("sections.gradingPolicy")}</h3>
          <ul>
            {course.gradingNotes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

function ReadOnlyQuiz({
  quiz,
  language,
}: {
  quiz?: CoursePreviewQuiz | null;
  language: string;
}) {
  const { t } = useTranslation("coursePreview");
  if (!quiz || quiz.questions.length === 0) {
    return <p className="course-preview-empty">{t("sections.noItems")}</p>;
  }

  return (
    <div className="course-preview-quiz">
      <h3>{quiz.title}</h3>

      {quiz.passPercent !== undefined && (
        <p className="course-preview-muted">
          {t("sections.passThreshold")}: {quiz.passPercent}%
        </p>
      )}

      {quiz.questions.map((question, index) => (
        <article key={question.id} className="course-preview-quiz__question">
          <h4>
            Q{index + 1}. {question.text}
          </h4>

          {question.type && (
            <p className="course-preview-muted">
              Type: {question.type}
              {question.points !== undefined
                ? ` · Points: ${question.points}`
                : ""}
            </p>
          )}

          {question.choices && question.choices.length > 0 && (
            <ul className="course-preview-choice-list">
              {question.choices.map((choice) => (
                <li key={choice.id}>
                  <span aria-hidden="true">{choice.correct ? "✅" : "◻️"}</span>
                  {choice.text}
                </li>
              ))}
            </ul>
          )}

          {question.correctAnswer !== undefined && (
            <p>
              <strong>{t("sections.correctAnswer")}</strong>{" "}
              {String(question.correctAnswer)}
            </p>
          )}
        </article>
      ))}
    </div>
  );
}

function PracticeList({
  module,
  language,
}: {
  module: CoursePreviewModule;
  language: string;
}) {
  const { t } = useTranslation("coursePreview");
  if (module.practiceQuestions.length === 0) {
    return <p className="course-preview-empty">{t("sections.noItems")}</p>;
  }

  return (
    <div className="course-preview-practice-list">
      {module.practiceQuestions.map((question, index) => (
        <article key={question.id}>
          <h3>
            Q{index + 1}. {question.prompt}
          </h3>

          {question.referenceAnswer && (
            <details>
              <summary>{t("sections.suggestedAnswer")}</summary>
              <p>{question.referenceAnswer}</p>
            </details>
          )}
        </article>
      ))}
    </div>
  );
}

function MisconceptionsList({
  module,
  language,
}: {
  module: CoursePreviewModule;
  language: string;
}) {
  const { t } = useTranslation("coursePreview");
  if (module.misconceptions.length === 0) {
    return <p className="course-preview-empty">{t("sections.noItems")}</p>;
  }

  return (
    <div className="course-preview-misconceptions">
      {module.misconceptions.map((item, index) => (
        <article key={`${item}-${index}`}>
          <p>{item}</p>
        </article>
      ))}
    </div>
  );
}

export function CoursePreviewContent({
  course,
  activeSection,
  activeModuleTab,
  onModuleTabChange,
  renderers,
}: CoursePreviewContentProps) {
  const { t } = useTranslation("coursePreview");
  const activeModule = getActiveModule(course, activeSection);

  if (activeSection === "overview") {
    return (
      <main className="course-preview-content">
        <SectionTitle
          icon={<BookOpen size={30} />}
          title={t("sections.overview")}
        />
        {renderers?.overview ? (
          renderers.overview(course)
        ) : (
          <MarkdownView
            content={course.overview || t("sections.noContent")}
            courseId={course.courseId}
          />
        )}
      </main>
    );
  }

  if (activeSection === "course-info") {
    return (
      <main className="course-preview-content">
        <SectionTitle
          icon={<Info size={30} />}
          title={t("sections.courseInfo")}
        />
        {renderers?.courseInfo ? (
          renderers.courseInfo(course)
        ) : (
          <CourseInfo course={course} />
        )}
      </main>
    );
  }

  if (activeModule) {
    const { module, index } = activeModule;

    if (renderers?.module) {
      return (
        <main className="course-preview-content">
          {renderers.module({
            course,
            module,
            moduleIndex: index,
            activeModuleTab,
          })}
        </main>
      );
    }

    return (
      <main className="course-preview-content">
        <SectionTitle icon={<BookOpen size={30} />} title={module.title} />

        <CoursePreviewTabs<CoursePreviewModuleTabKey>
          ariaLabel="Module sections"
          activeKey={activeModuleTab}
          onChange={onModuleTabChange}
          tabs={[
            {
              key: "content",
              label: t("sections.content"),
              icon: <BookOpen size={15} />,
            },
            {
              key: "practice",
              label: t("sections.practice"),
              icon: <FileQuestion size={15} />,
            },
            {
              key: "quiz",
              label: t("sections.moduleQuiz"),
              icon: <GraduationCap size={15} />,
            },
            {
              key: "further-reading",
              label: t("sections.furtherReading"),
              icon: <BookOpenCheck size={15} />,
            },
            {
              key: "misconceptions",
              label: t("sections.misconceptions"),
              icon: <AlertTriangle size={15} />,
            },
            {
              key: "meta",
              label: t("sections.meta"),
              icon: <Settings size={15} />,
            },
          ]}
        />

        {activeModuleTab === "content" && (
          <MarkdownView
            content={module.content || t("sections.noContent")}
            courseId={course.courseId}
          />
        )}

        {activeModuleTab === "practice" && (
          <PracticeList module={module} language={course.language} />
        )}

        {activeModuleTab === "quiz" && (
          <ReadOnlyQuiz quiz={module.quiz} language={course.language} />
        )}

        {activeModuleTab === "further-reading" && (
          <div className="course-preview-resource-list">
            {module.furtherReading.length === 0 ? (
              <p className="course-preview-empty">{t("sections.noItems")}</p>
            ) : (
              module.furtherReading.map((resource, resourceIndex) => (
                <article key={`${resource.title}-${resourceIndex}`}>
                  <strong>{resource.title}</strong>
                  {resource.type && <span>{resource.type}</span>}
                  {resource.url && (
                    <a href={resource.url} target="_blank" rel="noreferrer">
                      {resource.url}
                    </a>
                  )}
                </article>
              ))
            )}
          </div>
        )}

        {activeModuleTab === "misconceptions" && (
          <MisconceptionsList module={module} language={course.language} />
        )}

        {activeModuleTab === "meta" && (
          <pre className="course-preview-code-block">
            {JSON.stringify(module.meta ?? {}, null, 2)}
          </pre>
        )}
      </main>
    );
  }

  if (activeSection === "final-quiz") {
    return (
      <main className="course-preview-content">
        <SectionTitle
          icon={<FileText size={30} />}
          title={t("sections.finalAssessment")}
        />
        {renderers?.finalAssessment ? (
          renderers.finalAssessment(course)
        ) : (
          <ReadOnlyQuiz quiz={course.finalQuiz} language={course.language} />
        )}
      </main>
    );
  }

  if (activeSection === "grades") {
    return (
      <main className="course-preview-content">
        <SectionTitle
          icon={<GraduationCap size={30} />}
          title={t("sections.grades")}
        />
        {renderers?.grades ? (
          renderers.grades(course)
        ) : (
          <p className="course-preview-info-box">
            {t("sections.enrollForGrades")}
          </p>
        )}
      </main>
    );
  }

  return (
    <main className="course-preview-content">
      <SectionTitle
        icon={<ClipboardCheck size={30} />}
        title={t("sections.resources")}
      />
      {renderers?.resources ? (
        renderers.resources(course)
      ) : (
        <ResourceList course={course} />
      )}
    </main>
  );
}
