# pylint: disable=redefined-outer-name
from test.random_refs import random_sku

import pytest
from sqlalchemy.orm import clear_mappers

from src import bootstrap, config
from src.adapters import notifications
from src.domain import commands
from src.service_layer import unit_of_work


@pytest.fixture
def bus(sqlite_session_factory, monkeypatch):
    sent_emails = []
    email_notifications = notifications.EmailNotifications()

    def capture_sendmail(from_addr, to_addrs, msg):
        sent_emails.append(
            {"from_addr": from_addr, "to_addrs": to_addrs, "msg": msg}
        )

    monkeypatch.setattr(email_notifications.server, "sendmail", capture_sendmail)

    bus = bootstrap.bootstrap(
        start_orm=True,
        uow=unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory),
        notifications=email_notifications,
        publish=lambda *args: None,
    )
    bus.sent_emails = sent_emails
    yield bus
    clear_mappers()


def get_email_from_mailhog(bus, sku):
    return next(email for email in bus.sent_emails if sku in email["msg"])


def test_out_of_stock_email(bus):
    sku = random_sku()
    bus.handle(commands.CreateBatch("batch1", sku, 9, None))
    bus.handle(commands.Allocate("order1", sku, 10))
    email = get_email_from_mailhog(bus, sku)
    assert email["from_addr"] == "allocations@example.com"
    assert email["to_addrs"] == ["stock@made.com"]
    assert f"Out of stock for {sku}" in email["msg"]