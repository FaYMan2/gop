

async function downloadWithProgress(id, filename) {

    const progress = document.getElementById(`progress-${id}`);
    const response = await fetch(`/download/${id}`);

    const reader = response.body.getReader();
    const contentLength = +response.headers.get("Content-Length");

    let received = 0;
    const chunks = [];

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      chunks.push(value);
      received += value.length;
      progress.value = (received / contentLength) * 100;
    }

    const blob = new Blob(chunks);
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
}

function readText(text) {
    alert(text);
}

function copyText(text) {
    if (!navigator.clipboard) {
      // fallback for HTTP/IP environments
      const textarea = document.createElement("textarea");
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      textarea.remove();
      alert("Copied (fallback)");
      return;
    }
  
    navigator.clipboard.writeText(text)
      .then(() => alert("Copied"))
      .catch(err => alert("Copy failed: " + err));
}