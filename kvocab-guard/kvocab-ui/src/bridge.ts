// bridge.ts — Tauri sidecar 통신 (개발 중에는 mock 데이터 반환)
//
// 실제 Tauri 빌드 시에는 @tauri-apps/plugin-shell 의 Command.sidecar 를 사용해
// kvocab_core.cli_server 와 stdin/stdout JSON-RPC 통신한다.
// 개발(Vite dev server) 환경에서는 window.__TAURI__ 가 없으므로 mock 을 반환한다.

import type {
  AnalyzeRequest,
  AnalyzeResult,
  AllowlistItem,
  LevelInfo,
  LessonInfo,
  LexemeSearchResult,
} from './types';

// ---------------------------------------------------------------------------
// JSON-RPC core (Tauri sidecar 연결 시 교체할 부분)
// ---------------------------------------------------------------------------

async function _rpc(method: string, params: Record<string, unknown>): Promise<unknown> {
  // TODO: 실 sidecar 연결
  //   const cmd = Command.sidecar('kvocab-sidecar');
  //   const child = await cmd.spawn();
  //   child.stdin.write(JSON.stringify({ id, method, params }) + '\n');
  //   const line = await readLine(child.stdout);
  //   return JSON.parse(line);

  // 개발용 mock — 실제 Python 프로세스 없이 UI 개발
  console.log('[bridge] RPC →', method, params);
  throw new Error(`[bridge] not yet connected: ${method}`);
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export async function apiInit(dbPath?: string) {
  return _rpc('init', { db_path: dbPath ?? null }) as Promise<{ seeded: boolean; lexeme_count: number }>;
}

export async function apiListLevels(): Promise<{ levels: LevelInfo[]; lessons: Record<string, LessonInfo[]> }> {
  return _rpc('list_levels_and_lessons', {}) as Promise<{ levels: LevelInfo[]; lessons: Record<string, LessonInfo[]> }>;
}

export async function apiAnalyze(req: AnalyzeRequest): Promise<AnalyzeResult> {
  return _rpc('analyze_text', { request_json: JSON.stringify(req) }) as Promise<AnalyzeResult>;
}

export async function apiSearchDict(
  query: string,
  targetLevel?: string,
  targetLesson?: string,
): Promise<LexemeSearchResult[]> {
  return _rpc('search_dictionary', {
    query,
    target_level: targetLevel ?? '',
    target_lesson: targetLesson ?? '',
  }) as Promise<LexemeSearchResult[]>;
}

export async function apiGetAllowlist(): Promise<AllowlistItem[]> {
  return _rpc('get_allowlist', {}) as Promise<AllowlistItem[]>;
}

export async function apiAddAllowlist(text: string, note?: string): Promise<{ id: number; text: string }> {
  return _rpc('add_to_allowlist', { text, note: note ?? null }) as Promise<{ id: number; text: string }>;
}

export async function apiRemoveAllowlist(itemId: number): Promise<{ deleted_id: number }> {
  return _rpc('remove_from_allowlist', { item_id: itemId }) as Promise<{ deleted_id: number }>;
}

export async function apiExtractFile(filePath: string): Promise<{ text: string; message: string | null; page_count: number }> {
  return _rpc('extract_text_from_file', { file_path: filePath }) as Promise<{ text: string; message: string | null; page_count: number }>;
}

export async function apiGetCover(level: string): Promise<{ base64: string | null }> {
  return _rpc('get_cover_base64', { level }) as Promise<{ base64: string | null }>;
}

export async function apiRunSeed(): Promise<{ stats: string }> {
  return _rpc('run_seed', {}) as Promise<{ stats: string }>;
}

export async function apiGetDbCounts(): Promise<Record<string, number>> {
  return _rpc('get_db_counts', {}) as Promise<Record<string, number>>;
}
