# 데이터 분석 모드 (Data Analysis Mode)

## 워크플로우
1. **프로파일링**: 데이터 구조, 타입, 결측치, 분포 파악
2. **EDA**: 시각화, 상관관계, 패턴 탐색
3. **인사이트 도출**: 비즈니스 관점 해석, 가설 검증

## 필수 보고 항목
- **데이터 개요**: 행/열 수, 메모리 사용량, 기간
- **결측치**: 컬럼별 비율, 패턴 (MCAR/MAR/MNAR)
- **분포**: 수치형 기술통계, 범주형 빈도
- **이상치**: IQR/Z-score 기반 탐지
- **상관관계**: 주요 변수 간 상관 매트릭스
- **카디널리티**: unique 값 수, high-cardinality 경고

## 코드 규칙
- `pandas` profiling → `ydata-profiling` 사용 가능
- 시각화: `matplotlib`/`seaborn` 기본, `plotly` 대화형
- 대용량 데이터: `dask` 또는 `polars` 고려
- SQL 쿼리: CTE 우선, 파티션 활용, 비용 명시

## 에이전트 활용
- 데이터 품질: `data-quality-reviewer`
- 통계 분석: `data-scientist`
- BQ 최적화: `bq-specialist`

## 출력 형식
```
## Data Analysis: [데이터셋명]
### 1. 데이터 프로파일
### 2. 주요 발견
- [인사이트] — 근거: [통계/시각화]
### 3. 데이터 품질 이슈
### 4. 권장 액션
### 5. 추가 분석 제안
```
