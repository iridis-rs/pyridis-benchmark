use pyridis_benchmark::prelude::{
    benchmark, libpyridis_file_ext,
    thirdparty::iridis::prelude::{thirdparty::*, *},
};

#[tokio::main]
async fn main() -> Result<()> {
    println!("Starting dynamic Python benchmark");

    benchmark(
        "dynamic",
        async |file_ext: &mut FileExtManagerBuilder| -> Result<()> {
            file_ext
                .load_dynamically_linked_plugin(libpyridis_file_ext()?)
                .await
        },
    )
    .await
}
