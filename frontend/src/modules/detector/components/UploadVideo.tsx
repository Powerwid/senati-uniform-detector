import { useState } from "react";
import { toast } from "react-toastify";

export default function UploadVideo() {
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);

  const handleUpload = async () => {
    const input = document.getElementById("video-input") as HTMLInputElement;
    const file = input?.files?.[0];

    if (!file) return toast.error("Selecciona un video");
    if (!file.type.startsWith("video/")) return toast.error("Debe ser un video");

    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(
        "http://localhost:8000/api/detect/video?confidence=0.25",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await res.json();

      if (!res.ok) {
        toast.error(data.detail || "Error al analizar video");
        return;
      }

      // -------------------------------
      //  VALIDAR DETECCIONES EN VIDEO
      // -------------------------------
      const threshold = 0.90;
      let uniformeDetectado = false;

      data.results.forEach((frame: any) => {
        const detecta = frame.detections?.some(
          (d: any) => d.confidence >= threshold
        );
        if (detecta) uniformeDetectado = true;
      });

      if (uniformeDetectado) {
        toast.success("Uniforme detectado en el video", { autoClose: 2000 });
      } else {
        toast.error("No se detectó uniforme en el video", { autoClose: 2000 });
      }

      console.log("RESULTADO VIDEO:", data);

    } catch {
      toast.error("Error al subir video");
    } finally {
      setLoading(false);
    }
  };

  const handlePreview = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const url = URL.createObjectURL(file);
    setPreview(url);
  };

  return (
    <div>
      <label className="block mb-3 text-sm text-gray-300">
        Seleccionar video (MP4/AVI)
      </label>

      <input
        id="video-input"
        type="file"
        accept="video/*"
        onChange={handlePreview}
        className="hidden"
      />

      <button
        onClick={() => document.getElementById("video-input")?.click()}
        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md text-white mb-4"
      >
        Subir Video
      </button>

      <button
        onClick={handleUpload}
        className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-md text-white ml-3"
      >
        Detectar
      </button>

      {/* PREVIEW */}
      <div className="mt-4">
        {preview ? (
          <video
            src={preview}
            controls
            className="w-full h-48 object-cover rounded-md border border-[#334155]"
          />
        ) : (
          <div className="w-full h-48 bg-black/60 rounded-md border border-[#334155]" />
        )}
      </div>

      {loading && <p className="text-sm text-blue-400 mt-2">Procesando...</p>}
    </div>
  );
}
