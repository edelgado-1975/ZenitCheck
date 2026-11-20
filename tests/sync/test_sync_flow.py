"""
Pruebas de validación previa al certificar y flujo de sincronización.
"""

from sync.engine import validate_certification_prerequisites


class TestSyncValidationFlow:
    def test_valid_prerequisites_pass(self):
        valid, errors = validate_certification_prerequisites(
            equipment_data={'serial_number': 'SN-VALID-1'},
            client_data={'client_name': 'Constructora Andina'}
        )
        assert valid is True
        assert len(errors) == 0

    def test_missing_client_fails_prerequisites(self):
        valid, errors = validate_certification_prerequisites(
            equipment_data={'serial_number': 'SN-VALID-1'},
            client_data={'client_name': ''}
        )
        assert valid is False
        assert any("cliente o propietario" in e for e in errors)
