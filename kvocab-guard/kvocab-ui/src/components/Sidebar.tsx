// Sidebar.tsx — 목표 단원 · 표지 · 검사 옵션 (탭은 우측 상단)
import type { LevelInfo, LessonInfo } from '../types';
import CoverCarousel, { COVER_LEVELS } from './CoverCarousel';
import Collapsible from './Collapsible';

interface Props {
  levels: LevelInfo[];
  lessons: Record<string, LessonInfo[]>;
  selectedLevel: string;
  selectedLesson: string;
  onLevelChange: (v: string) => void;
  onLessonChange: (v: string) => void;
  useMorph: boolean;
  onMorphChange: (v: boolean) => void;
  coverImage: string | null;
}

export default function Sidebar({
  levels, lessons,
  selectedLevel, selectedLesson,
  onLevelChange, onLessonChange,
  useMorph, onMorphChange,
  coverImage,
}: Props) {
  const currentLessons = lessons[selectedLevel] ?? [];

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">KVocab<em>Guard</em></div>
        <div className="brand-sub">서울대 한국어 교재 기준</div>
      </div>

      <div className="sidebar-scroll">
        <div className="target-block">
          <div className="target-label">목표 단원</div>
          <select
            className="target-select"
            value={selectedLevel}
            onChange={(e) => onLevelChange(e.target.value)}
          >
            {levels.map((lv) => (
              <option key={lv.level} value={lv.level}>
                {lv.level} — {lv.title_ko}
              </option>
            ))}
          </select>
          <select
            className="target-select"
            value={selectedLesson}
            onChange={(e) => onLessonChange(e.target.value)}
          >
            {currentLessons.map((ls) => (
              <option key={ls.lesson} value={ls.lesson}>
                {ls.lesson}{ls.unit_topic ? ` — ${ls.unit_topic}` : ''}
              </option>
            ))}
          </select>
        </div>

        <div className="cover-block">
          <CoverCarousel
            levels={[...COVER_LEVELS]}
            selectedLevel={selectedLevel}
            onLevelChange={onLevelChange}
            coverSrc={coverImage}
          />
        </div>

        <Collapsible title="검사 옵션" defaultOpen>
          <div className="toggle-row">
            <label className="toggle">
              <input
                type="checkbox"
                checked={useMorph}
                onChange={(e) => onMorphChange(e.target.checked)}
              />
              <span className="toggle-track" />
            </label>
            <span className="toggle-text">형태소 분석 사용 (Kiwi)</span>
          </div>
        </Collapsible>
      </div>

      <div className="sidebar-footer">v1.0.0 · © 2026 Bae Gichan</div>
    </aside>
  );
}
