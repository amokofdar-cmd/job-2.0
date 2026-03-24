const API = "/v1";

const tabs = document.querySelectorAll(".tab");
const panels = document.querySelectorAll(".panel");
const metricsGrid = document.getElementById("metricsGrid");
const attemptRows = document.getElementById("attemptRows");
const profileList = document.getElementById("profileList");
const jobRows = document.getElementById("jobRows");
const actionOutput = document.getElementById("actionOutput");

function setTab(name) {
  tabs.forEach((t) => t.classList.toggle("active", t.dataset.tab === name));
  panels.forEach((p) => p.classList.toggle("visible", p.id === name));
}

tabs.forEach((tab) => tab.addEventListener("click", () => setTab(tab.dataset.tab)));

document.getElementById("refreshAll").addEventListener("click", refreshAll);
document.getElementById("runAutopilot").addEventListener("click", async () => {
  const res = await fetch(`${API}/autopilot/run-once`, { method: "POST" });
  actionOutput.textContent = JSON.stringify(await res.json(), null, 2);
  await refreshAll();
});

document.getElementById("profileForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  const payload = Object.fromEntries(form.entries());
  payload.preferences_json = "{}";
  await postJson(`${API}/profiles`, payload);
  event.target.reset();
  await loadProfiles();
});

document.getElementById("jobForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  const payload = Object.fromEntries(form.entries());
  payload.external_id = null;
  await postJson(`${API}/jobs`, payload);
  event.target.reset();
  await loadJobs();
});

document.getElementById("applyForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  const profileId = Number(form.get("profile_id"));
  const jobId = Number(form.get("job_id"));
  const res = await fetch(`${API}/jobs/${jobId}/apply?profile_id=${profileId}`, { method: "POST" });
  actionOutput.textContent = JSON.stringify(await res.json(), null, 2);
  await refreshAll();
});

document.getElementById("qaForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(event.target).entries());
  payload.approved = true;
  const out = await postJson(`${API}/questions`, payload);
  actionOutput.textContent = JSON.stringify(out, null, 2);
  event.target.reset();
});

async function postJson(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

async function loadMetrics() {
  const metrics = await (await fetch(`${API}/dashboard/metrics`)).json();
  metricsGrid.innerHTML = "";
  Object.entries(metrics).forEach(([key, value]) => {
    const card = document.createElement("div");
    card.className = "metric";
    card.innerHTML = `<h4>${key}</h4><p>${value}</p>`;
    metricsGrid.appendChild(card);
  });
}

async function loadAttempts() {
  const attempts = await (await fetch(`${API}/attempts?limit=10`)).json();
  attemptRows.innerHTML = attempts
    .map((x) => `<tr><td>${x.id}</td><td>${x.job_id}</td><td>${x.channel}</td><td>${x.status}</td><td>${x.notes}</td></tr>`)
    .join("");
}

async function loadProfiles() {
  const profiles = await (await fetch(`${API}/profiles`)).json();
  profileList.innerHTML = profiles
    .map((x) => `<li>#${x.id} - ${x.full_name} (${x.email})</li>`)
    .join("");
}

async function loadJobs() {
  const jobs = await (await fetch(`${API}/jobs?limit=100`)).json();
  jobRows.innerHTML = jobs
    .map((x) => `<tr><td>${x.id}</td><td>${x.company}</td><td><a href="${x.url}" target="_blank">${x.title}</a></td><td>${x.tier}</td><td>${x.score}</td><td>${x.applied}</td></tr>`)
    .join("");
}

async function refreshAll() {
  await Promise.all([loadMetrics(), loadAttempts(), loadProfiles(), loadJobs()]);
}

await refreshAll();
