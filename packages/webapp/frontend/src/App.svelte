<script>
  import "./app.css";
  import { getPracticeAudioUrl } from "./lib/api/audio";
  import { deleteAccount, fetchCurrentUser, login, logout as logoutRequest, readJson, register } from "./lib/api/auth";
  import { getPracticeProgress, getPracticeQueue, submitPracticeAnswer } from "./lib/api/practice";
  import { getSettings, updateSettings } from "./lib/api/settings";
  import { authError, authMessage, authState, currentUser, resetAuthStore, setAnonymous, setAuthenticated, setAuthFailure } from "./lib/stores/auth";
  import { currentMode, currentSection, goToDashboard, resetPracticeNavigation, setCurrentSection, setPracticeMode } from "./lib/stores/practice";
  import { applySettingsPayload, resetSettingsStore, settingsLoadedForUser, theme, ttsSpeed } from "./lib/stores/settings";

  // ── helpers ─────────────────────────────────────────────────────────────
  const langLabel = (l) => ({ mirad: "Mirad", english: "English", practice: "" }[String(l ?? "").trim().toLowerCase()] ?? "");
  const promptTag = (c) => langLabel(c?.prompt_language);
  const answerTag = (c) => langLabel(c?.answer_language);
  const inputLabel = (c) => `Your ${langLabel(c?.answer_language)} answer`;
  const isEnMir = (c) => c?.prompt_language === "english" && c?.answer_language === "mirad";
  const fmtPct = (v) => (typeof v === "number" ? `${Math.round(v * 100)}%` : "—");
  const fmtN = (v) => (typeof v === "number" ? v : "—");
  const spd = (s) => `${Number(s).toFixed(1)}×`;
  const effSpd = () => { const n = Number($ttsSpeed); return Number.isFinite(n) ? n : 0.8; };
  const icKey = (c) => `${c?.audio_card_id ?? c?.base_card_id ?? c?.id ?? "x"}:${String(c?.prompt ?? "").trim().toLowerCase()}`;
  const icGlyph = (c) => (c?.type === "phrase" ? "❐" : "◌");
  const stopwords = new Set(["the","a","an","to","of","and","for","in","on","at","my","your","is","it","be","or","not","you","i","he","she","we","they","what","which","who","this","that"]);
  const allowedColls = new Set(["mdi","ph","tabler","solar","lucide","healthicons","fluent-emoji-flat"]);
  const IC_PAT = /^[a-z0-9-]+:[a-z0-9-]+$/;
  const IC_TMO = 2500;
  const IC_LIM = 6;
  const iconCache = new Map();

  function icKw(card) {
    return `${card?.prompt ?? ""} ${card?.type ?? ""}`.toLowerCase()
      .split(/[^a-z0-9]+/).filter(Boolean).filter(t => !stopwords.has(t) && t.length > 1).slice(0, 3);
  }
  function icOk(name) {
    if (!IC_PAT.test(name)) return false;
    const [c,i] = name.split(":");
    return allowedColls.has(c) && Boolean(i);
  }
  function icUrl(name) {
    const [c,i] = name.split(":");
    return `https://api.iconify.design/${encodeURIComponent(c)}/${encodeURIComponent(i)}.svg?color=%231d4ed8`;
  }
  function applyIc(s) {
    icStatus = s.status; icErr = s.error ?? "";
    icImg = s.img ?? ""; icAlt = s.alt ?? "";
    icGlyphV = s.glyph ?? icGlyph(currentCard);
    icMeta = s.meta ?? null; icLk = s.lk ?? "";
  }
  function icErrS(c, lk, r, d="") {
    return { status:"error", error:r, diagnostic:d, img:"", alt:"", glyph:icGlyph(c), lk, meta:{r, lk, p:c?.prompt??""} };
  }
  function icFallS(c, lk, r, d="") {
    return { status:"fallback", error:"", diagnostic:d, img:"", alt:"", glyph:icGlyph(c), lk, meta:{r, lk, p:c?.prompt??""} };
  }

  async function loadIc(card) {
    if (!card) { icStatus="idle"; return; }
    const lk = icKey(card);
    if (icLk === lk && icStatus !== "idle") return;
    const kws = icKw(card);
    applyIc({ status:"loading", error:"", img:"", alt:"", glyph:icGlyph(card), lk, meta:{lk, p:card.prompt??"", kws} });
    if (!kws.length) {
      const s = icFallS(card, lk, "no keywords");
      iconCache.set(lk, s);
      applyIc(s); return;
    }
    const ctrl = new AbortController();
    const to = setTimeout(() => ctrl.abort(), IC_TMO);
    try {
      const q = encodeURIComponent(kws.join(" "));
      const r = await fetch(`https://api.iconify.design/search?query=${q}&limit=${IC_LIM}`, { headers:{"Accept":"application/json"}, signal:ctrl.signal });
      const p = await readJson(r);
      const icons = Array.isArray(p?.icons) ? p.icons : [];
      const match = icons.find(icOk);
      let s;
      if (!r.ok) s = icErrS(card, lk, "api error", `status=${r.status}`);
      else if (!Array.isArray(p?.icons)) s = icFallS(card, lk, "no icons array");
      else if (!match) s = icFallS(card, lk, "no match", `found=${icons.length}`);
      else s = { status:"matched", error:"", diagnostic:`${match}`, img:icUrl(match), alt:`${card.prompt} icon`, glyph:icGlyph(card), lk, meta:{lk, m:match, kws, p:card.prompt??""} };
      iconCache.set(lk, s);
      if (icKey(currentCard) === lk) applyIc(s);
    } catch(e) {
      const s = e?.name==="AbortError" ? icErrS(card, lk, "timeout", "AbortError") : icErrS(card, lk, "request failed", e?.message??"");
      iconCache.set(lk, s);
      if (icKey(currentCard) === lk) applyIc(s);
    } finally { clearTimeout(to); }
  }

  // ── state ───────────────────────────────────────────────────────────────
  let username = $state("admin"), password = $state(""), regU = $state(""), regP = $state("");
  let submitting = $state(false);

  let practiceState = $state("idle"), practiceErr = $state(""), practiceQueue = $state(null);
  let practiceQueueCards = $state([]), practiceQueueIndex = $state(0), practiceQueueMode = $state(null);
  let currentCard = $state(null), answerSubmitting = $state(false), typedAnswer = $state(""), answerErr = $state("");
  let answerResult = $state(null), miradAudioUnlocked = $state(false), activeCardId = $state(null);

  let icStatus = $state("idle"), icErr = $state(""), icImg = $state(""), icAlt = $state(""), icGlyphV = $state("◌"), icMeta = $state(null), icLk = $state("");

  let audioState = $state("idle"), audioMsg = $state(""), audioBlobUrl = $state(""), activeAudio = $state(null), lastAudioCardId = $state(null);

  let analyticsState = $state("idle"), analyticsErr = $state(""), analyticsPayload = $state(null);

  let settingsState = $state("idle"), settingsErr = $state(""), settingsStatus = $state(""), settingsPhase = $state("");

  let deleteAccountState = $state("idle"), deleteAccountErr = $state(""), deleteAccountStatus = $state("");
  let deleteAccountConfirm = $state(""), deleteAccountUsername = $state("");

  // ── resets ───────────────────────────────────────────────────────────────
  const resetAudio = () => {
    if (activeAudio) { activeAudio.pause(); activeAudio = null; }
    if (audioBlobUrl) { URL.revokeObjectURL(audioBlobUrl); audioBlobUrl = ""; }
    audioState="idle"; audioMsg="";
  };
  const resetAnswer = () => {
    typedAnswer=""; answerErr=""; answerResult=null; miradAudioUnlocked=false;
  };
  const resetIcon = () => { icStatus="idle"; icErr=""; icImg=""; icAlt=""; icGlyphV="◌"; icLk=""; };
  const resetPracticeSurface = () => {
    resetAudio(); resetAnswer(); resetIcon();
    practiceState="idle"; practiceErr=""; practiceQueue=null;
    practiceQueueCards=[]; practiceQueueIndex=0; practiceQueueMode=null;
    currentCard=null; activeCardId=null; lastAudioCardId=null;
  };
  const resetAnalyticsSurface = () => { analyticsState="idle"; analyticsErr=""; analyticsPayload=null; };
  const resetSettingsSurface = () => {
    settingsState="idle"; settingsErr=""; settingsStatus=""; settingsPhase="";
    resetSettingsStore();
    deleteAccountState="idle"; deleteAccountErr=""; deleteAccountStatus=""; deleteAccountUsername=""; deleteAccountConfirm="";
  };
  const clearAuthMsgs = () => { authError.set(""); authMessage.set(""); };

  // ── settings helpers ─────────────────────────────────────────────────────
  const coerceTheme = (t) => (["light","dark"].includes(t) ? t : "system");
  const coerceSpeed = (s) => { const n = parseFloat(s); return isFinite(n) && n >= 0.5 && n <= 2.0 ? n : 0.8; };
  const syncSettings = (p, extra={}) => {
    applySettingsPayload(p ?? {});
    if (extra.state) settingsState = extra.state;
    if (extra.phase) settingsPhase = extra.phase;
    if (extra.msg) settingsStatus = extra.msg;
  };
  function applyTheme(theme) {
    if (typeof document === "undefined") return;
    document.documentElement.setAttribute("data-theme", coerceTheme(theme));
  }

  // ── auth ─────────────────────────────────────────────────────────────────
  async function loadCurrentUser() {
    authError.set("");
    try {
      const { response: r, payload: p } = await fetchCurrentUser();
      if (r.ok && p.authenticated && p.user) {
        setAuthenticated(p.user); goToDashboard();
        resetPracticeSurface(); resetAnalyticsSurface(); resetSettingsSurface();
        deleteAccountUsername=p.user?.username ?? "";
        await loadSettings({force:true});
        preloadPracticeQueue("mixed");
        return;
      }
      setAnonymous();
      resetSettingsSurface();
    } catch(_) { setAnonymous(); resetSettingsSurface(); authError.set("Could not reach MiraLingo auth."); }
  }

  async function submitLogin() {
    submitting=true;
    authError.set(""); authMessage.set("");
    try {
      const { response: r, payload: p } = await login(username, password);
      if (!r.ok || !p.authenticated || !p.user) { setAuthFailure("login-failed", p?.detail ?? "Login failed."); submitting=false; return; }
      setAuthenticated(p.user); password=""; goToDashboard();
      resetPracticeSurface(); resetAnalyticsSurface(); resetSettingsSurface();
      deleteAccountUsername=p.user?.username ?? "";
      await loadSettings({force:true});
      preloadPracticeQueue("mixed");
    } catch(_) { setAuthFailure("login-failed", "Could not reach MiraLingo auth."); }
    finally { submitting=false; }
  }

  async function submitRegistration() {
    submitting=true;
    authError.set(""); authMessage.set("");
    try {
      const { response: r, payload: p } = await register(regU, regP);
      if (!r.ok || !p.authenticated || !p.user) { setAuthFailure("registration-failed", p?.detail ?? "Registration failed."); submitting=false; return; }
      setAuthenticated(p.user); regP=""; goToDashboard();
      resetPracticeSurface(); resetAnalyticsSurface(); resetSettingsSurface();
      deleteAccountUsername=p.user?.username ?? "";
      await loadSettings({force:true});
      preloadPracticeQueue("mixed");
    } catch(_) { setAuthFailure("registration-failed", "Could not reach MiraLingo registration."); }
    finally { submitting=false; }
  }

  function clearAuthAppState(msg="") {
    resetPracticeSurface(); resetAnalyticsSurface(); resetSettingsSurface();
    username="admin"; password=""; regU=""; regP="";
    resetPracticeNavigation();
    resetAuthStore(msg);
  }

  async function logout() {
    clearAuthMsgs();
    try { await logoutRequest(); }
    finally { resetPracticeSurface(); resetSettingsSurface(); clearAuthAppState(); }
  }

  // ── settings ─────────────────────────────────────────────────────────────
  async function loadSettings({force=false}={}) {
    if (settingsState==="loading"||settingsState==="saving") return;
    if (!force && $settingsLoadedForUser===$currentUser?.username && settingsState!=="idle") return;
    settingsState="loading"; settingsErr=""; settingsStatus="";
    try {
      const { response: r, payload: p } = await getSettings();
      if (!r.ok || p.ok===false) { settingsState="error"; settingsPhase=p?.phase??"settings_get"; settingsErr=p?.detail??"Could not reach saved settings."; return; }
      syncSettings(p.settings, {state:"ready",phase:p.phase??"settings_get"});
      settingsLoadedForUser.set($currentUser?.username ?? null);
    } catch(_) {
      settingsLoadedForUser.set($currentUser?.username ?? null);
      applySettingsPayload({});
      settingsState="error"; settingsPhase="settings_get"; settingsErr="Could not reach saved settings.";
    }
  }

  async function saveSettings() {
    if (settingsState==="saving") return;
    settingsState="saving"; settingsPhase="settings_update"; settingsErr=""; settingsStatus="Saving…";
    const body = { theme: coerceTheme($theme), tts_speed: coerceSpeed($ttsSpeed) };
    try {
      const { response: r, payload: p } = await updateSettings(body);
      if (!r.ok || p.ok===false) { settingsState="error"; settingsPhase=p?.phase??"settings_update"; settingsErr=p?.detail??"Could not save."; settingsStatus=""; return; }
      syncSettings(p.settings, {state:"ready",phase:p.phase??"settings_update",msg:"Saved."});
      settingsLoadedForUser.set($currentUser?.username ?? $settingsLoadedForUser);
    } catch(_) { settingsState="error"; settingsPhase="settings_update"; settingsErr="Could not save settings."; settingsStatus=""; }
  }

  // ── practice queue ────────────────────────────────────────────────────────
  async function loadPracticeQueue(mode="mixed") {
    const silent = arguments[1]?.silent === true;
    resetAudio(); resetAnswer();
    if (!silent) practiceState="loading";
    practiceErr="";
    const LIMIT = 50;
    try {
      const { response: r, payload: p } = await getPracticeQueue(mode, LIMIT);
      if (!r.ok || p.ok===false) {
        practiceQueue=p; practiceQueueCards=[]; practiceQueueIndex=0; practiceQueueMode=null;
        currentCard=null; activeCardId=null; lastAudioCardId=null; resetAnswer();
        practiceState="error"; practiceErr=p?.detail??"Queue unavailable."; return;
      }
      practiceQueue=p;
      practiceQueueCards=Array.isArray(p.cards) ? p.cards : [];
      practiceQueueIndex=0; practiceQueueMode=mode; currentMode.set(mode);
      currentCard=practiceQueueCards[0] ?? null;
      practiceState=currentCard ? "ready" : "empty";
    } catch(_) {
      practiceState="error"; practiceQueue=null; practiceQueueCards=[]; practiceQueueIndex=0;
      currentCard=null; activeCardId=null; lastAudioCardId=null; resetAnswer();
      practiceErr="Could not reach practice.";
    }
  }

  async function preloadPracticeQueue(mode="mixed") {
    if ((practiceQueueCards.length && practiceQueueMode===mode) || practiceState==="loading") return;
    await loadPracticeQueue(mode, {silent:true});
  }

  async function openPracticeMode(mode) {
    setPracticeMode(mode);
    resetAnalyticsSurface();
    if (practiceQueueCards.length && practiceQueueMode===mode) {
      resetAudio(); resetAnswer();
      currentCard = practiceQueueCards[practiceQueueIndex] ?? practiceQueueCards[0] ?? null;
      practiceState = currentCard ? "ready" : "empty";
      return;
    }
    resetPracticeSurface();
    await loadPracticeQueue(mode);
  }

  async function advancePracticeCard() {
    if (practiceState==="loading" || answerSubmitting) return;
    resetAnswer(); // clears answerResult + miradAudioUnlocked so TTS gating resets per card
    const next = practiceQueueIndex + 1;
    if (next < practiceQueueCards.length) {
      practiceQueueIndex = next;
      currentCard = practiceQueueCards[next];
      resetAudio(); return;
    }
    await loadPracticeQueue(practiceQueueMode ?? "mixed");
  }

  async function recordAnswer(body) {
    if (!currentCard || answerSubmitting) return;
    answerSubmitting=true; practiceErr=""; answerErr="";
    try {
      const { response: r, payload: p } = await submitPracticeAnswer(body);
      if (!r.ok || p.ok===false) { practiceState="ready"; practiceErr=p?.detail??"Answer rejected."; return; }
      answerResult = { ...p, expected_answer: p.expected_answer ?? currentCard.answer, submitted_answer: p.submitted_answer ?? body.answer ?? "" };
      miradAudioUnlocked = true;
    } catch(_) { practiceState="ready"; practiceErr="Could not submit."; }
    finally { answerSubmitting=false; }
  }

  async function submitAnswer() {
    const norm = typedAnswer.trim(); answerErr=""; practiceErr="";
    if (!norm) { answerErr="Type an answer first."; return; }
    await recordAnswer({card_id:currentCard.id, answer:norm});
  }

  async function submitGiveUp() { answerErr=""; practiceErr=""; await recordAnswer({card_id:currentCard.id, correct:false}); }

  // ── audio ─────────────────────────────────────────────────────────────────
  async function playCardAudio() {
    if (!currentCard || audioState==="loading") return;
    if (!canPlayAudio()) { audioState="idle"; audioMsg="Reveal answer first."; return; }
    audioState="loading"; audioMsg="Preparing…";
    const playbackRate = effSpd();
    try {
      const cid = currentCard.audio_card_id ?? currentCard.base_card_id ?? currentCard.id;
      const r = await fetch(getPracticeAudioUrl(cid), {headers:{"Accept":"audio/wav,application/json"}});
      const ct = r.headers.get("content-type") ?? "";
      if (!r.ok || ct.includes("application/json")) {
        const p = await readJson(r);
        audioState = r.status===401 ? "error" : "unavailable";
        audioMsg = r.status===401 ? "Session expired." : (p?.error==="mbrola_unavailable" ? "Audio unavailable on this server." : "Audio unavailable.");
        return;
      }
      const blob = await r.blob();
      if (audioBlobUrl) URL.revokeObjectURL(audioBlobUrl);
      const url = URL.createObjectURL(blob);
      audioBlobUrl=url; activeAudio=new Audio(url);
      try { activeAudio.playbackRate=playbackRate; } catch(_) {}
      activeAudio.addEventListener("ended", () => { audioState="idle"; audioMsg=""; });
      await activeAudio.play();
      audioState="playing"; audioMsg="";
    } catch(_) { audioState="error"; audioMsg="Could not play audio."; }
  }

  function canPlayAudio() {
    return Boolean(currentCard) && (!isEnMir(currentCard) || miradAudioUnlocked);
  }

  // ── analytics ─────────────────────────────────────────────────────────────
  async function loadAnalytics() {
    analyticsState="loading"; analyticsErr="";
    try {
      const { response: r, payload: p } = await getPracticeProgress();
      if (!r.ok || p.ok===false) { analyticsPayload=p; analyticsState="error"; analyticsErr=p?.detail??"Analytics unavailable."; return; }
      analyticsPayload=p; analyticsState="ready";
    } catch(_) { analyticsPayload=null; analyticsState="error"; analyticsErr="Could not reach analytics."; }
  }

  // ── account deletion ───────────────────────────────────────────────────────
  async function submitDeleteAccount() {
    if (deleteAccountState==="submitting" || !$currentUser?.username || !canDeleteAccount()) return;
    deleteAccountState="submitting"; deleteAccountErr=""; deleteAccountStatus="Deleting…";
    try {
      const { response: r, payload: p } = await deleteAccount(deleteAccountUsername, deleteAccountConfirm);
      if (!r.ok || p.ok===false) { deleteAccountState="error"; deleteAccountErr=p?.detail??"Could not delete."; deleteAccountStatus=""; return; }
      deleteAccountState="done"; deleteAccountStatus="Account deleted."; deleteAccountErr="";
      clearAuthAppState("Account deleted. Create a new account or log in again.");
    } catch(_) { deleteAccountState="error"; deleteAccountErr="Could not reach account deletion."; deleteAccountStatus=""; }
  }

  const canDeleteAccount = () => ($currentUser?.username ?? "") !== "admin";
  const deleteConfirmPhrase = () => `${$currentUser?.username ?? ""} DELETE`.trim();
  const canSubmitDelete = () =>
    canDeleteAccount() &&
    deleteAccountUsername.trim()===($currentUser?.username ?? "") &&
    deleteAccountConfirm.trim()===deleteConfirmPhrase() &&
    deleteAccountState!=="submitting";

  // ── navigation helpers ────────────────────────────────────────────────────
  function goToMenu() { goToDashboard(); resetPracticeSurface(); }
  function activateItem(item) {
    if (item.action==="logout") { logout(); return; }
    if (item.section==="analytics") { setCurrentSection("analytics"); resetAudio(); resetAnswer(); loadAnalytics(); return; }
    if (item.section==="settings") { setCurrentSection("settings"); resetAudio(); resetAnswer(); deleteAccountUsername=$currentUser?.username ?? deleteAccountUsername; loadSettings(); return; }
    if (item.mode) openPracticeMode(item.mode);
  }

  // ── reactive ──────────────────────────────────────────────────────────────
  $effect(() => { if (currentCard?.id !== activeCardId) { activeCardId=currentCard?.id ?? null; resetAnswer(); } });
  $effect(() => { const id = currentCard?.audio_card_id ?? currentCard?.base_card_id ?? currentCard?.id ?? null; if (id !== lastAudioCardId) { resetAudio(); lastAudioCardId=id; } });
  $effect(() => { if (currentCard?.id) loadIc(currentCard); else resetIcon(); });
  $effect(() => { applyTheme($theme); });
  const getPracticeTitle = () =>
    $currentSection === "revision" ? "Revision" :
    $currentSection === "build_vocabulary" ? "Vocabulary" : "Practice";

  loadCurrentUser();
</script>

<svelte:head>
  <title>MiraLingo</title>
  <meta name="description" content="Practice Mirad." />
</svelte:head>

<!-- ══════════════════════════════════════════════════════════════════════
     PRACTICE — full-screen focused card
     ══════════════════════════════════════════════════════════════════════ -->
{#if $authState === "authenticated" && ($currentSection === "practice" || $currentSection === "revision" || $currentSection === "build_vocabulary")}
<main class="shell shell--practice">
  <!-- top bar -->
  <nav class="topbar">
    <button class="btn btn--ghost btn--sm" on:click={goToMenu}>&#x2190; Menu</button>
    <span class="topbar-title">{getPracticeTitle()}</span>
    <button class="btn btn--ghost btn--sm" on:click={advancePracticeCard} disabled={practiceState==="loading"||answerSubmitting}>&#x27a4;</button>
  </nav>

  <!-- centered card -->
  <div class="card-center">
    {#if practiceState === "loading"}
      <div class="center-msg">Loading…</div>
    {:else if practiceState === "empty"}
      <div class="center-msg">No cards. Import content first.</div>
    {:else if practiceState === "error"}
      <div class="center-msg center-msg--err">{practiceErr}</div>
    {:else if currentCard}
      <article class="pcard" aria-label="Practice card">

        <!-- visible Mirad text (prompt for Mir→En; answer for En→Mir after reveal) -->
        <div class="pcard-row">
          <div class="pcard-texts">
            <span class="pcard-lang">{isEnMir(currentCard) ? promptTag(currentCard) + " prompt" : answerTag(currentCard) + " answer"}</span>
            <span class="pcard-main">
              {isEnMir(currentCard) ? currentCard.prompt : (answerResult?.expected_answer ?? currentCard.answer)}
            </span>
          </div>
          <!-- Mirad text is either: prompt (Mir→En) or answer (En→Mir after reveal) -->
          {#if !isEnMir(currentCard) || miradAudioUnlocked}
            <button class="btn-tts" type="button" aria-label="Hear Mirad" disabled={audioState==="loading"} on:click={playCardAudio}>
              🔊
            </button>
          {/if}
        </div>

        <!-- icon (only shown when matched; hidden when using glyph) -->
        {#if icStatus === "matched" && icImg}
          <div class="pcard-icon-row">
            <div class="pcard-icon-frame">
              <img src={icImg} alt={icAlt} class="pcard-icon-img" />
            </div>
          </div>
        {/if}

        <!-- input form (hidden after answer revealed) -->
        {#if !answerResult}
          <form class="pcard-form" on:submit|preventDefault={submitAnswer}>
            <input
              id="typed-answer-input"
              class="pcard-input"
              aria-label={inputLabel(currentCard)}
              autocomplete="off"
              placeholder={inputLabel(currentCard)}
              bind:value={typedAnswer}
              disabled={answerSubmitting}
            />
            {#if answerErr}<p class="err-msg" role="alert">{answerErr}</p>{/if}
            {#if practiceErr}<p class="err-msg" role="alert">{practiceErr}</p>{/if}
            <div class="pcard-actions">
              <button class="btn btn--primary" type="submit" disabled={answerSubmitting || !typedAnswer.trim()}>
                {answerSubmitting ? "…" : "Submit"}
              </button>
              <button class="btn btn--ghost" type="button" disabled={answerSubmitting} on:click={submitGiveUp}>
                Skip
              </button>
            </div>
          </form>
        {/if}

        <!-- answer result -->
        {#if answerResult}
          <!-- Mirad answer for En→Mir cards (always revealed after submit) -->
          {#if isEnMir(currentCard)}
            <div class="pcard-row pcard-row--answer">
              <div class="pcard-texts">
                <span class="pcard-lang">{answerTag(currentCard)} answer</span>
                <span class="pcard-main pcard-main--lg">{answerResult.expected_answer ?? currentCard.answer}</span>
              </div>
              <button class="btn-tts" type="button" aria-label="Hear answer" disabled={audioState==="loading"} on:click={playCardAudio}>
                🔊
              </button>
            </div>
          {/if}

          <div class="pcard-resultbar">
            <span class="result-tag">{answerResult.correct ? "✓ Correct" : "✗ Not quite"}</span>
            <button class="btn btn--primary" on:click={advancePracticeCard}>Continue</button>
          </div>
        {/if}

      </article>
    {/if}
  </div>

  <!-- audio errors at bottom -->
  {#if (audioState==="error" || audioState==="unavailable") && audioMsg}
    <p class="audio-err" role="alert">{audioMsg}</p>
  {/if}
</main>

<!-- ══════════════════════════════════════════════════════════════════════
     MENU
     ══════════════════════════════════════════════════════════════════════ -->
{:else if $authState === "authenticated" && $currentSection === "dashboard"}
<main class="shell shell--menu">
  <div class="menu-wrap">
    <p class="welcome-name">Welcome back, {$currentUser?.username ?? "admin"}.</p>
    <nav class="menu-btns">
      <button class="menu-btn" on:click={() => activateItem({section:"practice",mode:"mixed"})}>
        <span class="menu-btn-title">Continue Practice</span>
        <span class="menu-btn-sub">Mixed recall</span>
      </button>
      <button class="menu-btn" on:click={() => activateItem({section:"revision",mode:"revision"})}>
        <span class="menu-btn-title">Revision</span>
        <span class="menu-btn-sub">Review mastered</span>
      </button>
      <button class="menu-btn" on:click={() => activateItem({section:"build_vocabulary",mode:"build_vocabulary"})}>
        <span class="menu-btn-title">Vocabulary</span>
        <span class="menu-btn-sub">Build new words</span>
      </button>
      <button class="menu-btn" on:click={() => activateItem({section:"analytics"})}>
        <span class="menu-btn-title">Analytics</span>
        <span class="menu-btn-sub">View progress</span>
      </button>
      <button class="menu-btn" on:click={() => activateItem({section:"settings"})}>
        <span class="menu-btn-title">Settings</span>
        <span class="menu-btn-sub">Theme, speed</span>
      </button>
      <button class="menu-btn menu-btn--danger" on:click={logout}>
        <span class="menu-btn-title">Log Out</span>
      </button>
    </nav>
  </div>
</main>

<!-- ══════════════════════════════════════════════════════════════════════
     ANALYTICS
     ══════════════════════════════════════════════════════════════════════ -->
{:else if $authState === "authenticated" && $currentSection === "analytics"}
<main class="shell shell--section">
  <nav class="topbar">
    <button class="btn btn--ghost btn--sm" on:click={goToMenu}>&#x2190; Menu</button>
    <span class="topbar-title">Analytics</span>
    <button class="btn btn--ghost btn--sm" on:click={loadAnalytics} disabled={analyticsState==="loading"}>&#x21bb;</button>
  </nav>
  <div class="card-center">
    {#if analyticsState === "loading"}
      <div class="center-msg">Loading…</div>
    {:else if analyticsErr}
      <div class="center-msg center-msg--err">{analyticsErr}</div>
    {:else if analyticsPayload}
      <div class="stats-grid">
        <div class="stat"><span class="stat-val">{fmtN(analyticsPayload.event_count ?? 0)}</span><span class="stat-lbl">practiced</span></div>
        <div class="stat"><span class="stat-val">{fmtPct(analyticsPayload.accuracy)}</span><span class="stat-lbl">accuracy</span></div>
        <div class="stat"><span class="stat-val">{fmtN(analyticsPayload.weak_count ?? 0)}</span><span class="stat-lbl">weak</span></div>
        <div class="stat"><span class="stat-val">{fmtN(analyticsPayload.mastered_count ?? 0)}</span><span class="stat-lbl">mastered</span></div>
        <div class="stat"><span class="stat-val">{fmtN(analyticsPayload.stale_count ?? 0)}</span><span class="stat-lbl">stale</span></div>
        <div class="stat"><span class="stat-val">{fmtN(analyticsPayload.new_count ?? 0)}</span><span class="stat-lbl">new</span></div>
      </div>
    {:else}
      <div class="center-msg">No data yet.</div>
    {/if}
  </div>
</main>

<!-- ══════════════════════════════════════════════════════════════════════
     SETTINGS
     ══════════════════════════════════════════════════════════════════════ -->
{:else if $authState === "authenticated" && $currentSection === "settings"}
<main class="shell shell--section">
  <nav class="topbar">
    <button class="btn btn--ghost btn--sm" on:click={goToMenu}>&#x2190; Menu</button>
    <span class="topbar-title">Settings</span>
  </nav>
  <div class="card-center">
    {#if settingsErr}<p class="err-msg" role="alert">{settingsErr}</p>{/if}
    {#if settingsStatus}<p class="ok-msg">{settingsStatus}</p>{/if}
    {#if deleteAccountErr}<p class="err-msg" role="alert">{deleteAccountErr}</p>{/if}

    <form class="settings-form" on:submit|preventDefault={saveSettings}>
      <fieldset class="fset">
        <legend class="fset-legend">Theme</legend>
        <div class="toggle-row">
          {#each [{v:"system",l:"System"},{v:"light",l:"Light"},{v:"dark",l:"Dark"}] as o}
            <label class="toggle"><input bind:group={$theme} type="radio" value={o.v} />{o.l}</label>
          {/each}
        </div>
      </fieldset>

      <fieldset class="fset">
        <legend class="fset-legend">TTS speed: {spd($ttsSpeed)}</legend>
        <div class="toggle-row">
          {#each [0.7,0.8,0.9,1.0,1.1] as opt}
            <label class="toggle"><input bind:group={$ttsSpeed} type="radio" value={opt} />{spd(opt)}</label>
          {/each}
        </div>
      </fieldset>

      <button class="btn btn--primary" type="submit" disabled={settingsState==="saving"}>
        {settingsState==="saving" ? "Saving…" : "Save"}
      </button>
    </form>

    {#if canDeleteAccount()}
      <div class="danger-zone">
        <p class="danger-title">Delete account</p>
        <form class="del-form" on:submit|preventDefault={submitDeleteAccount}>
          <label class="field-label" for="del-username">Username</label>
          <input id="del-username" class="field-input" bind:value={deleteAccountUsername} autocomplete="username" />
          <label class="field-label" for="del-confirm">Type <strong>{deleteConfirmPhrase()}</strong> to confirm</label>
          <input id="del-confirm" class="field-input" bind:value={deleteAccountConfirm} placeholder={deleteConfirmPhrase()} />
          <button class="btn btn--danger" type="submit" disabled={!canSubmitDelete() || deleteAccountState==="submitting"}>
            {deleteAccountState==="submitting" ? "Deleting…" : "Delete account"}
          </button>
        </form>
      </div>
    {:else}
      <p class="sub-text">Admin account cannot be deleted.</p>
    {/if}
  </div>
</main>

<!-- ══════════════════════════════════════════════════════════════════════
     LOGIN / REGISTER
     ══════════════════════════════════════════════════════════════════════ -->
{:else}
<main class="shell shell--welcome">
  <div class="welcome-wrap">
    <div class="hero">
      <h1 class="hero-title">MiraLingo</h1>
      <p class="hero-sub">Practice Mirad pronunciation and translation.</p>
    </div>

    <div class="auth-forms">
      <form id="register" class="auth-card" on:submit|preventDefault={submitRegistration}>
        <h2>Create account</h2>
        {#if $authError && $authState==="registration-failed"}<p class="err-msg" role="alert">{$authError}</p>{/if}
        <label>Username<input autocomplete="username" bind:value={regU} required /></label>
        <label>Password<input autocomplete="new-password" bind:value={regP} required type="password" /></label>
        <button class="btn btn--primary" disabled={submitting} type="submit">{submitting ? "Creating…" : "Create account"}</button>
      </form>

      <form id="login" class="auth-card" on:submit|preventDefault={submitLogin}>
        <h2>Log in</h2>
        {#if $authError && $authState!=="registration-failed"}<p class="err-msg" role="alert">{$authError}</p>{/if}
        <label>Username<input autocomplete="username" bind:value={username} required /></label>
        <label>Password<input autocomplete="current-password" bind:value={password} required type="password" /></label>
        <button class="btn btn--primary" disabled={submitting} type="submit">{submitting ? "Signing in…" : "Log in"}</button>
      </form>
    </div>

    <p class="docs-link">
      <a href="https://en.wikibooks.org/wiki/Mirad_Grammar" target="_blank" rel="noopener">Mirad Grammar</a>
      &nbsp;·&nbsp;
      <a href="https://www.mirad.org/" target="_blank" rel="noopener">mirad.org</a>
    </p>
  </div>
</main>
{/if}