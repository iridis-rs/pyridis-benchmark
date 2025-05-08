set quiet

setup-uv:
    uv venv --python 3.12
    uv pip install -r requirements.txt

home:
    echo $(cat .venv/pyvenv.cfg | grep -i home | cut -d '=' -f 2)/..

lib:
    echo $(just home)/lib

static:
    LD_LIBRARY_PATH=$(just lib) cargo run --release --bin static

copy-plugin-unix:
    cargo build --release
    cp target/release/deps/libpyridis_file_ext-*.so plugins/libpyridis_file_ext.so

dyn: copy-plugin-unix
    LD_LIBRARY_PATH=$(just lib) cargo run --release --bin dyn
