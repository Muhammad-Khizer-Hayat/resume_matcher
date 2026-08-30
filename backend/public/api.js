// Same-origin by default: the backend serves this frontend directly, so
// relative URLs "just work" whether you're on localhost or deployed.
// Override by setting window.API_URL in a <script> tag before this file
// loads, if you ever split the frontend onto a different host.
const API_URL = window.API_URL || "";

async function matchResume({
  resumeFile,
  jobTitle,
  jobDescription,
  candidateName,
  requiredExperienceYears,
}) {
  const formData = new FormData();
  formData.append("resume_file", resumeFile);
  formData.append("job_title", jobTitle);
  formData.append("job_description", jobDescription);
  if (candidateName) formData.append("candidate_name", candidateName);
  if (requiredExperienceYears) {
    formData.append("required_experience_years", requiredExperienceYears);
  }

  const res = await fetch(`${API_URL}/api/match`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    let detail = `Request failed with status ${res.status}`;
    try {
      const errBody = await res.json();
      detail = errBody.detail || detail;
    } catch (_) {
      // response wasn't JSON; keep default message
    }
    throw new Error(detail);
  }

  return res.json();
}
