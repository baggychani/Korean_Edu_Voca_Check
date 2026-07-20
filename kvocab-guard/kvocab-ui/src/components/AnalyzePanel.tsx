// AnalyzePanel.tsx — text input + collapsible result groups
import { useState, useCallback, useMemo } from 'react';
import type { AnalyzeResult, Issue, FilterKey } from '../types';
import Collapsible from './Collapsible';

function VerdictBadge({ status }: { status: Issue['status'] }) {
  const map: Record<string, { cls: string; text: string }> = {
    before_introduced: { cls: 'badge-early', text: '아직 이름' },
    unknown: { cls: 'badge-unknown', text: '교재에 없음' },
    allowed: { cls: 'badge-ok', text: '사용 가능' },
    custom_allowed: { cls: 'badge-custom', text: '허용어' },
  };
  const info = map[status] ?? { cls: 'badge-ok', text: status };
  return <span className={`badge ${info.cls}`}>{info.text}</span>;
}

function StatCard({
  value, label, accent,
}: { value: string; label: string; accent?: string }) {
  return (
    <div className="stat-card" style={accent ? { '--accent': accent } as React.CSSProperties : {}}>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

const FILTERS: { key: FilterKey; label: string; dot?: string }[] = [
  { key: 'all', label: '전체' },
  { key: 'before_introduced', label: '아직 이름', dot: 'var(--red)' },
  { key: 'unknown', label: '교재에 없음', dot: 'var(--amber)' },
  { key: 'allowed', label: '사용 가능', dot: 'var(--green)' },
];

const STATUS_ORDER: Record<string, number> = {
  before_introduced: 0, unknown: 1, custom_allowed: 2, allowed: 3,
};

function sortIssues(issues: Issue[]) {
  return [...issues].sort((a, b) => {
    const oa = STATUS_ORDER[a.status] ?? 99;
    const ob = STATUS_ORDER[b.status] ?? 99;
    if (oa !== ob) return oa - ob;
    return a.start - b.start;
  });
}

function displaySurface(issue: Issue) {
  return issue.lemma && issue.lemma !== issue.surface
    ? `${issue.surface}(${issue.lemma})`
    : issue.surface;
}

function IssueTable({
  issues,
  selected,
  onSelect,
}: {
  issues: Issue[];
  selected: Issue | null;
  onSelect: (issue: Issue) => void;
}) {
  if (issues.length === 0) return null;
  return (
    <div className="table-wrap">
      <table className="results-table">
        <thead>
          <tr>
            <th>표현</th>
            <th>원형</th>
            <th>판정</th>
            <th>첫 등장</th>
            <th>문장</th>
          </tr>
        </thead>
        <tbody>
          {issues.map((issue, i) => (
            <tr
              key={`${issue.start}-${issue.end}-${issue.status}-${i}`}
              className={selected === issue ? 'selected' : ''}
              onClick={() => onSelect(issue)}
            >
              <td className="col-surface">{issue.surface}</td>
              <td className="col-lemma">
                {issue.equivalent_lemma
                  ? <>{issue.lemma} <span style={{ color: 'var(--ct-text3)', fontSize: 11 }}>→ {issue.equivalent_lemma}</span></>
                  : issue.lemma}
              </td>
              <td><VerdictBadge status={issue.status} /></td>
              <td className="col-first">
                {issue.first_level && issue.first_lesson
                  ? `${issue.first_level} ${issue.first_lesson}`
                  : '—'}
              </td>
              <td className="col-sent" title={issue.sentence}>{issue.sentence}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

interface Props {
  onAnalyze: (text: string) => Promise<AnalyzeResult | null>;
  onAllow: (issue: Issue) => void;
  targetLevel: string;
  targetLesson: string;
  busy: boolean;
}

export default function AnalyzePanel({ onAnalyze, onAllow, targetLevel, targetLesson, busy }: Props) {
  const [text, setText] = useState('');
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [filter, setFilter] = useState<FilterKey>('all');
  const [selected, setSelected] = useState<Issue | null>(null);
  const [running, setRunning] = useState(false);

  const handleAnalyze = useCallback(async () => {
    if (!text.trim() || running) return;
    setRunning(true);
    setSelected(null);
    try {
      const r = await onAnalyze(text);
      setResult(r);
      setFilter('all');
    } finally {
      setRunning(false);
    }
  }, [text, running, onAnalyze]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') handleAnalyze();
  };

  const handleClear = () => {
    setText('');
    setResult(null);
    setSelected(null);
  };

  const allIssues = useMemo(() => {
    if (!result) return [];
    return sortIssues([
      ...result.issues,
      ...result.allowed.filter((a) =>
        !result.issues.some((i) => i.start === a.start && i.end === a.end && i.status === a.status),
      ),
    ]);
  }, [result]);

  const filtered = filter === 'all'
    ? allIssues
    : allIssues.filter((i) => i.status === filter);

  const groups = useMemo(() => ({
    early: allIssues.filter((i) => i.status === 'before_introduced'),
    unknown: allIssues.filter((i) => i.status === 'unknown'),
    allowed: allIssues.filter((i) => i.status === 'allowed' || i.status === 'custom_allowed'),
  }), [allIssues]);

  const s = result?.summary;

  const onSelect = (issue: Issue) => {
    setSelected((prev) => (prev === issue ? null : issue));
  };

  return (
    <div className="panel-stack page-enter">
      <div className="card">
        <div className="card-head">
          <span className="card-title">텍스트 입력</span>
          <span className="card-hint">Ctrl+Enter 로 검사</span>
        </div>
        <div className="card-body">
          <textarea
            className="text-area"
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="검사할 한국어 텍스트를 붙여넣으세요…"
            disabled={running}
          />
          <div className="action-row">
            <button
              type="button"
              className="btn btn-ghost"
              disabled={running}
              onClick={() => alert('파일 열기 — Tauri API 연결 후 사용 가능')}
            >
              파일 열기
            </button>
            <button
              type="button"
              className="btn btn-ghost"
              disabled={!text && !result}
              onClick={handleClear}
            >
              지우기
            </button>
            <div className="spacer" />
            <button
              type="button"
              className="btn btn-primary"
              disabled={!text.trim() || running || busy}
              onClick={handleAnalyze}
            >
              {running ? <><span className="spinner" /> 검사 중…</> : '텍스트 검사'}
            </button>
          </div>
        </div>
      </div>

      {!result && !running && (
        <div className="card">
          <div className="empty-state">
            <div className="empty-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                <path d="M12 20h9" />
                <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
              </svg>
            </div>
            <div className="empty-text">검사할 텍스트를 입력하세요</div>
            <div className="empty-sub">목표 단원: {targetLevel} {targetLesson}</div>
          </div>
        </div>
      )}

      {result && s && (
        <>
          <div className="stats-grid">
            <StatCard value={s.target_display} label="목표 단원" accent="var(--accent)" />
            <StatCard
              value={String(s.issue_count)}
              label="경고 단어"
              accent={s.issue_count > 0 ? 'var(--ct-text)' : 'var(--green)'}
            />
            <StatCard value={String(s.before_introduced_count)} label="아직 이름" accent="var(--red)" />
            <StatCard value={String(s.unknown_count)} label="교재에 없음" accent="var(--amber)" />
            <StatCard value={s.max_known_display || '—'} label="확인된 최고 단원" />
          </div>

          <div className="result-groups">
            <Collapsible
              light
              defaultOpen={groups.early.length > 0}
              title={
                <>
                  <span className="group-dot" style={{ background: 'var(--red)' }} />
                  아직 이름
                  <span className="group-count">{groups.early.length}</span>
                </>
              }
            >
              <IssueTable issues={groups.early} selected={selected} onSelect={onSelect} />
              {groups.early.length === 0 && (
                <div className="empty-state" style={{ padding: '20px' }}>
                  <div className="empty-text" style={{ fontSize: 13 }}>해당 항목 없음</div>
                </div>
              )}
            </Collapsible>

            <Collapsible
              light
              defaultOpen={groups.unknown.length > 0}
              title={
                <>
                  <span className="group-dot" style={{ background: 'var(--amber)' }} />
                  교재에 없음
                  <span className="group-count">{groups.unknown.length}</span>
                </>
              }
            >
              <IssueTable issues={groups.unknown} selected={selected} onSelect={onSelect} />
              {groups.unknown.length === 0 && (
                <div className="empty-state" style={{ padding: '20px' }}>
                  <div className="empty-text" style={{ fontSize: 13 }}>해당 항목 없음</div>
                </div>
              )}
            </Collapsible>

            <Collapsible
              light
              defaultOpen={false}
              title={
                <>
                  <span className="group-dot" style={{ background: 'var(--green)' }} />
                  사용 가능
                  <span className="group-count">{groups.allowed.length}</span>
                </>
              }
            >
              <IssueTable issues={groups.allowed} selected={selected} onSelect={onSelect} />
            </Collapsible>
          </div>

          <div className="card">
            <div className="card-head" style={{ flexWrap: 'wrap', gap: 8 }}>
              <div className="filter-row">
                {FILTERS.map(({ key, label, dot }) => (
                  <button
                    key={key}
                    type="button"
                    className={`chip${filter === key ? ' active' : ''}`}
                    onClick={() => setFilter(key)}
                  >
                    {dot && <span className="chip-dot" style={{ background: dot }} />}
                    {label}
                  </button>
                ))}
              </div>
              <span className="count-badge">필터 · {filtered.length}개</span>
            </div>
            {s.issue_count === 0 && filter === 'all' ? (
              <div className="empty-state" style={{ padding: '28px 20px' }}>
                <div className="empty-text" style={{ color: 'var(--green)', fontWeight: 600 }}>
                  {s.target_display} 기준 경고 없음
                </div>
              </div>
            ) : (
              <IssueTable issues={filtered} selected={selected} onSelect={onSelect} />
            )}
          </div>

          <div className="selection-bar">
            <div>
              <div className="sel-hint">선택한 표현</div>
              <div className="sel-word">{selected ? displaySurface(selected) : '—'}</div>
            </div>
            <div className="sel-actions">
              <button
                type="button"
                className="btn btn-primary"
                disabled={!selected || selected.status === 'allowed' || selected.status === 'custom_allowed'}
                onClick={() => selected && onAllow(selected)}
                style={{ fontSize: 12, padding: '7px 14px' }}
              >
                허용어 추가
              </button>
              <button
                type="button"
                className="btn btn-ghost"
                disabled={!selected}
                onClick={() => selected && navigator.clipboard.writeText(displaySurface(selected))}
              >
                복사
              </button>
              <button
                type="button"
                className="btn btn-ghost"
                disabled={!selected?.sentence}
                onClick={() => selected?.sentence && navigator.clipboard.writeText(selected.sentence)}
              >
                문장 복사
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
