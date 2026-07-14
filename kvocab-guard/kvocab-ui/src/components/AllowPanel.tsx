// AllowPanel.tsx — 허용어 목록 탭
import { useState } from 'react';
import type { AllowlistItem } from '../types';

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

  return (
    <div className="animate-in" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      {/* 추가 폼 */}
      <div className="card">
        <div className="card-head">
          <span className="card-title">허용어 추가</span>
          <span className="card-hint">검사 시 경고하지 않을 단어 원형을 등록합니다</span>
        </div>
        <div className="card-body">
          <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
            <input
              className="search-input"
              placeholder="단어 원형 (예: 비빔밥)"
              value={addText}
              onChange={e => setAddText(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleAdd()}
            />
            <input
              className="search-input"
              placeholder="메모 (선택)"
              value={addNote}
              onChange={e => setAddNote(e.target.value)}
              style={{ maxWidth: 200 }}
              onKeyDown={e => e.key === 'Enter' && handleAdd()}
            />
            <button
              className="btn btn-primary"
              disabled={!addText.trim() || adding}
              onClick={handleAdd}
              style={{ flexShrink: 0 }}
            >
              {adding ? <span className="spinner" /> : '+ 추가'}
            </button>
          </div>
        </div>
      </div>

      {/* 목록 */}
      <div className="card">
        <div className="card-head">
          <span className="card-title">허용어 목록</span>
          <span className="card-hint">{items.length}개</span>
        </div>
        {items.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">✅</div>
            <div className="empty-text">등록된 허용어가 없습니다</div>
            <div className="empty-sub">위 폼에서 단어를 추가하거나, 검사 결과에서 "허용어 추가" 버튼을 사용하세요</div>
          </div>
        ) : (
          <div>
            {items.map(item => (
              <div key={item.id} className="allow-row">
                <div>
                  <div className="allow-text">{item.text}</div>
                  {item.note && <div className="allow-note">{item.note}</div>}
                </div>
                {item.is_protected
                  ? <span className="allow-protected">🔒 보호됨</span>
                  : <button
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
                }
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
