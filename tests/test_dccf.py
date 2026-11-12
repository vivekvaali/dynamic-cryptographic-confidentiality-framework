
import tempfile
import unittest

from dccf_framework import DCCF


class TestDCCF(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dccf = DCCF(key_dir=self.temp_dir.name)
        self.dccf.add_tenant("Tenant_A")
        self.dccf.add_tenant("Tenant_B")
        self.data = b"DCCF automated testing"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_encryption_decryption(self):
        encrypted = self.dccf.encrypt("Tenant_A", self.data)
        self.assertEqual(
            self.dccf.decrypt("Tenant_A", encrypted),
            self.data
        )

    def test_tenant_isolation(self):
        encrypted = self.dccf.encrypt("Tenant_A", self.data)
        with self.assertRaises(ValueError):
            self.dccf.decrypt("Tenant_B", encrypted)

    def test_key_rotation(self):
        old_record = self.dccf.encrypt("Tenant_A", self.data)
        old_key = old_record["kid"]

        new_key = self.dccf.rotate_key("Tenant_A")

        self.assertNotEqual(old_key, new_key)
        self.assertEqual(
            self.dccf.decrypt("Tenant_A", old_record),
            self.data
        )

    def test_cross_tenant_sharing(self):
        encrypted = self.dccf.encrypt("Tenant_A", self.data)
        shared = self.dccf.share_data(
            "Tenant_A", "Tenant_B", encrypted
        )

        self.assertEqual(
            self.dccf.decrypt("Tenant_B", shared),
            self.data
        )


if __name__ == "__main__":
    unittest.main()
