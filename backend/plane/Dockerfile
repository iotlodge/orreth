# orrethd — one image; the tier comes from the mounted profile (0000 §1).
FROM rust:slim AS build
WORKDIR /src
COPY . .
RUN cargo build --release -p orrethd

FROM debian:bookworm-slim
COPY --from=build /src/target/release/orrethd /usr/local/bin/orrethd
ENTRYPOINT ["orrethd"]
