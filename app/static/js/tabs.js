// 박람회 상세 페이지 탭 전환
document.addEventListener("DOMContentLoaded", () => {
  const tabButtons = document.querySelectorAll(".tabs button[data-tab]");
  const panels = document.querySelectorAll("[data-tab-panel]");

  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.tab;

      tabButtons.forEach((b) => b.classList.toggle("active", b === btn));
      panels.forEach((p) =>
        p.classList.toggle("active", p.dataset.tabPanel === target)
      );
    });
  });
});
