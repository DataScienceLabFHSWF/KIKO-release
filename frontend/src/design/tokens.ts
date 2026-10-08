// frontend/src/design/tokens.ts

import { colors } from "./colors";
import { spacing } from "./spacing";
import { typography } from "./typography";

export const tokens = {
  colors,
  spacing,
  typography,
  layout: {
    sidebarWidth: "220px",
    topbarHeight: "72px",
  },
  radius: {
    none: "0px",
    sm: "4px",
    md: "8px",
  },
} as const;
