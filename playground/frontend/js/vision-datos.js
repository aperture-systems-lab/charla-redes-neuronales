export const RUTAS = {
  manos: "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
  cara: "face_landmarker/face_landmarker/float16/1/face_landmarker.task",
  segmentacion: "image_segmenter/selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite",
  clasificacion: "image_classifier/efficientnet_lite0/float32/1/efficientnet_lite0.tflite",
};

export const REDES = [
  { clave: "manos", nombre: "manos", detalle: "21 puntos por mano", icono: "🖐️", tono: "--ambar" },
  { clave: "cara", nombre: "cara", detalle: "malla de 478 puntos", icono: "🙂", tono: "--turquesa" },
  { clave: "segmentacion", nombre: "segmentación", detalle: "cada píxel: pelo, piel, ropa…", icono: "🎨", tono: "--morado" },
  { clave: "clasificacion", nombre: "clasificación", detalle: "¿qué hay en la imagen? 1000 clases", icono: "🏷️", tono: "--azul" },
];

export const SEGMENTOS = {
  etiquetas: ["fondo", "pelo", "piel del cuerpo", "piel de la cara", "ropa", "accesorios"],
  colores: [null, "--ambar", "--rosa", "--coral", "--morado", "--verde"],
};
