## What problem are you solving?
<!-- One paragraph in your own words. What user-facing or system behaviour changes? -->

- [ ] I am using an agent and I take responsibility for this PR

---

## Changes

<!-- Agent/tool-generated summary below this line is fine -->

---

## Testing

- [ ] `pytest tests/unit/ -q` passes
- [ ] `python3 -m ruff check bootc_installer/ tests/` clean
- [ ] New `.py` files added to `meson.build` `sources = [...]`
- [ ] fisherman changes: `go vet ./...` + `go test ./...` pass (if applicable)
- [ ] UI tested locally with `./run-dev.sh` or `BOOTC_DEMO=1` (if UI changed)

## Risk

- Risk tier: <!-- 1 (Low), 2 (Moderate), 3 (High), or 4 (Critical); see docs/risk-tiers.md -->
- Mitigations and residual risk: <!-- tests, review focus, rollback, or N/A -->
- [ ] Tier 4 changes include complete-install and successful-reboot evidence

## Checklist

- [ ] Conventional commit (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`)
- [ ] No hardcoded secrets, credentials, or real disk paths
- [ ] fisherman submodule pushed separately before this PR (if fisherman changed)
- [ ] Coverage gate not lowered — `--cov-fail-under` in `python-test.yml` is a ratchet
