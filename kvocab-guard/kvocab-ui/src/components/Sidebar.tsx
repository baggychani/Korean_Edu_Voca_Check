// Sidebar.tsx
import { type LevelInfo, type LessonInfo, type Tab } from '../types';

interface Props {
  activeTab: Tab;
  onTabChange: (tab: Tab) => void;
  levels: LevelInfo[];
  lessons: Record<string, LessonInfo[]>;
  selectedLevel: string;
  selectedLesson: string;
  onLevelChange: (v: string) => void;
  onLessonChange: (v: string) => void;
  useMorph: boolean;
  onMorphChange: (v: boolean) => void;
  issueCount: number;
  coverImage: string | null;
}

const NAV_ITEMS: { tab: Tab; icon: string; label: string }[] = [
  { tab: 'analyze', icon: '🔍', label: '텍스트 검사' },
  { tab: 'dict',    icon: '📖', label: '어휘 사전' },
  { tab: 'allow',   icon: '✅', label: '허용어 목록' },
  { tab: 'data',    icon: '🗄️', label: '데이터 관리' },
];

export default function Sidebar({
  activeTab, onTabChange,
  levels, lessons,
  selectedLevel, selectedLesson,
  onLevelChange, onLessonChange,
  useMorph, onMorphChange,
  issueCount,
  coverImage,
}: Props) {
  const currentLessons = lessons[selectedLevel] ?? [];

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="logo-eyebrow">한국어교육</div>
        <div className="logo-title">단어 레벨{'\n'}검사기</div>
        <div className="logo-sub">서울대 한국어 교재 기준</div>
      </div>

      {/* Nav */}
      <nav className="sidebar-nav">
        <div className="nav-section">메뉴</div>
        {NAV_ITEMS.map(({ tab, icon, label }) => (
          <div
            key={tab}
            className={`nav-item${activeTab === tab ? ' active' : ''}`}
            onClick={() => onTabChange(tab)}
          >
            <span className="nav-icon">{icon}</span>
            <span>{label}</span>
            {tab === 'analyze' && issueCount > 0 && (
              <span className="nav-badge">{issueCount}</span>
            )}
          </div>
        ))}
      </nav>

      <div className="sidebar-sep" />

      {/* Target */}
      <div className="sidebar-bottom">
        {/* 교재 이미지 프리뷰 */}
        <div className="cover-preview-container">
          <div className="cover-preview">
            {coverImage ? (
              <img className="cover-img" src={coverImage} alt={`${selectedLevel} 표지`} />
            ) : (
              <span>표지 준비 중</span>
            )}
          </div>
        </div>

        <div className="target-card">
          <div className="target-label">🎯 목표 단원</div>
          <select
            className="target-select"
            value={selectedLevel}
            onChange={e => onLevelChange(e.target.value)}
          >
            {levels.map(lv => (
              <option key={lv.level} value={lv.level}>{lv.level} — {lv.title_ko}</option>
            ))}
          </select>
          <select
            className="target-select"
            value={selectedLesson}
            onChange={e => onLessonChange(e.target.value)}
          >
            {currentLessons.map(ls => (
              <option key={ls.lesson} value={ls.lesson}>
                {ls.lesson} {ls.unit_topic ? `— ${ls.unit_topic}` : ''}
              </option>
            ))}
          </select>
          <div className="toggle-row">
            <label className="toggle">
              <input
                type="checkbox"
                checked={useMorph}
                onChange={e => onMorphChange(e.target.checked)}
              />
              <span className="toggle-track" />
            </label>
            <span className="toggle-text">형태소 분석 사용</span>
          </div>
        </div>
      </div>

      <div className="version-row">v1.0.0 · © 2026 Bae Gichan</div>
    </aside>
  );
}
