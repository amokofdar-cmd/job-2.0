const API = "/v1";
let selectedProfileId = null;

function log(obj) {
  const el = document.getElementById("console");
  const line = typeof obj === "string" ? obj : JSON.stringify(obj, null, 2);
  el.textContent = `${new Date().toISOString()}\n${line}\n\n${el.textContent}`.slice(0, 12000);
}

async function request(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const json = await res.json();
  if (!res.ok) throw new Error(JSON.stringify(json));
  return json;
}

function metricCard(label, value) {
  return `<div class="card"><strong>${label}</strong><p>${value}</p></div>`;
}

async function loadStatus() {
  const [metrics, control] = await Promise.all([
    request("/dashboard/metrics"),
    request("/run-control"),
  ]);

  document.getElementById("status-grid").innerHTML = [
    metricCard("Total Jobs", metrics.total_jobs),
    metricCard("Applied", metrics.applied_jobs),
    metricCard("Pending", metrics.pending_jobs),
    metricCard("Attempts", metrics.attempts_total),
    metricCard("Success Rate", `${(metrics.success_rate * 100).toFixed(1)}%`),
  ].join("");

  const toggle = document.getElementById("autopilot-toggle");
  toggle.textContent = control.is_running ? "Pause" : "Resume";
  toggle.dataset.state = control.is_running ? "running" : "paused";
}

async function loadProfiles() {
  const profiles = await request("/profiles");
  const html = profiles.map((p) => (
    `<div class="list-item"><strong>${p.full_name}</strong><br/><small>${p.email}</small><br/>`
    + `<button class="secondary" data-pid="${p.id}">Use Profile #${p.id}</button></div>`
  )).join("");

  const list = document.getElementById("profiles-list");
  list.innerHTML = html || "<div class='list-item'>No profiles yet</div>";

  list.querySelectorAll("button[data-pid]").forEach((btn) => {
    btn.addEventListener("click", () => {
      selectedProfileId = Number(btn.dataset.pid);
      log(`Selected profile ${selectedProfileId}`);
    });
  });

  if (!selectedProfileId && profiles.length) {
    selectedProfileId = profiles[0].id;
  }
}

async function loadJobs() {
  const jobs = await request("/jobs?limit=200");
  const body = document.getElementById("jobs-body");
  body.innerHTML = jobs.map((j) => `
    <tr>
      <td>${j.id}</td>
      <td>${j.company}</td>
      <td><a href="${j.url}" target="_blank">${j.title}</a></td>
      <td>${j.tier ?? "-"}</td>
      <td>${Number(j.score || 0).toFixed(3)}</td>
      <td>${j.applied ? "Yes" : "No"}</td>
      <td>
        <button class="secondary" data-score="${j.id}">Score</button>
        <button data-apply="${j.id}">Apply</button>
      </td>
    </tr>
  `).join("");

  body.querySelectorAll("button[data-score]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        if (!selectedProfileId) return log("Select or create a profile first.");
        const out = await request(`/jobs/${btn.dataset.score}/score?profile_id=${selectedProfileId}`, { method: "POST" });
        log(out);
        await loadJobs();
      } catch (e) {
        log(e.message);
      }
    });
  });

  body.querySelectorAll("button[data-apply]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        if (!selectedProfileId) return log("Select or create a profile first.");
        const out = await request(`/jobs/${btn.dataset.apply}/apply?profile_id=${selectedProfileId}`, { method: "POST" });
        log(out);
        await loadAll();
      } catch (e) {
        log(e.message);
      }
    });
  });
}

async function loadAttempts() {
  const attempts = await request("/attempts?limit=100");
  document.getElementById("attempts-body").innerHTML = attempts.map((a) => `
    <tr>
      <td>${a.id}</td>
      <td>${a.job_id}</td>
      <td>${a.channel}</td>
      <td>${a.status}</td>
      <td>${a.notes}</td>
    </tr>
  `).join("");
}

async function loadAll() {
  await Promise.all([loadStatus(), loadProfiles(), loadJobs(), loadAttempts()]);
}

document.getElementById("refresh-all").addEventListener("click", () => void loadAll());

document.getElementById("run-once").addEventListener("click", async () => {
  try {
    const out = await request("/autopilot/run-once", { method: "POST" });
    log(out);
    await loadAll();
  } catch (e) {
    log(e.message);
  }
});

document.getElementById("autopilot-toggle").addEventListener("click", async (e) => {
  const btn = e.currentTarget;
  const running = btn.dataset.state === "running";
  try {
    const out = await request("/run-control", {
      method: "PATCH",
      body: JSON.stringify({ is_running: !running }),
    });
    log(out);
    await loadStatus();
  } catch (err) {
    log(err.message);
  }
});

document.getElementById("profile-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());
  try {
    const out = await request("/profiles", { method: "POST", body: JSON.stringify(data) });
    selectedProfileId = out.id;
    log(out);
    e.target.reset();
    await loadProfiles();
  } catch (err) {
    log(err.message);
  }
});

document.getElementById("job-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());
  data.external_id = null;
  try {
    const out = await request("/jobs", { method: "POST", body: JSON.stringify(data) });
    log(out);
    e.target.reset();
    await loadJobs();
    await loadStatus();
  } catch (err) {
    log(err.message);
  }
});

document.getElementById("question-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());
  try {
    const out = await request("/questions", { method: "POST", body: JSON.stringify(data) });
    log(out);
    e.target.reset();
  } catch (err) {
    log(err.message);
  }
});

document.getElementById("question-lookup-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const question_text = new FormData(e.target).get("lookup_question");
  try {
    const out = await request("/questions/lookup", {
      method: "POST",
      body: JSON.stringify({ question_text }),
    });
    document.getElementById("question-lookup-result").textContent = JSON.stringify(out, null, 2);
    log(out);
  } catch (err) {
    log(err.message);
  }
});

loadAll().catch((e) => log(e.message));
