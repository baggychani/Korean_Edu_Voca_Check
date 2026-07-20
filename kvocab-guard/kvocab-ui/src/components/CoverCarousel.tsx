// CoverCarousel.tsx — textbook cover carousel synced with level
import { useCallback, useMemo } from 'react';

export const COVER_LEVELS = [
  '1A', '1B', '2A', '2B', '3A', '3B', '4A', '4B', '5A', '5B', '6A', '6B',
] as const;

interface Props {
  levels: string[];
  selectedLevel: string;
  onLevelChange: (level: string) => void;
  coverSrc?: string | null;
}

function ChevronLeft() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M15 18l-6-6 6-6" />
    </svg>
  );
}

function ChevronRight() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 18l6-6-6-6" />
    </svg>
  );
}

export default function CoverCarousel({
  levels,
  selectedLevel,
  onLevelChange,
  coverSrc,
}: Props) {
  const list = useMemo(
    () => (levels.length > 0 ? levels : [...COVER_LEVELS]),
    [levels],
  );

  const index = Math.max(0, list.indexOf(selectedLevel));

  const go = useCallback(
    (dir: -1 | 1) => {
      const next = (index + dir + list.length) % list.length;
      onLevelChange(list[next]);
    },
    [index, list, onLevelChange],
  );

  return (
    <div className="cover-carousel">
      <div
        className="cover-track"
        style={{ transform: `translateX(-${index * 100}%)` }}
      >
        {list.map((lv) => {
          const src =
            lv === selectedLevel && coverSrc
              ? coverSrc
              : `/covers/${lv}.jpg`;
          return (
            <div key={lv} className="cover-slide">
              <img
                src={src}
                alt={`서울대 한국어 ${lv}`}
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = 'none';
                  const fb = (e.target as HTMLImageElement).nextElementSibling;
                  if (fb) (fb as HTMLElement).style.display = 'flex';
                }}
              />
              <div className="cover-fallback" style={{ display: 'none' }}>{lv}</div>
            </div>
          );
        })}
      </div>

      <div className="cover-level-tag">{selectedLevel}</div>

      <div className="cover-nav">
        <button type="button" aria-label="이전 교재" onClick={() => go(-1)}>
          <ChevronLeft />
        </button>
        <button type="button" aria-label="다음 교재" onClick={() => go(1)}>
          <ChevronRight />
        </button>
      </div>

      <div className="cover-dots">
        {list.map((lv, i) => (
          <button
            key={lv}
            type="button"
            className={`cover-dot${i === index ? ' active' : ''}`}
            aria-label={lv}
            onClick={() => onLevelChange(lv)}
          />
        ))}
      </div>
    </div>
  );
}
