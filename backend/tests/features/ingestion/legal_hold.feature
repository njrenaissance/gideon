Feature: Legal hold enforcement
  As a defense attorney
  I want documents under legal hold to be immutable in storage
  So that evidence integrity is preserved for court

  # Legal hold is enforced at the MinIO S3 storage layer.
  # When a matter is under legal hold, no document in that
  # matter can be deleted or overwritten in S3. New uploads
  # are still permitted.

  Background:
    Given a firm "Cora Firm" exists
    And a matter "People v. Smith" exists for "Cora Firm"
    And I am logged in as an attorney assigned to "People v. Smith"
    And MinIO S3 storage is available

  Scenario: Cannot delete a document under legal hold
    Given "exhibit_a.pdf" is stored in S3 for matter "People v. Smith"
    And a legal hold is active on matter "People v. Smith"
    When I attempt to delete "exhibit_a.pdf"
    Then the deletion should be rejected
    And the file should still exist in S3
    And the SHA-256 hash should still match the original

  Scenario: Cannot overwrite a document under legal hold
    Given "exhibit_a.pdf" is stored in S3 for matter "People v. Smith"
    And a legal hold is active on matter "People v. Smith"
    When I attempt to replace "exhibit_a.pdf" with new content
    Then the replacement should be rejected
    And the file in S3 should be byte-identical to the original

  Scenario: New uploads are allowed under legal hold
    Given a legal hold is active on matter "People v. Smith"
    When I upload "new_evidence.pdf" to matter "People v. Smith"
    Then the document should be stored with status "processed"
    And the original file should be stored in S3

  Scenario: Legal hold applies to all documents in the matter
    Given "doc_1.pdf" is stored in S3 for matter "People v. Smith"
    And "doc_2.pdf" is stored in S3 for matter "People v. Smith"
    And a legal hold is active on matter "People v. Smith"
    When I attempt to delete "doc_1.pdf"
    Then the deletion should be rejected
    When I attempt to delete "doc_2.pdf"
    Then the deletion should be rejected

  Scenario: Removing legal hold restores delete capability
    Given "exhibit_b.pdf" is stored in S3 for matter "People v. Smith"
    And a legal hold is active on matter "People v. Smith"
    When the legal hold is removed from matter "People v. Smith"
    And I attempt to delete "exhibit_b.pdf"
    Then the deletion should succeed
    And an audit log entry should record the deletion

  Scenario: Legal hold activation is audit logged
    When a legal hold is placed on matter "People v. Smith"
    Then an audit log entry should record the legal hold activation
    And the entry should include the matter and the user who activated it
