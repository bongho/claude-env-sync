# 배포 모드 (Deploy Mode)

## 배포 원칙
1. **안전성 우선**: 점진적 배포, 즉시 롤백 가능
2. **비용 의식**: 리소스 추정, 오토스케일링
3. **모니터링**: 배포 전 모니터링 설정 완료
4. **문서화**: 배포 절차, 롤백 절차 문서화

## 배포 체크리스트
- [ ] 모든 테스트 통과 (unit + integration + e2e)
- [ ] 보안 리뷰 완료
- [ ] 성능 테스트 완료 (latency, throughput)
- [ ] 비용 추정 완료
- [ ] 모니터링/알림 설정
- [ ] 롤백 절차 문서화 및 검증
- [ ] 하위 호환성 확인
- [ ] DB 마이그레이션 계획 (필요 시)

## 배포 전략
- **점진적 배포**: 1% → 10% → 50% → 100%
- **카나리 배포**: 소수 트래픽으로 검증 후 확대
- **Blue-Green**: 동시 실행 후 트래픽 전환
- **Feature Flag**: 코드 배포와 기능 활성화 분리

## ML 모델 배포 추가 항목
- [ ] 오프라인 메트릭 기준 충족
- [ ] 추론 지연시간 SLA 충족 (p50, p99)
- [ ] A/B 테스트 설계 완료
- [ ] 가드레일 메트릭 설정
- [ ] 모델 드리프트 모니터링
- [ ] 폴백 모델/로직 준비

## 비용 추정 항목
- 컴퓨팅: CPU/GPU 인스턴스 (on-demand vs spot)
- 스토리지: 모델 아티팩트, 데이터, 로그
- 네트워크: API 호출량, 데이터 전송
- 서드파티: 외부 API, SaaS 비용

## 에이전트 활용
- MLOps: `mlops-engineer`
- AWS 인프라: `aws-solution-architect`
- 백엔드: `backend-architect`
- 보안: `security-reviewer`

## 모니터링 지표
- **서비스**: latency (p50/p95/p99), error rate, throughput
- **리소스**: CPU, memory, GPU utilization
- **비즈니스**: 핵심 KPI (전환율, 매출 등)
- **ML**: prediction drift, feature drift, model staleness
