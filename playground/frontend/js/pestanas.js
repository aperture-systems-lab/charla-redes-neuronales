const aClave = (pestana) => pestana.id.replace(/^(tab|sub)-/, "");

export function montarPestanas(lista, { conHash = false, evento = "pestana" } = {}) {
  const pestanas = [...lista.querySelectorAll('[role="tab"]')];

  function activar(id, guardar = true) {
    for (const pestana of pestanas) {
      const suya = pestana.id === id;
      const vista = document.getElementById(pestana.getAttribute("aria-controls"));

      pestana.setAttribute("aria-selected", String(suya));
      pestana.tabIndex = suya ? 0 : -1;
      vista.hidden = !suya;

      if (suya && conHash && guardar) history.replaceState(null, "", `#${aClave(pestana)}`);
    }

    const clave = aClave(pestanas.find((p) => p.id === id));
    document.dispatchEvent(new CustomEvent(evento, { detail: clave }));
  }

  for (const pestana of pestanas) {
    pestana.addEventListener("click", () => activar(pestana.id));

    pestana.addEventListener("keydown", (ev) => {
      const salto = { ArrowRight: 1, ArrowLeft: -1 }[ev.key];
      if (!salto) return;

      ev.preventDefault();
      const i = pestanas.indexOf(pestana);
      const destino = pestanas[(i + salto + pestanas.length) % pestanas.length];
      activar(destino.id);
      destino.focus();
    });
  }

  const pedida = () => pestanas.find((p) => aClave(p) === location.hash.slice(1));
  activar(((conHash && pedida()) || pestanas[0]).id, false);

  if (conHash) {
    window.addEventListener("hashchange", () => {
      const destino = pedida();
      if (destino) activar(destino.id, false);
    });
  }
}

// Los módulos que cargan después leen con esto la pestaña inicial; luego escuchan el evento.
export const pestanaActual = () =>
  aClave(document.querySelector('.pestanas [role="tab"][aria-selected="true"]'));

montarPestanas(document.querySelector(".pestanas"), { conHash: true });
