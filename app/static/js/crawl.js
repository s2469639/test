// 대시보드 "크롤링 새로고침" 버튼: 눌리면 백그라운드 크롤링 시작, 진행 중에는
// 작은 스피너 아이콘을 옆에 표시하고 주기적으로 상태를 확인한다.
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("crawl-btn");
  const spinner = document.getElementById("crawl-spinner");
  const message = document.getElementById("crawl-message");
  if (!btn) return;

  let pollTimer = null;

  function setRunning(running) {
    btn.disabled = running;
    spinner.hidden = !running;
  }

  function poll() {
    fetch("/crawl/status")
      .then((res) => res.json())
      .then((data) => {
        setRunning(data.running);
        if (data.running) {
          message.textContent = "크롤링 진행 중...";
          return;
        }
        clearInterval(pollTimer);
        pollTimer = null;

        if (data.error) {
          message.textContent = `오류: ${data.error}`;
        } else if (data.finished_at) {
          let text =
            `완료 (신규 ${data.new_count}건, 업데이트 ${data.updated_count}건, ` +
            `비활성 ${data.deactivated_count}건) — 새로고침하면 반영됩니다`;
          if (data.failed_labels && data.failed_labels.length) {
            text += ` / 크롤링 실패한 카테고리: ${data.failed_labels.join(", ")}`;
          }
          message.textContent = text;
        }
      })
      .catch(() => {
        clearInterval(pollTimer);
        pollTimer = null;
        setRunning(false);
        message.textContent = "상태 확인에 실패했습니다.";
      });
  }

  btn.addEventListener("click", () => {
    message.textContent = "";
    fetch("/crawl/run", { method: "POST" })
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "already_running") {
          message.textContent = "이미 크롤링이 진행 중입니다.";
        }
        setRunning(true);
        if (!pollTimer) {
          pollTimer = setInterval(poll, 2000);
        }
      })
      .catch(() => {
        message.textContent = "크롤링 시작에 실패했습니다.";
      });
  });

  // 페이지를 새로 열었을 때도 이미 돌고 있는 크롤링이 있으면 이어서 표시
  fetch("/crawl/status")
    .then((res) => res.json())
    .then((data) => {
      setRunning(data.running);
      if (data.running && !pollTimer) {
        message.textContent = "크롤링 진행 중...";
        pollTimer = setInterval(poll, 2000);
      }
    });
});
