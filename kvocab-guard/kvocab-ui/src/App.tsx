// App.tsx — KVocabGuard shell (PySide 레이아웃: 좌 목표 / 우 상단 탭)
import { useState, useCallback, useEffect } from 'react';
import './App.css';

import Sidebar from './components/Sidebar';
import AnalyzePanel from './components/AnalyzePanel';
import DictPanel from './components/DictPanel';
import AllowPanel from './components/AllowPanel';
import DataPanel from './components/DataPanel';
import Greeting, { shouldShowGreeting } from './components/Greeting';

import {
  MOCK_LEVELS, MOCK_LESSONS, MOCK_ALLOWLIST, MOCK_RESULT, buildMockDict,
} from './mockData';

import type { Tab, AnalyzeResult, Issue, AllowlistItem } from './types';

const TABS: { id: Tab; label: string }[] = [
  { id: 'analyze', label: '검사' },
  { id: 'dict', label: '어휘 사전' },
  { id: 'allow', label: '허용어' },
  { id: 'data', label: '데이터' },
];

export default function App() {
  const [showGreeting, setShowGreeting] = useState(shouldShowGreeting);
  const [tab, setTab] = useState<Tab>('analyze');
  const [levels] = useState(MOCK_LEVELS);
  const [lessons] = useState(MOCK_LESSONS);
  const [selectedLevel, setLevel] = useState('2B');
  const [selectedLesson, setLesson] = useState('1-1');
  const [useMorph, setUseMorph] = useState(true);
  const [analyzeResult, setResult] = useState<AnalyzeResult | null>(null);
  const [allowlist, setAllowlist] = useState<AllowlistItem[]>(MOCK_ALLOWLIST);
  const [busy] = useState(false);
  const [statusText, setStatus] = useState('준비됨');
  const [statusBusy, setStatusBusy] = useState(false);
  const [coverImage, setCoverImage] = useState<string | null>(null);
  const [pageKey, setPageKey] = useState(0);

  useEffect(() => {
    setCoverImage(`/covers/${selectedLevel}.jpg`);
    if (typeof window !== 'undefined' && (window as unknown as { __TAURI__?: unknown }).__TAURI__) {
      import('./bridge').then(({ apiGetCover }) => {
        apiGetCover(selectedLevel).then((res) => {
          if (res?.base64) setCoverImage(res.base64);
        }).catch(() => { /* keep local */ });
      });
    }
  }, [selectedLevel]);

  useEffect(() => {
    const ls = lessons[selectedLevel];
    if (ls && ls.length > 0 && !ls.find((l) => l.lesson === selectedLesson)) {
      setLesson(ls[0].lesson);
    }
  }, [selectedLevel, lessons, selectedLesson]);

  const handleTabChange = useCallback((t: Tab) => {
    setTab(t);
    setPageKey((k) => k + 1);
  }, []);

  const handleAnalyze = useCallback(async (_text: string): Promise<AnalyzeResult | null> => {
    setStatus('검사 중…');
    setStatusBusy(true);
    await new Promise((r) => setTimeout(r, 800));
    const result = {
      ...MOCK_RESULT,
      summary: { ...MOCK_RESULT.summary, target_display: `${selectedLevel} ${selectedLesson}` },
    };
    setResult(result);
    setStatus('준비됨');
    setStatusBusy(false);
    return result;
  }, [selectedLevel, selectedLesson]);

  const handleAllow = useCallback(async (issue: Issue) => {
    const label = issue.lemma !== issue.surface ? `${issue.surface}(${issue.lemma})` : issue.surface;
    if (!window.confirm(`「${label}」의 원형 「${issue.lemma}」을(를) 허용어 목록에 추가합니까?`)) return;
    setAllowlist((prev) => [...prev, {
      id: Date.now(),
      text: issue.lemma,
      normalized_text: issue.normalized,
      allow_type: 'global',
      note: `추가 시 목표: ${selectedLevel} ${selectedLesson}`,
      is_protected: false,
    }]);
    alert(`「${issue.lemma}」을(를) 허용어 목록에 추가했습니다.`);
  }, [selectedLevel, selectedLesson]);

  const handleDictSearch = useCallback(async (query: string) => {
    await new Promise((r) => setTimeout(r, 120));
    const all = buildMockDict(selectedLevel, selectedLesson);
    if (!query.trim()) return all;
    const q = query.trim();
    return all.filter((r) => r.lemma.includes(q) || (r.gloss_ko ?? '').includes(q));
  }, [selectedLevel, selectedLesson]);

  const handleAddAllow = useCallback(async (text: string, note?: string) => {
    await new Promise((r) => setTimeout(r, 80));
    setAllowlist((prev) => [...prev, {
      id: Date.now(), text, normalized_text: text,
      allow_type: 'global', note: note ?? null, is_protected: false,
    }]);
  }, []);

  const handleDelAllow = useCallback(async (id: number) => {
    setAllowlist((prev) => prev.filter((i) => i.id !== id));
  }, []);

  const handleSeed = useCallback(async () => {
    setStatus('DB 초기화 중…');
    setStatusBusy(true);
    await new Promise((r) => setTimeout(r, 1200));
    setStatus('준비됨');
    setStatusBusy(false);
    alert('Seed 완료 (mock)');
  }, []);

  const handleImport = useCallback(async () => {
    alert('XLSX 가져오기 — Tauri API 연결 후 사용 가능');
  }, []);

  const issueCount = analyzeResult?.summary.issue_count ?? 0;

  return (
    <>
      {showGreeting && <Greeting onDone={() => setShowGreeting(false)} />}

      <div className={`app-shell${showGreeting ? ' with-greeting' : ''}`}>
        <Sidebar
          levels={levels}
          lessons={lessons}
          selectedLevel={selectedLevel}
          selectedLesson={selectedLesson}
          onLevelChange={setLevel}
          onLessonChange={setLesson}
          useMorph={useMorph}
          onMorphChange={setUseMorph}
          coverImage={coverImage}
        />

        <div className="main">
          <header className="main-header">
            <div className="main-header-inner">
              <nav className="seg-tabs" aria-label="주요 메뉴">
                {TABS.map(({ id, label }) => (
                  <button
                    key={id}
                    type="button"
                    className={`seg-tab${tab === id ? ' active' : ''}`}
                    onClick={() => handleTabChange(id)}
                  >
                    {label}
                    {id === 'analyze' && issueCount > 0 && (
                      <span className="seg-tab-badge">{issueCount}</span>
                    )}
                  </button>
                ))}
              </nav>
              <div className="main-header-right">
                <span className="topbar-meta">{selectedLevel} {selectedLesson}</span>
                <div className={`status-pill${statusBusy ? ' busy' : ''}`}>
                  <span className="status-pill-dot" />
                  {statusText}
                </div>
              </div>
            </div>
          </header>

          <div className="page-content" key={`${tab}-${pageKey}`}>
            {tab === 'analyze' && (
              <AnalyzePanel
                onAnalyze={handleAnalyze}
                onAllow={handleAllow}
                targetLevel={selectedLevel}
                targetLesson={selectedLesson}
                busy={busy || statusBusy}
              />
            )}
            {tab === 'dict' && (
              <DictPanel
                onSearch={handleDictSearch}
                targetLevel={selectedLevel}
                targetLesson={selectedLesson}
              />
            )}
            {tab === 'allow' && (
              <AllowPanel
                items={allowlist}
                onAdd={handleAddAllow}
                onDelete={handleDelAllow}
              />
            )}
            {tab === 'data' && (
              <DataPanel
                counts={{
                  lexemes: buildMockDict(selectedLevel, selectedLesson).length,
                  levels: levels.length,
                  lessons: Object.values(lessons).reduce((n, a) => n + a.length, 0),
                  allowlist: allowlist.length,
                }}
                onSeed={handleSeed}
                onImportXlsx={handleImport}
                busy={statusBusy}
              />
            )}
          </div>
        </div>
      </div>
    </>
  );
}
