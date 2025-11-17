import UploadImage from "../components/UploadImage";
import UploadVideo from "../components/UploadVideo";
import LiveCamera from "../components/LiveCamera";

export default function DetectorPage() {
  return (
    <div className="w-full min-h-screen bg-[#0f172a] text-white px-6 py-10">
      
      {/* Título */}
      <h1 className="text-3xl font-bold mb-6 text-center">
        Detector de Uniformes SENATI
      </h1>

      <p className="text-center text-gray-300 mb-10 max-w-2xl mx-auto">
        Selecciona una opción para realizar la detección. Puedes subir una imagen,
        un video o usar la cámara en vivo.
      </p>

      {/* Contenedor de opciones */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">

        {/* Subir imagen */}
        <div className="bg-[#1e293b] p-6 rounded-xl shadow-md border border-[#334155]">
          <h2 className="text-xl font-semibold mb-4">Subir Imagen</h2>
          <UploadImage />
        </div>

        {/* Cámara */}
        <div className="bg-[#1e293b] p-6 rounded-xl shadow-md border border-[#334155]">
          <h2 className="text-xl font-semibold mb-4">Cámara en Vivo</h2>
          <LiveCamera />
        </div>

        {/* Subir video */}
        <div className="bg-[#1e293b] p-6 rounded-xl shadow-md border border-[#334155]">
          <h2 className="text-xl font-semibold mb-4">Subir Video</h2>
          <UploadVideo />
        </div>

      </div>
    </div>
  );
}
