# Lab 39 — Troubleshooting exam

Diagnose a failing service without being told the faulty layer.
Prerequisites: labs 02, 20–23, 30 and 32.

## Topology and working baseline

Client `10.39.1.10` connects through r1 to server `10.39.2.10:8080` and DNS
`10.39.3.53`. r1 uses `.1` in each subnet. DNS serves `app.lab.test`.

Before injecting a fault, on client verify:

```sh
dig @10.39.3.53 app.lab.test
curl --max-time 5 --resolve app.lab.test:8080:10.39.2.10 http://app.lab.test:8080/
```

Expected: A record `10.39.2.10` and body `packet-path-labs`. `--resolve` deliberately
bypasses DNS to test the transport/application independently. For an end-to-end
DNS test, set client's `/etc/resolv.conf` to `nameserver 10.39.3.53` and use curl
without `--resolve` (inside the container only).

## Exam

Ask a tutor to run one scenario with `sh break.sh A` (A–E) from this directory
on the host. Do not read the script or instructor notes before diagnosing.
Use one fresh deployment per scenario: faults must not accumulate.

1. State the symptom and at least two possible causes before changing anything.
2. Collect route/neighbor/socket/DNS evidence and captures at adjacent hops.
3. Identify the first point where observed behavior differs from expectation.
4. Apply the smallest repair; demonstrate DNS, direct HTTP and named HTTP.
5. Explain why another plausible diagnosis was wrong.

Each curl must have a timeout. Avoid broad firewall flushes or indiscriminate
route replacement; those can hide the cause rather than diagnose it.

## Acceptance

For each scenario record: symptom → hypothesis → distinguishing test → root
cause → repair → verification. Solve all five independently. Tutor guidance and
expected repairs are in [INSTRUCTOR.md](INSTRUCTOR.md); consult after attempting.

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
