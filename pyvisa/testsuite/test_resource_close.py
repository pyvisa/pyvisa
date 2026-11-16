"""Resource cleanup with a synthetic VISA backend, without physical hardware."""

from unittest.mock import MagicMock

import pytest

from pyvisa import ResourceManager, constants, errors, highlevel, resources

CLOSE_OPERATIONS = (
    "disable_event",
    "discard_events",
    "uninstall_all_visa_handlers",
    "close",
)


@pytest.fixture
def opened_resource():
    library = MagicMock(spec=highlevel.VisaLibraryBase)
    library.library_path = "synthetic"
    library.resource_manager = None
    library.open_default_resource_manager.return_value = (
        1,
        constants.StatusCode.success,
    )
    library.open.return_value = (2, constants.StatusCode.success)
    manager = ResourceManager(library)
    resource = manager.open_resource(
        "TCPIP::192.0.2.1::INSTR", resource_pyclass=resources.Resource
    )
    try:
        yield library, manager, resource
    finally:
        for name in CLOSE_OPERATIONS:
            getattr(library, name).side_effect = None
        manager.close()


@pytest.mark.parametrize("operation", CLOSE_OPERATIONS)
def test_close_backend_invalidated_session(opened_resource, operation):
    library, manager, resource = opened_resource
    getattr(library, operation).side_effect = errors.VisaIOError(
        constants.StatusCode.error_invalid_object
    )

    resource.close()

    with pytest.raises(errors.InvalidSession):
        resource.session
    library.reset_mock()
    resource.close()
    assert library.mock_calls == []

    getattr(library, operation).side_effect = None
    manager.close()
    library.close.assert_called_once_with(1)
    with pytest.raises(errors.InvalidSession):
        manager.session


@pytest.mark.parametrize("operation", CLOSE_OPERATIONS)
@pytest.mark.parametrize(
    "error",
    [
        errors.VisaIOError(constants.StatusCode.error_closing_failed),
        errors.VisaIOError(constants.StatusCode.error_system_error),
        RuntimeError("backend failure"),
    ],
)
def test_close_preserves_other_failures(opened_resource, operation, error):
    library, _, resource = opened_resource
    getattr(library, operation).side_effect = error

    with pytest.raises(type(error)) as caught:
        resource.close()

    assert caught.value is error
    assert resource.session == 2


def test_manager_close_after_backend_invalidates_failed_close(opened_resource):
    library, manager, resource = opened_resource
    closing_error = errors.VisaIOError(constants.StatusCode.error_closing_failed)

    def failed_close(session):
        assert session == 2
        library.disable_event.side_effect = errors.VisaIOError(
            constants.StatusCode.error_invalid_object
        )
        raise closing_error

    library.close.side_effect = failed_close
    with pytest.raises(errors.VisaIOError) as caught:
        resource.close()
    assert caught.value is closing_error
    assert resource.session == 2

    library.close.side_effect = None
    library.close.reset_mock()
    manager.close()

    library.close.assert_called_once_with(1)
    with pytest.raises(errors.InvalidSession):
        resource.session
    with pytest.raises(errors.InvalidSession):
        manager.session
    assert library.resource_manager is None


def test_close_success_is_idempotent(opened_resource):
    library, _, resource = opened_resource

    resource.close()

    library.close.assert_called_once_with(2)
    with pytest.raises(errors.InvalidSession):
        resource.session
    library.reset_mock()
    resource.close()
    assert library.mock_calls == []
