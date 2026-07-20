// Collapsible.tsx — foldable accordion section
import { useState, type ReactNode } from 'react';

interface Props {
  title: ReactNode;
  children: ReactNode;
  defaultOpen?: boolean;
  light?: boolean;
  className?: string;
}

function Chevron() {
  return (
    <svg className="collapsible-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M6 9l6 6 6-6" />
    </svg>
  );
}

export default function Collapsible({
  title,
  children,
  defaultOpen = false,
  light = false,
  className = '',
}: Props) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className={`collapsible${open ? ' open' : ''}${light ? ' light' : ''} ${className}`.trim()}>
      <button
        type="button"
        className="collapsible-trigger"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
      >
        {title}
        <Chevron />
      </button>
      <div className="collapsible-body">
        <div className="collapsible-inner">
          <div className="collapsible-content">{children}</div>
        </div>
      </div>
    </div>
  );
}
