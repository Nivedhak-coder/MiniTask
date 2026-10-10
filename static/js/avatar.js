function avatarSVG(a) {
  const h = {
    short: `<path d="M52 85c0-45 30-60 48-60s48 15 48 60c-10-22-30-30-48-30s-38 8-48 30z" fill="${a.hair}"/>`,
    long: `<path d="M48 90c0-50 28-66 52-66s52 16 52 66v70h-22V90c-10-20-60-20-60 0v70H48z" fill="${a.hair}"/>`,
    bun: `<circle cx="100" cy="22" r="18" fill="${a.hair}"/><path d="M52 85c0-45 30-60 48-60s48 15 48 60c-10-22-30-30-48-30s-38 8-48 30z" fill="${a.hair}"/>`,
    curly: [60, 80, 100, 120, 140].map((x, i) => `<circle cx="${x}" cy="${i % 2 ? 40 : 50}" r="20" fill="${a.hair}"/>`).join(""),
    bald: ""
  }[a.hair_style] || "";
  const glasses = a.glasses ? `<g fill="none" stroke="#222" stroke-width="3"><circle cx="82" cy="98" r="13"/><circle cx="118" cy="98" r="13"/><path d="M95 98h10"/></g>` : "";
  const beard = a.beard ? `<path d="M54 115c4 34 22 44 46 44s42-10 46-44c-8 10-16 12-24 12H78c-8 0-16-2-24-12z" fill="${a.hair}"/>` : "";
  return `<svg viewBox="0 0 200 240" xmlns="http://www.w3.org/2000/svg">
    <rect x="88" y="140" width="24" height="34" fill="${a.skin}"/>
    <path d="M30 240c0-45 30-75 70-75s70 30 70 75z" fill="${a.outfit}"/>
    <ellipse cx="100" cy="95" rx="48" ry="56" fill="${a.skin}"/>
    <circle cx="52" cy="98" r="9" fill="${a.skin}"/><circle cx="148" cy="98" r="9" fill="${a.skin}"/>
    ${h}${beard}
    <circle cx="82" cy="98" r="5" fill="${a.eyes}"/><circle cx="118" cy="98" r="5" fill="${a.eyes}"/>
    <path d="M84 118Q100 132 116 118" fill="none" stroke="#3b2a2a" stroke-width="3" stroke-linecap="round"/>
    ${glasses}</svg>`;
}

document.addEventListener("DOMContentLoaded", () => {
  const box = document.getElementById("avatar-preview");
  if (!box) return;
  const v = id => document.getElementById(id);
  const draw = () => box.innerHTML = avatarSVG({
    skin: v("id_skin").value, eyes: v("id_eyes").value, hair: v("id_hair").value, outfit: v("id_outfit").value,
    hair_style: v("id_hair_style").value,
    glasses: v("id_glasses").checked, beard: v("id_beard").checked
  });
  document.querySelectorAll(".avatar-form input, .avatar-form select")
    .forEach(e => e.addEventListener("input", draw));
  draw();
});