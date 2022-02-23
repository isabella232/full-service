CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    account_id_hex char(64) NOT NULL UNIQUE,
    account_key bytea NOT NULL,
    entropy bytea NOT NULL,
    key_derivation_version int NOT NULL,
    main_subaddress_index bigint NOT NULL,
    change_subaddress_index bigint NOT NULL,
    next_subaddress_index bigint NOT NULL,
    first_block_index bigint NOT NULL,
    next_block_index bigint NOT NULL,
    import_block_index bigint,
    name TEXT NOT NULL,
    fog_enabled BOOLEAN NOT NULL
);

CREATE TABLE assigned_subaddresses (
    id SERIAL PRIMARY KEY,
    assigned_subaddress_b58 TEXT NOT NULL,
    account_id_hex char(64) NOT NULL REFERENCES accounts(account_id_hex),
    address_book_entry bigint,
    public_address bytea NOT NULL,
    subaddress_index bigint NOT NULL,
    comment TEXT NOT NULL,
    subaddress_spend_key bytea NOT NULL
);

CREATE TABLE gift_codes (
    id SERIAL PRIMARY KEY,
    gift_code_b58 TEXT NOT NULL,
    value bigint NOT NULL
);

CREATE TABLE transaction_logs (
    id SERIAL PRIMARY KEY,
    transaction_id_hex TEXT NOT NULL UNIQUE,
    account_id_hex char(64) NOT NULL REFERENCES accounts(account_id_hex),
    assigned_subaddress_b58 TEXT,
    value bigint NOT NULL,
    fee bigint,
    status TEXT NOT NULL,
    sent_time bigint,
    submitted_block_index bigint,
    finalized_block_index bigint,
    comment TEXT NOT NULL,
    direction TEXT NOT NULL,
    tx bytea
);

CREATE TABLE txos (
    id SERIAL PRIMARY KEY,
    txo_id_hex TEXT NOT NULL UNIQUE,
    value bigint NOT NULL,
    target_key bytea NOT NULL,
    public_key bytea NOT NULL,
    e_fog_hint bytea NOT NULL,
    txo bytea NOT NULL,
    subaddress_index bigint,
    key_image bytea,
    received_block_index bigint,
    pending_tombstone_block_index bigint,
    spent_block_index bigint,
    confirmation bytea,
    recipient_public_address_b58 TEXT NOT NULL,
    minted_account_id_hex TEXT,
    received_account_id_hex TEXT
);

CREATE TABLE transaction_txo_types (
    transaction_id_hex TEXT NOT NULL REFERENCES transaction_logs(transaction_id_hex),
    txo_id_hex TEXT NOT NULL REFERENCES txos(txo_id_hex),
    transaction_txo_type TEXT NOT NULL,
    PRIMARY KEY (transaction_id_hex, txo_id_hex)
);