import { useState } from "react";
import { toast } from "react-toastify";

export default function UploadImage() {
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const handleUpload = async () => {
    const input = document.getElementById("image-input") as HTMLInputElement;
    const file = input?.files?.[0];

    if (!file) return toast.error("Selecciona una imagen");

    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(
        "http://localhost:8000/api/detect?confidence=0.25",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await res.json();

      if (!res.ok) {
        toast.error(data.detail || "Error en la detección");
        return;
      }

      // --- Validación por confianza ---
      const threshold = 0.9;
      const detecta = data.detections?.some(
        (d: any) => d.confidence >= threshold
      );

      if (detecta) {
        toast.success("Uniforme detectado", { autoClose: 1500 });
      } else {
        toast.error("No se detectó uniforme", { autoClose: 1500 });
      }

      setResult(data); // ← guardar resultado en pantalla

    } catch {
      toast.error("Error al enviar imagen");
    } finally {
      setLoading(false);
    }
  };

  const handlePreview = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const url = URL.createObjectURL(file);
    setPreview(url);
    setResult(null); // limpiar resultado anterior
  };

  return (
    <div>
      <label className="block mb-3 text-sm text-gray-300">
        Seleccionar imagen (JPG/PNG)
      </label>

      <input
        id="image-input"
        type="file"
        accept="image/*"
        onChange={handlePreview}
        className="hidden"
      />

      <button
        onClick={() => document.getElementById("image-input")?.click()}
        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md text-white mb-4"
      >
        Subir Imagen
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
          <img
            src={preview}
            alt="preview"
            className="w-full h-48 object-cover rounded-md border border-[#334155]"
          />
        ) : (
          <div className="w-full h-48 bg-black/60 rounded-md border border-[#334155]" />
        )}
      </div>

      {loading && (
        <p className="text-sm text-blue-400 mt-2">Procesando imagen...</p>
      )}

      {/* ============================= */}
      {/*   RESULTADO DE LA DETECCIÓN   */}
      {/* ============================= */}
      {result && (
        <div className="mt-5 p-4 bg-[#1a1f29] text-gray-300 rounded-md border border-gray-700 w-full">
          <h3 className="text-lg font-semibold mb-2">Resultado</h3>

          <p className="text-sm">
            <strong>Detecciones:</strong> {result.detections_count}
          </p>

          {result.detections?.map((d: any, i: number) => (
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
