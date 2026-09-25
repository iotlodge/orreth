// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp7, cells: the topic wears the cell's namespace · 2026-09-25
//! The relay's real sink — mirrors `orreth_spine.sinks.KafkaSink` (canon
//! 0002). The TOPIC is the envelope's type (schema families, never
//! per-identity); the KEY is the aggregate id when the envelope wears one —
//! order holds exactly where it matters, per aggregate, and nowhere it
//! doesn't. A refused publish raises, the relay records the attempt, and the
//! row stays unpublished — at-least-once, honestly.

use crate::envelope;
use crate::outbox::Sink;
use crate::rail_error::RailError;
use crate::rails::{key_for, topic_for};
use rdkafka::config::ClientConfig;
use rdkafka::producer::{FutureProducer, FutureRecord};
use std::time::Duration;

pub struct KafkaSink {
    producer: FutureProducer,
    timeout: Duration,
    /// P7 sp7: the cell's namespace every topic wears.
    ns: String,
}

impl KafkaSink {
    pub fn new(bootstrap: &str, ns: &str) -> Result<KafkaSink, RailError> {
        let producer: FutureProducer = ClientConfig::new()
            .set("bootstrap.servers", bootstrap)
            .set("message.timeout.ms", "10000")
            .create()?;
        Ok(KafkaSink {
            producer,
            timeout: Duration::from_secs(10),
            ns: ns.to_string(),
        })
    }
}

impl Sink for KafkaSink {
    async fn publish(&mut self, message_id: &str, body: &[u8]) -> Result<(), RailError> {
        let env = envelope::decode(body)?;
        let topic = crate::rails::topic(
            topic_for(&env)
                .ok_or_else(|| RailError::Refused("the envelope names no type".into()))?,
            &self.ns,
        );
        let key = key_for(&env).unwrap_or_else(|| message_id.to_string());
        self.producer
            .send(
                FutureRecord::to(&topic).key(&key).payload(body),
                self.timeout,
            )
            .await
            .map(|_| ())
            .map_err(|(e, _)| RailError::Sink(format!("the events rail refused the publish: {e}")))
    }
}
