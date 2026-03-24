const API = "/v1";

const q = (id) => document.getElementById(id);

async function api(path, opts = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json();
}

function activeProfileId() {
  return Number(q("activeProfileId").value || 1);
}

async function refreshMetrics() {
  const m = await api("/dashboard/metrics");
  q("metrics").innerHTML = `
    <div class="metric"><strong>Total Jobs</strong><div>${m.total_jobs}</div></div>
    <div class="metric"><strong>Applied Jobs</strong><div>${m.applied_jobs}</div></div>
    <div class="metric"><strong>Pending</strong><div>${m.pending_jobs}</div></div>
    <div class="metric"><strong>Attempts</strong><div>${m.attempts_total}</div></div>
    <div class="metric"><strong>Success Rate</strong><div>${(m.success_rate * 100).toFixed(1)}%</div></div>
  `;
}

async function refreshProfiles() {
  const profiles = await api("/profiles");
  q("profiles").innerHTML = `<h3>Profiles</h3>${profiles
    .map(
      (p) =>
        `<div><code>${p.id}</code> ${p.full_name} (${p.email}) <span class="small">${p.linkedin_url || ""}</span></div>`
    )
    .join("")}`;
  if (profiles[0]) q("activeProfileId").value = String(profiles[0].id);
}

async function refreshJobs() {
  const jobs = await api("/jobs?limit=200");
  const tbody = q("jobsTable");
  tbody.innerHTML = "";

  jobs.forEach((job) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${job.id}</td>
      <td>${job.company}</td>
      <td><a href="${job.url}" target="_blank">${job.title}</a></td>
      <td>${job.tier || "-"}</td>
      <td>${job.score?.toFixed ? job.score.toFixed(3) : job.score}</td>
      <td>${job.applied ? "Applied" : "Pending"}</td>
      <td>
        <button class="secondary" data-action="score">Score</button>
        <button data-action="apply">Apply</button>
      </td>
    `;

    tr.querySelector('[data-action="score"]').addEventListener("click", async () => {
      await api(`/jobs/${job.id}/score?profile_id=${activeProfileId()}`, { method: "POST" });
      await refreshAll();
    });

    tr.querySelector('[data-action="apply"]').addEventListener("click", async () => {
      await api(`/jobs/${job.id}/apply?profile_id=${activeProfileId()}`, { method: "POST" });
      await refreshAll();
    });

    tbody.appendChild(tr);
  });
}

async function refreshAttempts() {
  const attempts = await api("/attempts?limit=50");
  q("attempts").innerHTML = attempts
    .map(
      (a) =>
        `<div><code>#${a.id}</code> job=${a.job_id} <strong>${a.status}</strong> via ${a.channel} - ${a.notes}</div>`
    )
    .join("");
}

async function refreshAll() {
  try {
    await Promise.all([refreshMetrics(), refreshProfiles(), refreshJobs(), refreshAttempts()]);
  } catch (err) {
    console.error(err);
    alert(err.message);
  }
}

q("profileForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const body = Object.fromEntries(fd.entries());
  body.preferences_json = "{}";
  await api("/profiles", { method: "POST", body: JSON.stringify(body) });
  e.target.reset();
  await refreshAll();
});

q("jobForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = Object.fromEntries(new FormData(e.target).entries());
  await api("/jobs", { method: "POST", body: JSON.stringify(body) });
  e.target.reset();
  await refreshAll();
});

q("questionForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = Object.fromEntries(new FormData(e.target).entries());
  body.approved = true;
  await api("/questions", { method: "POST", body: JSON.stringify(body) });
  e.target.reset();
  alert("Saved");
});

q("lookupForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = Object.fromEntries(new FormData(e.target).entries());
  const result = await api("/questions/lookup", { method: "POST", body: JSON.stringify(body) });
  q("lookupResult").textContent = JSON.stringify(result, null, 2);
});

q("seedBtn").addEventListener("click", async () => {
  await api("/dev/seed-demo", { method: "POST" });
  await refreshAll();
});

q("refreshBtn").addEventListener("click", refreshAll);

q("runAutoBtn").addEventListener("click", async () => {
  await api("/autopilot/run-once", { method: "POST" });
  await refreshAll();
});

refreshAll();
