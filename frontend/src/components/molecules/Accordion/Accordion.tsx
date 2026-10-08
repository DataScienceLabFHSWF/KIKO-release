// frontend/src/components/molecules/Accordion/Accordion.tsx

import { ChevronRight } from "lucide-react";
import { useState, type ReactNode } from "react";
import clsx from "clsx";
import { Button } from "@/components";
import "./Accordion.css";

export type AccordionItem = {
  id: string;
  title: ReactNode;
  content: ReactNode;
};

type AccordionProps = {
  items: AccordionItem[];
  defaultOpenId?: string;
};

export function Accordion({ items, defaultOpenId }: AccordionProps) {
  const [openId, setOpenId] = useState<string | null>(defaultOpenId ?? null);

  return (
    <div className="accordion">
      {items.map((item) => {
        const isOpen = openId === item.id;

        return (
          <section key={item.id} className="accordion__item">
            <Button
              type="button"
              variant="plain"
              className="accordion__trigger"
              aria-expanded={isOpen}
              onClick={() => setOpenId(isOpen ? null : item.id)}
            >
              <ChevronRight
                size={17}
                strokeWidth={2.4}
                className={clsx("accordion__chevron", {
                  "accordion__chevron--open": isOpen,
                })}
                aria-hidden="true"
              />

              <span>{item.title}</span>
            </Button>

            {isOpen && <div className="accordion__content">{item.content}</div>}
          </section>
        );
      })}
    </div>
  );
}
