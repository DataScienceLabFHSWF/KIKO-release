// frontend/src/components/atoms/MarkdownView/AuthenticatedMarkdownImage.tsx

import { useEffect, useMemo, useState, type ImgHTMLAttributes } from "react";
import { apiBlob } from "@/api/client";

type AuthenticatedMarkdownImageProps = ImgHTMLAttributes<HTMLImageElement> & {
  courseId?: number;
};

function isDirectImageUrl(src: string) {
  return /^(https?:|data:|blob:)/i.test(src);
}

function buildCourseImagePath(src: string, courseId?: number): string | null {
  const cleanSrc = src.trim();

  if (!cleanSrc || isDirectImageUrl(cleanSrc)) {
    return null;
  }

  // Already points to backend API.
  if (cleanSrc.startsWith("/api/course/")) {
    return cleanSrc.replace(/^\/api/, "");
  }

  // Already points to apiRequest path format.
  if (cleanSrc.startsWith("/course/")) {
    return cleanSrc;
  }

  if (!courseId) {
    return null;
  }

  // Supports: knw-ass1.png, ./knw-ass1.png, images/knw-ass1.png
  const filename = cleanSrc
    .split("?")[0]
    .split("#")[0]
    .replace(/^\.?\//, "")
    .replace(/^images\//, "")
    .split("/")
    .pop();

  if (!filename) {
    return null;
  }

  return `/course/${courseId}/images/${encodeURIComponent(filename)}`;
}

export function AuthenticatedMarkdownImage({
  courseId,
  src,
  alt,
  ...props
}: AuthenticatedMarkdownImageProps) {
  const source = typeof src === "string" ? src : "";

  const courseImagePath = useMemo(
    () => buildCourseImagePath(source, courseId),
    [source, courseId],
  );

  const [objectUrl, setObjectUrl] = useState<string | null>(null);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    setHasError(false);
    setObjectUrl(null);

    if (!courseImagePath) {
      return;
    }

    let isMounted = true;
    let nextObjectUrl: string | null = null;

    async function loadImage() {
      try {
        const blob = await apiBlob(courseImagePath!);
        nextObjectUrl = URL.createObjectURL(blob);

        if (isMounted) {
          setObjectUrl(nextObjectUrl);
        }
      } catch {
        if (isMounted) {
          setHasError(true);
        }
      }
    }

    void loadImage();

    return () => {
      isMounted = false;

      if (nextObjectUrl) {
        URL.revokeObjectURL(nextObjectUrl);
      }
    };
  }, [courseImagePath]);

  if (!source) {
    return null;
  }

  if (isDirectImageUrl(source)) {
    return (
      <img
        {...props}
        src={source}
        alt={alt ?? ""}
        className="markdown-view__image"
      />
    );
  }

  if (!courseImagePath) {
    return (
      <span className="markdown-view__image-error">
        Image cannot be loaded: {alt || source}
      </span>
    );
  }

  if (hasError) {
    return (
      <span className="markdown-view__image-error">
        Image not available: {alt || source}
      </span>
    );
  }

  if (!objectUrl) {
    return (
      <span className="markdown-view__image-loading">Loading image...</span>
    );
  }

  return (
    <img
      {...props}
      src={objectUrl}
      alt={alt ?? ""}
      className="markdown-view__image"
    />
  );
}
