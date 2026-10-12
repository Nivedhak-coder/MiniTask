function face(a, m = "neutral") {
  const lips = a.lips || "#d9777f", es = a.eye_style || "round";
  const arc = (x, y, cy) => `<path d="M${x - 8} ${y}Q${x} ${cy} ${x + 8} ${y}" fill="none" stroke="${a.eyes}" stroke-width="3.5" stroke-linecap="round"/>`;
  const eye = x => {
    const o = x < 100 ? -1 : 1;
    if (m === "happy") return arc(x, 100, 88);
    if (m === "sleepy") return arc(x, 98, 105);
    const ball = es === "big"
      ? `<circle cx="${x}" cy="98" r="7.5" fill="${a.eyes}"/><circle cx="${x + 2.5}" cy="95.5" r="2.4" fill="#fff"/>`
      : es === "narrow"
      ? `<ellipse cx="${x}" cy="98" rx="6.5" ry="3.8" fill="${a.eyes}"/><circle cx="${x + 2}" cy="97" r="1.2" fill="#fff"/>`
      : `<circle cx="${x}" cy="98" r="5.5" fill="${a.eyes}"/><circle cx="${x + 2}" cy="96" r="1.6" fill="#fff"/>`;
    return ball + `<path d="M${x - 9} 94Q${x} 88 ${x + 9} 94M${x + o * 9} 94l${o * 4} -3" fill="none" stroke="${a.eyes}" stroke-width="2.6" stroke-linecap="round"/>`;
  };
  const b = d => `<path d="${d}" fill="none" stroke="${a.hair}" stroke-width="4" stroke-linecap="round"/>`;
  const brows = m === "worried" ? b("M68 84L94 76M132 84L106 76")
    : m === "happy" ? b("M68 78Q82 68 94 74M106 74Q118 68 132 78")
    : b("M68 80Q82 71 94 77M106 77Q118 71 132 80");
  const mouth = { happy: "M80 114Q100 140 120 114Z", worried: "M86 128Q100 117 114 128", sleepy: "M92 122h16" }[m] || "M85 117Q100 132 115 117";
  return `<circle cx="68" cy="112" r="8" fill="#ff8a8a" opacity=".18"/><circle cx="132" cy="112" r="8" fill="#ff8a8a" opacity=".18"/>` +
    `${eye(82)}${eye(118)}${brows}` +
    `<path d="M98 108q2 4 4 0" fill="none" stroke="#000" stroke-opacity=".25" stroke-width="2" stroke-linecap="round"/>` +
    `<path d="${mouth}" fill="${m === "happy" ? "#c0504d" : "none"}" stroke="${lips}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>` +
    (m === "sleepy" ? `<text x="150" y="50" font-size="22" fill="#9aa4d6">z</text><text x="162" y="34" font-size="16" fill="#9aa4d6">z</text>` : "");
}

function avatarSVG(a, mood = "neutral") {
  const hr = a.hair, sk = a.skin, ac = a.accent || "#7657ff", hs = a.hair_style, os = a.outfit_style || "tee";
  const cap = `<path d="M52 85c0-45 30-60 48-60s48 15 48 60c-10-22-30-30-48-30s-38 8-48 30z" fill="${hr}"/>`;
  const back = {
    bob: `<path d="M46 150C38 60 66 20 100 20C134 20 162 60 154 150Q150 158 138 154L62 154Q50 158 46 150Z" fill="${hr}"/>`,
    ponytail: `<path d="M142 50C190 50 196 125 166 165C170 125 160 95 140 82Z" fill="${hr}"/><circle cx="143" cy="62" r="5" fill="${ac}"/>`,
    afro: `<circle cx="100" cy="68" r="64" fill="${hr}"/>`
  }[hs] || "";
  const front = {
    short: cap, bob: cap, ponytail: cap,
    long: `<path d="M46 175L48 95C46 48 72 22 102 22C138 22 156 52 152 95L154 175L130 175L131 98C128 72 108 56 84 50C74 56 70 76 70 98L70 175Z" fill="${hr}"/><path d="M60 62C55 100 55 140 58 170M144 62C147 100 147 140 144 170" fill="none" stroke="#000" stroke-opacity=".14" stroke-width="2"/>`,
    bun: `<circle cx="100" cy="22" r="18" fill="${hr}"/>` + cap,
    curly: [60, 80, 100, 120, 140].map((x, i) => `<circle cx="${x}" cy="${i % 2 ? 40 : 50}" r="20" fill="${hr}"/>`).join(""),
    spiky: `<path d="M52 85L56 50L70 62L76 30L92 52L104 22L116 52L132 30L134 62L148 50L148 85C138 66 120 58 100 58C80 58 62 66 52 85Z" fill="${hr}"/>`,
    afro: `<path d="M56 80C60 52 80 42 100 42C120 42 140 52 144 80C130 64 70 64 56 80Z" fill="${hr}"/>`,
    bald: ""
  }[hs] ?? cap;
  const body = `<path d="M30 240c0-45 30-75 70-75s70 30 70 75z" fill="${a.outfit}"/>`;
  const top = os === "hoodie"
    ? body + `<path d="M64 182C66 156 84 150 100 150C116 150 134 156 136 182Q100 170 64 182Z" fill="${a.outfit}" stroke="#000" stroke-opacity=".22" stroke-width="2"/><path d="M92 192v24M108 192v24" stroke="#fff" stroke-width="3" stroke-linecap="round"/>`
    : os === "collar"
    ? body + `<path d="M86 164L100 192L114 164Z" fill="${sk}"/><path d="M86 164L100 192L82 186L72 170ZM114 164L100 192L118 186L128 170Z" fill="#fff" stroke="#000" stroke-opacity=".15"/>`
    : body + `<path d="M80 168Q100 204 120 168L112 160H88Z" fill="${sk}"/>`;
  const shape = a.face === "round" ? `<ellipse cx="100" cy="97" rx="53" ry="53" fill="${sk}"/>`
    : a.face === "square" ? `<rect x="52" y="42" width="96" height="112" rx="34" fill="${sk}"/>`
    : `<ellipse cx="100" cy="95" rx="48" ry="56" fill="${sk}"/>`;
  const acc = {
    cap: `<path d="M54 60C54 28 76 14 100 14C124 14 146 28 146 60Z" fill="${ac}"/><path d="M44 60H158Q162 70 150 70H56Q40 70 44 60Z" fill="${ac}" stroke="#000" stroke-opacity=".2"/>`,
    headband: `<path d="M54 72C62 38 138 38 146 72" fill="none" stroke="${ac}" stroke-width="9" stroke-linecap="round"/>`,
    headphones: `<path d="M50 96C48 30 152 30 150 96" fill="none" stroke="${ac}" stroke-width="7"/><rect x="40" y="86" width="16" height="30" rx="7" fill="${ac}"/><rect x="144" y="86" width="16" height="30" rx="7" fill="${ac}"/>`,
    earrings: `<circle cx="50" cy="113" r="3.5" fill="${ac}"/><circle cx="150" cy="113" r="3.5" fill="${ac}"/>`
  }[a.accessory] || "";
  const glasses = a.glasses ? `<g fill="none" stroke="#222" stroke-width="3"><circle cx="82" cy="98" r="13"/><circle cx="118" cy="98" r="13"/><path d="M95 98h10"/></g>` : "";
  const beard = a.beard ? `<path d="M54 115c4 34 22 44 46 44s42-10 46-44c-8 10-16 12-24 12H78c-8 0-16-2-24-12z" fill="${hr}"/>` : "";
  return `<svg viewBox="0 0 200 240" xmlns="http://www.w3.org/2000/svg">${back}
    <rect x="88" y="140" width="24" height="34" fill="${sk}"/>${top}${shape}
    <circle cx="50" cy="98" r="9" fill="${sk}"/><circle cx="150" cy="98" r="9" fill="${sk}"/>
    ${face(a, mood)}${front}${beard}${glasses}${acc}</svg>`;
}

document.addEventListener("DOMContentLoaded", () => {
  const box = document.getElementById("avatar-preview"), form = document.querySelector(".avatar-form");
  if (!box || !form) return;
  const els = () => [...form.querySelectorAll("input[name]:not([name=csrfmiddlewaretoken]),select[name]")];
  const draw = () => {
    const o = {};
    els().forEach(e => o[e.name] = e.type === "checkbox" ? e.checked : e.value);
    box.innerHTML = avatarSVG(o);
  };
  const pick = a => a[Math.floor(Math.random() * a.length)];
  const P = {
    skin: ["#fde0c8", "#efc4a3", "#e0ac69", "#c68642", "#8d5524", "#5c3a21"],
    hair: ["#0a0a0a", "#2b1b12", "#6b3f1d", "#b5651d", "#e6c27a", "#c0392b", "#7d3cff"],
    eyes: ["#0d0d0d", "#3b2a1a", "#2f6f4e", "#3b6fb6", "#6b4b3a"],
    lips: ["#d9777f", "#c0504d", "#e89aa5", "#a64b5f", "#d68a7a"]
  };
  const COL = ["#7657ff", "#ff6b81", "#2ec4b6", "#f7b955", "#4d8dff", "#ffffff", "#222222"];
  const saved = els().map(e => [e, e.type === "checkbox" ? e.checked : e.value]);
  document.getElementById("avatar-random").onclick = () => {
    els().forEach(e => {
      if (e.name === "tone") return;
      if (e.type === "checkbox") e.checked = Math.random() < 0.25;
      else if (e.tagName === "SELECT") e.selectedIndex = Math.floor(Math.random() * e.options.length);
      else e.value = pick(P[e.name] || COL);
    });
    draw();
  };
  document.getElementById("avatar-reset").onclick = () => {
    saved.forEach(([e, v]) => { if (e.type === "checkbox") e.checked = v; else e.value = v; });
    draw();
  };
  form.addEventListener("input", draw);
  draw();
});