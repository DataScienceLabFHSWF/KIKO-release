// frontend/src/app/hooks/usePageMeta.ts

import { useEffect } from "react";

type UsePageMetaOptions = {
  title: string;
};

export function usePageMeta({ title }: UsePageMetaOptions) {
  useEffect(() => {
    document.title = title;
  }, [title]);
}
