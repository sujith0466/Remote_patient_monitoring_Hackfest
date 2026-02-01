import { useNavigate } from "react-router-dom";

export default function SelectRole() {
  const navigate = useNavigate();

  function selectRole(role) {
    localStorage.setItem("carewatch_role", role);
    navigate(`/${role}`, { replace: true });
  }

  return (
    <div className="min-h-[70vh] flex items-center justify-center">
      <div className="bg-white p-8 rounded-xl shadow-md w-full max-w-md text-center">
        <h1 className="text-2xl font-semibold mb-2">Welcome to CareWatch</h1>
        <p className="text-gray-600 mb-6">
          Please select your role to continue
        </p>

        <div className="space-y-4">
          <button
            onClick={() => selectRole("doctor")}
            className="w-full bg-blue-600 text-white py-3 rounded-lg text-lg hover:bg-blue-700 transition"
          >
            🧑‍⚕️ Doctor
          </button>

          <button
            onClick={() => selectRole("nurse")}
            className="w-full bg-green-600 text-white py-3 rounded-lg text-lg hover:bg-green-700 transition"
          >
            👩‍⚕️ Nurse
          </button>
        </div>
      </div>
    </div>
  );
}
