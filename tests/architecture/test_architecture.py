from pytest_archon import archrule


def test_domain_does_not_import_sqlalchemy():
    (
        archrule("Domain must not depend on SQLAlchemy")
        .match("*.domain.*")
        .should_not_import("sqlalchemy")
        .should_not_import("sqlalchemy.*")
        .check("src")
    )


def test_domain_does_not_import_infrastructure():
    (
        archrule("Domain must not depend on infrastructure")
        .match("*.domain.*")
        .should_not_import("*.infrastructure.*")
        .check("src")
    )


def test_application_does_not_import_infrastructure():
    (
        archrule("Application must not depend on infrastructure")
        .match("*.application.*")
        .should_not_import("*.infrastructure.*")
        .check("src")
    )


def test_work_management_does_not_import_integration_management():
    (
        archrule("work_management must not import integration_management")
        .match("work_management")
        .match("work_management.*")
        .should_not_import("integration_management")
        .should_not_import("integration_management.*")
        .check("work_management")
    )


def test_integration_management_does_not_import_work_management():
    (
        archrule("integration_management must not import work_management")
        .match("integration_management")
        .match("integration_management.*")
        .should_not_import("work_management")
        .should_not_import("work_management.*")
        .check("integration_management")
    )


def test_shared_domain_does_not_import_bounded_contexts():
    (
        archrule("Shared domain must not depend on bounded contexts")
        .match("shared.domain.*")
        .should_not_import("work_management")
        .should_not_import("work_management.*")
        .should_not_import("integration_management")
        .should_not_import("integration_management.*")
        .check("src")
    )


def test_shared_domain_does_not_import_shared_infrastructure():
    (
        archrule("Shared domain must not depend on shared infrastructure")
        .match("shared.domain.*")
        .should_not_import("shared.infrastructure")
        .should_not_import("shared.infrastructure.*")
        .check("src")
    )


def test_event_bus_does_not_cross_context_boundary():
    (
        archrule("Event handlers must not import from other bounded contexts")
        .match("integration_management.application.*")
        .should_not_import("work_management")
        .should_not_import("work_management.*")
        .check("src")
    )
