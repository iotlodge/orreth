// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam: the crew this kernel seats, said at light · 2026-09-24
//! `spine-bridge` — the Rust bridge, lit in SHADOW on :4601 beside the Python
//! Bridge on :4600 (canon 0008: fixture unchanged → SHADOW → the door). One
//! ground, one truth: an ask through either door is dispatched once (the
//! inbox's footprint, `dispatcher`'s shadow law), served by the Python
//! residents on their benches, and its reply shows at both.
//!
//!     cargo run -p orreth-spine --features bridge --bin spine-bridge
//!     scripts/dev.sh shadow            (background, log ~/.orreth/tmp/shadow.log)
//!
//! Dials: `SPINE_BRIDGE_PORT` (4601) · `SPINE_PG` · `SPINE_RABBIT` · `SPINE_KAFKA`
//! · `SPINE_SCOPE` · `SPINE_QUEUE_NS` · `SPINE_MASTERS` · `SPINE_HUMAN_ZONE` ·
//! `ORRETH_GLASS` (the page; default the crate's `../../../../spine/glass/index.html`)
//! · `SPINE_BODIES` (P7 sp6: `crew` — this kernel seats and governs the crew as
//! processes; `none` — the Python Bridge's bodies serve) · `ORRETH_SPINE` (the spine home).
//! Ctrl+C brings it down whole.

use orreth_spine::bridge::{light, Config};

#[tokio::main]
async fn main() {
    let cfg = Config::from_env();
    let lit = match light(cfg.clone()).await {
        Ok(l) => l,
        Err(e) => {
            eprintln!("the Rust bridge could not light: {e}");
            std::process::exit(1);
        }
    };
    println!(
        "the Rust bridge is lit: http://127.0.0.1:{}/  (scope {} · benches '{}' · dispatcher group {} · glass {})",
        lit.port,
        cfg.world.scope,
        cfg.world.ns,
        lit.group,
        cfg.glass.display()
    );
    match &lit.bodies {
        Some(b) => println!(
            "the crew is this kernel's: {} seats spawned as processes ({}); a body that dies is restarted, one that dies three times in five minutes is parked and said; Ctrl+C brings everything down whole.",
            b.seats.len(),
            b.seats.iter().map(|s| s.name.as_str()).collect::<Vec<_>>().join(" · ")
        ),
        None => println!("no bodies live here (SPINE_BODIES=none) — the Python Bridge's serve from their benches; Ctrl+C brings it down whole."),
    }
    if lit.wait_ready(std::time::Duration::from_secs(30)).await {
        println!("the feed and the dispatcher hold their assignments.");
    } else {
        println!("still waiting for the broker's assignment — the loops keep trying.");
    }
    let _ = tokio::signal::ctrl_c().await;
    println!("\nthe Rust bridge goes dark — stopping whole…");
    lit.stop().await;
    println!("the Rust bridge is dark — stopped whole, nothing left running.");
}
