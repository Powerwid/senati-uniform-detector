import { useState } from "react"

const HeroSection = () => {
  const [selectedFile, setSelectedFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [detectionResult, setDetectionResult] = useState(null)

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setSelectedFile(file)
      setPreview(URL.createObjectURL(file))
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return alert("Selecciona una imagen primero.")

    const formData = new FormData()
    formData.append("file", selectedFile)

    try {
      const res = await fetch("/api/detect", {
        method: "POST",
        body: formData,
      })

      const data = await res.json()
      setDetectionResult(data)
    } catch (error) {
      console.error(error)
      alert("Error al detectar el uniforme.")
    }
  }

  return (
    <section className="flex flex-col items-center justify-center py-16 bg-gray-50 min-h-[80vh]">
      <h2 className="text-3xl font-semibold text-gray-800 mb-6">
        Subir imagen para detectar uniforme
      </h2>

      <div className="bg-white p-6 rounded-2xl shadow-md w-[90%] max-w-md flex flex-col items-center">
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="mb-4"
        />

        {preview && (
          <img
            src={preview}
            alt="Vista previa"
            className="rounded-lg mb-4 max-h-64 object-cover"
          />
        )}

        <button
          onClick={handleUpload}
          className="bg-blue-700 hover:bg-blue-800 text-white font-medium py-2 px-4 rounded-lg"
        >
          Detectar uniforme
        </button>

        {detectionResult && (
          <div className="mt-6 w-full text-left">
            <h3 className="font-semibold text-gray-800 mb-2">
              Resultado de detección:
            </h3>
            <pre className="bg-gray-100 p-2 rounded text-sm overflow-x-auto">
              {JSON.stringify(detectionResult, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </section>
  )
}

export default HeroSection
