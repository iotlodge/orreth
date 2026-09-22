// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails · 2026-09-22
//! The events rail read side (Kafka) — the consumer half of
//! `orreth_spine.rails.events_breath` and the read loop of
//! `orreth_spine.projector` in miniature: a fresh group reads a topic from its
//! start (or from now), and the offset is committed only after the caller has
//! done its durable work. Topics are DECLARED before subscribing (the
//! bridgefeed lesson: a topic that exists only after its first fact leaves a
//! consumer assignment-less).

use crate::envelope;
use crate::rail_error::RailError;
use rdkafka::admin::{AdminClient, AdminOptions, NewTopic, TopicReplication};
use rdkafka::client::DefaultClientContext;
use rdkafka::config::ClientConfig;
use rdkafka::consumer::{CommitMode, Consumer, StreamConsumer};
use rdkafka::Message;
use serde_json::Value;
use std::time::{Duration, Instant};

/// Declare topics (one partition, one replica — the dev rig's shape); an
/// existing topic is fine.
pub async fn declare_topics(bootstrap: &str, topics: &[&str]) -> Result<(), RailError> {
    let admin: AdminClient<DefaultClientContext> = ClientConfig::new()
        .set("bootstrap.servers", bootstrap)
        .create()?;
    let wanted: Vec<NewTopic> = topics
        .iter()
        .map(|t| NewTopic::new(t, 1, TopicReplication::Fixed(1)))
        .collect();
    admin
        .create_topics(&wanted, &AdminOptions::new())
        .await
        .map_err(|e| RailError::Events(e.to_string()))?;
    Ok(())
}

/// A consumer standing on the rail as one group member for its whole life.
pub struct Reader {
    consumer: StreamConsumer,
}

impl Reader {
    /// `from_start` reads the topic from offset zero (replay, tests); else
    /// only what happens while the reader lives.
    pub async fn open(
        bootstrap: &str,
        group: &str,
        topics: &[&str],
        from_start: bool,
    ) -> Result<Reader, RailError> {
        declare_topics(bootstrap, topics).await?;
        let consumer: StreamConsumer = ClientConfig::new()
            .set("bootstrap.servers", bootstrap)
            .set("group.id", group)
            .set(
                "auto.offset.reset",
                if from_start { "earliest" } else { "latest" },
            )
            .set("enable.auto.commit", "false")
            .create()?;
        consumer.subscribe(topics)?;
        Ok(Reader { consumer })
    }

    /// Read until `want` accepts an envelope, committing every offset walked
    /// past (each one either not ours or already handed to `want`); the
    /// matching envelope's offset is committed too. Bodies that are not
    /// envelopes are walked past here (a projector would PARK them).
    pub async fn read_until(
        &self,
        timeout: Duration,
        mut want: impl FnMut(&Value) -> bool,
    ) -> Result<Value, RailError> {
        let deadline = Instant::now() + timeout;
        loop {
            let left = deadline.saturating_duration_since(Instant::now());
            if left.is_zero() {
                return Err(RailError::Timeout(
                    "the events rail never returned the fact".into(),
                ));
            }
            let msg = match tokio::time::timeout(left, self.consumer.recv()).await {
                Err(_) => continue,
                Ok(Err(e)) => return Err(e.into()),
                Ok(Ok(m)) => m,
            };
            let env = msg.payload().and_then(|p| envelope::decode(p).ok());
            let hit = env.as_ref().is_some_and(&mut want);
            self.consumer.commit_message(&msg, CommitMode::Sync)?;
            if hit {
                return Ok(env.unwrap());
            }
        }
    }
}
