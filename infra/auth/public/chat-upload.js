(function () {
  var AUTH_ORIGIN = "https://ia.fvmarketing.com.br";
  var ALLOWED_EXT = [
    "pdf","doc","docx","odt","rtf","xls","xlsx","csv","ppt","pptx",
    "txt","md","json","html","htm","png","jpg","jpeg","gif","bmp","webp"
  ];

  // Floating button
  var btn = document.createElement("button");
  btn.id = "oc-attach-fab";
  btn.title = "Anexar arquivo para o agente ler";
  btn.textContent = "📎";
  btn.setAttribute("style",
    "position:fixed;right:18px;bottom:18px;z-index:99999;" +
    "width:46px;height:46px;border-radius:50%;border:none;cursor:pointer;" +
    "background:#e63946;color:#fff;font-size:20px;line-height:46px;text-align:center;" +
    "box-shadow:0 6px 18px rgba(0,0,0,.35);transition:transform .15s;"
  );
  btn.onmouseenter = function () { btn.style.transform = "scale(1.08)"; };
  btn.onmouseleave = function () { btn.style.transform = "scale(1)"; };

  // Hidden file input
  var input = document.createElement("input");
  input.type = "file";
  input.multiple = true;
  input.style.display = "none";
  input.accept = "." + ALLOWED_EXT.join(",.");

  btn.onclick = function () { input.click(); };

  document.body.appendChild(btn);
  document.body.appendChild(input);

  function toast(msg, ok) {
    var t = document.createElement("div");
    t.textContent = msg;
    t.setAttribute("style",
      "position:fixed;right:18px;bottom:74px;z-index:99999;max-width:280px;" +
      "padding:10px 14px;border-radius:10px;font:500 13px/1.4 Inter,sans-serif;" +
      "color:#fff;background:" + (ok ? "#1f9d55" : "#b3261e") + ";" +
      "box-shadow:0 6px 18px rgba(0,0,0,.35);opacity:0;transition:opacity .25s;"
    );
    document.body.appendChild(t);
    requestAnimationFrame(function () { t.style.opacity = "1"; });
    setTimeout(function () {
      t.style.opacity = "0";
      setTimeout(function () { t.remove(); }, 300);
    }, 4200);
  }

  input.onchange = function () {
    var files = input.files;
    if (!files || !files.length) return;
    var pending = files.length;
    var done = 0;
    var errors = 0;
    for (var i = 0; i < files.length; i++) {
      (function (file) {
        var fd = new FormData();
        fd.append("file", file);
        fetch(AUTH_ORIGIN + "/api/upload", {
          method: "POST",
          body: fd,
          credentials: "include"
        })
          .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
          .then(function (res) {
            if (res.ok && res.j && res.j.success) {
              done++;
            } else {
              errors++;
              if (res.j && res.j.error) toast("Erro: " + res.j.error, false);
            }
          })
          .catch(function (e) { errors++; })
          .finally(function () {
            pending--;
            if (pending === 0) {
              if (errors === 0) toast("Enviado ✓ O agente lê automaticamente no próximo comando.", true);
              else if (done > 0) toast(done + " enviado(s), " + errors + " falhou(ram).", false);
              else toast("Falha no envio. Tente novamente.", false);
            }
          });
      })(files[i]);
    }
    input.value = "";
  };
})();
