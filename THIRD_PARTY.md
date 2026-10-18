# Third-party software

The founderealm-lens binary is built from Founderealm's own source and the Rust crates below, every one
compiled into the binary for at least one platform (a crate used only on Windows or only on
Linux is listed too). DuckDB (MIT) and tree-sitter (MIT) are compiled in from their own C and
C++ sources by libduckdb-sys and tree-sitter. Each license is the crate's own, as its
Cargo.toml declares it; the crate's repository has its full text. The Linux binaries also
carry LLVM's C++ runtime (libc++, libc++abi and libunwind, Apache-2.0 WITH LLVM-exception,
[llvm-project](https://github.com/llvm/llvm-project)), which Zig compiles in when it builds
them against glibc 2.28; from the system they load only the C library.

Grammars are not in the binary. The first capture in a repository fetches them into
founderealm/grammars/, one bundle of every grammar for the platform, from Founderealm's
mirror of the tree-sitter-language-pack release that crate's version names: release
[grammars-v1.22.1](https://github.com/Founderealm/Founderealm_Lens/releases/tag/grammars-v1.22.1),
with the bundles unchanged. Each grammar is under its own license. That release carries the
language pack's `GRAMMAR_NOTICES-1.22.1.md`, which names every grammar's repository, revision
and license and holds each license text, and Founderealm's `SUPPLEMENT.md`, which carries the
license and copyright notices of the two grammars (slint and t32) whose texts those notices
miss. Every license file was checked against its grammar's repository at the pinned revision
before the release was published.

This list is generated from `cargo metadata` and is regenerated whenever a dependency moves.

| crate | version | license |
|---|---|---|
| [adler2](https://github.com/oyvindln/adler2) | 2.0.1 | 0BSD OR MIT OR Apache-2.0 |
| [ahash](https://github.com/tkaitchuck/ahash) | 0.8.12 | MIT OR Apache-2.0 |
| [aho-corasick](https://github.com/BurntSushi/aho-corasick) | 1.1.5 | Unlicense OR MIT |
| [android_system_properties](https://github.com/nical/android_system_properties) | 0.1.6 | MIT OR Apache-2.0 |
| [arrow](https://github.com/apache/arrow-rs) | 58.4.0 | Apache-2.0 |
| [arrow-arith](https://github.com/apache/arrow-rs) | 58.4.0 | Apache-2.0 |
| [arrow-array](https://github.com/apache/arrow-rs) | 58.4.0 | Apache-2.0 AND MIT |
| [arrow-buffer](https://github.com/apache/arrow-rs) | 58.4.0 | Apache-2.0 |
| [arrow-cast](https://github.com/apache/arrow-rs) | 58.4.0 | Apache-2.0 |
| [arrow-data](https://github.com/apache/arrow-rs) | 58.4.0 | Apache-2.0 |
| [arrow-ord](https://github.com/apache/arrow-rs) | 58.4.0 | Apache-2.0 |
| [arrow-row](https://github.com/apache/arrow-rs) | 58.4.0 | Apache-2.0 |
| [arrow-schema](https://github.com/apache/arrow-rs) | 58.4.0 | Apache-2.0 |
| [arrow-select](https://github.com/apache/arrow-rs) | 58.4.0 | Apache-2.0 |
| [arrow-string](https://github.com/apache/arrow-rs) | 58.4.0 | Apache-2.0 |
| [atoi](https://github.com/pacman82/atoi-rs) | 2.0.0 | MIT |
| [autocfg](https://github.com/cuviper/autocfg) | 1.5.1 | Apache-2.0 OR MIT |
| [base64](https://github.com/marshallpierce/rust-base64) | 0.22.1 | MIT OR Apache-2.0 |
| [base64](https://github.com/marshallpierce/rust-base64) | 0.23.1 | MIT OR Apache-2.0 |
| [bitflags](https://github.com/bitflags/bitflags) | 2.13.2 | MIT OR Apache-2.0 |
| [block-buffer](https://github.com/RustCrypto/utils) | 0.12.1 | MIT OR Apache-2.0 |
| [bumpalo](https://github.com/fitzgen/bumpalo) | 3.20.3 | MIT OR Apache-2.0 |
| [byteorder](https://github.com/BurntSushi/byteorder) | 1.5.0 | Unlicense OR MIT |
| [bytes](https://github.com/tokio-rs/bytes) | 1.12.1 | MIT |
| [cast](https://github.com/japaric/cast.rs) | 0.3.0 | MIT OR Apache-2.0 |
| [cc](https://github.com/rust-lang/cc-rs) | 1.8.0 | MIT OR Apache-2.0 |
| [cfg-if](https://github.com/rust-lang/cfg-if) | 1.0.5 | MIT OR Apache-2.0 |
| [cfg_aliases](https://github.com/katharostech/cfg_aliases) | 0.2.2 | MIT |
| [chrono](https://github.com/chronotope/chrono) | 0.4.45 | MIT OR Apache-2.0 |
| [combine](https://github.com/Marwes/combine) | 4.6.9 | MIT |
| [comfy-table](https://github.com/nukesor/comfy-table) | 7.1.4 | MIT |
| [const-oid](https://github.com/RustCrypto/formats) | 0.10.2 | Apache-2.0 OR MIT |
| [const-random](https://github.com/tkaitchuck/constrandom) | 0.1.18 | MIT OR Apache-2.0 |
| [const-random-macro](https://github.com/tkaitchuck/constrandom) | 0.1.16 | MIT OR Apache-2.0 |
| [core-foundation](https://github.com/servo/core-foundation-rs) | 0.10.1 | MIT OR Apache-2.0 |
| [core-foundation-sys](https://github.com/servo/core-foundation-rs) | 0.8.7 | MIT OR Apache-2.0 |
| [cpufeatures](https://github.com/RustCrypto/utils) | 0.3.1 | MIT OR Apache-2.0 |
| [crc32fast](https://github.com/srijs/rust-crc32fast) | 1.5.2 | MIT OR Apache-2.0 |
| [crossterm](https://github.com/crossterm-rs/crossterm) | 0.28.1 | MIT |
| [crossterm_winapi](https://github.com/crossterm-rs/crossterm-winapi) | 0.9.1 | MIT |
| [crunchy](https://github.com/eira-fransham/crunchy) | 0.2.4 | MIT |
| [crypto-common](https://github.com/RustCrypto/traits) | 0.2.2 | MIT OR Apache-2.0 |
| [digest](https://github.com/RustCrypto/traits) | 0.11.3 | MIT OR Apache-2.0 |
| [dirs](https://codeberg.org/dirs/dirs-rs) | 7.0.0 | MIT OR Apache-2.0 |
| [dirs-sys](https://github.com/dirs-dev/dirs-sys-rs) | 0.5.0 | MIT OR Apache-2.0 |
| [duckdb](https://github.com/duckdb/duckdb-rs) | 1.10506.1 | MIT |
| [equivalent](https://github.com/indexmap-rs/equivalent) | 1.0.3 | Apache-2.0 OR MIT |
| [errno](https://github.com/lambda-fairy/rust-errno) | 0.3.14 | MIT OR Apache-2.0 |
| [fallible-iterator](https://github.com/sfackler/rust-fallible-iterator) | 0.3.0 | MIT/Apache-2.0 |
| [fallible-streaming-iterator](https://github.com/sfackler/fallible-streaming-iterator) | 0.1.9 | MIT/Apache-2.0 |
| [fd-lock](https://github.com/yoshuawuyts/fd-lock) | 4.0.4 | MIT OR Apache-2.0 |
| [filetime](https://github.com/alexcrichton/filetime) | 0.2.29 | MIT/Apache-2.0 |
| [find-msvc-tools](https://github.com/rust-lang/cc-rs) | 0.1.14 | MIT OR Apache-2.0 |
| [flate2](https://github.com/rust-lang/flate2-rs) | 1.1.10 | MIT OR Apache-2.0 |
| [foldhash](https://github.com/orlp/foldhash) | 0.1.5 | Zlib |
| [foldhash](https://github.com/orlp/foldhash) | 0.2.0 | Zlib |
| [futures-core](https://github.com/rust-lang/futures-rs) | 0.3.34 | MIT OR Apache-2.0 |
| [futures-task](https://github.com/rust-lang/futures-rs) | 0.3.34 | MIT OR Apache-2.0 |
| [futures-util](https://github.com/rust-lang/futures-rs) | 0.3.34 | MIT OR Apache-2.0 |
| [getrandom](https://github.com/rust-random/getrandom) | 0.2.17 | MIT OR Apache-2.0 |
| [getrandom](https://github.com/rust-random/getrandom) | 0.3.4 | MIT OR Apache-2.0 |
| [getrandom](https://github.com/rust-random/getrandom) | 0.4.3 | MIT OR Apache-2.0 |
| [glob](https://github.com/rust-lang/glob) | 0.3.4 | MIT OR Apache-2.0 |
| [half](https://github.com/VoidStarKat/half-rs) | 2.7.1 | MIT OR Apache-2.0 |
| [hashbrown](https://github.com/rust-lang/hashbrown) | 0.15.5 | MIT OR Apache-2.0 |
| [hashbrown](https://github.com/rust-lang/hashbrown) | 0.17.1 | MIT OR Apache-2.0 |
| [hashlink](https://github.com/kyren/hashlink) | 0.10.0 | MIT OR Apache-2.0 |
| [heck](https://github.com/withoutboats/heck) | 0.5.0 | MIT OR Apache-2.0 |
| [http](https://github.com/hyperium/http) | 1.5.0 | MIT OR Apache-2.0 |
| [httparse](https://github.com/seanmonstar/httparse) | 1.10.1 | MIT OR Apache-2.0 |
| [hybrid-array](https://github.com/RustCrypto/hybrid-array) | 0.4.15 | MIT OR Apache-2.0 |
| [iana-time-zone](https://github.com/strawlab/iana-time-zone) | 0.1.65 | MIT OR Apache-2.0 |
| [iana-time-zone-haiku](https://github.com/strawlab/iana-time-zone) | 0.1.2 | MIT OR Apache-2.0 |
| [indexmap](https://github.com/indexmap-rs/indexmap) | 2.14.2 | Apache-2.0 OR MIT |
| [itoa](https://github.com/dtolnay/itoa) | 1.0.18 | MIT OR Apache-2.0 |
| [jni](https://github.com/jni-rs/jni-rs) | 0.22.4 | MIT OR Apache-2.0 |
| [jni-macros](https://github.com/jni-rs/jni-rs) | 0.22.4 | MIT OR Apache-2.0 |
| [jni-sys](https://github.com/jni-rs/jni-sys) | 0.4.1 | MIT OR Apache-2.0 |
| [jni-sys-macros](https://github.com/jni-rs/jni-sys) | 0.4.1 | MIT OR Apache-2.0 |
| [jobserver](https://github.com/rust-lang/jobserver-rs) | 0.1.35 | MIT OR Apache-2.0 |
| [js-sys](https://github.com/wasm-bindgen/wasm-bindgen/tree/master/crates/js-sys) | 0.3.106 | MIT OR Apache-2.0 |
| [lexical-core](https://github.com/Alexhuszagh/rust-lexical) | 1.0.6 | MIT/Apache-2.0 |
| [lexical-parse-float](https://github.com/Alexhuszagh/rust-lexical) | 1.0.6 | MIT/Apache-2.0 |
| [lexical-parse-integer](https://github.com/Alexhuszagh/rust-lexical) | 1.0.6 | MIT/Apache-2.0 |
| [lexical-util](https://github.com/Alexhuszagh/rust-lexical) | 1.0.7 | MIT/Apache-2.0 |
| [lexical-write-float](https://github.com/Alexhuszagh/rust-lexical) | 1.0.6 | MIT/Apache-2.0 |
| [lexical-write-integer](https://github.com/Alexhuszagh/rust-lexical) | 1.0.6 | MIT/Apache-2.0 |
| [libc](https://github.com/rust-lang/libc) | 0.2.190 | MIT OR Apache-2.0 |
| [libduckdb-sys](https://github.com/duckdb/duckdb-rs) | 1.10506.1 | MIT |
| [libloading](https://github.com/nagisa/rust_libloading/) | 0.9.0 | ISC |
| [libm](https://github.com/rust-lang/compiler-builtins) | 0.2.16 | MIT |
| [libredox](https://gitlab.redox-os.org/redox-os/libredox.git) | 0.1.25 | MIT |
| [linux-raw-sys](https://github.com/sunfishcode/linux-raw-sys) | 0.12.1 | Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT |
| [linux-raw-sys](https://github.com/sunfishcode/linux-raw-sys) | 0.4.15 | Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT |
| [lock_api](https://github.com/Amanieu/parking_lot) | 0.4.14 | MIT OR Apache-2.0 |
| [log](https://github.com/rust-lang/log) | 0.4.34 | MIT OR Apache-2.0 |
| [memchr](https://github.com/BurntSushi/memchr) | 2.8.3 | Unlicense OR MIT |
| [miniz_oxide](https://github.com/Frommi/miniz_oxide/tree/master/miniz_oxide) | 0.9.1 | MIT OR Zlib OR Apache-2.0 |
| [nix](https://github.com/nix-rust/nix) | 0.31.3 | MIT |
| [num-bigint](https://github.com/rust-num/num-bigint) | 0.4.8 | MIT OR Apache-2.0 |
| [num-complex](https://github.com/rust-num/num-complex) | 0.4.6 | MIT OR Apache-2.0 |
| [num-integer](https://github.com/rust-num/num-integer) | 0.1.47 | MIT OR Apache-2.0 |
| [num-traits](https://github.com/rust-num/num-traits) | 0.2.19 | MIT OR Apache-2.0 |
| [once_cell](https://github.com/matklad/once_cell) | 1.21.4 | MIT OR Apache-2.0 |
| [openssl-probe](https://github.com/rustls/openssl-probe) | 0.2.1 | MIT OR Apache-2.0 |
| [option-ext](https://github.com/soc/option-ext.git) | 0.2.0 | MPL-2.0 |
| [parking_lot](https://github.com/Amanieu/parking_lot) | 0.12.5 | MIT OR Apache-2.0 |
| [parking_lot_core](https://github.com/Amanieu/parking_lot) | 0.9.12 | MIT OR Apache-2.0 |
| [percent-encoding](https://github.com/servo/rust-url/) | 2.3.2 | MIT OR Apache-2.0 |
| [pin-project-lite](https://github.com/taiki-e/pin-project-lite) | 0.2.17 | Apache-2.0 OR MIT |
| [pkg-config](https://github.com/rust-lang/pkg-config-rs) | 0.3.34 | MIT OR Apache-2.0 |
| [proc-macro2](https://github.com/dtolnay/proc-macro2) | 1.0.107 | MIT OR Apache-2.0 |
| [quote](https://github.com/dtolnay/quote) | 1.0.47 | MIT OR Apache-2.0 |
| [r-efi](https://github.com/r-efi/r-efi) | 5.3.0 | MIT OR Apache-2.0 OR LGPL-2.1-or-later |
| [r-efi](https://github.com/r-efi/r-efi) | 6.0.0 | MIT OR Apache-2.0 OR LGPL-2.1-or-later |
| [redox_syscall](https://gitlab.redox-os.org/redox-os/syscall) | 0.5.18 | MIT |
| [redox_users](https://gitlab.redox-os.org/redox-os/users) | 0.5.3 | MIT |
| [regex](https://github.com/rust-lang/regex) | 1.13.1 | MIT OR Apache-2.0 |
| [regex-automata](https://github.com/rust-lang/regex) | 0.4.18 | MIT OR Apache-2.0 |
| [regex-syntax](https://github.com/rust-lang/regex) | 0.8.11 | MIT OR Apache-2.0 |
| [ring](https://github.com/briansmith/ring) | 0.17.14 | Apache-2.0 AND ISC |
| [rustc_version](https://github.com/djc/rustc-version-rs) | 0.4.1 | MIT OR Apache-2.0 |
| [rustix](https://github.com/bytecodealliance/rustix) | 0.38.44 | Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT |
| [rustix](https://github.com/bytecodealliance/rustix) | 1.1.5 | Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT |
| [rustls](https://github.com/rustls/rustls) | 0.23.46 | Apache-2.0 OR ISC OR MIT |
| [rustls-native-certs](https://github.com/rustls/rustls-native-certs) | 0.8.5 | Apache-2.0 OR ISC OR MIT |
| [rustls-pki-types](https://github.com/rustls/pki-types) | 1.15.1 | MIT OR Apache-2.0 |
| [rustls-platform-verifier](https://github.com/rustls/rustls-platform-verifier) | 0.7.1 | MIT OR Apache-2.0 |
| [rustls-platform-verifier-android](https://github.com/rustls/rustls-platform-verifier) | 0.2.0 | MIT OR Apache-2.0 |
| [rustls-webpki](https://github.com/rustls/webpki) | 0.103.15 | ISC |
| [rustversion](https://github.com/dtolnay/rustversion) | 1.0.23 | MIT OR Apache-2.0 |
| [ryu](https://github.com/dtolnay/ryu) | 1.0.23 | Apache-2.0 OR BSL-1.0 |
| [same-file](https://github.com/BurntSushi/same-file) | 1.0.6 | Unlicense/MIT |
| [schannel](https://github.com/steffengy/schannel-rs) | 0.1.30 | MIT |
| [scopeguard](https://github.com/bluss/scopeguard) | 1.2.0 | MIT OR Apache-2.0 |
| [security-framework](https://github.com/kornelski/rust-security-framework) | 3.7.0 | MIT OR Apache-2.0 |
| [security-framework-sys](https://github.com/kornelski/rust-security-framework) | 2.17.0 | MIT OR Apache-2.0 |
| [semver](https://github.com/dtolnay/semver) | 1.0.28 | MIT OR Apache-2.0 |
| [serde](https://github.com/serde-rs/serde) | 1.0.229 | MIT OR Apache-2.0 |
| [serde_core](https://github.com/serde-rs/serde) | 1.0.229 | MIT OR Apache-2.0 |
| [serde_derive](https://github.com/serde-rs/serde) | 1.0.229 | MIT OR Apache-2.0 |
| [serde_json](https://github.com/serde-rs/json) | 1.0.154 | MIT OR Apache-2.0 |
| [serde_spanned](https://github.com/toml-rs/toml) | 1.1.2 | MIT OR Apache-2.0 |
| [sha2](https://github.com/RustCrypto/hashes) | 0.11.1 | MIT OR Apache-2.0 |
| [shlex](https://github.com/comex/rust-shlex) | 2.0.1 | MIT OR Apache-2.0 |
| [simd-adler32](https://github.com/mcountryman/simd-adler32) | 0.3.10 | MIT |
| [simd_cesu8](https://github.com/seancroach/simd_cesu8) | 1.2.0 | Apache-2.0 OR MIT |
| [simdutf8](https://github.com/rusticstuff/simdutf8) | 0.1.5 | MIT OR Apache-2.0 |
| [slab](https://github.com/tokio-rs/slab) | 0.4.12 | MIT |
| [smallvec](https://github.com/servo/rust-smallvec) | 1.16.3 | MIT OR Apache-2.0 |
| [socks](https://github.com/sfackler/rust-socks) | 0.3.4 | MIT/Apache-2.0 |
| [streaming-iterator](https://github.com/sfackler/streaming-iterator) | 0.1.9 | MIT OR Apache-2.0 |
| [strum](https://github.com/Peternator7/strum) | 0.27.2 | MIT |
| [strum_macros](https://github.com/Peternator7/strum) | 0.27.2 | MIT |
| [subtle](https://github.com/dalek-cryptography/subtle) | 2.6.1 | BSD-3-Clause |
| [syn](https://github.com/dtolnay/syn) | 2.0.119 | MIT OR Apache-2.0 |
| [syn](https://github.com/dtolnay/syn) | 3.0.9 | MIT OR Apache-2.0 |
| [tar](https://github.com/composefs/tar-rs) | 0.4.46 | MIT OR Apache-2.0 |
| [thiserror](https://github.com/dtolnay/thiserror) | 2.0.21 | MIT OR Apache-2.0 |
| [thiserror-impl](https://github.com/dtolnay/thiserror) | 2.0.21 | MIT OR Apache-2.0 |
| tiny-keccak | 2.0.2 | CC0-1.0 |
| [toml](https://github.com/toml-rs/toml) | 1.1.8+spec-1.1.0 | MIT OR Apache-2.0 |
| [toml_datetime](https://github.com/toml-rs/toml) | 1.1.2+spec-1.1.0 | MIT OR Apache-2.0 |
| [toml_parser](https://github.com/toml-rs/toml) | 1.1.5+spec-1.1.0 | MIT OR Apache-2.0 |
| [toml_writer](https://github.com/toml-rs/toml) | 1.1.3+spec-1.1.0 | MIT OR Apache-2.0 |
| [tracing](https://github.com/tokio-rs/tracing) | 0.1.44 | MIT |
| [tracing-attributes](https://github.com/tokio-rs/tracing) | 0.1.31 | MIT |
| [tracing-core](https://github.com/tokio-rs/tracing) | 0.1.36 | MIT |
| [tree-sitter](https://github.com/tree-sitter/tree-sitter) | 0.27.1 | MIT |
| [tree-sitter-language](https://github.com/tree-sitter/tree-sitter) | 0.1.9 | MIT |
| [tree-sitter-language-pack](https://github.com/xberg-io/tree-sitter-language-pack) | 1.22.1 | MIT |
| [typed-path](https://github.com/chipsenkbeil/typed-path) | 0.12.3 | MIT OR Apache-2.0 |
| [typenum](https://github.com/paholg/typenum) | 1.20.1 | MIT OR Apache-2.0 |
| [unicode-ident](https://github.com/dtolnay/unicode-ident) | 1.0.27 | (MIT OR Apache-2.0) AND Unicode-3.0 |
| [unicode-segmentation](https://github.com/unicode-rs/unicode-segmentation) | 1.13.3 | MIT OR Apache-2.0 |
| [unicode-width](https://github.com/unicode-rs/unicode-width) | 0.2.2 | MIT OR Apache-2.0 |
| [untrusted](https://github.com/briansmith/untrusted) | 0.9.0 | ISC |
| [ureq](https://github.com/algesten/ureq) | 3.4.2 | MIT OR Apache-2.0 |
| [ureq-proto](https://github.com/algesten/ureq-proto) | 0.6.4 | MIT OR Apache-2.0 |
| [utf8-zero](https://github.com/algesten/utf8-zero) | 0.8.1 | MIT OR Apache-2.0 |
| [vcpkg](https://github.com/mcgoo/vcpkg-rs) | 0.2.15 | MIT/Apache-2.0 |
| [version_check](https://github.com/SergioBenitez/version_check) | 0.9.5 | MIT/Apache-2.0 |
| [walkdir](https://github.com/BurntSushi/walkdir) | 2.5.0 | Unlicense/MIT |
| [wasi](https://github.com/bytecodealliance/wasi) | 0.11.1+wasi-snapshot-preview1 | Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT |
| [wasip2](https://github.com/bytecodealliance/wasi-rs) | 1.0.4+wasi-0.2.12 | Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT |
| [wasm-bindgen](https://github.com/wasm-bindgen/wasm-bindgen) | 0.2.129 | MIT OR Apache-2.0 |
| [wasm-bindgen-macro](https://github.com/wasm-bindgen/wasm-bindgen/tree/master/crates/macro) | 0.2.129 | MIT OR Apache-2.0 |
| [wasm-bindgen-macro-support](https://github.com/wasm-bindgen/wasm-bindgen/tree/main/crates/macro-support) | 0.2.129 | MIT OR Apache-2.0 |
| [wasm-bindgen-shared](https://github.com/wasm-bindgen/wasm-bindgen/tree/master/crates/shared) | 0.2.129 | MIT OR Apache-2.0 |
| [webpki-root-certs](https://github.com/rustls/webpki-roots) | 1.0.9 | CDLA-Permissive-2.0 |
| [webpki-roots](https://github.com/rustls/webpki-roots) | 1.0.9 | CDLA-Permissive-2.0 |
| [winapi](https://github.com/retep998/winapi-rs) | 0.3.9 | MIT/Apache-2.0 |
| [winapi-i686-pc-windows-gnu](https://github.com/retep998/winapi-rs) | 0.4.0 | MIT/Apache-2.0 |
| [winapi-util](https://github.com/BurntSushi/winapi-util) | 0.1.11 | Unlicense OR MIT |
| [winapi-x86_64-pc-windows-gnu](https://github.com/retep998/winapi-rs) | 0.4.0 | MIT/Apache-2.0 |
| [windows-core](https://github.com/microsoft/windows-rs) | 0.62.2 | MIT OR Apache-2.0 |
| [windows-implement](https://github.com/microsoft/windows-rs) | 0.60.2 | MIT OR Apache-2.0 |
| [windows-interface](https://github.com/microsoft/windows-rs) | 0.59.3 | MIT OR Apache-2.0 |
| [windows-link](https://github.com/microsoft/windows-rs) | 0.2.1 | MIT OR Apache-2.0 |
| [windows-result](https://github.com/microsoft/windows-rs) | 0.4.1 | MIT OR Apache-2.0 |
| [windows-strings](https://github.com/microsoft/windows-rs) | 0.5.1 | MIT OR Apache-2.0 |
| [windows-sys](https://github.com/microsoft/windows-rs) | 0.52.0 | MIT OR Apache-2.0 |
| [windows-sys](https://github.com/microsoft/windows-rs) | 0.59.0 | MIT OR Apache-2.0 |
| [windows-sys](https://github.com/microsoft/windows-rs) | 0.61.2 | MIT OR Apache-2.0 |
| [windows-targets](https://github.com/microsoft/windows-rs) | 0.52.6 | MIT OR Apache-2.0 |
| [windows_aarch64_gnullvm](https://github.com/microsoft/windows-rs) | 0.52.6 | MIT OR Apache-2.0 |
| [windows_aarch64_msvc](https://github.com/microsoft/windows-rs) | 0.52.6 | MIT OR Apache-2.0 |
| [windows_i686_gnu](https://github.com/microsoft/windows-rs) | 0.52.6 | MIT OR Apache-2.0 |
| [windows_i686_gnullvm](https://github.com/microsoft/windows-rs) | 0.52.6 | MIT OR Apache-2.0 |
| [windows_i686_msvc](https://github.com/microsoft/windows-rs) | 0.52.6 | MIT OR Apache-2.0 |
| [windows_x86_64_gnu](https://github.com/microsoft/windows-rs) | 0.52.6 | MIT OR Apache-2.0 |
| [windows_x86_64_gnullvm](https://github.com/microsoft/windows-rs) | 0.52.6 | MIT OR Apache-2.0 |
| [windows_x86_64_msvc](https://github.com/microsoft/windows-rs) | 0.52.6 | MIT OR Apache-2.0 |
| [winnow](https://github.com/winnow-rs/winnow) | 1.0.4 | MIT |
| [wit-bindgen](https://github.com/bytecodealliance/wit-bindgen) | 0.57.1 | Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT |
| [xattr](https://github.com/Stebalien/xattr) | 1.6.1 | MIT OR Apache-2.0 |
| [zerocopy](https://github.com/google/zerocopy) | 0.8.63 | BSD-2-Clause OR Apache-2.0 OR MIT |
| [zerocopy-derive](https://github.com/google/zerocopy) | 0.8.63 | BSD-2-Clause OR Apache-2.0 OR MIT |
| [zeroize](https://github.com/RustCrypto/utils) | 1.9.1 | Apache-2.0 OR MIT |
| [zip](https://github.com/zip-rs/zip2) | 9.0.4 | MIT |
| [zlib-rs](https://github.com/trifectatechfoundation/zlib-rs) | 0.6.8 | Zlib |
| [zmij](https://github.com/dtolnay/zmij) | 1.0.23 | MIT |
| [zopfli](https://github.com/zopfli-rs/zopfli) | 0.8.4 | Apache-2.0 |
| [zstd](https://github.com/gyscos/zstd-rs) | 0.14.3 | BSD-3-Clause |
| [zstd-safe](https://github.com/gyscos/zstd-rs) | 8.2.0 | BSD-3-Clause |
| [zstd-sys](https://github.com/gyscos/zstd-rs) | 2.1.2+zstd.1.5.7 | BSD-3-Clause |
