set quiet

setup-uv:
    uv venv --python 3.12
    uv pip install -r requirements.txt

home:
    echo $(cat .venv/pyvenv.cfg | grep -i home | cut -d '=' -f 2)/..

lib:
    echo $(just home)/lib

copy-plugin-unix: # TODO: make something that could work on window and macos as well
    cargo build --release
    cp target/release/deps/libpyridis_file_ext-*.so plugins/libpyridis_file_ext.so

static:
    LD_LIBRARY_PATH=$(just lib) cargo run --release --bin static

raw-static:
    LD_LIBRARY_PATH=$(just lib) cargo run --release --bin static --features "raw"

dyn: copy-plugin-unix
    LD_LIBRARY_PATH=$(just lib) cargo run --release --bin dyn

raw-dyn: copy-plugin-unix
    LD_LIBRARY_PATH=$(just lib) cargo run --release --bin dyn --features raw

draw:
    uv --directory draw run draw

bench: static raw-static dyn raw-dyn draw
