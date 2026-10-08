// frontend/src/features/evaluation/pages/EvaluationResultsPage.tsx

import { SearchCheck } from "lucide-react";
import { useMemo, useState } from "react";
import { useTranslation } from "node_modules/react-i18next";
import {
  Accordion,
  DataTable,
  ErrorState,
  LoadingState,
  PageHeader,
  StatCard,
  Tabs,
} from "@/components";
import { usePageMeta } from "@/app/hooks/usePageMeta";
import { evaluationTabs } from "../data/EvaluationConfig";
import { useEvaluationTabData } from "../hooks/UseEvaluationTabData";
import type { EvaluationTabId } from "../types/Evaluation";
import "./EvaluationResultsPage.css";

export function EvaluationResultsPage() {
  const { t } = useTranslation("evaluation");
  const [activeTabId, setActiveTabId] = useState<EvaluationTabId>("dataset");

  usePageMeta({
    title: t("metaTitle"),
  });

  const activeTab = useMemo(() => {
    return (
      evaluationTabs.find((item) => item.id === activeTabId) ??
      evaluationTabs[0]
    );
  }, [activeTabId]);

  const { data, isLoading, error } = useEvaluationTabData(activeTab);

  const ActiveIcon = activeTab.icon;

  const explanationBullets = t(`${activeTab.explanationKey}.bullets`, {
    returnObjects: true,
  }) as string[];

  const tableLabels = {
    searchPlaceholder: t("table.searchPlaceholder"),
    downloadCsv: t("table.downloadCsv"),
    rowsPerPage: t("table.rowsPerPage"),
    previous: t("table.previous"),
    next: t("table.next"),
    page: t("table.page"),
    of: t("table.of"),
    showing: t("table.showing"),
    rows: t("table.rows"),
  };

  return (
    <section className="evaluation-page">
      <PageHeader
        icon={<SearchCheck size={30} strokeWidth={2.3} />}
        title={t("title")}
        subtitle={t("subtitle")}
      />

      <Tabs
        activeId={activeTabId}
        onChange={setActiveTabId}
        items={evaluationTabs.map((tab) => ({
          id: tab.id,
          label: t(tab.labelKey),
        }))}
      />

      <section className="evaluation-page__section">
        <div className="evaluation-page__section-heading">
          <span className="evaluation-page__section-icon">
            <ActiveIcon size={24} strokeWidth={2.2} />
          </span>

          <div>
            <h2>{t(activeTab.headingKey)}</h2>
            <p>{t(activeTab.descriptionKey)}</p>
          </div>
        </div>

        <Accordion
          defaultOpenId="how-to-read"
          items={[
            {
              id: "how-to-read",
              title: t(`${activeTab.explanationKey}.title`),
              content: (
                <ul>
                  {explanationBullets.map((bullet) => (
                    <li key={bullet}>{bullet}</li>
                  ))}
                </ul>
              ),
            },
          ]}
        />
      </section>

      {isLoading && <LoadingState description={t("states.loading")} />}

      {error && (
        <ErrorState title={t("states.errorTitle")} description={error} />
      )}

      {!isLoading && !error && (
        <>
          <section className="evaluation-page__section">
            <h3>{t("sections.keyNumbers")}</h3>

            <div className="evaluation-page__stats">
              {data.stats.map((stat) => (
                <StatCard
                  key={stat.labelKey}
                  label={t(stat.labelKey)}
                  value={stat.value}
                />
              ))}
            </div>
          </section>

          <section className="evaluation-page__section">
            <h3>{t("sections.resultsTable")}</h3>

            <DataTable
              columns={data.columns}
              rows={data.rows}
              emptyLabel={t("empty.noRows")}
              fileName={`evaluation-${activeTab.id}-results.csv`}
              pageSize={5}
              enableSearch
              enableCsvDownload
              labels={tableLabels}
            />
          </section>

          {data.aggregateRows.length > 0 && (
            <section className="evaluation-page__section">
              <h3>{t("sections.quickAggregates")}</h3>

              <DataTable
                columns={data.aggregateColumns}
                rows={data.aggregateRows}
                emptyLabel={t("empty.noRows")}
                fileName={`evaluation-${activeTab.id}-aggregates.csv`}
                pageSize={5}
                enableSearch
                enableCsvDownload
                labels={tableLabels}
              />
            </section>
          )}

          {activeTab.chartSrc && (
            <section className="evaluation-page__section">
              <h3>{t("sections.visualization")}</h3>

              <div className="evaluation-page__chart-card">
                <img
                  src={activeTab.chartSrc}
                  alt={
                    activeTab.chartAltKey
                      ? t(activeTab.chartAltKey)
                      : t("sections.visualization")
                  }
                />
              </div>
            </section>
          )}
        </>
      )}
    </section>
  );
}
