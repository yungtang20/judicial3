"use strict";

const form = document.querySelector("#auth-form");
const inviteWrap = document.querySelector("#invite-wrap");
const inviteInput = document.querySelector("#invite-code");
const toggle = document.querySelector("#toggle-mode");
const submit = document.querySelector("#submit");
const status = document.querySelector("#auth-status");
let registrationAvailable = false;
let registering = false;
let authProvider = "local";
let loginIdentifier = "username";
let mfaPending = false;

function showError(message) {
  status.textContent = message;
  status.classList.add("error");
}

async function loadStatus() {
  const response = await fetch("/api/auth/status", { cache: "no-store", credentials: "same-origin" });
  if (!response.ok) throw new Error("無法確認登入狀態。");
  const data = await response.json();
  if (!data.auth_required) {
    window.location.replace("/");
    return;
  }
  if (data.authenticated) {
    window.location.replace("/");
    return;
  }
  authProvider = data.auth_provider || "local";
  loginIdentifier = data.login_identifier || "username";
  if (authProvider === "supabase" && loginIdentifier === "email") {
    const username = document.querySelector("#username");
    document.querySelector("#username-label").textContent = "電子郵件";
    username.type = "email";
    username.name = "email";
    username.maxLength = 320;
    username.removeAttribute("pattern");
    username.setAttribute("autocomplete", "email");
    document.querySelector("#auth-warning").textContent = "僅限核准的唯一帳號；登入後必須完成 MFA。";
  } else if (authProvider === "supabase") {
    document.querySelector("#auth-warning").textContent = "僅限核准的唯一帳號。";
  }
  registrationAvailable = data.registration_available === true;
  toggle.hidden = !registrationAvailable;
}

toggle.addEventListener("click", () => {
  registering = !registering;
  inviteWrap.hidden = !registering;
  inviteInput.required = registering;
  document.querySelector("#password").setAttribute("autocomplete", registering ? "new-password" : "current-password");
  submit.textContent = registering ? "註冊並登入" : "登入";
  toggle.textContent = registering ? "返回登入" : "建立帳號";
  status.textContent = registering
    ? "限建立一個帳號；需要管理員提供的邀請碼，密碼至少 8 字元。"
    : "";
  status.classList.remove("error");
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  status.textContent = "處理中…";
  status.classList.remove("error");
  submit.disabled = true;
  const values = new FormData(form);
  const payload = authProvider === "supabase" && loginIdentifier === "email"
    ? { email: String(values.get("email") || ""), password: String(values.get("password") || "") }
    : { username: String(values.get("username") || ""), password: String(values.get("password") || "") };
  if (registering) payload.invite_code = String(values.get("invite_code") || "");
  try {
    const endpoint = mfaPending ? "/api/auth/mfa/verify" : registering ? "/api/auth/register" : "/api/auth/login";
    const requestPayload = mfaPending ? { code: String(values.get("mfa_code") || "") } : payload;
    const response = await fetch(endpoint, {
      method: "POST",
      credentials: "same-origin",
      cache: "no-store",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestPayload),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.message || "登入或註冊失敗。");
    if (result.mfa_required) {
      mfaPending = true;
      document.querySelector("#credential-fields").hidden = true;
      document.querySelector("#mfa-wrap").hidden = false;
      document.querySelector("#mfa-code").required = true;
      toggle.hidden = true;
      submit.textContent = "完成 MFA 並登入";
      const qr = document.querySelector("#mfa-qr");
      if (result.mfa_setup && typeof result.qr_code === "string" && result.qr_code.startsWith("data:image/")) {
        qr.src = result.qr_code;
        qr.hidden = false;
        document.querySelector("#mfa-instructions").textContent = "請先使用驗證器掃描 QR Code，再輸入動態驗證碼。";
      }
      status.textContent = "密碼驗證通過，尚須完成 MFA。";
    } else {
      window.location.replace("/");
    }
  } catch (error) {
    showError(error instanceof Error ? error.message : "登入或註冊失敗。");
  } finally {
    submit.disabled = false;
  }
});

loadStatus().catch((error) => showError(error.message));
