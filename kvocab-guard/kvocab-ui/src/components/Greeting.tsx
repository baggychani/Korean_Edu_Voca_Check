// Greeting.tsx — session boot overlay
import { useEffect, useState } from 'react';

const SESSION_KEY = 'kvocab-greeted';

export function shouldShowGreeting(): boolean {
  try {
    return sessionStorage.getItem(SESSION_KEY) !== '1';
  } catch {
    return true;
  }
}

export function markGreeted(): void {
  try {
    sessionStorage.setItem(SESSION_KEY, '1');
  } catch {
    /* ignore */
  }
}

interface Props {
  onDone: () => void;
}

export default function Greeting({ onDone }: Props) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const t = window.setTimeout(() => {
      markGreeted();
      setVisible(false);
      onDone();
    }, 1400);
    return () => window.clearTimeout(t);
  }, [onDone]);

  if (!visible) return null;

  return (
    <div className="greeting" aria-hidden>
      <div className="greeting-inner">
        <div className="greeting-brand">
          KVocab<span>Guard</span>
        </div>
        <div className="greeting-line">서울대 한국어 교재 기준 · 어휘 레벨 검사</div>
      </div>
    </div>
  );
}
