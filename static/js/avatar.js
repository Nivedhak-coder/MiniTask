function face(a, m = "neutral") {
  const lips = a.lips || "#d9777f";
  const arc = (x, y, cy) => `<path d="M${x - 8} ${y}Q${x} ${cy} ${x + 8} ${y}" fill="none" stroke="${a.eyes}" stroke-width="3.5" stroke-linecap="round"/>`;
  const eye = x => {
    const o = x < 100 ? -1 : 1;
    if (m === "happy") return arc(x, 100, 88);
    if (m === "sleepy") return arc(x, 98, 105);
    return `<circle cx="${x}" cy="98" r="5.5" fill="${a.eyes}"/><circle cx="${x + 2}" cy="96" r="1.6" fill="#fff"/>` +
      `<path d="M${x - 9} 94Q${x} 88 ${x + 9} 94M${x + o * 9} 94l${o * 4} -3" fill="none" stroke="${a.eyes}" stroke-width="2.6" stroke-linecap="round"/>`;
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
  const hr = a.hair, sk = a.skin;
  const hairs = {
    short: `<path d="M52 85c0-45 30-60 48-60s48 15 48 60c-10-22-30-30-48-30s-38 8-48 30z" fill="${hr}"/>`,
    long: `<path d="M46 175L48 95C46 48 72 22 102 22C138 22 156 52 152 95L154 175L130 175L131 98C128 72 108 56 84 50C74 56 70 76 70 98L70 175Z" fill="${hr}"/><path d="M60 62C55 100 55 140 58 170M144 62C147 100 147 140 144 170" fill="none" stroke="#000" stroke-opacity=".14" stroke-width="2"/>`,
    bun: `<circle cx="100" cy="22" r="18" fill="${hr}"/><path d="M52 85c0-45 30-60 48-60s48 15 48 60c-10-22-30-30-48-30s-38 8-48 30z" fill="${hr}"/>`,
    curly: [60, 80, 100, 120, 140].map((x, i) => `<circle cx="${x}" cy="${i % 2 ? 40 : 50}" r="20" fill="${hr}"/>`).join(""),
    bald: ""
  }[a.hair_style] || "";
  const glasses = a.glasses ? `<g fill="none" stroke="#222" stroke-width="3"><circle cx="82" cy="98" r="13"/><circle cx="118" cy="98" r="13"/><path d="M95 98h10"/></g>` : "";
  const beard = a.beard ? `<path d="M54 115c4 34 22 44 46 44s42-10 46-44c-8 10-16 12-24 12H78c-8 0-16-2-24-12z" fill="${hr}"/>` : "";
  return `<svg viewBox="0 0 200 240" xmlns="http://www.w3.org/2000/svg">
    <rect x="88" y="140" width="24" height="34" fill="${sk}"/>
    <path d="M30 240c0-45 30-75 70-75s70 30 70 75z" fill="${a.outfit}"/>
    <path d="M80 168Q100 204 120 168L112 160H88Z" fill="${sk}"/>
    <ellipse cx="100" cy="95" rx="48" ry="56" fill="${sk}"/>
    <circle cx="52" cy="98" r="9" fill="${sk}"/><circle cx="148" cy="98" r="9" fill="${sk}"/>
    ${face(a, mood)}${hairs}${beard}${glasses}</svg>`;
}
document.addEventListener("DOMContentLoaded", () => {
  const box = document.getElementById("avatar-preview");
  if (!box) return;
  const v = id => document.getElementById(id);
  const draw = () => box.innerHTML = avatarSVG({
    skin: v("id_skin").value, eyes: v("id_eyes").value, lips: v("id_lips").value, hair: v("id_hair").value, outfit: v("id_outfit").value,
    hair_style: v("id_hair_style").value,
    glasses: v("id_glasses").checked, beard: v("id_beard").checked
  });
  document.querySelectorAll(".avatar-form input, .avatar-form select")
    .forEach(e => e.addEventListener("input", draw));
  draw();
});