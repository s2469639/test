// 기안서 작성: "기안서 자동 생성하기" 버튼 -> AI 호출, 폼 제출 -> 초안 저장
document.addEventListener("DOMContentLoaded", () => {
  const generateBtn = document.getElementById("generate-proposal-btn");
  const form = document.getElementById("proposal-form");
  const exhibitionId = window.location.pathname.split("/")[2];

  if (generateBtn) {
    generateBtn.addEventListener("click", async () => {
      generateBtn.disabled = true;
      generateBtn.textContent = "생성 중...";

      try {
        const res = await fetch(`/exhibitions/${exhibitionId}/proposal/generate`, {
          method: "POST",
        });
        const data = await res.json();
        form.querySelector("[name=content]").value = data.content || "";
      } catch (err) {
        alert("기안서 생성에 실패했습니다.");
      } finally {
        generateBtn.disabled = false;
        generateBtn.textContent = "기안서 자동 생성하기";
      }
    });
  }

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = Object.fromEntries(new FormData(form).entries());
      await fetch(`/exhibitions/${exhibitionId}/proposal/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      alert("초안이 저장되었습니다.");
    });
  }
});
