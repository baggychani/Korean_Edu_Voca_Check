// DictPanel.tsx — 화면을 채우는 사전 테이블 (PySide: 빈 검색 시 대량 목록)
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

  useEffect(() => {
    doSearch(initialQuery);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 목표 단원 바뀌면 판정 라벨 다시 로드
  useEffect(() => {
    doSearch(query);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [targetLevel, targetLesson]);

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') doSearch(query);
  };

  return (
    <div className="panel-fill page-enter">
      <div className="card card-fill">
        <div className="card-head">
          <span className="card-title">어휘 사전</span>
          <span className="card-hint">
            {loading ? '불러오는 중…' : `${results.length.toLocaleString()}개 · ${targetLevel} ${targetLesson} 기준`}
          </span>
        </div>
        <div className="card-body card-body-compact">
          <div className="search-row">
            <input
              className="search-input"
              type="text"
              placeholder="단어 검색… (비우면 전체 · Enter)"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKey}
            />
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => doSearch(query)}
              disabled={loading}
              style={{ flexShrink: 0 }}
            >
              {loading ? <span className="spinner" /> : '검색'}
            </button>
          </div>
        </div>

        {results.length > 0 ? (
          <div className="table-fill">
            <table className="dict-table">
              <thead>
                <tr>
                  <th>표제어</th>
                  <th>뜻풀이</th>
                  <th>첫 등장</th>
                  <th>목표 기준</th>
                </tr>
              </thead>
              <tbody>
                {results.map((r, i) => {
                  const firstSeen = r.first_level && r.first_lesson
                    ? `${r.first_level} ${r.first_lesson}`
                    : '—';
                  return (
                    <tr key={`${r.normalized_lemma}-${i}`}>
                      <td className="dict-lemma">{r.lemma}</td>
                      <td className="dict-gloss">{r.gloss_ko || r.gloss_en || '—'}</td>
                      <td className="dict-level">{firstSeen}</td>
                      <td>
                        {r.verdict_label_ko ? (
                          <span className={`badge ${
                            r.verdict_label_ko.includes('이릅') ? 'badge-early'
                              : r.verdict_label_ko.includes('없') ? 'badge-unknown'
                                : 'badge-ok'
                          }`}>
                            {r.verdict_label_ko.replace(/^[✅⚠❌]\s*/, '')}
                          </span>
                        ) : (
                          <span style={{ color: 'var(--ct-text3)', fontSize: 12 }}>—</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : !loading && (
          <div className="empty-state">
            <div className="empty-text">검색 결과가 없습니다</div>
            <div className="empty-sub">목표 단원: {targetLevel} {targetLesson}</div>
          </div>
        )}
      </div>
    </div>
  );
}
