FROM docker.io/node:22-bookworm-slim

# Build-time only: install everything while we still have internet.
# Runtime container will have no network access.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ripgrep \
    fd-find \
    jq \
    tree \
    ca-certificates \
    moreutils \
    && ln -sf /usr/bin/fdfind /usr/local/bin/fd \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g opencode-ai @ai-sdk/openai-compatible \
    && npm cache clean --force \
    && rm -rf /root/.npm /tmp/*

# Run as root inside the container. In rootless podman, container root
# maps to the host user (box, uid 1000), so write access to box-owned
# mounted files works correctly. Running as a non-root container user
# would map to a high host uid (100000+) and fail to write.
WORKDIR /repo

COPY --chmod=0755 loop.sh /usr/local/bin/loop.sh

ENTRYPOINT ["/bin/bash", "/usr/local/bin/loop.sh"]
