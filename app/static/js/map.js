// 대시보드 세계 지도: 대륙별 핀 클릭 시 해당 대륙 목록 페이지로 이동
document.addEventListener("DOMContentLoaded", () => {
  const mapEl = document.getElementById("world-map");
  if (!mapEl) return;

  const counts = JSON.parse(mapEl.dataset.counts || "{}");

  // TODO: 실제 지도(SVG) 위에 대륙별 좌표로 핀을 배치하고 클릭 이벤트 연결.
  // 지금은 최소 동작만: 대륙명을 클릭하면 /continent/<대륙>으로 이동.
  Object.keys(counts).forEach((continent) => {
    const pin = document.createElement("button");
    pin.className = "map-pin";
    pin.textContent = `${continent} (${counts[continent]})`;
    pin.addEventListener("click", () => {
      window.location.href = `/continent/${encodeURIComponent(continent)}`;
    });
    mapEl.appendChild(pin);
  });
});
