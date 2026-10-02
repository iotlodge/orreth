// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — W91 THE LOST SERVE: a returned publish is undelivered · 2026-10-02
//! The invoke rail (RabbitMQ) — mirrors `orreth_spine.dispatch.publish_command`
//! and `orreth_spine.rails.invoke_breath`. Publisher-side topology is the law:
//! on a fresh broker a topic exchange DROPS a message with no bound queue,
//! silently — so the publisher declares exchange + queue + binding
//! (idempotent) and publishes `mandatory` with confirms, so an unroutable
//! command fails LOUDLY instead of vanishing — and a RETURNED command is
//! read as undelivered, never as a delivery (W91). A consumer acknowledges only
//! after the bytes are verified (the ACK law, canon 0002 law 4).

use crate::envelope;
use crate::rail_error::RailError;
use crate::rails::{serve_key, serve_queue, COMMAND_EXCHANGE};
use lapin::options::{
    BasicAckOptions, BasicGetOptions, BasicNackOptions, BasicPublishOptions, ConfirmSelectOptions,
    ExchangeDeclareOptions, QueueBindOptions, QueueDeclareOptions,
};
use lapin::types::{FieldTable, ShortString};
use lapin::{
    BasicProperties, Channel, Confirmation, Connection, ConnectionProperties, ExchangeKind,
};
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
/// mandatory, wearing its message id. Declares the queue and its binding
/// first, so the road is there before the command takes it. Refuses by name
/// when the broker returns the command or does not confirm it.
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
    let out = publish_on(&ch, key, body, message_id).await;
    conn.close(200, ss("done")).await.ok();
    out
}

/// The publish itself, on a channel already in confirm mode — and the
/// reading of the broker's answer. W91 THE LOST SERVE (2026-09-30): a
/// `mandatory` publish with no queue bound to its key is CONFIRMED by the
/// broker and RETURNED in the same breath — lapin's `Ack` carries the
/// returned message. Reading `is_ack()` alone took a return as a delivery,
/// the dispatcher committed its footprint, and the ask waited for days
/// (27 commands entered the exchange and reached no queue on the dev
/// ground). A returned or unconfirmed command is `Undelivered` — the rail's
/// moment, not the fact's fault — so the caller's transaction rolls back
/// and the dispatcher stands again at the same fact.
pub async fn publish_on(
    ch: &Channel,
    key: &str,
    body: &[u8],
    message_id: &str,
) -> Result<(), RailError> {
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
    match confirmation {
        Confirmation::Ack(None) => Ok(()),
        Confirmation::Ack(Some(returned)) | Confirmation::Nack(Some(returned)) => {
            Err(RailError::Undelivered(format!(
                "the invoke rail returned the command unroutable — no queue was bound to \
                 `{key}` at that instant ({} {}); the command {message_id} was not delivered",
                returned.reply_code,
                returned.reply_text.as_str()
            )))
        }
        Confirmation::Nack(None) | Confirmation::NotRequested => Err(RailError::Undelivered(
            format!("the invoke rail did not confirm the command {message_id} on `{key}`"),
        )),
    }
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
