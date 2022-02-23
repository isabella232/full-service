table! {
    accounts (id) {
        id -> Int4,
        account_id_hex -> Bpchar,
        account_key -> Bytea,
        entropy -> Bytea,
        key_derivation_version -> Int4,
        main_subaddress_index -> Int8,
        change_subaddress_index -> Int8,
        next_subaddress_index -> Int8,
        first_block_index -> Int8,
        next_block_index -> Int8,
        import_block_index -> Nullable<Int8>,
        name -> Text,
        fog_enabled -> Bool,
    }
}

table! {
    assigned_subaddresses (id) {
        id -> Int4,
        assigned_subaddress_b58 -> Text,
        account_id_hex -> Bpchar,
        address_book_entry -> Nullable<Int8>,
        public_address -> Bytea,
        subaddress_index -> Int8,
        comment -> Text,
        subaddress_spend_key -> Bytea,
    }
}

table! {
    gift_codes (id) {
        id -> Int4,
        gift_code_b58 -> Text,
        value -> Int8,
    }
}

table! {
    transaction_logs (id) {
        id -> Int4,
        transaction_id_hex -> Text,
        account_id_hex -> Bpchar,
        assigned_subaddress_b58 -> Nullable<Text>,
        value -> Int8,
        fee -> Nullable<Int8>,
        status -> Text,
        sent_time -> Nullable<Int8>,
        submitted_block_index -> Nullable<Int8>,
        finalized_block_index -> Nullable<Int8>,
        comment -> Text,
        direction -> Text,
        tx -> Nullable<Bytea>,
    }
}

table! {
    transaction_txo_types (transaction_id_hex, txo_id_hex) {
        transaction_id_hex -> Text,
        txo_id_hex -> Text,
        transaction_txo_type -> Text,
    }
}

table! {
    txos (id) {
        id -> Int4,
        txo_id_hex -> Text,
        value -> Int8,
        target_key -> Bytea,
        public_key -> Bytea,
        e_fog_hint -> Bytea,
        txo -> Bytea,
        subaddress_index -> Nullable<Int8>,
        key_image -> Nullable<Bytea>,
        received_block_index -> Nullable<Int8>,
        pending_tombstone_block_index -> Nullable<Int8>,
        spent_block_index -> Nullable<Int8>,
        confirmation -> Nullable<Bytea>,
        recipient_public_address_b58 -> Text,
        minted_account_id_hex -> Nullable<Text>,
        received_account_id_hex -> Nullable<Text>,
    }
}

allow_tables_to_appear_in_same_query!(
    accounts,
    assigned_subaddresses,
    gift_codes,
    transaction_logs,
    transaction_txo_types,
    txos,
);
