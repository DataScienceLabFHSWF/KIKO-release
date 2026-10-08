// frontend/src/components/atoms/MarkdownView/MarkdownView.tsx

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { AuthenticatedMarkdownImage } from "./AuthenticatedMarkdownImage";
import "./MarkdownView.css";

type MarkdownViewProps = {
  content: string;
  courseId?: number;
};

export function MarkdownView({ content, courseId }: MarkdownViewProps) {
  return (
    <div className="markdown-view">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          img: ({ src, alt, ...props }) => (
            <AuthenticatedMarkdownImage
              {...props}
              courseId={courseId}
              src={src}
              alt={alt}
            />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
