# 보안 규칙 (Security Rules)

## 시크릿 관리
- **절대 금지**: API 키, 토큰, 패스워드, 인증서를 코드/커밋에 포함하지 않음
- 환경변수 또는 시크릿 매니저(AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault) 사용
- `.env` 파일은 반드시 `.gitignore`에 포함
- 커밋 전 `git diff --staged`로 시크릿 유출 검토

## 입력 검증 (OWASP Top 10)
- **SQL Injection**: 파라미터화된 쿼리만 사용, ORM 우선
- **XSS**: 사용자 입력 이스케이프, CSP 헤더 설정
- **Command Injection**: `subprocess`에 `shell=False`, 사용자 입력 직접 명령어로 전달 금지
- **SSRF**: 외부 URL 접근 시 allowlist 기반 검증
- **Path Traversal**: 파일 경로에 사용자 입력 사용 시 정규화 + 검증
- **Broken Authentication**: 세션 토큰 안전한 생성, 적절한 만료 시간
- **Insecure Deserialization**: `pickle.loads()` 등 신뢰할 수 없는 데이터 역직렬화 금지

## 의존성 보안
- 의존성 추가 시 알려진 취약점(CVE) 확인
- `pip-audit`, `npm audit`, `snyk` 등 정기 점검
- 최소 권한 원칙: 필요한 패키지만 설치

## DS/ML 데이터 보안
- **PII 처리**: 개인식별정보 마스킹/해싱 후 모델 학습
- **데이터 접근**: BigQuery/S3 등 데이터 소스 접근 시 IAM 기반 권한 관리
- **모델 보안**: 학습 데이터 유출 방지, adversarial attack 고려
- **로깅**: 분석 로그에 PII 포함 금지, 샘플 데이터 노출 최소화
- **데이터 거버넌스**: 데이터 리니지 추적, 접근 감사 로그 유지

## 네트워크 보안
- HTTPS 강제, 평문 통신 금지
- CORS 최소 허용 도메인 설정
- Rate limiting 적용

## 코드 리뷰 보안 체크리스트
- [ ] 시크릿/크레덴셜 하드코딩 없음
- [ ] 사용자 입력 검증/이스케이프 적용
- [ ] SQL 파라미터화 쿼리 사용
- [ ] 파일 업로드 검증 (타입, 크기)
- [ ] 에러 메시지에 내부 정보 노출 없음
- [ ] PII 데이터 적절히 마스킹
