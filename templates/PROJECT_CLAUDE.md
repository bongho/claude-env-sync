# 프로젝트: [프로젝트명]

## 목표
- 비즈니스 목표: [예: '신규 유저 30일 리텐션 5% 향상']
- 제품 가설: [예: '개인화 추천 제공 시 재방문율 증가']

## 성공 지표
- 제품 KPI: [예: CTR, 리텐션]
- 모델 KPI: [예: nDCG@10, Latency < 100ms]

## 기술 스택
- Cloud: [GCP/AWS]
- DW: [BigQuery]
- Orchestration: [Airflow]
- ML: [PyTorch/TensorFlow]
- Serving: [TF Serving/Triton]

## 핵심 데이터
- `project.dataset.user_logs`: 유저 행동 로그
  - 주요 컬럼: user_id, event_ts, item_id
- `project.dataset.items`: 상품 메타
  - 주요 컬럼: item_id, category, embedding

## 관련 문서
- PRD: [링크]
- 아키텍처: [링크]
- 실험 설계: [링크]

## 범위
- In-Scope: [포함 항목]
- Out-of-Scope: [제외 항목]
