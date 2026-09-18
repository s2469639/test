// 부스 컨셉 기획: "컨셉 자동 생성하기" 버튼 -> AI 호출 -> 폼에 채워넣기
document.addEventListener("DOMContentLoaded", () => {
  const generateBtn = document.getElementById("generate-concept-btn");
  const emptyState = document.getElementById("concept-empty");
  const form = document.getElementById("concept-form");

  if (generateBtn) {
    generateBtn.addEventListener("click", async () => {
      const exhibitionId = generateBtn.dataset.exhibitionId;
      generateBtn.disabled = true;
      generateBtn.textContent = "생성 중...";

      try {
        const res = await fetch(`/exhibitions/${exhibitionId}/concept/generate`, {
          method: "POST",
        });
        const data = await res.json();

        // TODO: services/llm.py가 구조화된 JSON(theme/slogan/selling_points/event_plan)을
        // 반환하도록 개선되면 아래 필드 채우기를 그에 맞게 수정
        if (form) {
          form.querySelector("[name=selling_points]").value = data.raw_text || "";
        }

        emptyState.hidden = true;
        form.hidden = false;
      } catch (err) {
        alert("컨셉 생성에 실패했습니다.");
      } finally {
        generateBtn.disabled = false;
        generateBtn.textContent = "컨셉 자동 생성하기";
      }
    });
  }

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const exhibitionId = generateBtn
        ? generateBtn.dataset.exhibitionId
        : window.location.pathname.split("/")[2];

      const payload = Object.fromEntries(new FormData(form).entries());
      await fetch(`/exhibitions/${exhibitionId}/concept/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      alert("초안이 저장되었습니다.");
    });
  }
});
