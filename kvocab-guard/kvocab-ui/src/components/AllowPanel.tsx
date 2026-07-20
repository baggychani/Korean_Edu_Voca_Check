// AllowPanel.tsx — 보호 16명 + 사용자 허용어 (화면 채움)
import { useState } from 'react';
import type { AllowlistItem } from '../types';
import Collapsible from './Collapsible';

interface Props {
  items: AllowlistItem[];
  onAdd: (text: string, note?: string) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

export default function AllowPanel({ items, onAdd, onDelete }: Props) {
  const [addText, setAddText] = useState('');
  const [addNote, setAddNote] = useState('');
  const [adding, setAdding] = useState(false);

  const handleAdd = async () => {
    if (!addText.trim() || adding) return;
    setAdding(true);
    try {
      await onAdd(addText.trim(), addNote.trim() || undefined);
      setAddText('');
      setAddNote('');
    } finally {
      setAdding(false);
    }
  };

  const protectedItems = items.filter((i) => i.is_protected);
  const customItems = items.filter((i) => !i.is_protected);

  return (
    <div className="panel-fill page-enter">
      <div className="card">
        <div className="card-head">
          <span className="card-title">허용어 추가</span>
          <span className="card-hint">검사 시 경고를 건너뜁니다</span>
        </div>
        <div className="card-body card-body-compact">
          <div className="search-row">
            <input
              className="search-input"
              placeholder="단어 원형 (예: 비빔밥)"
              value={addText}
              onChange={(e) => setAddText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
            />
            <input
              className="search-input"
              placeholder="메모 (선택)"
              value={addNote}
              onChange={(e) => setAddNote(e.target.value)}
              style={{ maxWidth: 220 }}
              onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
            />
            <button
              type="button"
              className="btn btn-primary"
              disabled={!addText.trim() || adding}
              onClick={handleAdd}
              style={{ flexShrink: 0 }}
            >
              {adding ? <span className="spinner" /> : '추가'}
            </button>
          </div>
        </div>
      </div>

      <div className="allow-fill">
        <div className="card card-fill">
          <div className="card-head">
            <span className="card-title">사용자 허용어</span>
            <span className="card-hint">{customItems.length}개</span>
          </div>
          <div className="table-fill allow-scroll">
            {customItems.length === 0 ? (
              <div className="empty-state" style={{ padding: '28px 20px' }}>
                <div className="empty-text" style={{ fontSize: 13 }}>등록된 사용자 허용어가 없습니다</div>
                <div className="empty-sub">위 폼 또는 검사 결과에서 추가하세요</div>
              </div>
            ) : (
              customItems.map((item) => (
                <div key={item.id} className="allow-row">
                  <div>
                    <div className="allow-text">{item.text}</div>
                    {item.note && <div className="allow-note">{item.note}</div>}
                  </div>
                  <button
                    type="button"
                    className="btn btn-danger"
                    style={{ fontSize: 11, padding: '4px 10px' }}
                    onClick={() => {
                      if (window.confirm(`「${item.text}」을(를) 허용어 목록에서 삭제합니까?`)) {
                        onDelete(item.id);
                      }
                    }}
                  >
                    삭제
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        <Collapsible
          light
          defaultOpen
          className="card-like"
          title={
            <>
              보호된 항목 (교재 등장인물)
              <span className="group-count">{protectedItems.length}</span>
            </>
          }
        >
          <div className="allow-scroll" style={{ maxHeight: 280 }}>
            {protectedItems.map((item) => (
              <div key={item.id} className="allow-row">
                <div>
                  <div className="allow-text">{item.text}</div>
                  {item.note && <div className="allow-note">{item.note}</div>}
                </div>
                <span className="allow-protected">보호됨</span>
              </div>
            ))}
          </div>
        </Collapsible>
      </div>
    </div>
  );
}
