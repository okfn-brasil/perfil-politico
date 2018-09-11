INSERT INTO core_politician_affiliation_history (politician_id, party_id)
(
    SELECT DISTINCT politician_voter.politician_id, party_voter.party_id

    FROM (
        SELECT party_id, voter_id
        FROM core_affiliation
    ) party_voter

    INNER JOIN (
        SELECT
            core_politician.id AS politician_id,
            core_affiliation.voter_id
        FROM core_politician
        INNER JOIN core_affiliation
        ON core_politician.current_affiliation_id = core_affiliation.id
    ) politician_voter ON politician_voter.voter_id = party_voter.voter_id
)
