// AnalyzePanel.tsx — 텍스트 입력 + 검사 결과 패널
import { useState, useCallback } from 'react';
import type { AnalyzeResult, Issue, FilterKey } from '../types';

// ── 판정 배지 ──────────────────────────────────────────────
function VerdictBadge({ status }: { status: Issue['status'] }) {
  const map: Record<string, { cls: string; text: string }> = {
    before_introduced: { cls: 'badge-early',   text: '⚠ 아직 이릅니다' },
    unknown:           { cls: 'badge-unknown',  text: '❌ 교재에 없음' },
    allowed:           { cls: 'badge-ok',       text: '✅ 사용 가능' },
    custom_allowed:    { cls: 'badge-custom',   text: '🔵 허용어' },
  };
  const info = map[status] ?? { cls: 'badge-ok', text: status };
  return <span className={`badge ${info.cls}`}>{info.text}</span>;
}

// ── 통계 카드 ──────────────────────────────────────────────
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

// ── 필터 칩 ───────────────────────────────────────────────
const FILTERS: { key: FilterKey; label: string; dot?: string }[] = [
  { key: 'all',               label: '전체' },
  { key: 'before_introduced', label: '아직 이릅니다',  dot: 'var(--red)' },
  { key: 'unknown',           label: '교재에 없음',    dot: 'var(--amber)' },
  { key: 'allowed',           label: '사용 가능',      dot: 'var(--green)' },
];

// ── 이슈 정렬 ─────────────────────────────────────────────
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

// ── 표시 이름 ─────────────────────────────────────────────
function displaySurface(issue: Issue) {
  return issue.lemma && issue.lemma !== issue.surface
    ? `${issue.surface}(${issue.lemma})`
    : issue.surface;
}

// ── 메인 컴포넌트 ──────────────────────────────────────────
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

  // filtered issues
  const allIssues = result
    ? sortIssues([
        ...result.issues,
        ...result.allowed.filter(a =>
          !result.issues.some(i => i.start === a.start && i.end === a.end && i.status === a.status)
        ),
      ])
    : [];

  const filtered = filter === 'all'
    ? allIssues
    : allIssues.filter(i => i.status === filter);

  const s = result?.summary;

  return (
    <div className="animate-in" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>

      {/* 입력 카드 */}
      <div className="card">
        <div className="card-head">
          <span className="card-title">텍스트 입력</span>
          <span className="card-hint">Ctrl+Enter 로 빠르게 검사할 수 있습니다</span>
        </div>
        <div className="card-body">
          <textarea
            className="text-area"
            value={text}
            onChange={e => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="검사할 한국어 텍스트를 붙여넣으세요…&#10;&#10;예) 저는 한국 음식을 정말 좋아해요."
            disabled={running}
          />
          <div className="action-row">
            <button className="btn btn-ghost" disabled={running} onClick={() => alert('파일 열기 — Tauri API 연결 후 사용 가능')}>
              📁 파일 열기
            </button>
            <button className="btn btn-ghost" disabled={!text && !result} onClick={handleClear}>
              🗑 지우기
            </button>
            <div className="spacer" />
            <button
              className="btn btn-primary"
              disabled={!text.trim() || running || busy}
              onClick={handleAnalyze}
            >
              {running ? <><span className="spinner" /> 검사 중…</> : '🔍 텍스트 검사'}
            </button>
          </div>
        </div>
      </div>

      {/* 결과 없는 상태 */}
      {!result && !running && (
        <div className="card">
          <div className="empty-state">
            <div className="empty-icon">📝</div>
            <div className="empty-text">검사할 텍스트를 입력하고 버튼을 누르세요</div>
            <div className="empty-sub">목표 단원: {targetLevel} {targetLesson}</div>
          </div>
        </div>
      )}

      {/* 결과 있는 상태 */}
      {result && s && (
        <>
          {/* 통계 */}
          <div className="stats-grid">
            <StatCard value={s.target_display}            label="목표 단원"          accent="var(--blue)" />
            <StatCard value={String(s.issue_count)}       label="경고 단어 수"       accent={s.issue_count > 0 ? 'var(--ct-text)' : 'var(--green)'} />
            <StatCard value={String(s.before_introduced_count)} label="아직 이릅니다"  accent="var(--red)" />
            <StatCard value={String(s.unknown_count)}     label="교재에 없음"        accent="var(--amber)" />
            <StatCard value={s.max_known_display || '—'}  label="확인된 최고 단원"   />
          </div>

          {/* 필터 + 테이블 카드 */}
          <div className="card">
            <div className="card-head" style={{ flexWrap: 'wrap', gap: 8 }}>
              <div className="filter-row">
                {FILTERS.map(({ key, label, dot }) => (
                  <button
                    key={key}
                    className={`chip${filter === key ? ' active' : ''}`}
                    onClick={() => setFilter(key)}
                  >
                    {dot && <span className="chip-dot" style={{ background: dot }} />}
                    {label}
                  </button>
                ))}
              </div>
              <span className="count-badge">판정순 · 등장순 · {filtered.length}개</span>
            </div>

            {s.issue_count === 0 && filter === 'all' && (
              <div className="empty-state" style={{ padding: '28px 20px' }}>
                <div className="empty-icon" style={{ fontSize: 28 }}>✅</div>
                <div className="empty-text" style={{ color: 'var(--green)', fontWeight: 700 }}>
                  {s.target_display} 기준 경고 없음
                </div>
              </div>
            )}

            {filtered.length > 0 && (
              <div className="table-wrap">
                <table className="results-table">
                  <thead>
                    <tr>
                      <th>표현</th>
                      <th>원형</th>
                      <th>판정</th>
                      <th>처음 나오는 곳</th>
                      <th>문장</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map((issue, i) => (
                      <tr
                        key={`${issue.start}-${issue.end}-${issue.status}-${i}`}
                        className={selected === issue ? 'selected' : ''}
                        onClick={() => setSelected(prev => prev === issue ? null : issue)}
                      >
                        <td className="col-surface">{issue.surface}</td>
                        <td className="col-lemma">
                          {issue.equivalent_lemma
                            ? <>{issue.lemma} <span style={{ color: 'var(--ct-text3)', fontSize: 11 }}>→ {issue.equivalent_lemma}</span></>
                            : issue.lemma}
                        </td>
                        <td><VerdictBadge status={issue.status} /></td>
                        <td className="col-first">{issue.first_level && issue.first_lesson ? `${issue.first_level} ${issue.first_lesson}` : '—'}</td>
                        <td className="col-sent" title={issue.sentence}>{issue.sentence}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* 선택 바 */}
          <div className="selection-bar">
            <div className="sel-info">
              <div className="sel-hint">선택한 표현</div>
              <div className="sel-word">{selected ? displaySurface(selected) : '—'}</div>
            </div>
            <div className="sel-actions">
              <button
                className="btn btn-primary"
                disabled={!selected || selected.status === 'allowed' || selected.status === 'custom_allowed'}
                onClick={() => selected && onAllow(selected)}
                style={{ fontSize: 12, padding: '7px 14px' }}
              >
                + 허용어 추가
              </button>
              <button
                className="btn btn-ghost"
                disabled={!selected}
                onClick={() => selected && navigator.clipboard.writeText(displaySurface(selected))}
              >
                복사
              </button>
              <button
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
