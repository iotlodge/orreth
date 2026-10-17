# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp2: one image for the kernel · 2026-09-29
# Amended: Claude Fable 5.1 (claude-fable-5-1) — W95: procps in the box (ps · pkill) · 2026-10-02
# Amended: Claude Fable 5.1 (claude-fable-5-1) — 0.2.0: the image for linux/arm64 AND linux/amd64 (buildx; amd64 PAID) · 2026-10-16
#
# orrethd — the Orreth kernel, one image. The Rust kernel (`orreth-spine`, feature `bridge`)
# is THE door on :4600; the crew it seats are Python bodies (`orreth_spine.body`), spawned as
# processes it governs — so the image carries both: the release binary and the spine's venv,
# beside the glass page, the crew manifest, the templates, the tool declarations and the canon
# the MITL reads on disk (docs/rearch). Build from the repo root:
#
#     docker build -t ghcr.io/iotlodge/orrethd .                     # this machine's own platform
#     docker compose -f spine/compose.yaml --profile kernel up -d     # beside the rig's four boxes
#
# The RELEASE is one image for two platforms (0.2.0, 2026-10-16 — amd64 was owed from 0.1.0): every
# stage below is platform-neutral (rust · debian · uv publish both), so buildx builds the Rust stage
# once per platform (the foreign one under the Desktop's emulation; slow, but the same bytes a native
# box would make) and `:latest` is the same manifest list:
#
#     docker buildx build --platform linux/amd64,linux/arm64 \
#         -t ghcr.io/iotlodge/orrethd:$(cat VERSION) -t ghcr.io/iotlodge/orrethd:latest --load .
#     docker buildx build --platform linux/amd64,linux/arm64 -t ... --push .   # the publish, on JB's word
#
# Dials the container reads: SPINE_PG · SPINE_RABBIT · SPINE_KAFKA (the rails by service name),
# SPINE_GATEWAY (LiteLLM), SPINE_BRIDGE_PORT (4600), SPINE_BIND (0.0.0.0 here — the box's door must be
# reachable through the published port; the host kernel keeps loopback), SPINE_BODIES (crew | none), ORRETH_HOME
# (the kernel self's and the bodies' seeds — mount a volume to keep the same selves every life).

# ---- stage 1: the kernel, release --------------------------------------------------------
FROM rust:1-bookworm AS build
RUN apt-get update && apt-get install -y --no-install-recommends cmake g++ pkg-config libssl-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY backend/plane backend/plane
RUN cd backend/plane && cargo build --release -p orreth-spine --features bridge --bin orrethd

# ---- stage 2: the bodies' python beside the binary ---------------------------------------
FROM debian:bookworm-slim
# procps (W95, the book's walk): `ps` and `pkill` inside the box — debian slim ships neither
RUN apt-get update && apt-get install -y --no-install-recommends python3 ca-certificates curl procps \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /opt/orreth
# the spine home: the reference package (the bodies), the glass, the crew, the templates, the tools
COPY spine spine
# the canon the MITL acquires from disk (mitl.py · mitl.rs read docs/rearch/000N-*.md and the covenant by path)
COPY docs/rearch docs/rearch
COPY .claude/skills/orreth-covenant .claude/skills/orreth-covenant
COPY VERSION VERSION
RUN cd spine && uv sync --no-dev --frozen 2>/dev/null || (cd spine && uv sync --no-dev)
COPY --from=build /src/backend/plane/target/release/orrethd /usr/local/bin/orrethd

ENV ORRETH_SPINE=/opt/orreth/spine \
    ORRETH_GLASS=/opt/orreth/spine/glass/index.html \
    ORRETH_HOME=/var/lib/orreth \
    SPINE_PYTHON=/opt/orreth/spine/.venv/bin/python3 \
    SPINE_BRIDGE_PORT=4600 \
    SPINE_BIND=0.0.0.0 \
    SPINE_BODIES=crew
VOLUME ["/var/lib/orreth"]
EXPOSE 4600
HEALTHCHECK --interval=10s --timeout=4s --retries=12 CMD curl -sf http://127.0.0.1:4600/health || exit 1
ENTRYPOINT ["orrethd"]
