# 실험 모드 (Experiment Mode)

## 실험 원칙
1. **Baseline 먼저**: 항상 비교 기준 확립
2. **단일 변수**: 한 번에 하나만 변경
3. **기록**: 모든 설정과 결과 문서화
4. **비교**: 통계적 유의성 검증

## 실험 워크플로우
```
Baseline 확립 → 가설 수립 → 단일 변수 변경 → 실행 → 기록 → 비교 → 결정
```

## 필수 기록 항목
- **가설**: 명확한 예측 문장
- **변경 사항**: 정확히 무엇을 바꿨는지
- **파라미터**: 모든 하이퍼파라미터
- **random_seed**: 재현성 보장
- **데이터 버전**: 스냅샷/해시
- **코드 버전**: git SHA
- **메트릭**: 주요 + 보조 + 비즈니스 메트릭
- **결과**: baseline 대비 절대/상대 변화
- **p-value / CI**: 통계적 유의성

## 실험 네이밍
- `exp-YYYYMMDD-<description>`
- 예: `exp-20240115-xgb-lr-tuning`

## 에이전트 활용
- 실험 추적: `experiment-tracker`
- 모델 평가: `model-evaluator`
- 데이터 검증: `data-quality-reviewer`
- 통계 분석: `data-scientist`

## 금지 사항
- 가설 없는 실험 금지
- 다중 변수 동시 변경 금지 (명확한 사유 없이)
- Baseline 미설정 상태에서 성능 주장 금지
- 재현 불가능한 실험 결과 보고 금지

## 출력 형식
```
## Experiment: [exp-YYYYMMDD-name]
### 가설
### 설정 (config YAML)
### 결과
| Metric | Baseline | Experiment | Δ | p-value |
### 분석
### 결정: 채택/기각/추가실험
### 다음 단계
```
