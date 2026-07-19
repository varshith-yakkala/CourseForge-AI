import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';
import './MarkdownViewer.css';

export function MarkdownViewer({ content }) {
  if (!content) return null;

  return (
    <div className="cf-markdown-content">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={{
          table: ({ node, ...props }) => (
            <div className="cf-markdown-table-wrapper">
              <table {...props} />
            </div>
          ),
          code: ({ node, inline, className, children, ...props }) => {
            if (inline) {
              return <code className="cf-inline-code" {...props}>{children}</code>;
            }
            return (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
