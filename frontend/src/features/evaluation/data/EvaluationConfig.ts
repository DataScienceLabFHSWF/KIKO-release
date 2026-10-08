// frontend/src/features/evaluation/data/EvaluationConfig.ts

import { Bot, ClipboardList, Database } from "lucide-react";
import type { EvaluationTabConfig } from "../types/Evaluation";

import corpusCsvUrl from "@/assets/evaluation/results/eductum_eval.csv?url";

import apertusCsvUrl from "@/assets/evaluation/results/chat_eval_results_Apertus.csv?url";
import llamaCsvUrl from "@/assets/evaluation/results/chat_eval_results_llama3.csv?url";
import kimiCsvUrl from "@/assets/evaluation/results/chat_eval_results_kimik2.csv?url";
import gradingCsvUrl from "@/assets/evaluation/results/grading_eval_results_deepseek.csv?url";

import apertusSummaryCsvUrl from "@/assets/evaluation/results/summary_eval_results_Apertus_deepseek.csv?url";
import llamaSummaryCsvUrl from "@/assets/evaluation/results/summary_eval_results_llama3_deepseek.csv?url";
import kimiSummaryCsvUrl from "@/assets/evaluation/results/summary_eval_results_kimik2_deepseek.csv?url";

import apertusChart from "@/assets/evaluation/plots/distribution_chats_Apertus.png";
import llamaChart from "@/assets/evaluation/plots/distribution_chats_llama3.png";
import kimiChart from "@/assets/evaluation/plots/distribution_chats_kimik2.png";
import gradingChart from "@/assets/evaluation/plots/confusion_matrix_grades_deepseek.png";

export const evaluationTabs: readonly EvaluationTabConfig[] = [
  {
    id: "dataset",
    labelKey: "tabs.dataset",
    headingKey: "dataset.heading",
    descriptionKey: "dataset.description",
    explanationKey: "dataset.explanation",
    icon: Database,
    resultCsvUrl: corpusCsvUrl,
    statDefinitions: [
      { labelKey: "stats.rows", source: "computed", computedKey: "rows" },
      { labelKey: "stats.columns", source: "computed", computedKey: "columns" },
      {
        labelKey: "stats.missingValues",
        source: "computed",
        computedKey: "missingValues",
      },
      {
        labelKey: "stats.avgCharsPerRow",
        source: "computed",
        computedKey: "avgCharsPerRow",
      },
    ],
  },
  {
    id: "llama",
    labelKey: "tabs.llama",
    headingKey: "llama.heading",
    descriptionKey: "llama.description",
    explanationKey: "llama.explanation",
    icon: Bot,
    resultCsvUrl: llamaCsvUrl,
    summaryCsvUrl: llamaSummaryCsvUrl,
    chartSrc: llamaChart,
    chartAltKey: "llama.chartAlt",
    statDefinitions: [
      {
        labelKey: "stats.rouge",
        source: "summary",
        summaryKey: "chat_ROUGE-L_avg",
      },
      {
        labelKey: "stats.bleu",
        source: "summary",
        summaryKey: "chat_BLEU_avg",
      },
      {
        labelKey: "stats.bertScore",
        source: "summary",
        summaryKey: "chat_BERTScore_F1_avg",
      },
      {
        labelKey: "stats.citationRate",
        source: "summary",
        summaryKey: "chat_CitationRate",
      },
    ],
  },
  {
    id: "apertus",
    labelKey: "tabs.apertus",
    headingKey: "apertus.heading",
    descriptionKey: "apertus.description",
    explanationKey: "apertus.explanation",
    icon: Bot,
    resultCsvUrl: apertusCsvUrl,
    summaryCsvUrl: apertusSummaryCsvUrl,
    chartSrc: apertusChart,
    chartAltKey: "apertus.chartAlt",
    statDefinitions: [
      {
        labelKey: "stats.rouge",
        source: "summary",
        summaryKey: "chat_ROUGE-L_avg",
      },
      {
        labelKey: "stats.bleu",
        source: "summary",
        summaryKey: "chat_BLEU_avg",
      },
      {
        labelKey: "stats.bertScore",
        source: "summary",
        summaryKey: "chat_BERTScore_F1_avg",
      },
      {
        labelKey: "stats.citationRate",
        source: "summary",
        summaryKey: "chat_CitationRate",
      },
    ],
  },
  {
    id: "kimi",
    labelKey: "tabs.kimi",
    headingKey: "kimi.heading",
    descriptionKey: "kimi.description",
    explanationKey: "kimi.explanation",
    icon: Bot,
    resultCsvUrl: kimiCsvUrl,
    summaryCsvUrl: kimiSummaryCsvUrl,
    chartSrc: kimiChart,
    chartAltKey: "kimi.chartAlt",
    statDefinitions: [
      {
        labelKey: "stats.rouge",
        source: "summary",
        summaryKey: "chat_ROUGE-L_avg",
      },
      {
        labelKey: "stats.bleu",
        source: "summary",
        summaryKey: "chat_BLEU_avg",
      },
      {
        labelKey: "stats.bertScore",
        source: "summary",
        summaryKey: "chat_BERTScore_F1_avg",
      },
      {
        labelKey: "stats.citationRate",
        source: "summary",
        summaryKey: "chat_CitationRate",
      },
    ],
  },
  {
    id: "grading",
    labelKey: "tabs.grading",
    headingKey: "grading.heading",
    descriptionKey: "grading.description",
    explanationKey: "grading.explanation",
    icon: ClipboardList,
    resultCsvUrl: gradingCsvUrl,
    summaryCsvUrl: llamaSummaryCsvUrl,
    chartSrc: gradingChart,
    chartAltKey: "grading.chartAlt",
    statDefinitions: [
      { labelKey: "stats.items", source: "computed", computedKey: "rows" },
      {
        labelKey: "stats.accuracy",
        source: "summary",
        summaryKey: "grade_Accuracy_exact",
      },
      {
        labelKey: "stats.mae",
        source: "summary",
        summaryKey: "grade_MAE",
      },
      {
        labelKey: "stats.kappa",
        source: "summary",
        summaryKey: "grade_QWKappa",
      },
    ],
  },
];
