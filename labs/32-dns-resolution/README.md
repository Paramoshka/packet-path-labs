# Lab 32 — DNS resolution and caching

Follow a query through a caching resolver to an authoritative server.
Prerequisites: labs 02 and 30. No public DNS dependency for the experiments.

## Topology

`client 10.32.0.2 — resolver 10.32.0.1 / 10.32.1.1 — auth 10.32.1.2`

The resolver forwards only `lab.test` to auth. The reserved `.test` zone is local.
This demonstrates forwarding/caching, not a complete root-to-TLD recursive walk.

## Experiments

1. On client run `dig @10.32.0.1 app.lab.test A`. Expect `192.0.2.80`.
   Query auth directly with `dig @10.32.1.2 app.lab.test A +norecurse` and compare
   AA/RA flags. The example address is DNS data, not a deployed web service.
2. Capture port 53 on resolver eth2. Repeat the query within 30 seconds:
   the answer should come from cache and its TTL decrease.
3. Query `www.lab.test` and explain CNAME versus A. Query `missing.lab.test`:
   expect NXDOMAIN. Query `app.lab.test AAAA`: expect NOERROR with no AAAA answer.
4. Stop auth's named process. After cache expiry, query with a bounded wait,
   e.g. `dig @10.32.0.1 app.lab.test +time=3 +tries=1`. The client may time out
   before the resolver finishes retrying; distinguish that from a DNS SERVFAIL
   response. Restart with `named -u root -c /etc/lab/named.conf` on auth.
5. Compare UDP and `dig +tcp`. Explain why permitting only UDP/53 is incomplete.

## Acceptance

Demonstrate cache hit/miss by capture, distinguish NXDOMAIN / NOERROR-no-data /
SERVFAIL / timeout, and identify whether client, resolver or authority failed.
Config checks: `named-checkconf /etc/lab/named.conf` on both servers and
`named-checkzone lab.test /etc/lab/lab.test.zone` on auth.

Reference: [BIND documentation](https://bind9.readthedocs.io/en/stable/).

## Lifecycle

From this directory:

```sh
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

Run host-side `docker exec` commands as a user with Docker access. Commands
inside a node affect that container, not the host. New Linux nodes install
packages at deployment time; Internet access to Alpine repositories is required.
Runtime edits disappear on destroy/deploy. Save intentional changes in the
mounted source configs or topology and verify them with a fresh deployment.
