#!/bin/bash

# Copyright (c) 2018-2020 MobileCoin Inc.

set -e

if [[ ! -z "$1" ]]; then
    cd "$1"
fi

for toml in $(grep --exclude-dir cargo --exclude-dir rust-mbedtls --exclude-dir mobilecoin --include=Cargo.toml -r . -e '\[workspace\]' | cut -d: -f1); do
  pushd $(dirname $toml) >/dev/null
  echo "Linting in $PWD"
  cargo fmt -- --unstable-features --check
  cargo clippy --all --all-features
  echo "Linting in $PWD complete."
  popd >/dev/null
done
