const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const defaultData = {
  profile: {
    name: "Jessa",
    email: "jessa@example.com",
    department: "Computer Science",
    platform: "",
    notifications: true
  },
  meetings: [],
  invitations: [
    {
      id: crypto.randomUUID(),
      title: "Design Team Sync",
      organizer: "Maya",
      date: "2026-09-18",
      time: "16:00",
      platform: "Google Meet",
      status: "pending"
    },
    {
      id: crypto.randomUUID(),
      title: "Mini Project Discussion",
      organizer: "Rahul",
      date: "2026-09-20",
      time: "18:30",
      platform: "Microsoft Teams",
      status: "pending"
    }
  ],
  communities: [],
  recommendation: ""
};

function loadData() {
  const saved = localStorage.getItem("meetwise-data");
  if (!saved) {
    localStorage.setItem("meetwise-data", JSON.stringify(defaultData));
    return structuredClone(defaultData);
  }
  return JSON.parse(saved);
}

let data = loadData();
let inviteFilter = "pending";

function saveData() {
  localStorage.setItem("meetwise-data", JSON.stringify(data));
  renderAll();
}

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2300);
}

function navigate(pageId) {
  $$(".page").forEach(p => p.classList.toggle("active", p.id === pageId));
  $$(".nav-btn").forEach(b => b.classList.toggle("active", b.dataset.page === pageId));
  const label = $(`.nav-btn[data-page="${pageId}"] span`);
  $("#pageTitle").textContent = label ? label.textContent : "MeetWise";
  window.scrollTo({ top: 0, behavior: "smooth" });
}

$$(".nav-btn").forEach(btn => btn.addEventListener("click", () => navigate(btn.dataset.page)));
$$("[data-jump]").forEach(btn => btn.addEventListener("click", () => navigate(btn.dataset.jump)));

function formatDate(dateString) {
  if (!dateString) return "";
  return new Date(dateString + "T00:00:00").toLocaleDateString("en-IN", {
    day: "numeric", month: "short", year: "numeric"
  });
}

function upcomingMeetings() {
  const today = new Date();
  today.setHours(0,0,0,0);
  return data.meetings
    .filter(m => new Date(m.date + "T00:00:00") >= today)
    .sort((a,b) => (a.date + a.time).localeCompare(b.date + b.time));
}

function renderDashboard() {
  const upcoming = upcomingMeetings();
  $("#statMeetings").textContent = upcoming.length;
  $("#statInvites").textContent = data.invitations.filter(i => i.status === "pending").length;
  $("#statCommunities").textContent = data.communities.length;
  $("#statPlatform").textContent = data.profile.platform || data.recommendation || "—";

  const holder = $("#dashboardMeetings");
  if (!upcoming.length) {
    holder.className = "list-container empty-state";
    holder.textContent = "No upcoming meetings yet.";
  } else {
    holder.className = "list-container";
    holder.innerHTML = upcoming.slice(0,4).map(m => `
      <div class="mini-meeting">
        <div>
          <h4>${escapeHtml(m.title)}</h4>
          <p>${formatDate(m.date)} • ${m.time} • ${escapeHtml(m.platform)}</p>
        </div>
        <span class="badge">${escapeHtml(m.duration)}</span>
      </div>
    `).join("");
  }
}

function renderMeetings() {
  const holder = $("#meetingCards");
  const query = ($("#meetingSearch")?.value || "").toLowerCase();
  const filter = $("#meetingFilter")?.value || "all";
  const today = new Date(); today.setHours(0,0,0,0);

  let list = data.meetings.filter(m => m.title.toLowerCase().includes(query));
  if (filter === "upcoming") list = list.filter(m => new Date(m.date + "T00:00:00") >= today);
  if (filter === "completed") list = list.filter(m => new Date(m.date + "T00:00:00") < today);

  if (!list.length) {
    holder.innerHTML = `<div class="panel empty-state" style="grid-column:1/-1;min-height:190px;">No meetings found. Create your first meeting!</div>`;
    return;
  }

  holder.innerHTML = list
    .sort((a,b) => (a.date+a.time).localeCompare(b.date+b.time))
    .map(m => `
      <article class="meeting-card">
        <span class="badge">${new Date(m.date + "T00:00:00") >= today ? "Upcoming" : "Completed"}</span>
        <h3>${escapeHtml(m.title)}</h3>
        <p class="muted">${escapeHtml(m.description || "No description provided.")}</p>
        <div class="meta">
          <span>📅 ${formatDate(m.date)} at ${m.time}</span>
          <span>⏱ ${escapeHtml(m.duration)}</span>
          <span>💻 ${escapeHtml(m.platform)}</span>
          <span>👥 ${escapeHtml(m.participants || "No participants added")}</span>
        </div>
        <div class="card-actions">
          <button class="secondary-btn" onclick="editMeeting('${m.id}')">Edit</button>
          <button class="danger-btn" onclick="deleteMeeting('${m.id}')">Delete</button>
        </div>
      </article>
    `).join("");
}

function renderInvitations() {
  const holder = $("#invitationList");
  const items = data.invitations.filter(i => i.status === inviteFilter);
  if (!items.length) {
    holder.innerHTML = `<div class="panel empty-state" style="min-height:190px;">No ${inviteFilter} invitations.</div>`;
    return;
  }
  holder.innerHTML = items.map(i => `
    <article class="invite-card">
      <div>
        <span class="badge ${i.status === "accepted" ? "success" : i.status === "declined" ? "danger" : ""}">
          ${i.status}
        </span>
        <h3>${escapeHtml(i.title)}</h3>
        <p class="muted">Hosted by ${escapeHtml(i.organizer)} • ${formatDate(i.date)} at ${i.time} • ${escapeHtml(i.platform)}</p>
      </div>
      ${i.status === "pending" ? `
        <div class="card-actions">
          <button class="primary-btn" onclick="respondInvite('${i.id}','accepted')">Accept</button>
          <button class="danger-btn" onclick="respondInvite('${i.id}','declined')">Decline</button>
        </div>` : ""}
    </article>
  `).join("");
}

function renderCommunities() {
  const holder = $("#communityCards");
  if (!data.communities.length) {
    holder.innerHTML = `<div class="panel empty-state" style="grid-column:1/-1;min-height:190px;">You haven't joined any communities yet.</div>`;
    return;
  }

  holder.innerHTML = data.communities.map(c => `
    <article class="community-card">
      <span class="badge">Community</span>
      <h3>${escapeHtml(c.name)}</h3>
      <p class="muted">${escapeHtml(c.description || "A MeetWise community.")}</p>
      <div class="meta">
        <span>👥 ${c.members || 1} member${(c.members || 1) === 1 ? "" : "s"}</span>
        <span>🎉 ${escapeHtml(c.event || "No upcoming event")}</span>
      </div>
      <button class="danger-btn" onclick="leaveCommunity('${c.id}')">Leave</button>
    </article>
  `).join("");
}

function renderProfile() {
  const p = data.profile;
  const initial = (p.name || "U").trim().charAt(0).toUpperCase();
  $("#headerAvatar").textContent = initial;
  $("#profileAvatar").textContent = initial;
  $("#profileDisplayName").textContent = p.name || "User";
  $("#profileMeetingCount").textContent = data.meetings.length;
  $("#profileCommunityCount").textContent = data.communities.length;

  const form = $("#profileForm");
  form.elements.name.value = p.name || "";
  form.elements.email.value = p.email || "";
  form.elements.department.value = p.department || "";
  form.elements.platform.value = p.platform || "";
  form.elements.notifications.checked = !!p.notifications;
}

function renderAll() {
  renderDashboard();
  renderMeetings();
  renderInvitations();
  renderCommunities();
  renderProfile();
}

function escapeHtml(value = "") {
  return String(value).replace(/[&<>"']/g, ch => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  }[ch]));
}

// Meeting modal
$("#openMeetingModal").addEventListener("click", () => {
  $("#meetingForm").reset();
  $("#meetingForm").elements.id.value = "";
  $("#meetingModalTitle").textContent = "Create meeting";
  $("#meetingModal").classList.add("open");
});

$("#meetingForm").addEventListener("submit", e => {
  e.preventDefault();
  const values = Object.fromEntries(new FormData(e.target).entries());
  if (values.id) {
    const index = data.meetings.findIndex(m => m.id === values.id);
    if (index >= 0) data.meetings[index] = { ...data.meetings[index], ...values };
    showToast("Meeting updated.");
  } else {
    data.meetings.push({ ...values, id: crypto.randomUUID() });
    showToast("Meeting created.");
  }
  $("#meetingModal").classList.remove("open");
  saveData();
});

window.editMeeting = function(id) {
  const m = data.meetings.find(m => m.id === id);
  if (!m) return;
  const f = $("#meetingForm");
  Object.keys(m).forEach(key => {
    if (f.elements[key]) f.elements[key].value = m[key];
  });
  $("#meetingModalTitle").textContent = "Edit meeting";
  $("#meetingModal").classList.add("open");
}

window.deleteMeeting = function(id) {
  if (!confirm("Delete this meeting?")) return;
  data.meetings = data.meetings.filter(m => m.id !== id);
  saveData();
  showToast("Meeting deleted.");
}

$("#meetingSearch").addEventListener("input", renderMeetings);
$("#meetingFilter").addEventListener("change", renderMeetings);

// Invitation tabs
$$("[data-invite-filter]").forEach(tab => tab.addEventListener("click", () => {
  inviteFilter = tab.dataset.inviteFilter;
  $$("[data-invite-filter]").forEach(t => t.classList.toggle("active", t === tab));
  renderInvitations();
}));

window.respondInvite = function(id, status) {
  const invite = data.invitations.find(i => i.id === id);
  if (invite) invite.status = status;
  saveData();
  showToast(status === "accepted" ? "Invitation accepted!" : "Invitation declined.");
}

// Platform recommendation
$("#platformForm").addEventListener("submit", e => {
  e.preventDefault();
  const f = Object.fromEntries(new FormData(e.target).entries());
  const scores = { "Google Meet": 0, "Zoom": 0, "Microsoft Teams": 0 };

  if (f.participants === "small") scores["Google Meet"] += 3;
  if (f.participants === "medium") { scores["Zoom"] += 2; scores["Microsoft Teams"] += 2; }
  if (f.participants === "large") scores["Zoom"] += 4;

  if (f.purpose === "casual") scores["Google Meet"] += 3;
  if (f.purpose === "presentation") scores["Zoom"] += 3;
  if (f.purpose === "professional") scores["Microsoft Teams"] += 3;

  if (f.feature === "easy") scores["Google Meet"] += 3;
  if (f.feature === "recording") scores["Zoom"] += 3;
  if (f.feature === "collaboration") scores["Microsoft Teams"] += 4;

  if (f.duration === "short") scores["Google Meet"] += 2;
  if (f.duration === "medium") scores["Zoom"] += 1;
  if (f.duration === "long") scores["Microsoft Teams"] += 2;

  const winner = Object.entries(scores).sort((a,b) => b[1]-a[1])[0][0];
  const emoji = winner === "Google Meet" ? "🟢" : winner === "Zoom" ? "🔵" : "🟣";
  const max = Math.max(...Object.values(scores), 1);

  data.recommendation = winner;
  $("#recommendationResult").innerHTML = `
    <div class="platform-logo">${emoji}</div>
    <p class="eyebrow">Recommended platform</p>
    <h2>${winner}</h2>
    <p class="muted">This platform best matches the meeting style you selected.</p>
    <div class="score-row">
      ${Object.entries(scores).map(([name,score]) => `
        <div><strong>${name}</strong> <span class="muted">${score} pts</span></div>
        <div class="score-track"><div class="score-fill" style="width:${Math.round(score/max*100)}%"></div></div>
      `).join("")}
    </div>
    <button id="savePreference" class="primary-btn">Save as preference</button>
  `;
  $("#savePreference").addEventListener("click", () => {
    data.profile.platform = winner;
    saveData();
    showToast(`${winner} saved as your preference.`);
  });
  saveData();
});

// Community
$("#openCommunityModal").addEventListener("click", () => $("#communityModal").classList.add("open"));
$("#communityForm").addEventListener("submit", e => {
  e.preventDefault();
  const values = Object.fromEntries(new FormData(e.target).entries());
  data.communities.push({ ...values, id: crypto.randomUUID(), members: 1 });
  $("#communityModal").classList.remove("open");
  e.target.reset();
  saveData();
  showToast("Community created.");
});

$("#joinSuggested").addEventListener("click", () => {
  if (!data.communities.some(c => c.name === "Study Circle")) {
    data.communities.push({
      id: crypto.randomUUID(),
      name: "Study Circle",
      description: "A space for frequent classmates to plan study meetings and stay connected.",
      event: "Weekly study session",
      members: 6
    });
    saveData();
    showToast("Joined Study Circle!");
  } else {
    showToast("You're already in Study Circle.");
  }
});

window.leaveCommunity = function(id) {
  data.communities = data.communities.filter(c => c.id !== id);
  saveData();
  showToast("Left community.");
}

// Profile
$("#profileForm").addEventListener("submit", e => {
  e.preventDefault();
  const form = e.target;
  data.profile = {
    name: form.elements.name.value,
    email: form.elements.email.value,
    department: form.elements.department.value,
    platform: form.elements.platform.value,
    notifications: form.elements.notifications.checked
  };
  saveData();
  showToast("Profile saved.");
});

// Modals
$$("[data-close]").forEach(btn => btn.addEventListener("click", () => {
  $("#" + btn.dataset.close).classList.remove("open");
}));
$$(".modal-backdrop").forEach(backdrop => backdrop.addEventListener("click", e => {
  if (e.target === backdrop) backdrop.classList.remove("open");
}));

// Theme
const savedTheme = localStorage.getItem("meetwise-theme") || "light";
if (savedTheme === "dark") document.body.classList.add("dark");

function updateThemeText() {
  $("#themeToggle").textContent = document.body.classList.contains("dark") ? "☀️ Light Mode" : "🌙 Dark Mode";
}
updateThemeText();

$("#themeToggle").addEventListener("click", () => {
  document.body.classList.toggle("dark");
  localStorage.setItem("meetwise-theme", document.body.classList.contains("dark") ? "dark" : "light");
  updateThemeText();
});

$("#notificationBtn").addEventListener("click", () => {
  const pending = data.invitations.filter(i => i.status === "pending").length;
  showToast(pending ? `You have ${pending} pending invitation${pending > 1 ? "s" : ""}.` : "No new notifications.");
});

renderAll();