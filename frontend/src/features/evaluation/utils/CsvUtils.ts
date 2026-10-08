// frontend/src/features/evaluation/utils/CsvUtils.ts

import Papa from "papaparse";
import type { DataTableColumn, DataTableRow } from "@/components";

export async function loadCsvRows(csvUrl: string): Promise<DataTableRow[]> {
  const response = await fetch(csvUrl);

  if (!response.ok) {
    throw new Error(`Could not load CSV file: ${response.status}`);
  }

  const csvText = await response.text();

  const parsed = Papa.parse<Record<string, unknown>>(csvText, {
    header: true,
    skipEmptyLines: true,
    transformHeader: (header) => header.trim(),
    transform: (value) => value.trim(),
  });

  if (parsed.errors.length > 0) {
    console.warn("CSV parse warnings:", parsed.errors);
  }

  return parsed.data.map((row) => {
    const normalized: DataTableRow = {};

    Object.entries(row).forEach(([key, value]) => {
      normalized[key] =
        value === null || value === undefined ? "" : String(value);
    });

    return normalized;
  });
}

export function columnsFromRows(rows: DataTableRow[]): DataTableColumn[] {
  const firstRow = rows[0];

  if (!firstRow) return [];

  return Object.keys(firstRow).map((key) => ({
    key,
    label: key,
  }));
}

export function countMissingValues(rows: DataTableRow[]) {
  return rows.reduce((count, row) => {
    return (
      count +
      Object.values(row).filter(
        (value) =>
          value === null || value === undefined || String(value).trim() === "",
      ).length
    );
  }, 0);
}

export function averageCharactersPerRow(rows: DataTableRow[]) {
  if (rows.length === 0) return 0;

  const total = rows.reduce((sum, row) => {
    return (
      sum +
      Object.values(row).reduce((rowSum, value) => {
        return rowSum + String(value ?? "").length;
      }, 0)
    );
  }, 0);

  return Math.round(total / rows.length);
}

export function formatMetric(value: unknown) {
  if (value === null || value === undefined || value === "") return "—";

  const numeric = Number(value);

  if (!Number.isNaN(numeric) && Number.isFinite(numeric)) {
    return Number.isInteger(numeric) ? numeric : numeric.toFixed(4);
  }

  return String(value);
}
