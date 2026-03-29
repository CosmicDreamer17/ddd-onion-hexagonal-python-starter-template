---
name: fix-issue
description: Fix a GitHub issue following this project's DDD/Onion/Hexagonal patterns
disable-model-invocation: true
---

Fix GitHub issue: $ARGUMENTS

Follow this workflow:

1. **Understand the issue**: Run `gh issue view $ARGUMENTS` to get details
2. **Explore**: Read the relevant bounded context files to understand current patterns
3. **Plan**: Identify which layers (domain, application, infrastructure) need changes
4. **Implement**: Make changes following the established patterns:
   - Domain: `@dataclass(slots=True)`, `abc.ABC` ports, `Error` suffix exceptions
   - Application: plain function use cases, UoW pattern, frozen read models
   - Infrastructure: explicit ORM mapping, `SqlAlchemy` prefix adapters
5. **Test**: Write tests for all new logic (domain unit tests, use case integration tests, API tests)
6. **Verify**: Run `make all-checks` — must pass lint, test, arch-check, and deps-check
7. **Commit**: Create a descriptive commit with `Closes #$ARGUMENTS`
8. **PR**: Push branch and create PR with `gh pr create`

Critical rules:
- Never import across bounded contexts
- Domain layer must have zero framework imports
- One use case function = one transaction
- Use domain-specific NotFoundError, never ValueError
