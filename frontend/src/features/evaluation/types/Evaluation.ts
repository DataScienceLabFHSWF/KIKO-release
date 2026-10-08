// frontend/src/features/evaluation/types/Evaluation.ts

import type { LucideIcon } from "lucide-react";
import type { DataTableColumn, DataTableRow } from "@/components";

export type EvaluationTabId =
  | "dataset"
  | "apertus"
  | "llama"
  | "kimi"
  | "grading";

export type EvaluationStatDefinition = {
  labelKey: string;
  source: "computed" | "summary";
  summaryKey?: string;
  computedKey?: "rows" | "columns" | "missingValues" | "avgCharsPerRow";
};

export type EvaluationTabConfig = {
  id: EvaluationTabId;
  labelKey: string;
  headingKey: string;
  descriptionKey: string;
  explanationKey: string;
  icon: LucideIcon;

  resultCsvUrl: string;
  summaryCsvUrl?: string;

  chartSrc?: string;
  chartAltKey?: string;

  statDefinitions: EvaluationStatDefinition[];
};

export type EvaluationLoadedTabData = {
  columns: DataTableColumn[];
  rows: DataTableRow[];
  aggregateColumns: DataTableColumn[];
  aggregateRows: DataTableRow[];
  stats: Array<{
    labelKey: string;
    value: string | number;
  }>;
};
