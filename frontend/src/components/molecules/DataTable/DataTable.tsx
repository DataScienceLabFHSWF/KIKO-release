// frontend/src/components/molecules/DataTable/DataTable.tsx

import { Download, Search } from "lucide-react";
import { useMemo, useState } from "react";
import { Button } from "@/components";
import "./DataTable.css";

export type DataTableColumn = {
  key: string;
  label: string;
};

export type DataTableRow = Record<
  string,
  string | number | boolean | null | undefined
>;

type DataTableLabels = {
  searchPlaceholder: string;
  downloadCsv: string;
  rowsPerPage: string;
  previous: string;
  next: string;
  page: string;
  of: string;
  showing: string;
  rows: string;
};

type DataTableProps = {
  columns: DataTableColumn[];
  rows: DataTableRow[];
  emptyLabel: string;
  fileName?: string;
  pageSize?: number;
  enableSearch?: boolean;
  enableCsvDownload?: boolean;
  labels: DataTableLabels;
};

function normalizeValue(value: DataTableRow[string]) {
  if (value === null || value === undefined) return "";
  return String(value);
}

function escapeCsvValue(value: string) {
  const escaped = value.replaceAll('"', '""');
  return `"${escaped}"`;
}

function downloadCsvFile(
  columns: DataTableColumn[],
  rows: DataTableRow[],
  fileName: string,
) {
  const header = columns
    .map((column) => escapeCsvValue(column.label))
    .join(",");

  const body = rows
    .map((row) =>
      columns
        .map((column) => escapeCsvValue(normalizeValue(row[column.key])))
        .join(","),
    )
    .join("\n");

  const csv = `${header}\n${body}`;
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const objectUrl = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = fileName.endsWith(".csv") ? fileName : `${fileName}.csv`;
  link.click();

  URL.revokeObjectURL(objectUrl);
}

export function DataTable({
  columns,
  rows,
  emptyLabel,
  fileName = "table-export.csv",
  pageSize = 5,
  enableSearch = true,
  enableCsvDownload = true,
  labels,
}: DataTableProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  const filteredRows = useMemo(() => {
    const query = searchTerm.trim().toLowerCase();

    if (!query) return rows;

    return rows.filter((row) =>
      columns.some((column) =>
        normalizeValue(row[column.key]).toLowerCase().includes(query),
      ),
    );
  }, [columns, rows, searchTerm]);

  const totalPages = Math.max(1, Math.ceil(filteredRows.length / pageSize));

  const safeCurrentPage = Math.min(currentPage, totalPages);

  const paginatedRows = useMemo(() => {
    const startIndex = (safeCurrentPage - 1) * pageSize;
    return filteredRows.slice(startIndex, startIndex + pageSize);
  }, [filteredRows, pageSize, safeCurrentPage]);

  function handleSearchChange(value: string) {
    setSearchTerm(value);
    setCurrentPage(1);
  }

  const hasToolbar = enableSearch || enableCsvDownload;
  const shouldPaginate = filteredRows.length > pageSize;

  return (
    <section className="data-table-wrapper">
      {hasToolbar && (
        <div className="data-table-toolbar">
          {enableSearch && (
            <label className="data-table-toolbar__search">
              <Search size={16} strokeWidth={2.2} aria-hidden="true" />
              <input
                type="search"
                value={searchTerm}
                placeholder={labels.searchPlaceholder}
                onChange={(event) =>
                  handleSearchChange(event.currentTarget.value)
                }
              />
            </label>
          )}

          {enableCsvDownload && (
            <Button
              type="button"
              variant="secondary"
              size="sm"
              className="data-table-toolbar__button"
              disabled={filteredRows.length === 0}
              onClick={() => downloadCsvFile(columns, filteredRows, fileName)}
            >
              <Download size={16} strokeWidth={2.2} aria-hidden="true" />
              {labels.downloadCsv}
            </Button>
          )}
        </div>
      )}

      {filteredRows.length === 0 ? (
        <p className="data-table__empty">{emptyLabel}</p>
      ) : (
        <>
          <div className="data-table" role="region" tabIndex={0}>
            <table>
              <thead>
                <tr>
                  {columns.map((column) => (
                    <th key={column.key}>{column.label}</th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {paginatedRows.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {columns.map((column) => (
                      <td key={column.key}>
                        {normalizeValue(row[column.key]) || "—"}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="data-table-footer">
            <span>
              {labels.showing} {paginatedRows.length} / {filteredRows.length}{" "}
              {labels.rows}
            </span>

            {shouldPaginate && (
              <div className="data-table-pagination">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  disabled={safeCurrentPage === 1}
                  onClick={() => setCurrentPage((page) => page - 1)}
                >
                  {labels.previous}
                </Button>

                <span>
                  {labels.page} {safeCurrentPage} {labels.of} {totalPages}
                </span>

                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  disabled={safeCurrentPage === totalPages}
                  onClick={() => setCurrentPage((page) => page + 1)}
                >
                  {labels.next}
                </Button>
              </div>
            )}
          </div>
        </>
      )}
    </section>
  );
}
