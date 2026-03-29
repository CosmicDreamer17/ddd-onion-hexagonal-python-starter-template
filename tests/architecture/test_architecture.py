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


def test_domain_does_not_import_fastapi():
    (
        archrule("Domain must not depend on FastAPI")
        .match("*.domain.*")
        .should_not_import("fastapi")
        .should_not_import("fastapi.*")
        .check("src")
    )


def test_application_does_not_import_fastapi():
    (
        archrule("Application must not depend on FastAPI")
        .match("*.application.*")
        .should_not_import("fastapi")
        .should_not_import("fastapi.*")
        .check("src")
    )
