import unittest
from linkoteq_importer.preservation import Limits, archive_bytes, ArchiveError
from linkoteq_importer.staad_lexical import detect_staad, lex_staad

LIMITS = Limits(10000, 100, 100, 500, 100, 1000, 1000, 100000)

def run(data, limits=LIMITS):
    archive = archive_bytes(data, filename="model.sbk", extension=".sbk",
                            project_ref="p", namespace="n", policy_id="ret", limits=limits)
    return lex_staad(archive, limits=limits)

class StaadLexicalTests(unittest.TestCase):
    def test_detect_content_not_extension(self):
        self.assertIsNotNone(detect_staad(b"STAAD SPACE\n", "foo.txt"))
        self.assertIsNone(detect_staad(b"not a model", "foo.std"))
    def test_reject_binary(self):
        self.assertIsNone(detect_staad(b"STAAD SPACE\x00"))
    def test_preserve_crlf_and_comments(self):
        data = b"STAAD SPACE\r\n* note\r\nJOINT COORDINATES\r\n1 0 0 0\r\n"
        result = run(data)
        self.assertEqual(result.records[1].classification, "comment")
        self.assertEqual(b"".join(data[s.startByte:s.endByte] for s in result.spans), data)
        self.assertEqual(result.records[2].startByte, len(b"STAAD SPACE\r\n* note\r\n"))
    def test_continuation_tracks_physical_lines(self):
        result = run(b"STAAD SPACE\nMEMBER INCIDENCES -\n1 1 2\n")
        self.assertEqual(result.records[1].physicalSpanOrdinals, (1, 2))
    def test_unterminated_continuation(self):
        result = run(b"STAAD SPACE\n1 2 -")
        self.assertIn("UNTERMINATED_CONTINUATION", result.diagnostics)
    def test_semicolon_remains_opaque(self):
        result = run(b"STAAD SPACE\n1 1 2; 2 2 3\n")
        self.assertIn(";", result.records[1].text)
    def test_reject_record_limit(self):
        with self.assertRaisesRegex(ArchiveError, "MAX_LOGICAL_RECORDS"):
            run(b"STAAD SPACE\n1\n2\n", Limits(10000, 100, 2, 500, 100, 1000, 1000, 100000))
    def test_reject_continuation_limit(self):
        with self.assertRaisesRegex(ArchiveError, "MAX_CONTINUATION_BYTES"):
            run(b"STAAD SPACE\nMEMBER INCIDENCES -\n1 1 2\n", Limits(10000, 100, 100, 15, 100, 1000, 1000, 100000))
    def test_no_core_mapping_claim(self):
        self.assertIn("SEMANTIC_MAPPING_NOT_ATTEMPTED", run(b"STAAD SPACE\n").diagnostics)
    def test_non_utf8_diagnostic(self):
        self.assertIn("ENCODING_UNVERIFIED_LATIN1_VIEW", run(b"STAAD SPACE\n* \xff\n").diagnostics)

if __name__ == "__main__": unittest.main()
