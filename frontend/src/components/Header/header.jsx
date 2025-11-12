import { FaTshirt } from "react-icons/fa"

const Header = () => {
  return (
    <header className="w-full bg-blue-700 text-white shadow-md">
      <div className="max-w-7xl mx-auto flex items-center justify-between py-4 px-6">
        <div className="flex items-center gap-2">
          <FaTshirt className="text-2xl" />
          <h1 className="text-xl font-semibold">SENATI Uniform Detector</h1>
        </div>
        <nav className="flex gap-4 text-sm font-medium">
          <a href="#" className="hover:text-gray-200">Inicio</a>
          <a href="#" className="hover:text-gray-200">Documentación</a>
          <a href="#" className="hover:text-gray-200">Contacto</a>
        </nav>
      </div>
    </header>
  )
}

export default Header
