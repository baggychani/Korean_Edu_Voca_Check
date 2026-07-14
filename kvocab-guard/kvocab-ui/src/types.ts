// types.ts — 공유 타입 정의

export interface AnalyzeRequest {
  text: string;
  target_level: string;
  target_lesson: string;
  strictness?: 'loose' | 'balanced' | 'strict';
  use_morph?: boolean;
  show_debug_ignored?: boolean;
}

export interface Issue {
  surface: string;
  lemma: string;
  normalized: string;
  pos: string;
  status: 'allowed' | 'before_introduced' | 'unknown' | 'custom_allowed' | 'ignored_nnp' | 'ignored_pattern';
  severity: 'none' | 'low' | 'medium' | 'high';
  reason: string;
  first_level: string | null;
  first_lesson: string | null;
  first_page: number | null;
  sentence: string;
  start: number;
  end: number;
  suggestions: string[];
  review_status: string | null;
  equivalent_lemma: string | null;
  first_seen_display?: string;
}

export interface AnalyzeSummary {
  target_display: string;
  total_tokens: number;
  issue_count: number;
  before_introduced_count: number;
  unknown_count: number;
  ignored_count: number;
  allowed_count: number;
  max_known_order_index: number | null;
  max_known_display: string;
}

export interface AnalyzeResult {
  summary: AnalyzeSummary;
  issues: Issue[];
  allowed: Issue[];
  debug_ignored: Issue[];
}

export interface LevelInfo {
  level: string;
  series: string;
  title_ko: string;
  title_en: string;
  sort_order: number;
}

export interface LessonInfo {
  lesson: string;
  unit_no: number;
  lesson_no: number;
  unit_topic: string;
  unit_title: string;
  order_index: number;
}

export interface LexemeSearchResult {
  lemma: string;
  gloss_en: string | null;
  gloss_ko: string | null;
  first_level: string | null;
  first_lesson: string | null;
  first_page: number | null;
  first_order_index: number | null;
  source_type: string;
  review_status: string;
  item_type: string;
  normalized_lemma: string;
  verdict_label_ko: string;
  occurrences: Record<string, unknown>[];
  other_occurrences: string[];
  equivalent_forms: string[];
}

export interface AllowlistItem {
  id: number;
  text: string;
  normalized_text: string;
  allow_type: string;
  note: string | null;
  is_protected: boolean;
}

export type Tab = 'analyze' | 'dict' | 'allow' | 'data';
export type FilterKey = 'all' | 'allowed' | 'before_introduced' | 'unknown';
