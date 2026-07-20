// mockData.ts — PySide와 맞춘 mock (sidecar 연결 전 UI 밀도용)
import type {
  AllowlistItem, AnalyzeResult, LevelInfo, LessonInfo, LexemeSearchResult,
} from './types';

export const MOCK_LEVELS: LevelInfo[] = [
  '1A', '1B', '2A', '2B', '3A', '3B', '4A', '4B', '5A', '5B', '6A', '6B',
].map((level, i) => ({
  level,
  series: '서울대 한국어',
  title_ko: `서울대 한국어 ${level}`,
  title_en: `SNU Korean ${level}`,
  sort_order: i + 1,
}));

export const MOCK_LESSONS: Record<string, LessonInfo[]> = {
  '2A': [
    { lesson: '1-1', unit_no: 1, lesson_no: 1, unit_topic: '일상생활', unit_title: '하루 일과', order_index: 201011 },
    { lesson: '1-2', unit_no: 1, lesson_no: 2, unit_topic: '일상생활', unit_title: '시간 표현', order_index: 201012 },
    { lesson: '2-1', unit_no: 2, lesson_no: 1, unit_topic: '취미와 여가', unit_title: '취미 소개', order_index: 201021 },
    { lesson: '2-2', unit_no: 2, lesson_no: 2, unit_topic: '취미와 여가', unit_title: '동호회 활동', order_index: 201022 },
    { lesson: '3-1', unit_no: 3, lesson_no: 1, unit_topic: '음식', unit_title: '한국 음식', order_index: 201031 },
  ],
};

for (const lv of MOCK_LEVELS.map((l) => l.level)) {
  if (!MOCK_LESSONS[lv]) {
    MOCK_LESSONS[lv] = [
      { lesson: '1-1', unit_no: 1, lesson_no: 1, unit_topic: '', unit_title: '1과', order_index: 0 },
      { lesson: '2-1', unit_no: 2, lesson_no: 1, unit_topic: '', unit_title: '2과', order_index: 1 },
      { lesson: '3-1', unit_no: 3, lesson_no: 1, unit_topic: '', unit_title: '3과', order_index: 2 },
    ];
  }
}

/** PySide DEFAULT_CHARACTER_NAMES 와 동일 (16명) */
const CHARACTER_NAMES = [
  '테오', '마리', '나나', '엥흐', '크리스', '소날', '제니',
  '김민우', '닛쿤', '이유진', '하이', '아야나', '안나',
  '다니엘', '에릭', '자밀라',
] as const;

export const MOCK_ALLOWLIST: AllowlistItem[] = CHARACTER_NAMES.map((name, i) => ({
  id: i + 1,
  text: name,
  normalized_text: name,
  allow_type: 'global',
  note: '교재 고정 등장인물',
  is_protected: true,
}));

const SEED_VOCAB: { lemma: string; gloss: string; level: string; lesson: string; page: number }[] = [
  { lemma: '안녕하세요', gloss: '인사말', level: '1A', lesson: '1-1', page: 10 },
  { lemma: '만나다', gloss: 'to meet', level: '1A', lesson: '1-1', page: 12 },
  { lemma: '이름', gloss: 'name', level: '1A', lesson: '1-1', page: 14 },
  { lemma: '학생', gloss: 'student', level: '1A', lesson: '1-2', page: 18 },
  { lemma: '선생님', gloss: 'teacher', level: '1A', lesson: '1-2', page: 20 },
  { lemma: '가다', gloss: 'to go', level: '1A', lesson: '2-1', page: 28 },
  { lemma: '오다', gloss: 'to come', level: '1A', lesson: '2-1', page: 28 },
  { lemma: '먹다', gloss: 'to eat', level: '1A', lesson: '2-2', page: 36 },
  { lemma: '마시다', gloss: 'to drink', level: '1A', lesson: '2-2', page: 36 },
  { lemma: '좋아하다', gloss: 'to like', level: '1A', lesson: '2-1', page: 14 },
  { lemma: '친구', gloss: 'friend', level: '1A', lesson: '3-1', page: 44 },
  { lemma: '가족', gloss: 'family', level: '1A', lesson: '3-1', page: 46 },
  { lemma: '학교', gloss: 'school', level: '1A', lesson: '3-2', page: 52 },
  { lemma: '집', gloss: 'house / home', level: '1A', lesson: '3-2', page: 54 },
  { lemma: '시간', gloss: 'time', level: '1B', lesson: '1-1', page: 10 },
  { lemma: '오늘', gloss: 'today', level: '1B', lesson: '1-1', page: 12 },
  { lemma: '내일', gloss: 'tomorrow', level: '1B', lesson: '1-1', page: 12 },
  { lemma: '어제', gloss: 'yesterday', level: '1B', lesson: '1-2', page: 18 },
  { lemma: '음식', gloss: 'food', level: '1B', lesson: '3-1', page: 30 },
  { lemma: '식당', gloss: 'restaurant', level: '1B', lesson: '3-1', page: 32 },
  { lemma: '커피', gloss: 'coffee', level: '1B', lesson: '3-2', page: 38 },
  { lemma: '물', gloss: 'water', level: '1B', lesson: '3-2', page: 38 },
  { lemma: '날씨', gloss: 'weather', level: '1B', lesson: '4-1', page: 48 },
  { lemma: '춥다', gloss: 'to be cold', level: '1B', lesson: '4-1', page: 50 },
  { lemma: '덥다', gloss: 'to be hot', level: '1B', lesson: '4-1', page: 50 },
  { lemma: '취미', gloss: 'hobby', level: '2A', lesson: '1-1', page: 12 },
  { lemma: '운동', gloss: 'exercise / sports', level: '2A', lesson: '1-1', page: 14 },
  { lemma: '영화', gloss: 'movie', level: '2A', lesson: '1-2', page: 22 },
  { lemma: '음악', gloss: 'music', level: '2A', lesson: '1-2', page: 24 },
  { lemma: '여행', gloss: 'travel', level: '2A', lesson: '2-1', page: 34 },
  { lemma: '사진', gloss: 'photo', level: '2A', lesson: '2-1', page: 36 },
  { lemma: '쇼핑', gloss: 'shopping', level: '2A', lesson: '2-2', page: 42 },
  { lemma: '시장', gloss: 'market', level: '2A', lesson: '2-2', page: 44 },
  { lemma: '한국 음식', gloss: 'Korean food', level: '2A', lesson: '3-1', page: 54 },
  { lemma: '비빔밥', gloss: 'bibimbap', level: '3A', lesson: '1-1', page: 22 },
  { lemma: '된장찌개', gloss: 'soybean paste stew', level: '3B', lesson: '2-1', page: 44 },
  { lemma: '즐기다', gloss: 'to enjoy', level: '2B', lesson: '4-1', page: 88 },
  { lemma: '경험', gloss: 'experience', level: '2B', lesson: '1-1', page: 12 },
  { lemma: '문화', gloss: 'culture', level: '2B', lesson: '1-2', page: 20 },
  { lemma: '전통', gloss: 'tradition', level: '2B', lesson: '2-1', page: 30 },
  { lemma: '축제', gloss: 'festival', level: '2B', lesson: '2-2', page: 40 },
  { lemma: '교통', gloss: 'transportation', level: '2B', lesson: '3-1', page: 50 },
  { lemma: '지하철', gloss: 'subway', level: '2B', lesson: '3-1', page: 52 },
  { lemma: '버스', gloss: 'bus', level: '2B', lesson: '3-1', page: 52 },
  { lemma: '택시', gloss: 'taxi', level: '2B', lesson: '3-2', page: 58 },
  { lemma: '예약하다', gloss: 'to reserve', level: '3A', lesson: '1-1', page: 14 },
  { lemma: '신청하다', gloss: 'to apply', level: '3A', lesson: '1-2', page: 24 },
  { lemma: '설명하다', gloss: 'to explain', level: '3A', lesson: '2-1', page: 34 },
  { lemma: '비교하다', gloss: 'to compare', level: '3A', lesson: '2-2', page: 44 },
  { lemma: '결정하다', gloss: 'to decide', level: '3A', lesson: '3-1', page: 54 },
  { lemma: '준비하다', gloss: 'to prepare', level: '3A', lesson: '3-2', page: 62 },
  { lemma: '건강', gloss: 'health', level: '3B', lesson: '1-1', page: 12 },
  { lemma: '병원', gloss: 'hospital', level: '3B', lesson: '1-1', page: 14 },
  { lemma: '약', gloss: 'medicine', level: '3B', lesson: '1-2', page: 22 },
  { lemma: '환경', gloss: 'environment', level: '3B', lesson: '2-1', page: 34 },
  { lemma: '쓰레기', gloss: 'trash', level: '3B', lesson: '2-2', page: 44 },
  { lemma: '재활용', gloss: 'recycling', level: '3B', lesson: '2-2', page: 46 },
  { lemma: '사회', gloss: 'society', level: '4A', lesson: '1-1', page: 12 },
  { lemma: '경제', gloss: 'economy', level: '4A', lesson: '1-2', page: 22 },
  { lemma: '정치', gloss: 'politics', level: '4A', lesson: '2-1', page: 34 },
  { lemma: '교육', gloss: 'education', level: '4A', lesson: '2-2', page: 44 },
  { lemma: '기술', gloss: 'technology', level: '4A', lesson: '3-1', page: 54 },
  { lemma: '인터넷', gloss: 'internet', level: '4A', lesson: '3-2', page: 62 },
  { lemma: '의견', gloss: 'opinion', level: '4B', lesson: '1-1', page: 12 },
  { lemma: '주장하다', gloss: 'to claim / argue', level: '4B', lesson: '1-2', page: 22 },
  { lemma: '반대하다', gloss: 'to oppose', level: '4B', lesson: '2-1', page: 34 },
  { lemma: '동의하다', gloss: 'to agree', level: '4B', lesson: '2-1', page: 34 },
  { lemma: '연구', gloss: 'research', level: '4B', lesson: '3-1', page: 54 },
  { lemma: '발표하다', gloss: 'to present', level: '4B', lesson: '3-2', page: 62 },
];

function orderIndex(level: string, lesson: string): number {
  const lo: Record<string, number> = {
    '1A': 1, '1B': 2, '2A': 3, '2B': 4, '3A': 5, '3B': 6,
    '4A': 7, '4B': 8, '5A': 9, '5B': 10, '6A': 11, '6B': 12,
  };
  const [u, l] = lesson.split('-').map(Number);
  return (lo[level] ?? 1) * 1000 + (u || 1) * 10 + (l || 1);
}

export function buildMockDict(targetLevel: string, targetLesson: string): LexemeSearchResult[] {
  const target = orderIndex(targetLevel, targetLesson);
  return SEED_VOCAB.map((v) => {
    const first = orderIndex(v.level, v.lesson);
    const early = first > target;
    return {
      lemma: v.lemma,
      gloss_en: v.gloss,
      gloss_ko: v.gloss,
      first_level: v.level,
      first_lesson: v.lesson,
      first_page: v.page,
      first_order_index: first,
      source_type: 'glossary_index',
      review_status: 'approved',
      item_type: 'vocab',
      normalized_lemma: v.lemma,
      verdict_label_ko: early ? '아직 이릅니다' : '사용 가능',
      occurrences: [],
      other_occurrences: [],
      equivalent_forms: [],
    };
  });
}

export const MOCK_RESULT: AnalyzeResult = {
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
    { surface: '비빔밥', lemma: '비빔밥', normalized: '비빔밥', pos: '', status: 'before_introduced', severity: 'high', reason: '뒤 단원', first_level: '3A', first_lesson: '1-1', first_page: 22, sentence: '특히 비빔밥과 된장찌개를 즐겨 먹습니다.', start: 3, end: 6, suggestions: [], review_status: 'approved', equivalent_lemma: null },
    { surface: '된장찌개', lemma: '된장찌개', normalized: '된장찌개', pos: '', status: 'before_introduced', severity: 'high', reason: '뒤 단원', first_level: '3B', first_lesson: '2-1', first_page: 44, sentence: '특히 비빔밥과 된장찌개를 즐겨 먹습니다.', start: 8, end: 12, suggestions: [], review_status: 'approved', equivalent_lemma: null },
    { surface: '즐겨', lemma: '즐기다', normalized: '즐기다', pos: '', status: 'before_introduced', severity: 'high', reason: '뒤 단원', first_level: '2B', first_lesson: '4-1', first_page: 88, sentence: '특히 비빔밥과 된장찌개를 즐겨 먹습니다.', start: 14, end: 16, suggestions: [], review_status: 'approved', equivalent_lemma: null },
    { surface: '특히', lemma: '특히', normalized: '특히', pos: '', status: 'unknown', severity: 'medium', reason: '교재 미등록', first_level: null, first_lesson: null, first_page: null, sentence: '특히 비빔밥과 된장찌개를 즐겨 먹습니다.', start: 0, end: 2, suggestions: [], review_status: null, equivalent_lemma: null },
    { surface: '정말', lemma: '정말', normalized: '정말', pos: '', status: 'unknown', severity: 'medium', reason: '교재 미등록', first_level: null, first_lesson: null, first_page: null, sentence: '저는 한국 음식을 정말 좋아해요.', start: 10, end: 12, suggestions: [], review_status: null, equivalent_lemma: null },
  ],
  allowed: [
    { surface: '좋아해요', lemma: '좋아하다', normalized: '좋아하다', pos: '', status: 'allowed', severity: 'none', reason: '목표 내', first_level: '1A', first_lesson: '2-1', first_page: 14, sentence: '저는 한국 음식을 정말 좋아해요.', start: 13, end: 17, suggestions: [], review_status: 'approved', equivalent_lemma: null },
    { surface: '음식', lemma: '음식', normalized: '음식', pos: '', status: 'allowed', severity: 'none', reason: '목표 내', first_level: '1B', first_lesson: '3-1', first_page: 30, sentence: '저는 한국 음식을 정말 좋아해요.', start: 7, end: 9, suggestions: [], review_status: 'approved', equivalent_lemma: null },
  ],
  debug_ignored: [],
};
