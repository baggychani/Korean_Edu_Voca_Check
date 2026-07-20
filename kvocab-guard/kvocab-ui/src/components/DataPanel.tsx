// DataPanel.tsx
import { useState } from 'react';
import Collapsible from './Collapsible';

interface Counts {
  lexemes?: number;
  levels?: number;
  lessons?: number;
  allowlist?: number;
}

interface Props {
  counts: Counts;
  onSeed: () => Promise<void>;
  onImportXlsx: () => Promise<void>;
  busy: boolean;
}

function CountCard({ value, label, accent }: { value: number | undefined; label: string; accent?: string }) {
  return (
    <div className="stat-card" style={accent ? { '--accent': accent } as React.CSSProperties : {}}>
      <div className="stat-value">{value !== undefined ? value.toLocaleString() : '—'}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

export default function DataPanel({ counts, onSeed, onImportXlsx, busy }: Props) {
  const [seeding, setSeeding] = useState(false);
  const [importing, setImporting] = useState(false);

  const handleSeed = async () => {
    if (!window.confirm(
      'DB를 초기화하고 기본 어휘 데이터(seed)를 다시 불러옵니다.\n' +
      '사용자가 추가한 허용어는 보존됩니다.\n' +
      'XLSX import 어휘는 삭제됩니다.\n\n계속하시겠습니까?',
    )) return;
    setSeeding(true);
    try {
      await onSeed();
    } finally {
      setSeeding(false);
    }
  };

  const handleImport = async () => {
    setImporting(true);
    try {
      await onImportXlsx();
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="panel-stack page-enter">
      <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
        <CountCard value={counts.lexemes} label="전체 어휘" accent="var(--accent)" />
        <CountCard value={counts.levels} label="레벨 수" accent="var(--green)" />
        <CountCard value={counts.lessons} label="단원 수" accent="var(--cyan)" />
        <CountCard value={counts.allowlist} label="사용자 허용어" accent="var(--amber)" />
      </div>

      <div className="result-groups">
        <Collapsible light defaultOpen title="데이터베이스">
          <div style={{ padding: '4px 16px 16px' }}>
            <div className="data-actions">
              <button
                type="button"
                className="btn btn-ghost"
                disabled={busy || seeding || importing}
                onClick={handleSeed}
              >
                {seeding
                  ? <><span className="spinner dark" /> 초기화 중…</>
                  : 'DB 초기화 (Seed)'}
              </button>
              <button
                type="button"
                className="btn btn-ghost"
                disabled={busy || seeding || importing}
                onClick={handleImport}
              >
                {importing
                  ? <><span className="spinner dark" /> 가져오는 중…</>
                  : 'XLSX 가져오기'}
              </button>
            </div>
            <p className="data-note">
              · <strong>DB 초기화</strong>: 앱 내장 어휘 데이터를 새로 불러옵니다. 허용어는 보존됩니다.<br />
              · <strong>XLSX 가져오기</strong>: 사용자 정의 어휘 파일(.xlsx)을 추가로 불러옵니다.
            </p>
          </div>
        </Collapsible>

        <Collapsible light defaultOpen={false} title="정보">
          <div style={{ padding: '4px 16px 16px' }}>
            <p className="data-note">
              공식 Glossary는 seed XLSX에서 관리됩니다.
              스터디 커스텀 어휘 레이어는 이후 버전에서 추가될 예정입니다.
            </p>
          </div>
        </Collapsible>
      </div>
    </div>
  );
}
