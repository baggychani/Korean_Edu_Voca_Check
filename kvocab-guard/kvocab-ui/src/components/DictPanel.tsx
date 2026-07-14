// DictPanel.tsx — 어휘 사전 탭
import { useState, useCallback, useEffect } from 'react';
import type { LexemeSearchResult } from '../types';

interface Props {
  onSearch: (query: string) => Promise<LexemeSearchResult[]>;
  targetLevel: string;
  targetLesson: string;
  initialQuery?: string;
}

export default function DictPanel({ onSearch, targetLevel, targetLesson, initialQuery = '' }: Props) {
  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState<LexemeSearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  const doSearch = useCallback(async (q: string) => {
    setLoading(true);
    try {
      const r = await onSearch(q);
      setResults(r);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [onSearch]);

  // 마운트 시 초기 로드
  useEffect(() => {
    doSearch(initialQuery);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') doSearch(query);
  };

  return (
    <div className="animate-in" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div className="card">
        <div className="card-head">
          <span className="card-title">어휘 사전</span>
          <span className="card-hint">목표 단원 기준 단어 레벨을 확인합니다</span>
        </div>
        <div className="card-body">
          <div style={{ display: 'flex', gap: 8 }}>
            <input
              className="search-input"
              type="text"
              placeholder="단어 검색… (Enter 로 검색)"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={handleKey}
            />
            <button className="btn btn-primary" onClick={() => doSearch(query)} disabled={loading} style={{ flexShrink: 0 }}>
              {loading ? <span className="spinner" /> : '검색'}
            </button>
          </div>
        </div>

        {results.length > 0 ? (
          <div className="table-wrap" style={{ borderRadius: 0 }}>
            <table className="dict-table">
              <thead>
                <tr>
                  <th>표제어</th>
                  <th>뜻풀이</th>
                  <th>처음 나오는 곳</th>
                  <th>목표 기준</th>
                </tr>
              </thead>
              <tbody>
                {results.map((r, i) => {
                  const firstSeen = r.first_level && r.first_lesson
                    ? `${r.first_level} ${r.first_lesson}` : '—';
                  return (
                    <tr key={`${r.normalized_lemma}-${i}`}>
                      <td className="dict-lemma">{r.lemma}</td>
                      <td className="dict-gloss">{r.gloss_ko || r.gloss_en || '—'}</td>
                      <td className="dict-level">{firstSeen}</td>
                      <td>
                        {r.verdict_label_ko
                          ? <span className={`badge ${
                              r.verdict_label_ko.includes('이릅') ? 'badge-early' :
                              r.verdict_label_ko.includes('없') ? 'badge-unknown' : 'badge-ok'
                            }`}>{r.verdict_label_ko}</span>
                          : <span style={{ color: 'var(--ct-text3)', fontSize: 12 }}>—</span>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : !loading && (
          <div className="empty-state">
            <div className="empty-icon">📖</div>
            <div className="empty-text">검색어를 입력하거나 Enter 를 눌러 전체 목록을 불러오세요</div>
            <div className="empty-sub">목표 단원: {targetLevel} {targetLesson}</div>
          </div>
        )}
      </div>
    </div>
  );
}
