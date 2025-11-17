import { Link } from "react-router-dom";

export default function Header() {
    return (
        <header className="w-full bg-[#0f172a] text-white shadow-lg fixed top-0 left-0 z-50">
            <nav className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                <Link
                    to="/"
                    className="text-xl font-semibold tracking-wide"
                >
                    SENATI Uniform Detector
                </Link>
                <div className="flex items-center gap-6 text-sm font-medium">
                    <Link
                        to="/"
                        className="hover:text-blue-400 transition-colors"
                    >
                        Inicio
                    </Link>
                    <Link
                        to="/detector"
                        className="hover:text-blue-400 transition-colors"
                    >
                        Detector
                    </Link>
                    <Link
                        to="/info"
                        className="hover:text-blue-400 transition-colors"
                    >
                        Información
                    </Link>
                </div>
            </nav>
        </header>
    );
}
