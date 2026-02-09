"""sync_rules 모듈 테스트."""


from claude_env_sync.models.sync_rules import (
    SyncRule,
    SyncTier,
    get_default_rules,
    get_excluded_patterns,
    get_rules_by_tier,
)


class TestSyncTier:
    """동기화 Tier 열거형 테스트."""

    def test_tier1_exists(self):
        assert SyncTier.TIER1.value == 1

    def test_tier2_exists(self):
        assert SyncTier.TIER2.value == 2

    def test_tier3_exists(self):
        assert SyncTier.TIER3.value == 3


class TestSyncRule:
    """동기화 규칙 모델 테스트."""

    def test_create_file_rule(self):
        rule = SyncRule(
            pattern="CLAUDE.md",
            tier=SyncTier.TIER1,
            is_directory=False,
            description="메인 설정 파일",
        )
        assert rule.pattern == "CLAUDE.md"
        assert rule.tier == SyncTier.TIER1
        assert rule.is_directory is False

    def test_create_directory_rule(self):
        rule = SyncRule(
            pattern="agents/",
            tier=SyncTier.TIER1,
            is_directory=True,
            description="에이전트 설정 디렉토리",
        )
        assert rule.is_directory is True
        assert rule.pattern == "agents/"

    def test_rule_has_description(self):
        rule = SyncRule(
            pattern="CLAUDE.md",
            tier=SyncTier.TIER1,
            is_directory=False,
            description="메인 설정",
        )
        assert rule.description == "메인 설정"


class TestDefaultRules:
    """기본 동기화 규칙 테스트."""

    def test_returns_list(self):
        rules = get_default_rules()
        assert isinstance(rules, list)
        assert len(rules) > 0

    def test_tier1_includes_claude_md(self):
        rules = get_default_rules()
        patterns = [r.pattern for r in rules if r.tier == SyncTier.TIER1]
        assert "CLAUDE.md" in patterns

    def test_tier1_includes_settings_json(self):
        rules = get_default_rules()
        patterns = [r.pattern for r in rules if r.tier == SyncTier.TIER1]
        assert "settings.json" in patterns

    def test_tier1_includes_agents(self):
        rules = get_default_rules()
        patterns = [r.pattern for r in rules if r.tier == SyncTier.TIER1]
        assert "agents/" in patterns

    def test_tier1_includes_installed_plugins(self):
        rules = get_default_rules()
        patterns = [r.pattern for r in rules if r.tier == SyncTier.TIER1]
        assert "plugins/installed_plugins.json" in patterns

    def test_tier2_includes_skills(self):
        rules = get_default_rules()
        patterns = [r.pattern for r in rules if r.tier == SyncTier.TIER2]
        assert "skills/" in patterns

    def test_tier2_includes_history(self):
        rules = get_default_rules()
        patterns = [r.pattern for r in rules if r.tier == SyncTier.TIER2]
        assert "history.jsonl" in patterns


class TestGetRulesByTier:
    """Tier별 규칙 필터링 테스트."""

    def test_filter_tier1_only(self):
        rules = get_rules_by_tier(max_tier=SyncTier.TIER1)
        assert all(r.tier == SyncTier.TIER1 for r in rules)

    def test_filter_up_to_tier2(self):
        rules = get_rules_by_tier(max_tier=SyncTier.TIER2)
        assert all(r.tier.value <= 2 for r in rules)
        tiers = {r.tier for r in rules}
        assert SyncTier.TIER1 in tiers
        assert SyncTier.TIER2 in tiers

    def test_get_patterns_from_rules(self):
        rules = get_rules_by_tier(max_tier=SyncTier.TIER2)
        patterns = [r.pattern for r in rules]
        assert "CLAUDE.md" in patterns
        assert "skills/" in patterns


class TestExcludedPatterns:
    """제외 패턴 테스트."""

    def test_excludes_debug(self):
        excluded = get_excluded_patterns()
        assert "debug/" in excluded

    def test_excludes_cache(self):
        excluded = get_excluded_patterns()
        assert "cache/" in excluded

    def test_excludes_session_env(self):
        excluded = get_excluded_patterns()
        assert "session-env/" in excluded

    def test_excludes_statusline_log(self):
        excluded = get_excluded_patterns()
        assert "statusline.log" in excluded
