// App.tsx — KVocabGuard 메인 앱
import { useState, useCallback, useEffect } from 'react';
import './App.css';

import Sidebar     from './components/Sidebar';
import AnalyzePanel from './components/AnalyzePanel';
import DictPanel   from './components/DictPanel';
import AllowPanel  from './components/AllowPanel';
import DataPanel   from './components/DataPanel';

import type {
  Tab, AnalyzeResult, Issue,
  AllowlistItem, LevelInfo, LessonInfo,
  LexemeSearchResult,
} from './types';

// ── mock data (Tauri sidecar 연결 전 UI 개발용) ──────────────
const MOCK_LEVELS: LevelInfo[] = [
  { level: '1A', series: '서울대 한국어', title_ko: '서울대 한국어 1A', title_en: 'SNU Korean 1A', sort_order: 1 },
  { level: '1B', series: '서울대 한국어', title_ko: '서울대 한국어 1B', title_en: 'SNU Korean 1B', sort_order: 2 },
  { level: '2A', series: '서울대 한국어', title_ko: '서울대 한국어 2A', title_en: 'SNU Korean 2A', sort_order: 3 },
  { level: '2B', series: '서울대 한국어', title_ko: '서울대 한국어 2B', title_en: 'SNU Korean 2B', sort_order: 4 },
  { level: '3A', series: '서울대 한국어', title_ko: '서울대 한국어 3A', title_en: 'SNU Korean 3A', sort_order: 5 },
  { level: '3B', series: '서울대 한국어', title_ko: '서울대 한국어 3B', title_en: 'SNU Korean 3B', sort_order: 6 },
];

const MOCK_LESSONS: Record<string, LessonInfo[]> = {
  '2A': [
    { lesson: '1-1', unit_no: 1, lesson_no: 1, unit_topic: '일상생활', unit_title: '하루 일과', order_index: 201011 },
    { lesson: '1-2', unit_no: 1, lesson_no: 2, unit_topic: '일상생활', unit_title: '시간 표현', order_index: 201012 },
    { lesson: '2-1', unit_no: 2, lesson_no: 1, unit_topic: '취미와 여가', unit_title: '취미 소개', order_index: 201021 },
    { lesson: '2-2', unit_no: 2, lesson_no: 2, unit_topic: '취미와 여가', unit_title: '동호회 활동', order_index: 201022 },
    { lesson: '3-1', unit_no: 3, lesson_no: 1, unit_topic: '음식', unit_title: '한국 음식', order_index: 201031 },
  ],
};
for (const lv of ['1A','1B','2B','3A','3B']) {
  MOCK_LESSONS[lv] = [
    { lesson: '1-1', unit_no:1, lesson_no:1, unit_topic:'', unit_title:'1과', order_index: 0 },
    { lesson: '2-1', unit_no:2, lesson_no:1, unit_topic:'', unit_title:'2과', order_index: 1 },
  ];
}

const MOCK_RESULT: AnalyzeResult = {
  summary: {
    target_display: '2A 3-1',
    total_tokens: 18,
    issue_count: 5,
    before_introduced_count: 3,
    unknown_count: 2,
    ignored_count: 0,
    allowed_count: 2,
    max_known_order_index: 301011,
    max_known_display: '3A 1-1',
  },
  issues: [
    { surface:'비빔밥', lemma:'비빔밥', normalized:'비빔밥', pos:'', status:'before_introduced', severity:'high', reason:'뒤 단원', first_level:'3A', first_lesson:'1-1', first_page:22, sentence:'특히 비빔밥과 된장찌개를 즐겨 먹습니다.', start:3, end:6, suggestions:[], review_status:'approved', equivalent_lemma:null },
    { surface:'된장찌개', lemma:'된장찌개', normalized:'된장찌개', pos:'', status:'before_introduced', severity:'high', reason:'뒤 단원', first_level:'3B', first_lesson:'2-1', first_page:44, sentence:'특히 비빔밥과 된장찌개를 즐겨 먹습니다.', start:8, end:12, suggestions:[], review_status:'approved', equivalent_lemma:null },
    { surface:'즐겨', lemma:'즐기다', normalized:'즐기다', pos:'', status:'before_introduced', severity:'high', reason:'뒤 단원', first_level:'2B', first_lesson:'4-1', first_page:88, sentence:'특히 비빔밥과 된장찌개를 즐겨 먹습니다.', start:14, end:16, suggestions:[], review_status:'approved', equivalent_lemma:null },
    { surface:'특히', lemma:'특히', normalized:'특히', pos:'', status:'unknown', severity:'medium', reason:'교재 미등록', first_level:null, first_lesson:null, first_page:null, sentence:'특히 비빔밥과 된장찌개를 즐겨 먹습니다.', start:0, end:2, suggestions:[], review_status:null, equivalent_lemma:null },
    { surface:'정말', lemma:'정말', normalized:'정말', pos:'', status:'unknown', severity:'medium', reason:'교재 미등록', first_level:null, first_lesson:null, first_page:null, sentence:'저는 한국 음식을 정말 좋아해요.', start:10, end:12, suggestions:[], review_status:null, equivalent_lemma:null },
  ],
  allowed: [
    { surface:'좋아해요', lemma:'좋아하다', normalized:'좋아하다', pos:'', status:'allowed', severity:'none', reason:'목표 내', first_level:'1A', first_lesson:'2-1', first_page:14, sentence:'저는 한국 음식을 정말 좋아해요.', start:13, end:17, suggestions:[], review_status:'approved', equivalent_lemma:null },
    { surface:'음식', lemma:'음식', normalized:'음식', pos:'', status:'allowed', severity:'none', reason:'목표 내', first_level:'1B', first_lesson:'3-1', first_page:30, sentence:'저는 한국 음식을 정말 좋아해요.', start:7, end:9, suggestions:[], review_status:'approved', equivalent_lemma:null },
  ],
  debug_ignored: [],
};

const MOCK_DICT: LexemeSearchResult[] = [
  { lemma:'안녕하세요', gloss_en:'hello', gloss_ko:'안녕 인사말', first_level:'1A', first_lesson:'1-1', first_page:10, first_order_index:101011, source_type:'glossary_index', review_status:'approved', item_type:'vocab', normalized_lemma:'안녕하세요', verdict_label_ko:'✅ 사용 가능', occurrences:[], other_occurrences:[], equivalent_forms:['안녕'] },
  { lemma:'좋아하다', gloss_en:'to like', gloss_ko:'좋아하다', first_level:'1A', first_lesson:'2-1', first_page:14, first_order_index:101021, source_type:'glossary_index', review_status:'approved', item_type:'vocab', normalized_lemma:'좋아하다', verdict_label_ko:'✅ 사용 가능', occurrences:[], other_occurrences:[], equivalent_forms:[] },
  { lemma:'비빔밥', gloss_en:'bibimbap', gloss_ko:'비빔밥 (음식)', first_level:'3A', first_lesson:'1-1', first_page:22, first_order_index:301011, source_type:'glossary_index', review_status:'approved', item_type:'vocab', normalized_lemma:'비빔밥', verdict_label_ko:'⚠ 아직 이릅니다', occurrences:[], other_occurrences:[], equivalent_forms:[] },
];

const MOCK_ALLOWLIST: AllowlistItem[] = [
  { id:1, text:'테오', normalized_text:'테오', allow_type:'global', note:'교재 고정 등장인물', is_protected:true },
  { id:2, text:'마리', normalized_text:'마리', allow_type:'global', note:'교재 고정 등장인물', is_protected:true },
  { id:3, text:'김민우', normalized_text:'김민우', allow_type:'global', note:'교재 고정 등장인물', is_protected:true },
];

// ── App ───────────────────────────────────────────────────
export default function App() {
  const [tab, setTab]                   = useState<Tab>('analyze');
  const [levels]                        = useState<LevelInfo[]>(MOCK_LEVELS);
  const [lessons]                       = useState<Record<string, LessonInfo[]>>(MOCK_LESSONS);
  const [selectedLevel, setLevel]       = useState('2A');
  const [selectedLesson, setLesson]     = useState('3-1');
  const [useMorph, setUseMorph]         = useState(true);
  const [analyzeResult, setResult]      = useState<AnalyzeResult | null>(null);
  const [allowlist, setAllowlist]       = useState<AllowlistItem[]>(MOCK_ALLOWLIST);
  const [busy]                          = useState(false);
  const [statusText, setStatus]         = useState('준비됨');
  const [statusBusy, setStatusBusy]     = useState(false);
  const [coverImage, setCoverImage]     = useState<string | null>(null);

  // 교재 이미지 프리뷰 업데이트 훅
  useEffect(() => {
    // 1단계: 로컬 개발 환경용 public/covers/ 직접 매핑 시도
    setCoverImage(`/covers/${selectedLevel}.jpg`);

    // 2단계: Tauri 환경(window.__TAURI__)일 경우 Tauri Bridge를 통해 사이드카에서 가져옴
    // (이중 검증 처리로 개발 모드/Tauri GUI 모드 둘 다 작동 보장)
    if (typeof window !== 'undefined' && (window as any).__TAURI__) {
      import('./bridge').then(({ apiGetCover }) => {
        apiGetCover(selectedLevel).then(res => {
          if (res && res.base64) {
            setCoverImage(res.base64);
          }
        });
      });
    }
  }, [selectedLevel]);

  // 초기 단원 동기화
  useEffect(() => {
    const ls = lessons[selectedLevel];
    if (ls && ls.length > 0 && !ls.find(l => l.lesson === selectedLesson)) {
      setLesson(ls[0].lesson);
    }
  }, [selectedLevel, lessons, selectedLesson]);

  // ── 검사 ─────────────────────────────────────────────────
  const handleAnalyze = useCallback(async (_text: string): Promise<AnalyzeResult | null> => {
    setStatus('검사 중…');
    setStatusBusy(true);
    // mock: 실제로는 apiAnalyze 호출
    await new Promise(r => setTimeout(r, 800));
    const result = { ...MOCK_RESULT, summary: { ...MOCK_RESULT.summary, target_display: `${selectedLevel} ${selectedLesson}` } };
    setResult(result);
    setStatus('준비됨');
    setStatusBusy(false);
    return result;
  }, [selectedLevel, selectedLesson]);

  // ── 허용어 추가 (검사 결과에서) ───────────────────────────
  const handleAllow = useCallback(async (issue: Issue) => {
    const label = issue.lemma !== issue.surface ? `${issue.surface}(${issue.lemma})` : issue.surface;
    if (!window.confirm(`「${label}」의 원형 「${issue.lemma}」을(를) 허용어 목록에 추가합니까?`)) return;
    // mock
    const newItem: AllowlistItem = {
      id: Date.now(),
      text: issue.lemma,
      normalized_text: issue.normalized,
      allow_type: 'global',
      note: `추가 시 목표: ${selectedLevel} ${selectedLesson}`,
      is_protected: false,
    };
    setAllowlist(prev => [...prev, newItem]);
    alert(`「${issue.lemma}」을(를) 허용어 목록에 추가했습니다.`);
  }, [selectedLevel, selectedLesson]);

  // ── 사전 검색 ─────────────────────────────────────────────
  const handleDictSearch = useCallback(async (query: string): Promise<LexemeSearchResult[]> => {
    await new Promise(r => setTimeout(r, 200));
    if (!query) return MOCK_DICT;
    return MOCK_DICT.filter(r => r.lemma.includes(query) || (r.gloss_ko ?? '').includes(query));
  }, []);

  // ── 허용어 추가/삭제 ─────────────────────────────────────
  const handleAddAllow = useCallback(async (text: string, note?: string) => {
    await new Promise(r => setTimeout(r, 100));
    setAllowlist(prev => [...prev, {
      id: Date.now(), text, normalized_text: text,
      allow_type: 'global', note: note ?? null, is_protected: false,
    }]);
  }, []);

  const handleDelAllow = useCallback(async (id: number) => {
    setAllowlist(prev => prev.filter(i => i.id !== id));
  }, []);

  // ── seed / import ─────────────────────────────────────────
  const handleSeed = useCallback(async () => {
    setStatus('DB 초기화 중…'); setStatusBusy(true);
    await new Promise(r => setTimeout(r, 1200));
    setStatus('준비됨'); setStatusBusy(false);
    alert('Seed 완료 (mock)');
  }, []);
  const handleImport = useCallback(async () => {
    alert('XLSX 가져오기 — Tauri API 연결 후 사용 가능');
  }, []);

  const issueCount = analyzeResult?.summary.issue_count ?? 0;

  const TAB_LABELS: Record<Tab, string> = {
    analyze: '🔍 검사',
    dict:    '📖 어휘 사전',
    allow:   '✅ 허용어',
    data:    '🗄️ 데이터',
  };

  return (
    <div className="app-shell">
      <Sidebar
        activeTab={tab}
        onTabChange={setTab}
        levels={levels}
        lessons={lessons}
        selectedLevel={selectedLevel}
        selectedLesson={selectedLesson}
        onLevelChange={v => { setLevel(v); }}
        onLessonChange={setLesson}
        useMorph={useMorph}
        onMorphChange={setUseMorph}
        issueCount={issueCount}
        coverImage={coverImage}
      />

      <div className="main">
        {/* Topbar */}
        <div className="topbar">
          <span className="topbar-title">한국어교육 단어 레벨 검사기</span>
          <span className="topbar-spacer" />
          <div className={`status-pill${statusBusy ? ' busy' : ''}`}>
            <span className="status-pill-dot" />
            {statusText}
          </div>
        </div>

        {/* Tab bar */}
        <div className="tab-bar">
          {(Object.keys(TAB_LABELS) as Tab[]).map(t => (
            <div
              key={t}
              className={`tab${tab === t ? ' active' : ''}`}
              onClick={() => setTab(t)}
            >
              {TAB_LABELS[t]}
            </div>
          ))}
        </div>

        {/* Page */}
        <div className="page-content">
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
              counts={{ lexemes: 4832, levels: 6, lessons: 72, allowlist: allowlist.length }}
              onSeed={handleSeed}
              onImportXlsx={handleImport}
              busy={statusBusy}
            />
          )}
        </div>
      </div>
    </div>
  );
}
