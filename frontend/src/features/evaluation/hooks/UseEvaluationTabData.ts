// frontend/src/features/evaluation/hooks/UseEvaluationTabData.ts

import { useEffect, useState } from "react";
import type { DataTableColumn, DataTableRow } from "@/components";
import type {
  EvaluationLoadedTabData,
  EvaluationTabConfig,
} from "../types/Evaluation";
import {
  averageCharactersPerRow,
  columnsFromRows,
  countMissingValues,
  formatMetric,
  loadCsvRows,
} from "../utils/CsvUtils";

type EvaluationTabDataState = {
  data: EvaluationLoadedTabData;
  isLoading: boolean;
  error: string | null;
};

const emptyData: EvaluationLoadedTabData = {
  columns: [],
  rows: [],
  aggregateColumns: [],
  aggregateRows: [],
  stats: [],
};

function getComputedValue(
  key: string | undefined,
  rows: DataTableRow[],
  columns: DataTableColumn[],
) {
  if (key === "rows") return rows.length;
  if (key === "columns") return columns.length;
  if (key === "missingValues") return countMissingValues(rows);
  if (key === "avgCharsPerRow") return averageCharactersPerRow(rows);

  return "—";
}

function buildStats(
  tab: EvaluationTabConfig,
  rows: DataTableRow[],
  columns: DataTableColumn[],
  aggregateRows: DataTableRow[],
) {
  const firstAggregateRow = aggregateRows[0] ?? {};

  return tab.statDefinitions.map((definition) => {
    if (definition.source === "computed") {
      return {
        labelKey: definition.labelKey,
        value: getComputedValue(definition.computedKey, rows, columns),
      };
    }

    return {
      labelKey: definition.labelKey,
      value: formatMetric(
        definition.summaryKey
          ? firstAggregateRow[definition.summaryKey]
          : undefined,
      ),
    };
  });
}

export function useEvaluationTabData(tab: EvaluationTabConfig) {
  const [state, setState] = useState<EvaluationTabDataState>({
    data: emptyData,
    isLoading: true,
    error: null,
  });

  useEffect(() => {
    let isCancelled = false;

    async function loadData() {
      setState({
        data: emptyData,
        isLoading: true,
        error: null,
      });

      try {
        const rows = await loadCsvRows(tab.resultCsvUrl);
        const columns = columnsFromRows(rows);

        const aggregateRows = tab.summaryCsvUrl
          ? await loadCsvRows(tab.summaryCsvUrl)
          : [];

        const aggregateColumns = columnsFromRows(aggregateRows);

        const stats = buildStats(tab, rows, columns, aggregateRows);

        if (!isCancelled) {
          setState({
            data: {
              columns,
              rows,
              aggregateColumns,
              aggregateRows,
              stats,
            },
            isLoading: false,
            error: null,
          });
        }
      } catch (error) {
        if (!isCancelled) {
          setState({
            data: emptyData,
            isLoading: false,
            error:
              error instanceof Error
                ? error.message
                : "Could not load evaluation data.",
          });
        }
      }
    }

    void loadData();

    return () => {
      isCancelled = true;
    };
  }, [tab]);

  return state;
}
