// frontend/src/features/faq/components/FaqSection.tsx

import type { ReactNode } from "react";
import { useTranslation } from "node_modules/react-i18next";
import { Accordion, type AccordionItem } from "@/components";
import type { FaqItemConfig } from "../data/FaqConfig";
import "./FaqSection.css";

type FaqSectionProps = {
  title: string;
  icon: ReactNode;
  items: readonly FaqItemConfig[];
};

export function FaqSection({ title, icon, items }: FaqSectionProps) {
  const { t } = useTranslation("faq");

  const accordionItems: AccordionItem[] = items.map((item) => {
    const bullets = t(`items.${item.key}.bullets`, {
      returnObjects: true,
    }) as string[];

    return {
      id: item.key,
      title: t(`items.${item.key}.question`),
      content: (
        <ul>
          {bullets.map((bullet) => (
            <li key={bullet}>{bullet}</li>
          ))}
        </ul>
      ),
    };
  });

  return (
    <section className="faq-section">
      <h2>
        <span className="faq-section__icon">{icon}</span>
        {title}
      </h2>

      <Accordion items={accordionItems} />
    </section>
  );
}
