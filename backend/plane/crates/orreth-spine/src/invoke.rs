// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails · 2026-09-22
//! The invoke rail (RabbitMQ) — mirrors `orreth_spine.dispatch.publish_command`
//! and `orreth_spine.rails.invoke_breath`. Publisher-side topology is the law:
//! on a fresh broker a topic exchange DROPS a message with no bound queue,
//! silently — so the publisher declares exchange + queue + binding
//! (idempotent) and publishes `mandatory` with confirms, so an unroutable
//! command fails LOUDLY instead of vanishing. A consumer acknowledges only
//! after the bytes are verified (the ACK law, canon 0002 law 4).

use crate::envelope;
use crate::rail_error::RailError;
use crate::rails::{serve_key, serve_queue, COMMAND_EXCHANGE};
use lapin::options::{
    BasicAckOptions, BasicGetOptions, BasicNackOptions, BasicPublishOptions, ConfirmSelectOptions,
    ExchangeDeclareOptions, QueueBindOptions, QueueDeclareOptions,
};
use lapin::types::{FieldTable, ShortString};
use lapin::{BasicProperties, Channel, Connection, ConnectionProperties, ExchangeKind};
use serde_json::Value;
use std::time::{Duration, Instant};

fn ss(s: &str) -> ShortString {
    s.into()
}

pub async fn connect(url: &str) -> Result<Connection, RailError> {
    Ok(Connection::connect(url, ConnectionProperties::default()).await?)
}

/// Declare the command exchange, the queue and its binding — idempotent.
pub async fn declare(ch: &Channel, queue: &str, key: &str) -> Result<(), RailError> {
    ch.exchange_declare(
        ss(COMMAND_EXCHANGE),
        ExchangeKind::Topic,
        ExchangeDeclareOptions {
            durable: true,
            ..Default::default()
        },
        FieldTable::default(),
    )
    .await?;
    ch.queue_declare(
        ss(queue),
        QueueDeclareOptions {
            durable: true,
            ..Default::default()
        },
        FieldTable::default(),
    )
    .await?;
    ch.queue_bind(
        ss(queue),
        ss(COMMAND_EXCHANGE),
        ss(key),
        QueueBindOptions::default(),
        FieldTable::default(),
    )
    .await?;
    Ok(())
}

/// Publish one body on the command exchange with confirms: persistent,
/// mandatory, wearing its message id. Refuses by name when the broker does
/// not confirm.
pub async fn publish(
    url: &str,
    queue: &str,
    key: &str,
    body: &[u8],
    message_id: &str,
) -> Result<(), RailError> {
    let conn = connect(url).await?;
    let ch = conn.create_channel().await?;
    ch.confirm_select(ConfirmSelectOptions::default()).await?;
    declare(&ch, queue, key).await?;
    let confirmation = ch
        .basic_publish(
            ss(COMMAND_EXCHANGE),
            ss(key),
            BasicPublishOptions {
                mandatory: true,
                ..Default::default()
            },
            body,
            BasicProperties::default()
                .with_delivery_mode(2)
                .with_message_id(message_id.to_string().into()),
        )
        .await?
        .await?;
    let ok = confirmation.is_ack();
    conn.close(200, ss("done")).await.ok();
    if !ok {
        return Err(RailError::Refused(
            "the invoke rail did not confirm the publish".into(),
        ));
    }
    Ok(())
}

/// A committed fact becomes an invoke command: a targeted command routes to
/// the named resident's own queue, an untargeted one to the shared bench —
/// `ns` is the session's `SPINE_QUEUE_NS`.
pub async fn publish_command(url: &str, env: &Value, ns: &str) -> Result<(), RailError> {
    let target = env
        .get("payload")
        .and_then(|p| p.get("target"))
        .and_then(Value::as_str);
    let raw = envelope::encode(env)?;
    let message_id = env["message_id"].as_str().unwrap_or_default();
    publish(
        url,
        &serve_queue(ns, target),
        &serve_key(ns, target),
        &raw,
        message_id,
    )
    .await
}

/// Take from a queue until `want` matches a body (acked) or the deadline
/// passes; another's message is put back (nack + requeue). Returns the
/// matching bytes.
pub async fn receive(
    url: &str,
    queue: &str,
    key: &str,
    timeout: Duration,
    mut want: impl FnMut(&[u8]) -> bool,
) -> Result<Vec<u8>, RailError> {
    let conn = connect(url).await?;
    let ch = conn.create_channel().await?;
    declare(&ch, queue, key).await?;
    let deadline = Instant::now() + timeout;
    let found = loop {
        if Instant::now() >= deadline {
            break None;
        }
        match ch.basic_get(ss(queue), BasicGetOptions::default()).await? {
            None => tokio::time::sleep(Duration::from_millis(50)).await,
            Some(msg) => {
                if want(&msg.data) {
                    msg.acker.ack(BasicAckOptions::default()).await?;
                    break Some(msg.data.clone());
                }
                msg.acker
                    .nack(BasicNackOptions {
                        requeue: true,
                        ..Default::default()
                    })
                    .await?;
            }
        }
    };
    conn.close(200, ss("done")).await.ok();
    found.ok_or_else(|| RailError::Timeout("the invocation rail never returned the message".into()))
}
