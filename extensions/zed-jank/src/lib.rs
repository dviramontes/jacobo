use zed_extension_api::{self as zed, LanguageServerId, Result};

struct JankExtension;

impl zed::Extension for JankExtension {
    fn new() -> Self {
        Self
    }

    fn language_server_command(
        &mut self,
        _language_server_id: &LanguageServerId,
        worktree: &zed::Worktree,
    ) -> Result<zed::Command> {
        let python = worktree
            .which("python3")
            .ok_or("Jank definitions require python3 on PATH")?;
        let kondo = worktree.which("clj-kondo").ok_or(
            "Jank definitions require clj-kondo on PATH (brew install borkdude/brew/clj-kondo)",
        )?;
        Ok(zed::Command {
            command: python,
            args: vec![
                "-u".into(),
                "-c".into(),
                include_str!("../server/jank_lsp.py").into(),
                kondo,
            ],
            env: Default::default(),
        })
    }
}

zed::register_extension!(JankExtension);
