use pyridis_benchmark::prelude::{
    benchmark,
    thirdparty::{
        iridis::prelude::{thirdparty::*, *},
        pyridis_file_ext::prelude::*,
    },
};

#[tokio::main]
async fn main() -> Result<()> {
    println!("Starting static Python benchmark");

    benchmark(
        "static",
        async |file_ext: &mut FileExtManagerBuilder| -> Result<()> {
            file_ext
                .load_statically_linked_plugin::<PythonFileExtPlugin>()
                .await
        },
    )
    .await
}
