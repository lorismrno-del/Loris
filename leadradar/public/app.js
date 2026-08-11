/* ==========================================================================
   Lorino Leadradar - Frontend
   Reines JavaScript, kein Build-Schritt. DOM wird über h() gebaut, damit
   Fremddaten (Firmennamen aus Google/OSM) nie als HTML interpretiert werden.
   ========================================================================== */

// ------------------------------------------------------------------ Werkzeug

/** Baut ein Element. Strings werden als Text eingefügt - nie als HTML. */
function h(tag, props = {}, ...children) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(props || {})) {
    if (value == null || value === false) continue;
    if (key === 'class') el.className = value;
    else if (key === 'text') el.textContent = value;
    else if (key === 'html') el.innerHTML = value; // nur für eigene, feste Inhalte
    else if (key.startsWith('on') && typeof value === 'function') {
      el.addEventListener(key.slice(2).toLowerCase(), value);
    } else if (key === 'dataset') Object.assign(el.dataset, value);
    else if (key === 'style' && typeof value === 'object') Object.assign(el.style, value);
    else if (value === true) el.setAttribute(key, '');
    else el.setAttribute(key, value);
  }
  for (const child of children.flat()) {
    if (child == null || child === false) continue;
    el.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return el;
}

const $ = (sel) => document.querySelector(sel);
const clear = (el) => { while (el.firstChild) el.removeChild(el.firstChild); return el; };

async function api(path, options) {
  const res = await fetch(path, {
    headers: { 'content-type': 'application/json' },
    ...options,
    body: options?.body ? JSON.stringify(options.body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (res.status === 401 && data.login) {
    // Sitzung abgelaufen - zurück zur Anmeldung
    location.href = '/login.html';
    throw new Error('Nicht angemeldet');
  }
  if (!res.ok) throw new Error(data.error || `Fehler ${res.status}`);
  return data;
}

let toastTimer;
function toast(message, kind = '') {
  const el = $('#toast');
  el.textContent = message;
  el.style.background = kind === 'error' ? '#dc2626' : kind === 'ok' ? '#16a34a' : '#0f172a';
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.hidden = true; }, 2800);
}

async function copyText(text, label = 'Kopiert') {
  try {
    await navigator.clipboard.writeText(text);
    toast('✓ ' + label, 'ok');
  } catch {
    // Fallback für Browser ohne Clipboard-API (z. B. ohne HTTPS)
    const ta = h('textarea', { style: { position: 'fixed', opacity: '0' } });
    ta.value = text;
    document.body.append(ta);
    ta.select();
    document.execCommand('copy');
    ta.remove();
    toast('✓ ' + label, 'ok');
  }
}

const fmtDate = (iso) => {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('de-CH', { day: '2-digit', month: '2-digit', year: '2-digit' });
};
const fmtTime = (iso) =>
  new Date(iso).toLocaleString('de-CH', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });

/** Telefonnummer für tel:-Links (ohne Leerzeichen). */
const telHref = (phone) => 'tel:' + String(phone).replace(/[^\d+]/g, '');
/** WhatsApp braucht die Nummer ohne + und ohne Leerzeichen. */
const waHref = (phone, text) =>
  `https://wa.me/${String(phone).replace(/\D/g, '')}?text=${encodeURIComponent(text)}`;

// -------------------------------------------------------------------- Zustand

const state = {
  meta: null,
  settings: null,
  leads: [],
  total: 0,
  page: 1,
  perPage: 60,
  selectedTrades: new Set(),
  selectedId: null,
  view: 'liste',
};

// ------------------------------------------------------------------- Ansichten

function switchView(name) {
  state.view = name;
  for (const tab of document.querySelectorAll('.tab')) {
    tab.classList.toggle('is-active', tab.dataset.view === name);
  }
  for (const view of document.querySelectorAll('.view')) {
    const isActive = view.id === 'view-' + name;
    view.classList.toggle('is-active', isActive);
    view.hidden = !isActive;
  }
  $('#kpis').hidden = name === 'einstellungen';
}

// ------------------------------------------------------------------ Kennzahlen

async function loadStats() {
  const s = await api('/api/stats');
  const box = clear($('#kpis'));
  const kpi = (value, label, cls = '') =>
    h('div', { class: 'kpi ' + cls },
      h('div', { class: 'kpi-value', text: String(value) }),
      h('div', { class: 'kpi-label', text: label }));

  // Nulls herausfiltern - append() würde sonst den Text "null" einfügen
  box.append(...[
    kpi(s.total, 'Leads total'),
    kpi(s.hot, '🔥 Sehr heiss', 'is-hot'),
    kpi(s.noWebsite, 'Ohne Webseite'),
    kpi(s.withPhone, 'Mit Telefonnummer'),
    kpi(s.byStatus.kontaktiert || 0, 'Kontaktiert'),
    kpi(s.byStatus.termin || 0, 'Termine'),
    kpi(s.kunden, 'Kunden ✅', 'is-good'),
    s.dueFollowUps ? kpi(s.dueFollowUps, 'Wiedervorlage fällig', 'is-due') : null,
  ].filter(Boolean));
}

// ---------------------------------------------------------------------- Suche

function renderTradeChips() {
  const box = clear($('#tradeChips'));
  for (const trade of state.meta.trades) {
    const chip = h('button', {
      class: 'chip' + (state.selectedTrades.has(trade.id) ? ' is-on' : ''),
      type: 'button',
      text: `${trade.emoji} ${trade.label}`,
      onClick() {
        if (state.selectedTrades.has(trade.id)) state.selectedTrades.delete(trade.id);
        else state.selectedTrades.add(trade.id);
        renderTradeChips();
      },
    });
    box.append(chip);
  }
}

const HANDWERK = ['schreiner', 'maler', 'sanitaer', 'elektriker', 'bau', 'dachdecker',
  'gartenbau', 'bodenleger', 'metallbau', 'fenster', 'kuechenbau'];

async function startSearch() {
  const trades = [...state.selectedTrades];
  if (trades.length === 0) return toast('Bitte mindestens eine Branche wählen', 'error');

  const body = {
    source: $('#sourceSelect').value,
    trades,
    place: $('#placeInput').value.trim(),
    radiusKm: Number($('#radiusInput').value),
    limit: Number($('#limitInput').value),
    doAudit: $('#auditCheck').checked,
  };

  const btn = $('#searchBtn');
  btn.disabled = true;
  btn.textContent = '⏳ Läuft …';
  $('#searchResult').hidden = true;
  $('#searchProgress').hidden = false;
  $('#progressFill').style.width = '5%';
  $('#progressStep').textContent = 'Start …';

  try {
    const { jobId } = await api('/api/search', { method: 'POST', body });
    await pollJob(jobId);
  } catch (err) {
    showSearchResult(err.message, 'is-error');
  } finally {
    btn.disabled = false;
    btn.textContent = '🔍 Suche starten';
  }
}

function pollJob(jobId) {
  return new Promise((resolve) => {
    const tick = async () => {
      let job;
      try {
        job = await api('/api/jobs/' + jobId);
      } catch {
        setTimeout(tick, 1500);
        return;
      }

      $('#progressStep').textContent = job.step;
      const pct = job.total > 0 ? 10 + (job.done / job.total) * 85 : 12;
      $('#progressFill').style.width = Math.min(97, pct) + '%';

      if (job.state === 'running') { setTimeout(tick, 700); return; }

      $('#progressFill').style.width = '100%';
      setTimeout(() => { $('#searchProgress').hidden = true; }, 700);

      if (job.state === 'error') {
        showSearchResult(job.error, 'is-error');
      } else {
        const r = job.result || {};
        if (r.found === 0) {
          showSearchResult(r.hint || 'Keine Treffer.', 'is-error');
        } else {
          showSearchResult(
            `✓ ${r.found} Betriebe gefunden – ${r.added} neu, ${r.updated} aktualisiert` +
            (r.place ? ` (${r.place}, ${r.radiusKm} km)` : '') +
            '. Wechsle zur Anrufliste, um loszulegen.',
            'is-ok',
          );
          await Promise.all([loadLeads(), loadStats()]);
          if (r.added > 0) setTimeout(() => switchView('liste'), 900);
        }
      }
      resolve();
    };
    tick();
  });
}

function showSearchResult(message, cls) {
  const box = $('#searchResult');
  box.className = 'notice ' + cls;
  box.textContent = message;
  box.hidden = false;
}

// --------------------------------------------------------------- Lead-Liste

function currentFilters() {
  const p = new URLSearchParams();
  p.set('q', $('#fSearch').value.trim());
  p.set('status', $('#fStatus').value);
  p.set('tier', $('#fTier').value);
  p.set('websiteStatus', $('#fWebsite').value);
  p.set('trade', $('#fTrade').value);
  p.set('city', $('#fCity').value);
  p.set('sort', $('#fSort').value);
  if ($('#fPhone').checked) p.set('onlyPhone', '1');
  if ($('#fHideDone').checked) p.set('hideDone', '1');
  return p;
}

async function loadLeads(append = false) {
  const p = currentFilters();
  p.set('page', String(append ? state.page + 1 : 1));
  p.set('perPage', String(state.perPage));

  const data = await api('/api/leads?' + p.toString());
  state.page = data.page;
  state.total = data.total;
  state.leads = append ? [...state.leads, ...data.leads] : data.leads;

  // Ortsfilter befüllen (nur einmal pro Datenstand)
  const citySel = $('#fCity');
  if (citySel.options.length - 1 !== data.cities.length) {
    const chosen = citySel.value;
    clear(citySel).append(h('option', { value: 'alle' }, 'Alle Orte'));
    for (const c of data.cities) citySel.append(h('option', { value: c }, c));
    citySel.value = data.cities.includes(chosen) ? chosen : 'alle';
  }

  renderLeads();
  $('#exportBtn').href = '/api/export.csv?' + currentFilters().toString();
}

function renderLeads() {
  const box = clear($('#leads'));
  $('#listCount').textContent =
    state.total === 0 ? 'Keine Leads' : `${state.total} Lead${state.total === 1 ? '' : 's'}`;

  if (state.leads.length === 0) {
    $('#emptyState').hidden = false;
    clear($('#emptyState')).append(
      h('h3', {}, '📭 Noch nichts hier'),
      h('p', { class: 'muted' },
        'Wechsle zu „Leads finden", wähle deine Branchen und starte die Suche. ' +
        'Zum Ausprobieren kannst du die Datenquelle „Demo-Daten" nehmen.'),
      h('div', { style: { marginTop: '16px' } },
        h('button', { class: 'btn btn-primary', onClick: () => switchView('suche') }, 'Jetzt Leads suchen')),
    );
    $('#loadMoreWrap').hidden = true;
    return;
  }
  $('#emptyState').hidden = true;

  for (const lead of state.leads) box.append(renderLeadRow(lead));

  $('#loadMoreWrap').hidden = state.leads.length >= state.total;
}

function renderLeadRow(lead) {
  const tier = lead.tier || { key: 'low', emoji: '·', color: '#94a3b8' };
  const phone = lead.customPhone || lead.phone;
  const email = lead.customEmail || lead.email;
  const status = state.meta.statuses.find((s) => s.id === lead.status);

  const row = h('article', {
    class: `lead tier-${tier.key}` +
      (lead.id === state.selectedId ? ' is-selected' : '') +
      (lead.status === 'nichtstoeren' ? ' is-blocked' : ''),
    dataset: { id: lead.id },
    onClick: (e) => {
      if (e.target.closest('a, button')) return;
      openDetail(lead.id);
    },
  });

  row.append(
    h('div', { class: 'score-badge', style: { background: tier.color + '18' } },
      h('b', { style: { color: tier.color }, text: String(lead.score ?? '–') }),
      h('span', { text: tier.emoji })),

    h('div', { class: 'lead-main' },
      h('div', { class: 'lead-title' },
        lead.starred ? h('span', { text: '⭐' }) : null,
        h('span', { class: 'lead-name', text: lead.name }),
        status ? h('span', { class: 'pill pill-status', style: { background: status.color + '1a', color: status.color }, text: status.label }) : null,
        lead.isDemo ? h('span', { class: 'pill pill-demo', text: 'DEMO' }) : null),

      h('div', { class: 'lead-headline', text: lead.headline || '' }),

      h('div', { class: 'lead-meta' },
        lead.address?.city ? h('span', {}, '📍 ' + [lead.address.zip, lead.address.city].filter(Boolean).join(' ')) : null,
        phone ? h('span', {}, '📞 ' + phone) : h('span', { style: { color: '#dc2626' } }, '✗ keine Nummer'),
        email ? h('span', {}, '✉️ ' + email) : null,
        lead.googleReviews ? h('span', {}, `⭐ ${lead.googleRating} (${lead.googleReviews})`) : null,
        lead.inactiveYears >= 2 ? h('span', { class: 'pill pill-warn' }, `${lead.inactiveYears} J. inaktiv`) : null,
        lead.distanceKm != null ? h('span', {}, `${lead.distanceKm} km`) : null)),

    h('div', { class: 'lead-actions' },
      phone
        ? h('a', { class: 'icon-btn', href: telHref(phone), title: 'Anrufen', onClick: () => logActivity(lead.id, 'call') }, '📞')
        : h('span', { class: 'icon-btn is-off' }, '📞'),
      phone
        ? h('a', { class: 'icon-btn', href: waHref(phone, ''), target: '_blank', rel: 'noopener', title: 'WhatsApp' }, '💬')
        : h('span', { class: 'icon-btn is-off' }, '💬'),
      h('button', {
        class: 'icon-btn', title: lead.starred ? 'Stern entfernen' : 'Merken',
        onClick: async (e) => {
          e.stopPropagation();
          await api('/api/leads/' + encodeURIComponent(lead.id), { method: 'PATCH', body: { starred: !lead.starred } });
          lead.starred = !lead.starred;
          renderLeads();
        },
      }, lead.starred ? '⭐' : '☆')),
  );

  return row;
}

// -------------------------------------------------------------- Detail-Panel

async function openDetail(id) {
  state.selectedId = id;
  renderLeads();
  $('#detail').hidden = false;
  $('#backdrop').hidden = false;
  const box = clear($('#detailInner'));
  box.append(h('p', { class: 'muted' }, 'Lade …'));

  try {
    const data = await api('/api/leads/' + encodeURIComponent(id));
    renderDetail(data);
  } catch (err) {
    clear(box).append(h('p', { class: 'notice is-error', text: err.message }));
  }
}

function closeDetail() {
  $('#detail').hidden = true;
  $('#backdrop').hidden = true;
  state.selectedId = null;
  renderLeads();
}

function renderDetail({ lead, script, email, whatsapp, sms }) {
  const box = clear($('#detailInner'));
  const phone = lead.customPhone || lead.phone;
  const mail = lead.customEmail || lead.email;
  const tier = lead.tier || {};

  // ---- Kopf
  box.append(
    h('div', { class: 'detail-head' },
      h('div', {},
        h('h2', { text: lead.name }),
        h('p', { class: 'muted', text: [lead.headline, lead.address?.city].filter(Boolean).join(' · ') })),
      h('button', { class: 'close-btn', onClick: closeDetail }, '✕')),

    h('div', { style: { marginTop: '10px' } },
      h('span', {
        class: 'pill', style: { background: (tier.color || '#94a3b8') + '1a', color: tier.color || '#475569', fontSize: '12px', padding: '5px 12px' },
        text: `${tier.emoji || ''} ${tier.label || ''} · ${lead.score ?? 0}/100`,
      })),
  );

  // ---- Direktaktionen
  const bar = h('div', { class: 'callbar' });
  if (phone) {
    bar.append(
      h('a', { class: 'btn btn-primary btn-wide', href: telHref(phone), onClick: () => logActivity(lead.id, 'call') },
        '📞 ' + phone),
      h('a', { class: 'btn btn-gold', href: waHref(phone, whatsapp), target: '_blank', rel: 'noopener', onClick: () => logActivity(lead.id, 'whatsapp') },
        '💬 WhatsApp'),
      h('button', { class: 'btn btn-secondary', onClick: () => logActivity(lead.id, 'call_noanswer') },
        '📵 Nicht erreicht'),
    );
  } else {
    bar.append(h('div', { class: 'notice btn-wide', style: { gridColumn: '1/-1' } },
      'Keine Telefonnummer hinterlegt. Tipp: Firmenname + Ort auf local.ch suchen und Nummer unten eintragen.'));
  }
  if (mail) {
    bar.append(h('a', {
      class: 'btn btn-secondary btn-wide',
      href: `mailto:${mail}?subject=${encodeURIComponent(email.subject)}&body=${encodeURIComponent(email.body)}`,
      onClick: () => logActivity(lead.id, 'email'),
    }, '✉️ E-Mail mit Vorlage öffnen'));
  }
  box.append(bar);

  // ---- Warum dieser Lead
  if (lead.reasons?.length) {
    box.append(section('Warum dieser Lead',
      h('div', { class: 'reasons' },
        ...lead.reasons.slice(0, 12).map((r) =>
          h('span', { class: 'reason kind-' + (r.kind || 'need'), text: r.label })))));
  }

  // ---- Gesprächsleitfaden
  const scriptBox = h('div', {});
  for (const step of script.steps) {
    scriptBox.append(
      h('div', { class: 'script-step' },
        h('h4', { text: step.title }),
        step.hint ? h('div', { class: 'hint', text: step.hint }) : null,
        h('p', { text: step.text })));
  }
  scriptBox.append(
    h('button', {
      class: 'btn btn-ghost btn-sm',
      onClick: () => copyText(script.steps.map((s) => s.title + '\n' + s.text).join('\n\n'), 'Leitfaden kopiert'),
    }, '📋 Ganzen Leitfaden kopieren'));
  box.append(section('📞 Gesprächsleitfaden', scriptBox));

  // ---- Fakten fürs Gespräch
  if (script.facts?.length) {
    box.append(section('Fakten fürs Gespräch',
      h('ul', { class: 'facts' }, ...script.facts.map((f) => h('li', { text: f })))));
  }

  // ---- Deine Argumente
  if (script.usps?.length) {
    box.append(section('Deine Argumente',
      h('ul', { class: 'facts' }, ...script.usps.map((u) => h('li', { text: u })))));
  }

  // ---- Nachrichten-Vorlagen
  box.append(section('Vorlagen',
    copyBox('WhatsApp / SMS', whatsapp),
    copyBox('E-Mail-Betreff', email.subject),
    copyBox('E-Mail-Text', email.body),
    copyBox('Kurz-SMS', sms)));

  // ---- Status
  const picker = h('div', { class: 'status-picker' });
  for (const s of state.meta.statuses) {
    picker.append(h('button', {
      class: 'status-opt' + (lead.status === s.id ? ' is-on' : ''),
      style: lead.status === s.id ? { background: s.color } : {},
      text: s.label,
      onClick: async () => {
        await api('/api/leads/' + encodeURIComponent(lead.id), { method: 'PATCH', body: { status: s.id } });
        toast('Status: ' + s.label, 'ok');
        await Promise.all([loadLeads(), loadStats()]);
        openDetail(lead.id);
      },
    }));
  }
  box.append(section('Status', picker));

  // ---- Wiedervorlage
  const dateInput = h('input', { type: 'date', value: lead.followUpAt ? lead.followUpAt.slice(0, 10) : '' });
  box.append(section('Wiedervorlage',
    h('div', { style: { display: 'flex', gap: '8px' } },
      dateInput,
      h('button', {
        class: 'btn btn-secondary btn-sm',
        onClick: async () => {
          await api('/api/leads/' + encodeURIComponent(lead.id), {
            method: 'PATCH',
            body: { followUpAt: dateInput.value ? new Date(dateInput.value).toISOString() : null },
          });
          toast('Wiedervorlage gesetzt', 'ok');
          loadStats();
        },
      }, 'Merken'))));

  // ---- Notiz
  const noteInput = h('textarea', { rows: '2', placeholder: 'Was wurde besprochen?' });
  const noteList = h('div', { class: 'note-list' },
    ...(lead.notes || []).slice(0, 10).map((n) =>
      h('div', { class: 'note' }, h('time', { text: fmtTime(n.ts) }), h('div', { text: n.text }))));

  box.append(section('Notizen',
    noteInput,
    h('button', {
      class: 'btn btn-secondary btn-sm', style: { marginTop: '7px' },
      onClick: async () => {
        if (!noteInput.value.trim()) return;
        await api(`/api/leads/${encodeURIComponent(lead.id)}/notes`, { method: 'POST', body: { text: noteInput.value } });
        noteInput.value = '';
        openDetail(lead.id);
        toast('Notiz gespeichert', 'ok');
      },
    }, '+ Notiz speichern'),
    noteList));

  // ---- Kontaktdaten (bearbeitbar)
  const fPhone = h('input', { value: lead.customPhone || lead.phone || '', placeholder: '+41 …' });
  const fMail = h('input', { value: lead.customEmail || lead.email || '', placeholder: 'info@…' });
  const fName = h('input', { value: lead.contactName || '', placeholder: 'Herr Muster' });

  box.append(section('Kontaktdaten',
    h('div', { class: 'field' }, h('label', {}, 'Ansprechperson'), fName),
    h('div', { class: 'field' }, h('label', {}, 'Telefon'), fPhone),
    h('div', { class: 'field' }, h('label', {}, 'E-Mail'), fMail),
    h('button', {
      class: 'btn btn-secondary btn-sm',
      onClick: async () => {
        await api('/api/leads/' + encodeURIComponent(lead.id), {
          method: 'PATCH',
          body: { contactName: fName.value.trim(), customPhone: fPhone.value.trim(), customEmail: fMail.value.trim() },
        });
        toast('Gespeichert', 'ok');
        loadLeads();
        openDetail(lead.id);
      },
    }, 'Speichern')));

  // ---- Technische Analyse
  const a = lead.audit || {};
  const dl = h('dl', { class: 'info-grid' });
  const addRow = (label, value) => { if (value != null && value !== '') dl.append(h('dt', { text: label }), h('dd', { text: String(value) })); };
  addRow('Webseite', lead.website || '—');
  addRow('Status', a.summary || websiteStatusText(a.status));
  addRow('Geprüft am', a.checkedAt ? fmtTime(a.checkedAt) : '—');
  if (a.status === 'ok') {
    addRow('HTTPS', a.https ? 'ja' : 'nein');
    addRow('Mobiltauglich', a.hasViewport ? 'ja' : 'nein');
    addRow('Ladezeit', a.responseMs ? (a.responseMs / 1000).toFixed(1) + ' s' : '—');
    addRow('Seitengrösse', a.pageBytes ? (a.pageBytes / 1000).toFixed(0) + ' KB' : '—');
    addRow('Copyright', a.copyrightYear || '—');
    addRow('Impressum', a.hasImpressum ? 'ja' : 'nein');
    addRow('Kontaktformular', a.hasContactForm ? 'ja' : 'nein');
    addRow('Technik', (a.techFlags || []).join(', ') || '—');
    addRow('Seitentitel', a.title || '—');
  }
  addRow('Quelle', lead.source);

  const links = h('div', { class: 'actions', style: { marginTop: '10px' } });
  if (lead.website) links.append(h('a', { class: 'btn btn-ghost btn-sm', href: lead.website, target: '_blank', rel: 'noopener nofollow' }, '🌐 Webseite öffnen'));
  if (lead.googleMapsUrl) links.append(h('a', { class: 'btn btn-ghost btn-sm', href: lead.googleMapsUrl, target: '_blank', rel: 'noopener' }, '🗺️ Google Maps'));
  links.append(h('a', {
    class: 'btn btn-ghost btn-sm',
    href: 'https://www.local.ch/de/q?what=' + encodeURIComponent(lead.name) + '&where=' + encodeURIComponent(lead.address?.city || ''),
    target: '_blank', rel: 'noopener',
  }, '🔎 local.ch (Stern-Eintrag prüfen)'));
  links.append(h('button', {
    class: 'btn btn-ghost btn-sm',
    onClick: async (e) => {
      e.target.textContent = '⏳ Prüfe …';
      try {
        await api(`/api/leads/${encodeURIComponent(lead.id)}/reaudit`, { method: 'POST' });
        toast('Webseite neu geprüft', 'ok');
        await loadLeads();
        openDetail(lead.id);
      } catch (err) { toast(err.message, 'error'); }
    },
  }, '🔄 Erneut prüfen'));

  box.append(section('Technische Analyse', dl, links));

  // ---- Verlauf
  if (lead.activities?.length) {
    box.append(section('Verlauf',
      h('div', { class: 'activity' },
        ...lead.activities.slice(0, 15).map((act) =>
          h('div', {}, h('time', { text: fmtTime(act.ts) }), h('span', { text: act.text }))))));
  }

  // ---- Weitergabe + Löschen
  const footer = h('div', { class: 'actions', style: { marginTop: '24px' } });
  if (state.settings?.webhooks?.some((w) => w.enabled && w.url)) {
    footer.append(h('button', {
      class: 'btn btn-secondary btn-sm',
      onClick: async () => {
        try {
          const r = await api(`/api/leads/${encodeURIComponent(lead.id)}/push`, { method: 'POST', body: {} });
          toast(r.sent > 0 ? `An ${r.sent} Ziel(e) übergeben` : (r.hint || 'Nichts gesendet'), r.sent ? 'ok' : 'error');
        } catch (err) { toast(err.message, 'error'); }
      },
    }, '📤 An anderes Tool übergeben'));
  }
  footer.append(h('button', {
    class: 'btn btn-ghost btn-sm',
    onClick: async () => {
      const data = await api(`/api/leads/${encodeURIComponent(lead.id)}/payload`);
      copyText(JSON.stringify(data, null, 2), 'Lead als JSON kopiert');
    },
  }, '{ } JSON kopieren'));
  footer.append(h('button', {
    class: 'btn btn-danger btn-sm',
    onClick: async () => {
      if (!confirm(`"${lead.name}" wirklich löschen?`)) return;
      await api('/api/leads/' + encodeURIComponent(lead.id), { method: 'DELETE' });
      closeDetail();
      await Promise.all([loadLeads(), loadStats()]);
      toast('Gelöscht');
    },
  }, '🗑 Löschen'));
  box.append(footer);

  $('#detail').scrollTop = 0;
}

function section(title, ...children) {
  return h('div', { class: 'detail-section' }, h('h3', { text: title }), ...children);
}

function copyBox(label, text) {
  return h('div', { style: { marginBottom: '10px' } },
    h('div', { class: 'copyrow' },
      h('strong', { style: { fontSize: '13px' }, text: label }),
      h('button', { class: 'linkbtn', onClick: () => copyText(text, label + ' kopiert') }, 'Kopieren')),
    h('div', { class: 'copybox', text }));
}

function websiteStatusText(status) {
  return {
    none: 'Keine Webseite', dead: 'Webseite tot', parked: 'Platzhalterseite',
    social_only: 'Nur Social Media', directory_only: 'Nur Verzeichnis',
    ok: 'Webseite vorhanden', error: 'Prüfung fehlgeschlagen',
  }[status] || 'Nicht geprüft';
}

async function logActivity(id, type) {
  try {
    await api(`/api/leads/${encodeURIComponent(id)}/activity`, { method: 'POST', body: { type } });
    await Promise.all([loadLeads(), loadStats()]);
  } catch { /* Anruf soll nie blockiert werden */ }
}

// --------------------------------------------------------------- Einstellungen

function fillSettings(s) {
  state.settings = s;
  $('#sAgencyName').value = s.agencyName;
  $('#sOwnerName').value = s.ownerName;
  $('#sPhone').value = s.phone;
  $('#sEmail').value = s.email;
  $('#sWebsite').value = s.website;
  $('#sInstagram').value = s.instagram;
  $('#sSlogan').value = s.slogan;
  $('#sBookingUrl').value = s.bookingUrl || '';
  $('#sPitch').value = s.pitch;
  $('#sFreePreview').checked = s.freePreview;
  $('#sFreePreviewLine').value = s.freePreviewLine;
  $('#sUsps').value = (s.usps || []).join('\n');
  $('#brandAgency').textContent = s.agencyName;
  renderWebhooks();
}

function renderWebhooks() {
  const box = clear($('#webhookList'));
  const hooks = state.settings.webhooks || [];

  hooks.forEach((hook, i) => {
    const label = h('input', { value: hook.label || '', placeholder: 'Name (z. B. Agentur-OS)' });
    const url = h('input', { value: hook.url || '', placeholder: 'https://… (POST-Endpunkt)' });
    const on = h('label', { class: 'toggle' },
      h('input', { type: 'checkbox', ...(hook.enabled ? { checked: true } : {}) }), 'aktiv');

    const sync = () => {
      hooks[i] = {
        label: label.value.trim(),
        url: url.value.trim(),
        enabled: on.querySelector('input').checked,
        secret: hook.secret || '',
      };
    };
    for (const el of [label, url, on.querySelector('input')]) el.addEventListener('change', sync);

    box.append(h('div', { class: 'webhook-row' }, label, url, on,
      h('button', {
        class: 'btn btn-ghost btn-sm',
        onClick: () => { hooks.splice(i, 1); renderWebhooks(); },
      }, '✕')));
  });

  if (hooks.length === 0) {
    box.append(h('p', { class: 'muted' }, 'Noch kein Ziel hinterlegt.'));
  }
}

async function saveSettings() {
  const patch = {
    agencyName: $('#sAgencyName').value,
    ownerName: $('#sOwnerName').value,
    phone: $('#sPhone').value,
    email: $('#sEmail').value,
    website: $('#sWebsite').value,
    instagram: $('#sInstagram').value,
    slogan: $('#sSlogan').value,
    bookingUrl: $('#sBookingUrl').value,
    pitch: $('#sPitch').value,
    freePreview: $('#sFreePreview').checked,
    freePreviewLine: $('#sFreePreviewLine').value,
    usps: $('#sUsps').value.split('\n').map((l) => l.trim()).filter(Boolean),
    webhooks: (state.settings.webhooks || []).filter((w) => w.url),
  };
  const { settings } = await api('/api/settings', { method: 'PUT', body: patch });
  fillSettings(settings);
  const hint = $('#savedHint');
  hint.hidden = false;
  setTimeout(() => { hint.hidden = true; }, 2200);
  toast('Einstellungen gespeichert', 'ok');
}

function renderSourceStatus() {
  const box = clear($('#sourceStatus'));
  for (const src of state.meta.sources) {
    box.append(h('div', { style: { marginBottom: '10px' } },
      h('strong', { text: (src.available ? '✅ ' : '⚠️ ') + src.label }),
      h('div', { class: 'muted', text: src.note })));
  }
}

// ------------------------------------------------------------------ Rechtliches

function showLegal() {
  const box = clear($('#legalContent'));
  for (const note of state.meta.legal) {
    box.append(h('div', { class: 'legal-item' },
      h('h4', { text: note.title }),
      h('p', { text: note.text })));
  }
  $('#legalModal').hidden = false;
}

// -------------------------------------------------------------------- Start

async function init() {
  state.meta = await api('/api/meta');
  fillSettings(state.meta.settings);

  // Abmelden-Knopf nur zeigen, wenn ein Passwort gesetzt ist
  if (state.meta.schutzAktiv) {
    $('.topbar-right').append(h('button', {
      class: 'btn btn-ghost btn-sm',
      title: 'Abmelden',
      onClick: async () => {
        await fetch('/api/logout', { method: 'POST' });
        location.href = '/login.html';
      },
    }, '⏻'));
  }

  // Branchen
  for (const t of HANDWERK) state.selectedTrades.add(t);
  renderTradeChips();

  // Auswahlfelder befüllen
  const tradeOptions = (sel, allLabel) => {
    clear(sel).append(h('option', { value: 'alle' }, allLabel));
    for (const t of state.meta.trades) sel.append(h('option', { value: t.id }, `${t.emoji} ${t.label}`));
  };
  tradeOptions($('#fTrade'), 'Alle Branchen');
  clear($('#mTrade'));
  for (const t of state.meta.trades) $('#mTrade').append(h('option', { value: t.id }, t.label));

  clear($('#fStatus')).append(h('option', { value: 'alle' }, 'Alle Status'));
  for (const s of state.meta.statuses) $('#fStatus').append(h('option', { value: s.id }, s.label));

  const srcSel = clear($('#sourceSelect'));
  for (const src of state.meta.sources) {
    srcSel.append(h('option', { value: src.id, ...(src.available ? {} : { disabled: true }) },
      src.label + (src.available ? '' : ' – nicht konfiguriert')));
  }
  srcSel.value = state.meta.sources.find((s) => s.available && s.id === 'google') ? 'google' : 'osm';
  const updateNote = () => {
    $('#sourceNote').textContent = state.meta.sources.find((s) => s.id === srcSel.value)?.note || '';
  };
  srcSel.addEventListener('change', updateNote);
  updateNote();

  const dl = clear($('#placeList'));
  for (const c of state.meta.places.cities) dl.append(h('option', { value: c.name }));
  for (const c of state.meta.places.cantons) dl.append(h('option', { value: c.name }));

  renderSourceStatus();
  await Promise.all([loadLeads(), loadStats()]);
}

// ------------------------------------------------------------------ Ereignisse

$('#tabs').addEventListener('click', (e) => {
  const tab = e.target.closest('.tab');
  if (tab) switchView(tab.dataset.view);
});

$('#searchBtn').addEventListener('click', startSearch);
$('#tradeAll').addEventListener('click', () => {
  state.meta.trades.forEach((t) => state.selectedTrades.add(t.id));
  renderTradeChips();
});
$('#tradeNone').addEventListener('click', () => { state.selectedTrades.clear(); renderTradeChips(); });
$('#tradeHandwerk').addEventListener('click', () => {
  state.selectedTrades.clear();
  HANDWERK.forEach((t) => state.selectedTrades.add(t));
  renderTradeChips();
});
$('#radiusInput').addEventListener('input', (e) => { $('#radiusOut').textContent = e.target.value; });

$('#manualAddBtn').addEventListener('click', async () => {
  const name = $('#mName').value.trim();
  if (!name) return toast('Firmenname fehlt', 'error');
  try {
    await api('/api/leads', {
      method: 'POST',
      body: {
        name, trade: $('#mTrade').value, phone: $('#mPhone').value.trim(),
        city: $('#mCity').value.trim(), email: $('#mEmail').value.trim(),
        website: $('#mWebsite').value.trim(),
      },
    });
    for (const id of ['#mName', '#mPhone', '#mCity', '#mEmail', '#mWebsite']) $(id).value = '';
    toast('Lead hinzugefügt', 'ok');
    await Promise.all([loadLeads(), loadStats()]);
  } catch (err) { toast(err.message, 'error'); }
});

let filterTimer;
for (const id of ['#fStatus', '#fTier', '#fWebsite', '#fTrade', '#fCity', '#fSort', '#fPhone', '#fHideDone']) {
  $(id).addEventListener('change', () => loadLeads());
}
$('#fSearch').addEventListener('input', () => {
  clearTimeout(filterTimer);
  filterTimer = setTimeout(() => loadLeads(), 280);
});
$('#loadMoreBtn').addEventListener('click', () => loadLeads(true));

$('#backdrop').addEventListener('click', closeDetail);
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    if (!$('#legalModal').hidden) $('#legalModal').hidden = true;
    else closeDetail();
  }
});

$('#legalBtn').addEventListener('click', showLegal);
$('#legalClose').addEventListener('click', () => { $('#legalModal').hidden = true; });
$('#saveSettingsBtn').addEventListener('click', () => saveSettings().catch((e) => toast(e.message, 'error')));
$('#addWebhookBtn').addEventListener('click', () => {
  state.settings.webhooks = state.settings.webhooks || [];
  state.settings.webhooks.push({ label: '', url: '', enabled: true, secret: '' });
  renderWebhooks();
});

init().catch((err) => {
  document.body.prepend(h('div', { class: 'notice is-error', style: { margin: '16px' } },
    'Start fehlgeschlagen: ' + err.message));
});
