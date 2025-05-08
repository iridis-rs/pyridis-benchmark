set quiet

setup-uv:
    uv venv --python 3.12
    uv pip install -r requirements.txt
    # maturin develop --manifest-path /home/enzo/Documents/iridis/pyridis/crates/pyridis-api/Cargo.toml --uv
    # cargo build --manifest-path /home/enzo/Documents/iridis/pyridis/crates/pyridis-file-ext/Cargo.toml --release --features cdylib
    # cp /home/enzo/Documents/iridis/pyridis/target/release/libpyridis_file_ext.so plugins

home:
    echo $(cat .venv/pyvenv.cfg | grep -i home | cut -d '=' -f 2)/..

lib:
    echo $(just home)/lib

static:
    LD_LIBRARY_PATH=$(just lib) cargo run --release --bin static

dyn:
    LD_LIBRARY_PATH=$(just lib) cargo run --release --bin dyn
