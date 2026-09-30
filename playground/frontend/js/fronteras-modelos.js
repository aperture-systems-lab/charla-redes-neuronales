// Una red densa para dos clases: una sola neurona sigmoide a la salida da p(clase B).
// Se entrena con Adam sobre todo el lote. Con tamanos = [2, 1] no tiene capas ocultas:
// es exactamente una regresión logística.

const ACTIVACIONES = {
  tanh: { f: Math.tanh, d: (a) => 1 - a * a },
  relu: { f: (z) => (z > 0 ? z : 0), d: (a) => (a > 0 ? 1 : 0) },
  sigmoide: { f: (z) => 1 / (1 + Math.exp(-z)), d: (a) => a * (1 - a) },
};

function gauss() {
  const u = 1 - Math.random();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * Math.random());
}

export class Red {
  constructor(tamanos, activacion = "tanh", tasa = 0.03) {
    this.tamanos = tamanos;
    this.activacion = ACTIVACIONES[activacion];
    this.tasa = tasa;
    this.epoca = 0;
    this.paso = 0;
    this.perdida = NaN;
    this.acierto = NaN;

    this.capas = tamanos.slice(1).map((salen, l) => {
      const entran = tamanos[l];
      const oculta = l < tamanos.length - 2;
      const escala = Math.sqrt((activacion === "relu" && oculta ? 2 : 1) / entran);
      const n = salen * entran;

      return {
        entran,
        salen,
        W: Float64Array.from({ length: n }, () => gauss() * escala),
        b: new Float64Array(salen),
        gW: new Float64Array(n),
        gb: new Float64Array(salen),
        mW: new Float64Array(n),
        vW: new Float64Array(n),
        mb: new Float64Array(salen),
        vb: new Float64Array(salen),
      };
    });

    this.a = tamanos.map((n) => new Float64Array(n));
    this.delta = tamanos.map((n) => new Float64Array(n));
    this.probs = new Float64Array(2);
  }

  get parametros() {
    return this.capas.reduce((suma, c) => suma + c.W.length + c.b.length, 0);
  }

  predecir(x, y) {
    const a = this.a;
    a[0][0] = x;
    a[0][1] = y;

    const ultima = this.capas.length - 1;
    for (let l = 0; l <= ultima; l++) {
      const { W, b, entran, salen } = this.capas[l];
      const ent = a[l];
      const sal = a[l + 1];

      for (let j = 0; j < salen; j++) {
        let z = b[j];
        const fila = j * entran;
        for (let i = 0; i < entran; i++) z += W[fila + i] * ent[i];
        sal[j] = z;
      }

      if (l < ultima) {
        for (let j = 0; j < salen; j++) sal[j] = this.activacion.f(sal[j]);
      } else {
        sal[0] = 1 / (1 + Math.exp(-sal[0]));
      }
    }

    // [p(A), p(B)], para que el dibujo trate igual a la red y al árbol.
    const p = a[a.length - 1][0];
    this.probs[0] = 1 - p;
    this.probs[1] = p;
    return this.probs;
  }

  entrenar(puntos, epocas = 1) {
    const n = puntos.length;
    if (!n) return;

    const L = this.capas.length;
    for (let e = 0; e < epocas; e++) {
      for (const c of this.capas) {
        c.gW.fill(0);
        c.gb.fill(0);
      }

      let perdida = 0;
      let aciertos = 0;

      for (const punto of puntos) {
        const p = this.predecir(punto.x, punto.y)[1];

        if ((p > 0.5 ? 1 : 0) === punto.clase) aciertos++;
        perdida -= Math.log(Math.max(punto.clase ? p : 1 - p, 1e-12));

        // Entropía cruzada binaria + sigmoide: el error de la salida es simplemente p − y.
        this.delta[L][0] = p - punto.clase;

        for (let l = L - 1; l >= 0; l--) {
          const { W, gW, gb, entran, salen } = this.capas[l];
          const ent = this.a[l];
          const dSig = this.delta[l + 1];
          const dEnt = this.delta[l];

          if (l > 0) dEnt.fill(0);

          for (let j = 0; j < salen; j++) {
            const d = dSig[j];
            gb[j] += d;
            const fila = j * entran;
            for (let i = 0; i < entran; i++) {
              gW[fila + i] += d * ent[i];
              if (l > 0) dEnt[i] += W[fila + i] * d;
            }
          }

          if (l > 0) {
            for (let i = 0; i < entran; i++) dEnt[i] *= this.activacion.d(ent[i]);
          }
        }
      }

      this.adam(n);
      this.epoca++;
      this.perdida = perdida / n;
      this.acierto = aciertos / n;
    }
  }

  adam(n) {
    const B1 = 0.9;
    const B2 = 0.999;
    this.paso++;
    const c1 = 1 - B1 ** this.paso;
    const c2 = 1 - B2 ** this.paso;

    const actualizar = (P, G, M, V) => {
      for (let i = 0; i < P.length; i++) {
        const g = G[i] / n;
        M[i] = B1 * M[i] + (1 - B1) * g;
        V[i] = B2 * V[i] + (1 - B2) * g * g;
        P[i] -= (this.tasa * (M[i] / c1)) / (Math.sqrt(V[i] / c2) + 1e-8);
      }
    };

    for (const c of this.capas) {
      actualizar(c.W, c.gW, c.mW, c.vW);
      actualizar(c.b, c.gb, c.mb, c.vb);
    }
  }
}

// Árbol de decisión CART: en cada nodo, el corte "x < u" o "y < u" que más baja el Gini.

function gini(conteo, n) {
  if (!n) return 0;
  let suma = 0;
  for (const c of conteo) suma += (c / n) ** 2;
  return 1 - suma;
}

export class Arbol {
  constructor(profundidadMax = 5) {
    this.profundidadMax = profundidadMax;
    this.raiz = null;
  }

  ajustar(puntos, K) {
    this.K = K;
    this.hojas = 0;
    this.profundidad = 0;
    this.raiz = puntos.length ? this.crecer(puntos, 0) : null;

    let aciertos = 0;
    for (const p of puntos) if (this.nodoDe(p.x, p.y).clase === p.clase) aciertos++;
    this.acierto = puntos.length ? aciertos / puntos.length : NaN;
  }

  crecer(puntos, nivel) {
    const conteo = new Array(this.K).fill(0);
    for (const p of puntos) conteo[p.clase]++;

    const n = puntos.length;
    const clase = conteo.indexOf(Math.max(...conteo));
    const nodo = { conteo, clase, probs: conteo.map((c) => c / n) };
    this.profundidad = Math.max(this.profundidad, nivel);

    const corte = nivel < this.profundidadMax && gini(conteo, n) > 0 ? this.mejorCorte(puntos, conteo) : null;
    if (!corte) {
      this.hojas++;
      return nodo;
    }

    const { eje, umbral } = corte;
    nodo.eje = eje;
    nodo.umbral = umbral;
    nodo.izq = this.crecer(puntos.filter((p) => p[eje] < umbral), nivel + 1);
    nodo.der = this.crecer(puntos.filter((p) => p[eje] >= umbral), nivel + 1);
    return nodo;
  }

  mejorCorte(puntos, conteo) {
    const n = puntos.length;
    const base = gini(conteo, n);
    let mejor = null;

    for (const eje of ["x", "y"]) {
      const orden = [...puntos].sort((a, b) => a[eje] - b[eje]);
      const izq = new Array(this.K).fill(0);
      const der = [...conteo];

      for (let i = 1; i < n; i++) {
        izq[orden[i - 1].clase]++;
        der[orden[i - 1].clase]--;
        if (orden[i][eje] === orden[i - 1][eje]) continue;

        const impureza = (i * gini(izq, i) + (n - i) * gini(der, n - i)) / n;
        if (base - impureza > 1e-9 && (!mejor || impureza < mejor.impureza)) {
          mejor = { eje, umbral: (orden[i][eje] + orden[i - 1][eje]) / 2, impureza };
        }
      }
    }
    return mejor;
  }

  nodoDe(x, y) {
    let nodo = this.raiz;
    while (nodo.eje) nodo = (nodo.eje === "x" ? x : y) < nodo.umbral ? nodo.izq : nodo.der;
    return nodo;
  }

  predecir(x, y) {
    return this.nodoDe(x, y).probs;
  }
}
