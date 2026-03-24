const API = "/v1";

const statusEl = document.getElementById("status");
const metricsEl = document.getElementById("metrics");
const jobsBody = document.getElementById("jobsBody");
const attemptsBody = document.getElementById("attemptsBody");
const profilesEl = document.getElementById("profiles");

function setStatus(text) {
  statusEl.textContent = text;
}

async function api(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function renderMetrics(m) {
  const cards = [
    ["Total Jobs", m.total_jobs],
    ["Applied", m.applied_jobs],
    ["Pending", m.pending_jobs],
    ["Attempts", m.attempts_total],
    ["Success Rate", `${(m.success_rate * 100).toFixed(1)}%`],
  ];
  metricsEl.innerHTML = cards
    .map(([k, v]) => `<div class="metric-card"><h3>${k}</h3><p>${v}</p></div>`)
    .join("");
}

function optionVal(id) {
  return document.getElementById(id).value;
}

async function loadJobs() {
  const applied = optionVal("appliedFilter");
  const tier = optionVal("tierFilter");
  const q = new URLSearchParams({ limit: "200" });
  if (applied !== "") q.set("applied", applied);
  if (tier !== "") q.set("tier", tier);
  const jobs = await api(`/jobs?${q.toString()}`);

  jobsBody.innerHTML = jobs
    .map(
      (j) => `
    <tr>
      <td>${j.id}</td>
      <td>${j.company}</td>
      <td><a href="${j.url}" target="_blank">${j.title}</a></td>
      <td>${j.tier}</td>
      <td>${Number(j.score).toFixed(3)}</td>
      <td>${j.applied ? "✅" : "⏳"}</td>
      <td>
        <button onclick="scoreJob(${j.id})">Score</button>
        <button onclick="applyJob(${j.id})">Apply</button>
      </td>
    </tr>`
    )
    .join("");
}

async function loadAttempts() {
  const attempts = await api("/attempts?limit=100");
  attemptsBody.innerHTML = attempts
    .map(
      (a) => `
      <tr>
        <td>${a.id}</td>
        <td>${a.job_id}</td>
        <td>${a.channel}</td>
        <td>${a.status}</td>
        <td>${a.notes}</td>
      </tr>`
    )
    .join("");
}

async function loadProfiles() {
  const profiles = await api("/profiles");
  profilesEl.innerHTML =
    profiles.length === 0
      ? "<p>No profiles yet.</p>"
      : `<ul>${profiles
          .map((p) => `<li><strong>#${p.id}</strong> ${p.full_name} (${p.email})</li>`)
          .join("")}</ul>`;
}

async function refreshAll() {
  const metrics = await api("/dashboard/metrics");
  renderMetrics(metrics);
  await Promise.all([loadJobs(), loadAttempts(), loadProfiles()]);
}

async function firstProfileId() {
  const profiles = await api("/profiles");
  if (!profiles.length) throw new Error("Create a profile first.");
  return profiles[0].id;
}

window.scoreJob = async function scoreJob(jobId) {
  try {
    const profileId = await firstProfileId();
    await api(`/jobs/${jobId}/score?profile_id=${profileId}`, { method: "POST" });
    await refreshAll();
    setStatus(`Job ${jobId} scored.`);
  } catch (err) {
    setStatus(`Score failed: ${err.message}`);
  }
};

window.applyJob = async function applyJob(jobId) {
  try {
    const profileId = await firstProfileId();
    await api(`/jobs/${jobId}/apply?profile_id=${profileId}`, { method: "POST" });
    await refreshAll();
    setStatus(`Job ${jobId} applied.`);
  } catch (err) {
    setStatus(`Apply failed: ${err.message}`);
  }
};

document.getElementById("refreshBtn").addEventListener("click", async () => {
  await refreshAll();
  setStatus("Refreshed.");
});

document.getElementById("runOnceBtn").addEventListener("click", async () => {
  try {
    const res = await api("/autopilot/run-once", { method: "POST" });
    await refreshAll();
    setStatus(`Autopilot applied ${res.applied_this_cycle} jobs.`);
  } catch (err) {
    setStatus(`Autopilot error: ${err.message}`);
  }
});

document.getElementById("seedBtn").addEventListener("click", async () => {
  try {
    await api("/bootstrap/demo", { method: "POST" });
    await refreshAll();
    setStatus("Seeded demo data.");
  } catch (err) {
    setStatus(`Seed error: ${err.message}`);
  }
});

document.getElementById("profileForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target));
  try {
    await api("/profiles", { method: "POST", body: JSON.stringify(data) });
    e.target.reset();
    await refreshAll();
    setStatus("Profile saved.");
  } catch (err) {
    setStatus(`Profile error: ${err.message}`);
  }
});

document.getElementById("jobForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target));
  try {
    await api("/jobs", { method: "POST", body: JSON.stringify(data) });
    e.target.reset();
    await refreshAll();
    setStatus("Job saved.");
  } catch (err) {
    setStatus(`Job error: ${err.message}`);
  }
});

document.getElementById("questionForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const payload = {
    question_text: fd.get("question_text"),
    answer_text: fd.get("answer_text"),
    approved: fd.get("approved") === "on",
  };
  try {
    await api("/questions", { method: "POST", body: JSON.stringify(payload) });
    e.target.reset();
    setStatus("Q&A saved.");
  } catch (err) {
    setStatus(`Question save error: ${err.message}`);
  }
});

document.getElementById("lookupForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = Object.fromEntries(new FormData(e.target));
  try {
    const res = await api("/questions/lookup", { method: "POST", body: JSON.stringify(payload) });
    document.getElementById("lookupResult").textContent = JSON.stringify(res, null, 2);
    setStatus("Lookup complete.");
  } catch (err) {
    setStatus(`Lookup error: ${err.message}`);
  }
});

["appliedFilter", "tierFilter"].forEach((id) => {
  document.getElementById(id).addEventListener("change", () => {
    void loadJobs();
  });
});

void refreshAll();
