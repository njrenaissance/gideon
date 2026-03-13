Feature: Document deduplication
  As a defense attorney
  I want duplicate documents to be detected at ingestion
  So that the same file is not stored and searched twice

  # Deduplication is based entirely on SHA-256 content hash,
  # never on filename. Two files with the same name but different
  # content are distinct documents. Two files with different names
  # but identical content are duplicates.

  Background:
    Given a firm "Cora Firm" exists
    And a matter "People v. Smith" exists for "Cora Firm"
    And I am logged in as an attorney assigned to "People v. Smith"

  Scenario: Duplicate content is rejected regardless of filename
    Given a document with SHA-256 hash "aaa111" has been ingested into "People v. Smith"
    When I upload a file whose SHA-256 hash is also "aaa111" to "People v. Smith"
    Then the upload should be rejected as a duplicate
    And the original document should remain unchanged

  Scenario: Same content under a different filename is rejected
    Given "report_v1.pdf" with SHA-256 hash "bbb222" has been ingested into "People v. Smith"
    When I upload "report_v1_copy.pdf" whose SHA-256 hash is also "bbb222" to "People v. Smith"
    Then the upload should be rejected as a duplicate

  Scenario: Different content with same filename is accepted
    Given "witness_statement.pdf" with SHA-256 hash "ccc333" has been ingested into "People v. Smith"
    When I upload "witness_statement.pdf" with SHA-256 hash "ddd444" to "People v. Smith"
    Then the document should be stored with status "processed"
    And both versions should exist in the matter

  Scenario: Same hash in different matters is accepted
    Given a document with SHA-256 hash "eee555" has been ingested into "People v. Smith"
    And a matter "People v. Jones" exists for "Cora Firm"
    And I am assigned to "People v. Jones"
    When I upload a file whose SHA-256 hash is "eee555" to "People v. Jones"
    Then the document should be stored with status "processed"

  Scenario: SHA-256 hash is computed at ingestion
    When I upload "discovery_batch_001.pdf" to matter "People v. Smith"
    Then the document record should include a SHA-256 content hash
    And the hash should match the actual file content
