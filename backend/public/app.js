const form = document.getElementById("upload-form");
const submitBtn = document.getElementById("submit-btn");
const submitBtnLabel = document.getElementById("submit-btn-label");
const submitSpinner = document.getElementById("submit-spinner");
const errorBox = document.getElementById("error");

const emptyState = document.getElementById("empty-state");
const resultBox = document.getElementById("match-result");

const fileInput = document.getElementById("resume-file");
const fileDrop = document.getElementById("file-drop");
const fileDropLabel = document.getElementById("file-drop-label");

const resultHeadingName = document.getElementById("result-heading-name");
const resultHeadingRole = document.getElementById("result-heading-role");
const recommendationBadge = document.getElementById("recommendation-badge");

const gaugeArc = document.getElementById("gauge-arc");
const gaugeValue = document.getElementById("gauge-value");
const equalizer = document.getElementById("equalizer");

const matchedSkillsList = document.getElementById("matched-skills");
const missingSkillsList = document.getElementById("missing-skills");
const aiSummary = document.getElementById("ai-summary");

const GAUGE_CIRCUMFERENCE = 251.2; // length of the semicircle path at r=80

fileDrop.addEventListener("click", () => {
  fileInput.click();
});

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  fileDropLabel.textContent = file ? file.name : "Choose PDF, DOCX or TXT…";
  fileDrop.classList.toggle("has-file", Boolean(file));
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const resumeFile = fileInput.files[0];
  const candidateName = document.getElementById("candidate-name").value.trim();
  const jobTitle = document.getElementById("job-title").value.trim();
  const jobDescription = document.getElementById("job-description").value.trim();
  const requiredExperienceYearsRaw = document.getElementById("required-experience").value;

  if (!resumeFile || !jobTitle || !jobDescription) return;

  setLoading(true);
  hideError();

  try {
    const data = await matchResume({
      resumeFile,
      candidateName,
      jobTitle,
      jobDescription,
      requiredExperienceYears: requiredExperienceYearsRaw
        ? Number(requiredExperienceYearsRaw)
        : undefined,
    });
    renderResult(data);
  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(false);
  }
});

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  submitBtnLabel.textContent = isLoading ? "Analyzing…" : "Run Match";
  submitSpinner.classList.toggle("hidden", !isLoading);
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function hideError() {
  errorBox.hidden = true;
  errorBox.textContent = "";
}

function bandFor(value) {
  if (value >= 75) return { key: "strong", color: "#2DD9C4" };
  if (value >= 50) return { key: "moderate", color: "#F5B342" };
  return { key: "weak", color: "#FB7185" };
}

function renderResult(result) {
  emptyState.hidden = true;
  resultBox.hidden = false;

  resultHeadingName.textContent = result.candidate_name || "Candidate";
  resultHeadingRole.textContent = `→ ${result.job_title}`;

  const band = bandFor(result.overall_match);
  recommendationBadge.textContent = result.recommendation;
  recommendationBadge.className = `badge ${band.key}`;

  // Gauge
  const offset = GAUGE_CIRCUMFERENCE * (1 - result.overall_match / 100);
  requestAnimationFrame(() => {
    gaugeArc.style.stroke = band.color;
    gaugeArc.setAttribute("stroke-dashoffset", String(offset));
  });
  animateNumber(gaugeValue, result.overall_match);

  // Equalizer bars for sub-scores
  equalizer.innerHTML = "";
  const rows = [
    { label: "Semantic similarity", value: result.semantic_similarity },
    { label: "Skills match", value: result.skills_match_pct },
    { label: "Experience match", value: result.experience_match_pct },
    { label: "Education match", value: result.education_match_pct },
  ];
  for (const row of rows) {
    equalizer.appendChild(buildEqRow(row.label, row.value));
  }

  renderSkillList(matchedSkillsList, result.matched_skills, "No overlapping skills found");
  renderSkillList(missingSkillsList, result.missing_skills, "Full coverage — nothing missing");

  aiSummary.textContent = result.ai_summary;

  resultBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function buildEqRow(label, value) {
  const row = document.createElement("div");
  row.className = "eq-row";

  const labelEl = document.createElement("span");
  labelEl.className = "eq-label";
  labelEl.textContent = label;

  const track = document.createElement("div");
  track.className = "eq-track";
  const fill = document.createElement("div");
  fill.className = "eq-fill";
  fill.style.width = "0%";
  fill.style.background = bandFor(value).color;
  track.appendChild(fill);

  const valueEl = document.createElement("span");
  valueEl.className = "eq-value";
  valueEl.textContent = `${value}%`;

  row.appendChild(labelEl);
  row.appendChild(track);
  row.appendChild(valueEl);

  requestAnimationFrame(() => {
    fill.style.width = `${Math.max(0, Math.min(100, value))}%`;
  });

  return row;
}

function renderSkillList(listEl, items, emptyText) {
  listEl.innerHTML = "";
  listEl.classList.toggle("empty", !items || items.length === 0);
  if (!items || items.length === 0) {
    const li = document.createElement("li");
    li.textContent = emptyText;
    listEl.appendChild(li);
    return;
  }
  for (const skill of items) {
    const li = document.createElement("li");
    li.textContent = skill;
    listEl.appendChild(li);
  }
}

function animateNumber(el, target) {
  const start = 0;
  const duration = 800;
  const startTime = performance.now();

  function tick(now) {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(start + (target - start) * eased);
    el.textContent = `${current}%`;
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}
