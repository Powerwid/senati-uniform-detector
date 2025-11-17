import Header from "@layouts/header/header";
import { Outlet } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function App() {
  return (
    <>
      <Header />

      <main className="mt-[60px]">
        <Outlet />
      </main>

      {/* CONTENEDOR DE NOTIFICACIONES */}
      <ToastContainer
        position="top-center"
        theme="dark"
        autoClose={2000}
        pauseOnHover={false}
        hideProgressBar={false}
      />
    </>
  );
}

export default App;
