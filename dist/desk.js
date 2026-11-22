(() => {
  "use strict";

  const key = "incipient-visitor-desk-v1";
  const routes = {
    table: {
      reference: "OT–24",
      purpose: "The Saturday Open Table",
      firstDate: "24 October 2026 · 12:04",
      firstEntry: "Place set at the far end of the table. Desk sheet has a signature. No arrival time was entered.",
      secondDate: "7 November 2026 · 12:32",
      secondEntry: "The minute-taker recognized the speaker from the earlier sitting. Two people at the table remember the same sentence. Each remembers being the person who said it.",
      letter: "We are checking the attribution on the two copies of the minutes. The sentence appears to have reached a second speaker, and we would like both to remain traceable.",
    },
    meadow: {
      reference: "MP–17",
      purpose: "A walk on the meadow path",
      firstDate: "17 October 2026 · 11:40",
      firstEntry: "Issued a grounds map at the east desk. The copy returned that afternoon has a second route marked in the margin.",
      secondDate: "14 November 2026 · 10:18",
      secondEntry: "The second route was confirmed by a walker who asked us to remove it from the map. The name on your copy appears above the request in a different hand.",
      letter: "We have the map you returned and a second copy with your route already marked. We intend to keep both in circulation while we ask how the route was passed on.",
    },
    residence: {
      reference: "RF–03",
      purpose: "An on-site fellowship",
      firstDate: "26 October 2026 · 05:46",
      firstEntry: "Overnight return lists a second occupant of Room 3. No second key was issued. Housekeeping notes that the spare pillow had been used.",
      secondDate: "12 November 2026 · 08:15",
      secondEntry: "The register shows a key returned under your name. Facilities counted the room as occupied on the morning round.",
      letter: "We have put the key back into circulation. The next person in the room could describe how you used to be called in for supper. We have entered this as confirmation of your stay and asked them to note who they think was calling.",
    },
  };
  const corrections = {
    visit: {
      amendment: "Visitor disputes both dates of attendance. Statement entered as a third account.",
      reply: "Thank you for getting in touch. I’ve added your statement to the earlier copies. It is the first account we have from you in which neither visit took place. We’ll include it in the participation return.",
    },
    likeness: {
      amendment: "Name removed from the caption. Likeness filed with the people who identified it.",
      reply: "I’ve removed the printed name. We’ll keep the image with the accounts of the people who recognized you, since their recognition is the part we’re following.",
    },
    close: {
      amendment: "Visitor file closed. Subsequent references to the visitor transferred to the relevant room or route.",
      reply: "Your file is closed. I’ve asked the desk to keep later observations under the room or route so you won’t need to receive them.",
    },
  };

  let memory = null;
  let storage = null;
  try {
    storage = window.localStorage;
  } catch {
    // The desk remains usable for the current page if browser storage is unavailable.
  }

  function loadRecord() {
    try {
      const raw = storage ? storage.getItem(key) : memory;
      const value = JSON.parse(raw);
      if (
        value && Object.hasOwn(routes, value.route) &&
        typeof value.alias === "string" && value.alias.length <= 36 &&
        (value.correction === null || Object.hasOwn(corrections, value.correction)) &&
        typeof value.read === "boolean"
      ) return value;
    } catch {
      return null;
    }
    return null;
  }

  function saveRecord(record) {
    memory = record ? JSON.stringify(record) : null;
    try {
      if (record) storage?.setItem(key, memory);
      else storage?.removeItem(key);
    } catch {
      storage = null;
    }
  }

  function showLinkedView() {
    if (!window.location.hash) return;
    const panel = document.getElementById(window.location.hash.slice(1));
    if (!panel?.dataset.cameraView) return;
    const camera = document.getElementById(panel.dataset.cameraView);
    if (!camera) return;
    camera.checked = true;
    panel.tabIndex = -1;
    panel.scrollIntoView();
    panel.focus({ preventScroll: true });
  }

  const desk = document.querySelector("[data-record-desk]");
  const followups = document.querySelectorAll("[data-desk-followup]");
  const find = name => desk.querySelector("[data-desk-" + name + "]");

  function setText(name, text) {
    for (const node of desk.querySelectorAll("[data-desk-" + name + "]")) {
      node.textContent = text;
    }
  }

  function render(record) {
    for (const link of followups) link.hidden = !record;
    if (!desk) return;
    find("start").hidden = Boolean(record);
    find("file").hidden = !record;
    if (!record) {
      setText("name", "");
      return;
    }

    const route = routes[record.route];
    const correction = corrections[record.correction];
    setText("reference", "East desk · " + route.reference);
    setText("name", record.alias);
    setText("purpose", route.purpose);
    setText("count", correction ? "3" : "2");
    setText("first-date", route.firstDate);
    setText("first-entry", route.firstEntry);
    setText("second-date", route.secondDate);
    setText("second-entry", route.secondEntry);
    setText("letter-body", route.letter);
    setText("amendment-entry", correction?.amendment ?? "");
    setText("resolution-body", correction?.reply ?? "");
    find("amendment").hidden = !correction;
    find("read").hidden = record.read;
    find("letter").hidden = !record.read;
    find("correction").hidden = Boolean(correction);
    find("resolution").hidden = !correction;
    for (const entry of desk.querySelectorAll("[data-desk-attachment]")) {
      entry.hidden = entry.dataset.deskAttachment !== record.route;
    }
  }

  function recordCopy(record) {
    const route = routes[record.route];
    const correction = corrections[record.correction];
    return [
      "INCIPIENT INSTITUTE",
      "Visitor record desk · " + route.reference,
      "",
      "Name on the register: " + record.alias,
      "Purpose of visit: " + route.purpose,
      "",
      route.firstDate,
      route.firstEntry,
      "",
      route.secondDate,
      route.secondEntry,
      ...(correction ? ["", "Desk amendment", correction.amendment, "", correction.reply] : []),
      "",
      "Fictional visitor record",
    ].join("\n");
  }

  if (desk) {
    const alias = document.getElementById("desk-alias");
    const purpose = document.getElementById("desk-purpose");
    const correctionChoice = document.getElementById("desk-correction");
    const focus = id => document.getElementById(id).focus();

    find("form").addEventListener("submit", event => {
      event.preventDefault();
      if (!Object.hasOwn(routes, purpose.value)) return;
      const record = { alias: alias.value.trim() || "Visitor", route: purpose.value, read: false, correction: null };
      saveRecord(record);
      render(record);
      focus("desk-file-title");
    });
    find("read").addEventListener("click", () => {
      const record = loadRecord();
      if (!record) return;
      record.read = true;
      saveRecord(record);
      render(record);
      focus("desk-letter-title");
    });
    find("correction").addEventListener("submit", event => {
      event.preventDefault();
      const record = loadRecord();
      if (!record?.read || record.correction || !Object.hasOwn(corrections, correctionChoice.value)) return;
      record.correction = correctionChoice.value;
      if (record.correction === "likeness") {
        record.alias = "Withheld";
        alias.value = "";
      }
      saveRecord(record);
      render(record);
      focus("desk-resolution-title");
    });
    find("download").addEventListener("click", () => {
      const record = loadRecord();
      if (!record) return;
      const file = new Blob([recordCopy(record)], { type: "text/plain;charset=utf-8" });
      const url = URL.createObjectURL(file);
      const link = document.createElement("a");
      link.href = url;
      link.download = "Incipient-visitor-record.txt";
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
    find("clear").addEventListener("click", () => {
      saveRecord(null);
      find("form").reset();
      find("correction").reset();
      render(null);
      focus("desk-alias");
    });
  }

  render(loadRecord());
  showLinkedView();
  window.addEventListener("hashchange", showLinkedView);
  window.addEventListener("storage", event => {
    if (event.key === key || event.key === null) render(loadRecord());
  });
})();
