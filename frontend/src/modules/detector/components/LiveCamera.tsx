import { useEffect, useRef, useState } from "react";
import { toast } from "react-toastify";

export default function LiveCamera() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [active, setActive] = useState(false);
  const [lastResult, setLastResult] = useState<any>(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        setActive(true);
      }
    } catch {
      toast.error("No se pudo acceder a la cámara");
    }
  };

  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((t) => t.stop());
    }
    setActive(false);
  };

  // CAPTURAR FRAME Y ENVIAR AL BACKEND
  const captureFrame = async () => {
    if (!videoRef.current) return;

    const canvas = document.createElement("canvas");
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(videoRef.current, 0, 0);

    canvas.toBlob(async (blob) => {
      if (!blob) return;

      const formData = new FormData();
      formData.append("file", blob, "frame.jpg");

      try {
        const res = await fetch(
          "http://localhost:8000/api/detect/live-frame?confidence=0.25",
          {
            method: "POST",
            body: formData,
          }
        );

        const data = await res.json();

        if (!res.ok) {
          toast.error(data.detail || "Error detectando");
          return;
        }

        setLastResult(data);

        // --------- NOTIFICACIONES ---------
        const threshold = 0.90;
        const detecta = data.detections?.some(
          (d: any) => d.confidence >= threshold
        );

        detecta
          ? toast.success("Uniforme detectado", { autoClose: 1500 })
          : toast.error("No se detectó uniforme", { autoClose: 1500 });
        // ----------------------------------

      } catch {
        toast.error("Error enviando frame");
      }
    }, "image/jpeg");
  };

  useEffect(() => () => stopCamera(), []);

  return (
    <div className="flex flex-col items-start w-full">
      <label className="block mb-3 text-sm text-gray-300">
        Active la cámara (permita el acceso)
      </label>

      <div className="flex gap-3">
        {!active ? (
          <button
            onClick={startCamera}
            className="bg-blue-600 px-4 py-2 rounded text-white"
          >
            Activar Cámara
          </button>
        ) : (
          <button
            onClick={stopCamera}
            className="bg-red-600 px-4 py-2 rounded text-white"
          >
            Detener Cámara
          </button>
        )}

        <button
          onClick={captureFrame}
          className="bg-green-600 px-4 py-2 rounded text-white"
        >
          Detectar
        </button>
      </div>

      {/* VIDEO */}
      <div className="mt-8 w-full h-48 rounded border border-gray-600 bg-[#0f1218] flex items-center justify-center">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          className="w-full h-full object-cover rounded"
        ></video>
      </div>

      {/* RESULTADO DEBAJO DEL VIDEO */}
      {lastResult && (
        <div className="mt-5 p-4 bg-[#1a1f29] text-gray-300 rounded-md border border-gray-700 w-full">
          <h3 className="text-lg font-semibold mb-2">Resultado</h3>

          <p className="text-sm">
            <strong>Detecciones:</strong> {lastResult.detections_count}
          </p>

          {lastResult.detections?.map((d: any, i: number) => (
            <div key={i} className="mt-2 p-2 bg-black/30 rounded">
              <p><strong>Confianza:</strong> {d.confidence}</p>
              <p><strong>Clase:</strong> {d.class}</p>
              <p><strong>BBox:</strong> {JSON.stringify(d.bbox)}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
