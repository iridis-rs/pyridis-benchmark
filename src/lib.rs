pub mod prelude {
    pub use crate::benchmark::*;

    pub mod thirdparty {
        pub use iridis;
        pub use pyridis_file_ext;
    }
}

pub(crate) mod benchmark {
    use std::path::PathBuf;

    use crate::prelude::thirdparty::iridis::prelude::{thirdparty::*, *};

    pub fn libpyridis_file_ext() -> Result<PathBuf> {
        let path = std::env::var("CARGO_MANIFEST_DIR")?;
        let path = format!("{}/plugins", path);

        let prefix = std::env::consts::DLL_PREFIX;
        let dylib = std::env::consts::DLL_SUFFIX;

        Ok(PathBuf::from(&format!(
            "{}/{}pyridis_file_ext{}",
            path, prefix, dylib
        )))
    }

    fn pyfile(name: &str) -> Result<Url> {
        let path = std::env::var("CARGO_MANIFEST_DIR")?;
        let path = format!("file://{}/nodes", path);

        Url::parse(&format!("{}/{}", path, name)).map_err(eyre::Report::msg)
    }

    fn source_pyfile() -> Result<Url> {
        pyfile("source.py")
    }

    fn sink_pyfile() -> Result<Url> {
        pyfile("sink.py")
    }

    pub async fn benchmark(
        mode: &str,
        plugins: impl AsyncFnOnce(&mut FileExtManagerBuilder) -> Result<()>,
    ) -> Result<()> {
        let mut layout = DataflowLayout::new();

        let (source, (source_latency, source_throughput)) = layout
            .node("source", async |io: &mut NodeIOBuilder| {
                (io.output("latency"), io.output("throughput"))
            })
            .await;

        let (sink, (sink_latency, sink_throughput)) = layout
            .node("sink", async |io: &mut NodeIOBuilder| {
                (io.input("latency"), io.input("throughput"))
            })
            .await;

        let layout = layout.build();

        let flows = Flows::new(layout.clone(), async move |connector: &mut FlowsBuilder| {
            connector.connect(sink_latency, source_latency, Some(128))?;
            connector.connect(sink_throughput, source_throughput, Some(128))?;

            Ok(())
        })
        .await?;

        let runtime = Runtime::new(
            async |file_ext: &mut FileExtManagerBuilder,
                   _url_scheme: &mut UrlSchemeManagerBuilder| {
                plugins(file_ext).await
            },
        )
        .await?;

        runtime
            .run(flows, async move |loader: &mut NodeLoader| {
                #[cfg(not(feature = "raw"))]
                let sink_cfg: serde_yml::Value =
                    serde_yml::from_str(format!("prefix: \"\"\nsuffix: \"{}\"\n", mode).as_str())?;

                #[cfg(feature = "raw")]
                let sink_cfg: serde_yml::Value = serde_yml::from_str(
                    format!("prefix: \"raw\"\nsuffix: \"{}\"\n", mode).as_str(),
                )?;

                #[cfg(not(feature = "raw"))]
                let source_cfg: serde_yml::Value =
                    serde_yml::from_str(format!("prefix: \"\"\nsuffix: \"{}\"\n", mode).as_str())?;

                #[cfg(feature = "raw")]
                let source_cfg: serde_yml::Value = serde_yml::from_str(
                    format!("prefix: \"raw\"\nsuffix: \"{}\"\n", mode).as_str(),
                )?;

                loader.load_url(sink_pyfile()?, sink, sink_cfg).await?;

                loader
                    .load_url(source_pyfile()?, source, source_cfg)
                    .await?;

                Ok(())
            })
            .await
    }
}
