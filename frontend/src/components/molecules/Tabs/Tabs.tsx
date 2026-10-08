// frontend/src/components/molecules/Tabs/Tabs.tsx

import type { ReactNode } from "react";
import clsx from "clsx";
import { Button } from "@/components";
import "./Tabs.css";

export type TabItem<T extends string> = {
  id: T;
  label: ReactNode;
};

type TabsProps<T extends string> = {
  items: readonly TabItem<T>[];
  activeId: T;
  onChange: (id: T) => void;
};

export function Tabs<T extends string>({
  items,
  activeId,
  onChange,
}: TabsProps<T>) {
  return (
    <div className="tabs" role="tablist">
      {items.map((item) => (
        <Button
          key={item.id}
          type="button"
          role="tab"
          variant="plain"
          aria-selected={activeId === item.id}
          className={clsx("tabs__item", {
            "tabs__item--active": activeId === item.id,
          })}
          onClick={() => onChange(item.id)}
        >
          {item.label}
        </Button>
      ))}
    </div>
  );
}
