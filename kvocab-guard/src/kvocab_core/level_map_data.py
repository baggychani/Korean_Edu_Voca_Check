"""SNU Korean table of contents data (PDF 차례 기준)."""

from __future__ import annotations

SNU_2A_LESSONS: list[dict] = [
    {"lesson": "1-1", "unit_no": 1, "lesson_no": 1, "unit_topic": "소개", "unit_title": "한국어를 배우려고 한국에 왔어요", "page_start": 22, "page_end": 27},
    {"lesson": "1-2", "unit_no": 1, "lesson_no": 2, "unit_topic": "소개", "unit_title": "제 고향은 춘천인데 닭갈비가 유명합니다", "page_start": 28, "page_end": 37},
    {"lesson": "2-1", "unit_no": 2, "lesson_no": 1, "unit_topic": "취미", "unit_title": "저는 요리하는 걸 좋아해요", "page_start": 38, "page_end": 43},
    {"lesson": "2-2", "unit_no": 2, "lesson_no": 2, "unit_topic": "취미", "unit_title": "매주 금요일이나 토요일에 모입니다", "page_start": 44, "page_end": 53},
    {"lesson": "3-1", "unit_no": 3, "lesson_no": 1, "unit_topic": "여행 경험", "unit_title": "부산에 가 봤어요?", "page_start": 54, "page_end": 59},
    {"lesson": "3-2", "unit_no": 3, "lesson_no": 2, "unit_topic": "여행 경험", "unit_title": "1박 2일 동안 전주에 갔다 왔어요", "page_start": 60, "page_end": 69},
    {"lesson": "4-1", "unit_no": 4, "lesson_no": 1, "unit_topic": "쇼핑", "unit_title": "이거보다 더 긴 거 있어요?", "page_start": 70, "page_end": 75},
    {"lesson": "4-2", "unit_no": 4, "lesson_no": 2, "unit_topic": "쇼핑", "unit_title": "지난주에 산 운동화를 교환하고 싶습니다", "page_start": 76, "page_end": 85},
    {"lesson": "5-1", "unit_no": 5, "lesson_no": 1, "unit_topic": "우체국과 은행", "unit_title": "소포를 보내려고 왔는데요", "page_start": 86, "page_end": 91},
    {"lesson": "5-2", "unit_no": 5, "lesson_no": 2, "unit_topic": "우체국과 은행", "unit_title": "비밀번호를 눌러 주세요", "page_start": 92, "page_end": 101},
    {"lesson": "6-1", "unit_no": 6, "lesson_no": 1, "unit_topic": "하루 일과", "unit_title": "토요일마다 청소를 해요", "page_start": 102, "page_end": 107},
    {"lesson": "6-2", "unit_no": 6, "lesson_no": 2, "unit_topic": "하루 일과", "unit_title": "수업이 끝난 후에 인사동에 갔어요", "page_start": 108, "page_end": 117},
    {"lesson": "7-1", "unit_no": 7, "lesson_no": 1, "unit_topic": "길 찾기", "unit_title": "서울대학교까지 얼마나 걸릴까요?", "page_start": 118, "page_end": 123},
    {"lesson": "7-2", "unit_no": 7, "lesson_no": 2, "unit_topic": "길 찾기", "unit_title": "영화관이 어디에 있는지 아세요?", "page_start": 124, "page_end": 133},
    {"lesson": "8-1", "unit_no": 8, "lesson_no": 1, "unit_topic": "모임", "unit_title": "축하 파티를 하기로 했어요", "page_start": 134, "page_end": 139},
    {"lesson": "8-2", "unit_no": 8, "lesson_no": 2, "unit_topic": "모임", "unit_title": "제가 먹을 것을 준비할게요", "page_start": 140, "page_end": 149},
    {"lesson": "9-1", "unit_no": 9, "lesson_no": 1, "unit_topic": "건강한 생활", "unit_title": "약을 먹는 게 어때요?", "page_start": 150, "page_end": 155},
    {"lesson": "9-2", "unit_no": 9, "lesson_no": 2, "unit_topic": "건강한 생활", "unit_title": "목이 부은 것 같아요", "page_start": 156, "page_end": 164},
]

# 서울대 한국어 2B 차례 (PDF p.14, 단원 10~18, 부록 p.165)
SNU_2B_LESSONS: list[dict] = [
    {"lesson": "10-1", "unit_no": 10, "lesson_no": 1, "unit_topic": "학교생활", "unit_title": "우리 같이 시험공부를 하자", "page_start": 22, "page_end": 27},
    {"lesson": "10-2", "unit_no": 10, "lesson_no": 2, "unit_topic": "학교생활", "unit_title": "기숙사를 신청하려면 어떻게 해야 하나요?", "page_start": 28, "page_end": 37},
    {"lesson": "11-1", "unit_no": 11, "lesson_no": 1, "unit_topic": "음식", "unit_title": "난 순두부찌개 먹을래", "page_start": 38, "page_end": 43},
    {"lesson": "11-2", "unit_no": 11, "lesson_no": 2, "unit_topic": "음식", "unit_title": "제가 먹어 본 냉면 중에서 제일 맛있었어요", "page_start": 44, "page_end": 53},
    {"lesson": "12-1", "unit_no": 12, "lesson_no": 1, "unit_topic": "외모와 성격", "unit_title": "까만 스웨터를 입고 있어요", "page_start": 54, "page_end": 59},
    {"lesson": "12-2", "unit_no": 12, "lesson_no": 2, "unit_topic": "외모와 성격", "unit_title": "제 친구는 바다처럼 마음이 넓습니다", "page_start": 60, "page_end": 69},
    {"lesson": "13-1", "unit_no": 13, "lesson_no": 1, "unit_topic": "감정", "unit_title": "너무 속상하겠어요", "page_start": 70, "page_end": 75},
    {"lesson": "13-2", "unit_no": 13, "lesson_no": 2, "unit_topic": "감정", "unit_title": "친구들과 친해지고 싶습니다", "page_start": 76, "page_end": 85},
    {"lesson": "14-1", "unit_no": 14, "lesson_no": 1, "unit_topic": "인생", "unit_title": "대학교에 입학하게 됐어요", "page_start": 86, "page_end": 91},
    {"lesson": "14-2", "unit_no": 14, "lesson_no": 2, "unit_topic": "인생", "unit_title": "고마운 사람을 만난 적이 있습니다", "page_start": 92, "page_end": 101},
    {"lesson": "15-1", "unit_no": 15, "lesson_no": 1, "unit_topic": "집", "unit_title": "방이 넓어서 살기 좋아요", "page_start": 102, "page_end": 107},
    {"lesson": "15-2", "unit_no": 15, "lesson_no": 2, "unit_topic": "집", "unit_title": "벽에 가족사진이 걸려 있습니다", "page_start": 108, "page_end": 117},
    {"lesson": "16-1", "unit_no": 16, "lesson_no": 1, "unit_topic": "예절", "unit_title": "반말을 해도 돼요?", "page_start": 118, "page_end": 123},
    {"lesson": "16-2", "unit_no": 16, "lesson_no": 2, "unit_topic": "예절", "unit_title": "공연 중에 사진을 찍으면 안 됩니다", "page_start": 124, "page_end": 133},
    {"lesson": "17-1", "unit_no": 17, "lesson_no": 1, "unit_topic": "문화", "unit_title": "콘서트를 보기 위해서 표를 사 놓았어요", "page_start": 134, "page_end": 137},
    {"lesson": "17-2", "unit_no": 17, "lesson_no": 2, "unit_topic": "문화", "unit_title": "추석은 한국의 큰 명절 중 하나다", "page_start": 138, "page_end": 149},
    {"lesson": "18-1", "unit_no": 18, "lesson_no": 1, "unit_topic": "추억과 꿈", "unit_title": "이번 학기가 끝나서 좋기는 하지만 아쉬워요", "page_start": 150, "page_end": 155},
    {"lesson": "18-2", "unit_no": 18, "lesson_no": 2, "unit_topic": "추억과 꿈", "unit_title": "한국에 온 지 벌써 6개월이나 됐다", "page_start": 156, "page_end": 164},
]

# 서울대 한국어 3A 차례 (xlsx Level_Map 기준)
SNU_3A_LESSONS: list[dict] = [
    {"lesson": "1-1", "unit_no": 1, "lesson_no": 1, "unit_topic": "새로운 출발", "unit_title": "시작과 만남", "page_start": 24, "page_end": 29},
    {"lesson": "1-2", "unit_no": 1, "lesson_no": 2, "unit_topic": "새로운 출발", "unit_title": "학교생활", "page_start": 30, "page_end": 39},
    {"lesson": "2-1", "unit_no": 2, "lesson_no": 1, "unit_topic": "날씨와 여행", "unit_title": "날씨 정보", "page_start": 40, "page_end": 45},
    {"lesson": "2-2", "unit_no": 2, "lesson_no": 2, "unit_topic": "날씨와 여행", "unit_title": "휴가 계획", "page_start": 46, "page_end": 55},
    {"lesson": "3-1", "unit_no": 3, "lesson_no": 1, "unit_topic": "인터넷 콘텐츠", "unit_title": "재미있는 콘텐츠", "page_start": 56, "page_end": 61},
    {"lesson": "3-2", "unit_no": 3, "lesson_no": 2, "unit_topic": "인터넷 콘텐츠", "unit_title": "흥미로운 뉴스", "page_start": 62, "page_end": 71},
    {"lesson": "4-1", "unit_no": 4, "lesson_no": 1, "unit_topic": "약속과 만남", "unit_title": "약속", "page_start": 72, "page_end": 77},
    {"lesson": "4-2", "unit_no": 4, "lesson_no": 2, "unit_topic": "약속과 만남", "unit_title": "모임 장소", "page_start": 78, "page_end": 87},
    {"lesson": "5-1", "unit_no": 5, "lesson_no": 1, "unit_topic": "음식과 조리법", "unit_title": "좋아하는 음식", "page_start": 88, "page_end": 93},
    {"lesson": "5-2", "unit_no": 5, "lesson_no": 2, "unit_topic": "음식과 조리법", "unit_title": "조리법", "page_start": 94, "page_end": 103},
    {"lesson": "6-1", "unit_no": 6, "lesson_no": 1, "unit_topic": "여가 생활", "unit_title": "함께 하는 운동", "page_start": 104, "page_end": 109},
    {"lesson": "6-2", "unit_no": 6, "lesson_no": 2, "unit_topic": "여가 생활", "unit_title": "색다른 취미", "page_start": 110, "page_end": 119},
    {"lesson": "7-1", "unit_no": 7, "lesson_no": 1, "unit_topic": "소비와 절약", "unit_title": "소비 성향", "page_start": 120, "page_end": 125},
    {"lesson": "7-2", "unit_no": 7, "lesson_no": 2, "unit_topic": "소비와 절약", "unit_title": "중고 거래", "page_start": 126, "page_end": 135},
    {"lesson": "8-1", "unit_no": 8, "lesson_no": 1, "unit_topic": "한국 생활", "unit_title": "문제와 해결", "page_start": 136, "page_end": 141},
    {"lesson": "8-2", "unit_no": 8, "lesson_no": 2, "unit_topic": "한국 생활", "unit_title": "문화 차이", "page_start": 142, "page_end": 151},
    {"lesson": "9-1", "unit_no": 9, "lesson_no": 1, "unit_topic": "사건과 사고", "unit_title": "사고와 부상", "page_start": 152, "page_end": 157},
    {"lesson": "9-2", "unit_no": 9, "lesson_no": 2, "unit_topic": "사건과 사고", "unit_title": "분실", "page_start": 158, "page_end": 166},
]

LEVEL_LESSONS: dict[str, list[dict]] = {
    "2A": SNU_2A_LESSONS,
    "2B": SNU_2B_LESSONS,
    "3A": SNU_3A_LESSONS,
}
