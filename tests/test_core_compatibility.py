import copy
from hashlib import sha256
import unittest
from linkoteq_importer.core_compatibility import (
    CompatibilityError, canonical_bytes, compare_registry, load_registry, negotiate)


class CompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.doc = {'core_contract': 'v0.5', 'core_commit': 'pinned-commit', 'capabilities': [
            {'name': 'sections.joist', 'kind': 'catalog', 'schema_revision': 1,
             'mapping_revision': None, 'evidence_id': None},
            {'name': 'diaphragm.semirigid', 'kind': 'engineering', 'schema_revision': 1,
             'mapping_revision': 'map-v1', 'evidence_id': 'review-42'}]}

    def load(self, doc=None, **kwargs):
        doc = self.doc if doc is None else doc
        digest = sha256(canonical_bytes(doc)).hexdigest()
        return load_registry(doc, expected_digest=kwargs.get('digest', digest),
                             expected_core_commit=kwargs.get('commit', 'pinned-commit'),
                             supported_contract=kwargs.get('contract', 'v0.5'))

    def test_catalog_enabled_only_on_exact_schema(self):
        result = negotiate(self.load(), supported_catalog_schemas={'sections.joist': 1},
                           approved_engineering_mappings={})
        self.assertEqual([r.status for r in result], ['enabled', 'blocked'])

    def test_diaphragm_requires_mapping_and_evidence(self):
        result = negotiate(self.load(), supported_catalog_schemas={},
                           approved_engineering_mappings={'diaphragm.semirigid': ('map-v1', 'review-42')})
        self.assertEqual([r.status for r in result], ['blocked', 'enabled'])

    def test_mismatched_evidence_blocks(self):
        result = negotiate(self.load(), supported_catalog_schemas={},
                           approved_engineering_mappings={'diaphragm.semirigid': ('map-v1', 'other')})
        self.assertEqual(result[1].status, 'blocked')

    def test_digest_mismatch_rejected(self):
        with self.assertRaises(CompatibilityError): self.load(digest='0' * 64)

    def test_contract_mismatch_rejected(self):
        with self.assertRaises(CompatibilityError): self.load(contract='v0.6')

    def test_commit_mismatch_rejected(self):
        with self.assertRaises(CompatibilityError): self.load(commit='other')

    def test_duplicate_capabilities_rejected(self):
        doc = copy.deepcopy(self.doc)
        doc['capabilities'].append(copy.deepcopy(doc['capabilities'][0]))
        with self.assertRaises(CompatibilityError): self.load(doc)

    def test_boolean_revision_rejected(self):
        doc = copy.deepcopy(self.doc)
        doc['capabilities'][0]['schema_revision'] = True
        with self.assertRaises(CompatibilityError): self.load(doc)

    def test_unknown_fields_rejected(self):
        doc = copy.deepcopy(self.doc)
        doc['capabilities'][0]['auto_enable'] = True
        with self.assertRaises(CompatibilityError): self.load(doc)

    def test_change_detection_no_auto_approval(self):
        old = self.load()
        doc = copy.deepcopy(self.doc)
        doc['capabilities'][0]['schema_revision'] = 2
        doc['capabilities'].append({'name':'sections.new','kind':'catalog','schema_revision':1,
                                    'mapping_revision':None,'evidence_id':None})
        changes = compare_registry(old, self.load(doc))
        self.assertEqual(changes['added'], ('sections.new',))
        self.assertEqual(changes['changed'], ('sections.joist',))

if __name__ == '__main__': unittest.main()
