// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam: the crew this kernel seats, said at light · 2026-09-24
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp2: `orrethd` — THE door on :4600 · 2026-09-29
//! `orrethd` — the Orreth kernel, THE door on :4600 (re-base sp2). It was born
//! `spine-bridge`, lit in SHADOW on :4601 beside the Python Bridge through P7
//! (canon 0008: fixture unchanged → SHADOW → the door); the old `orrethd` crate
//! it is named after rests at the tag `main-v0.72-old-world`. One ground, one
//! truth: the Python reference (`scripts/dev.sh reference`, :4601) reads the
//! same ground and serves the same page.
//!
//!     cargo run -p orreth-spine --features bridge --bin orrethd
//!     scripts/dev.sh kernel            (background, log ~/.orreth/tmp/kernel.log)
//!
//! Dials: `SPINE_BRIDGE_PORT` (4600) · `SPINE_PG` · `SPINE_RABBIT` · `SPINE_KAFKA`
//! · `SPINE_SCOPE` · `SPINE_QUEUE_NS` · `SPINE_MASTERS` · `SPINE_HUMAN_ZONE` ·
//! `ORRETH_GLASS` (the page; default the crate's `../../../../spine/glass/index.html`)
//! · `SPINE_BODIES` (P7 sp6: `crew` — this kernel seats and governs the crew as
//! processes; `none` — the Python reference's bodies serve) · `ORRETH_SPINE` (the spine home).
//! Ctrl+C brings it down whole.

use orreth_spine::bridge::{light, Config};

#[tokio::main]
async fn main() {
    let cfg = Config::from_env();
    let lit = match light(cfg.clone()).await {
        Ok(l) => l,
        Err(e) => {
            eprintln!("orrethd could not light: {e}");
            std::process::exit(1);
        }
    };
    println!(
        "orrethd is lit: http://127.0.0.1:{}/  (scope {} · benches '{}' · dispatcher group {} · glass {})",
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
        None => println!("no bodies live here (SPINE_BODIES=none) — the Python reference's serve from their benches; Ctrl+C brings it down whole."),
    }
    if lit.wait_ready(std::time::Duration::from_secs(30)).await {
        println!("the feed and the dispatcher hold their assignments.");
    } else {
        println!("still waiting for the broker's assignment — the loops keep trying.");
    }
    let _ = tokio::signal::ctrl_c().await;
    println!("\norrethd goes dark — stopping whole…");
    lit.stop().await;
    println!("orrethd is dark — stopped whole, nothing left running.");
}
