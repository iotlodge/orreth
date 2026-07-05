# PROVENANCE: authored by Opus 4.8 (2026-07-05), pending Fable 5 review — see agents/PROVENANCE.md
#
# A minimal, modular agent image. An agent is a CLIENT — it needs only network reach to a
# floor — so this image carries the SDK + all three flavors and runs any of them from anywhere:
#
#   docker build -t orreth-agent -f agents/Dockerfile agents
#   docker run --rm --network host orreth-agent \
#       flavors/01-prototype/run.py --field http://127.0.0.1:4970 --once
#
# Point --field at a floor in another cluster or across the internet and it joins the same way.
FROM python:3.12-slim

WORKDIR /agent
COPY orreth-agent-sdk /agent/orreth-agent-sdk
COPY flavors /agent/flavors

# the SDK + every flavor's runtime deps, resolved once at build
RUN pip install --no-cache-dir ./orreth-agent-sdk[governed] pyyaml langgraph

ENV PYTHONPATH=/agent/orreth-agent-sdk
ENTRYPOINT ["python"]
CMD ["flavors/01-prototype/run.py", "--field", "http://host.docker.internal:4970", "--forever"]
