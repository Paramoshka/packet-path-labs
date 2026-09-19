# Lab 15 — VXLAN Bridge and FDB

Add multiple endpoints behind each VTEP and study MAC learning in the bridge FDB and VXLAN data plane.

## Topology

```text
h1a,h1b -- vtep1 ===== VXLAN ===== vtep2 -- h2a,h2b
```

## Run

```bash
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

## Explore

- Generate traffic between several MAC pairs.
- Inspect local and remote MAC entries with `bridge fdb show`.
- Flush the FDB and observe flood-and-learn behavior.

## Useful checks

- `docker exec clab-pp15-vtep1 bridge fdb show`
- `docker exec clab-pp15-vtep2 bridge fdb show`


