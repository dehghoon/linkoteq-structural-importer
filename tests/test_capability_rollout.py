import unittest
from linkoteq_importer.core_compatibility import Capability, Registry, CompatibilityError
from linkoteq_importer.capability_rollout import plan_rollout

class RolloutTests(unittest.TestCase):
    def setUp(self):
        self.old = Registry('v0.5', 'a'*40, '0'*64, (Capability('steel', 'catalog', 1),))
        self.new = Registry('v0.5', 'b'*40, '1'*64, (
            Capability('steel', 'catalog', 1),
            Capability('joist', 'catalog', 1),
            Capability('diaphragm', 'engineering', 1, 'm1', 'ev1')))

    def test_unpinned_catalogs_and_unapproved_engineering_blocked(self):
        p = plan_rollout(self.old, self.new, supported_catalog_schemas={'steel':1, 'joist':1}, approved_engineering_mappings={})
        self.assertEqual([i.decision for i in p.items], ['blocked','blocked','blocked'])
        self.assertTrue(p.requires_review)

    def test_pinned_catalogs_and_approved_engineering(self):
        digests = {'steel':'a'*64, 'joist':'b'*64}
        p = plan_rollout(self.old, self.new, supported_catalog_schemas={'steel':1,'joist':1},
            approved_engineering_mappings={'diaphragm':('m1','ev1')},
            approved_catalog_digests=digests, candidate_catalog_digests=digests)
        self.assertEqual([i.decision for i in p.items], ['enabled','enabled','enabled'])
        self.assertTrue(p.requires_review)  # changes still require review

    def test_removal_blocks(self):
        candidate = Registry('v0.5','b'*40,'1'*64,())
        p = plan_rollout(self.old,candidate,supported_catalog_schemas={},approved_engineering_mappings={})
        self.assertEqual(p.items[0].change,'removed')
        self.assertEqual(p.items[0].decision,'blocked')

    def test_contract_change_rejected(self):
        candidate = Registry('v0.6','b'*40,'1'*64,())
        with self.assertRaises(CompatibilityError):
            plan_rollout(self.old,candidate,supported_catalog_schemas={},approved_engineering_mappings={})

    def test_wrong_catalog_digest_blocks(self):
        p = plan_rollout(self.old,self.new,supported_catalog_schemas={'steel':1,'joist':1},
            approved_engineering_mappings={},approved_catalog_digests={'joist':'a'*64},
            candidate_catalog_digests={'joist':'b'*64})
        self.assertEqual(next(i.decision for i in p.items if i.name=='joist'),'blocked')

if __name__ == '__main__':
    unittest.main()
