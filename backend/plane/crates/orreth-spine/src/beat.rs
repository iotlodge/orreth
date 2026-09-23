// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops · 2026-09-23
//! THE BEAT LOCK — the loops' shadow law (`orreth_spine.ground.beat`). Two
//! kernels stand on one ground in SHADOW (the Python Bridge on :4600, this
//! bridge on :4601) and each runs the standing loops — the scheduler's tick,
//! the intent rail's turn. A beat reads what is due and acts on it; two beats
//! at once would file the same occurrence twice, observe the same red twice,
//! plan the same cause twice. So a beat is CLAIMED before it runs: a session
//! advisory lock on the ground keyed by the beat's class and this world's
//! scope (`pg_try_advisory_lock(class, hashtext(scope))`), held for the beat,
//! released after; the other kernel's beat finds it held and steps back,
//! saying so. The lock is Postgres's own: a kernel that dies mid-beat drops it
//! with its connection. One ground, one beat at a time, per world. The
//! classes and the words are pure, measured by `loops-v0.json` (`beat_lock`).

/// The beat classes count up from here (the DDL guard is 742199).
pub const BEAT_LOCK: i64 = 742200;
pub const BEATS: [(&str, i64); 3] = [("scheduler", 1), ("intent", 2), ("keeper", 3)];
pub const HELD: &str = "the beat is held by another kernel on this ground";

/// The advisory lock's first key for a beat class; an unknown class is `None`.
pub fn beat_key(name: &str) -> Option<i32> {
    BEATS
        .iter()
        .find(|(n, _)| *n == name)
        .map(|(_, c)| (BEAT_LOCK + c) as i32)
}

#[cfg(feature = "rails")]
pub use live::*;

#[cfg(feature = "rails")]
mod live {
    use super::beat_key;
    use crate::ground::Ground;
    use crate::rail_error::RailError;

    /// Claim this world's beat of a class — true when it is ours to run.
    pub async fn try_beat(g: &Ground, scope: &str, name: &str) -> Result<bool, RailError> {
        let key =
            beat_key(name).ok_or_else(|| RailError::Refused(format!("no beat named {name}")))?;
        let row = g
            .client()
            .query_one(
                "SELECT pg_try_advisory_lock($1::int, hashtext($2))",
                &[&key, &scope],
            )
            .await?;
        Ok(row.get(0))
    }

    /// Release it — however the beat ended.
    pub async fn end_beat(g: &Ground, scope: &str, name: &str) -> Result<(), RailError> {
        let key =
            beat_key(name).ok_or_else(|| RailError::Refused(format!("no beat named {name}")))?;
        g.client()
            .execute(
                "SELECT pg_advisory_unlock($1::int, hashtext($2))",
                &[&key, &scope],
            )
            .await?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_keys_count_up_from_the_base() {
        assert_eq!(beat_key("scheduler"), Some(742201));
        assert_eq!(beat_key("intent"), Some(742202));
        assert_eq!(beat_key("nothing"), None);
    }
}
